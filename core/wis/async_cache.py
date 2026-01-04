import asyncio
import gzip
import json
import time
from pathlib import Path
from typing import Any, List, Optional, Tuple

import aiosqlite

from core.async_logger import wis_logger, base_directory


DEFAULT_CACHE_DIR = base_directory / "wis_cache"
MAIN_CACHE_FILE = DEFAULT_CACHE_DIR / "main_cache.sqlite"


class ValueTooLargeError(Exception):
    pass


def _utc_now_seconds() -> int:
    return int(time.time())


def _serialize_value(value: Any) -> Tuple[bytes, str]:
    """Serialize Python value to bytes with format marker.

    Returns:
        (payload_bytes, value_format)
    value_format in {"json", "bytes"}
    """
    if isinstance(value, (bytes, bytearray, memoryview)):
        return (bytes(value), "bytes")
    # Fallback to JSON for str, dict, list, int, float, bool, None
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), "json")


def _deserialize_value(payload: bytes, value_format: str) -> Any:
    if value_format == "bytes":
        return payload
    # json
    return json.loads(payload.decode("utf-8"))


def _to_sql_like(pattern: str) -> str:
    """Translate simple glob-like pattern to SQL LIKE pattern.

    '*' => '%', '?' => '_'.
    Note: We intentionally do not escape existing '%' or '_' to keep behavior simple.
    """
    return pattern.replace("*", "%").replace("?", "_")


class SqliteCache:
    """An async SQLite-backed key-value cache with TTL, namespace, and optional gzip compression.

    TTL unit: minutes. TTL == 0 means never expires.

    Table schema (cache_items):
        namespace TEXT NOT NULL,
        key TEXT NOT NULL,
        value_blob BLOB NOT NULL,
        value_format TEXT NOT NULL,   -- json | bytes
        compression TEXT NOT NULL,    -- none | gzip
        size_bytes INTEGER NOT NULL,
        expires_at INTEGER NOT NULL,  -- Unix seconds; 0 means never expire
        created_at INTEGER NOT NULL,
        UNIQUE(namespace, key)
    Indexes:
        idx_cache_expires_at(expires_at)
    """

    def __init__(
        self,
        db_path: Path,
        default_namespace: Optional[str] = None,
        gzip_threshold_bytes: int = 32 * 1024,
        max_item_bytes: int = 10 * 1024 * 1024,
        busy_timeout_ms: int = 3000,
        cleanup_interval_seconds: int = 60,
        autostart_cleanup_task: bool = False,
    ) -> None:
        # default_namespace is optional; callers may provide namespace per-call
        self.default_namespace = default_namespace
        self.db_path = db_path
        self.gzip_threshold_bytes = int(gzip_threshold_bytes)
        self.max_item_bytes = int(max_item_bytes)
        self.busy_timeout_ms = int(busy_timeout_ms)
        self.cleanup_interval_seconds = int(cleanup_interval_seconds)
        self.autostart_cleanup_task = autostart_cleanup_task

        self._connection: Optional[aiosqlite.Connection] = None
        self._write_lock = asyncio.Lock()  # serialize writes and cleanup
        self._cleanup_task: Optional[asyncio.Task] = None
        self._closed = True

    def _resolve_namespace(self, namespace: Optional[str]) -> str:
        ns = namespace or self.default_namespace
        if not ns:
            raise ValueError("namespace must be provided either per-call or as default_namespace in constructor")
        return ns

    # -------------- lifecycle --------------
    async def open(self) -> None:
        if self._connection is not None and not self._closed:
            return

        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._connection = await aiosqlite.connect(self.db_path, timeout=self.busy_timeout_ms / 1000.0)
        self._connection.row_factory = aiosqlite.Row

        # PRAGMA for WAL, performance and safety
        # Note: execute PRAGMA one by one for clarity
        pragmas = [
            "PRAGMA journal_mode=WAL;",
            "PRAGMA synchronous=NORMAL;",
            f"PRAGMA busy_timeout={self.busy_timeout_ms};",
            "PRAGMA wal_autocheckpoint=1000;",
            "PRAGMA temp_store=MEMORY;",
            "PRAGMA secure_delete=ON;",
        ]
        for stmt in pragmas:
            try:
                await self._connection.execute(stmt)
            except Exception as e:
                wis_logger.warning(f"Failed to set PRAGMA '{stmt}': {e}")

        await self._initialize_schema()
        await self._connection.commit()
        self._closed = False

        # Initial cleanup at startup
        try:
            cleaned_count = await self._cleanup_expired_items_batch()
            wis_logger.debug(f"auto cleanup deleted {cleaned_count} expired items at startup")
            await self._connection.commit()
        except Exception as e:
            wis_logger.warning(f"Initial cleanup failed: {e}")

        if self.autostart_cleanup_task:
            task_ns = self.default_namespace or "*"
            self._cleanup_task = asyncio.create_task(self._cleanup_loop(), name=f"SqliteCacheCleanup[{task_ns}]")

    async def close(self) -> None:
        if self._closed:
            return
        try:
            # Final cleanup on shutdown
            cleaned_count = await self._cleanup_expired_items_batch()
            wis_logger.debug(f"auto cleanup deleted {cleaned_count} expired items at shutdown")
            await self._connection.commit()
        except Exception as e:
            wis_logger.warning(f"Final cleanup failed: {e}")

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                wis_logger.warning(f"Cleanup task termination error: {e}")
            self._cleanup_task = None

        if self._connection is not None:
            await self._connection.close()
            self._connection = None

        self._closed = True

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    # -------------- public API --------------
    async def get(
        self,
        key: str,
        namespace: Optional[str] = None,
        include_expires_at: bool = False,
    ) -> Optional[Any]:
        """Get value by key; if expired, delete and return None.

        Args:
            key: Cache key.
            namespace: Optional namespace; defaults to the cache's default namespace.
            include_expires_at: If True, return a tuple `(value, expires_at)` where
                `expires_at` is the item's expiration unix timestamp in seconds
                (0 means never expires). If False, return only the stored value.
        """
        await self._ensure_open()
        now = _utc_now_seconds()
        ns = self._resolve_namespace(namespace)

        assert self._connection is not None
        cursor = await self._connection.execute(
            """
            SELECT value_blob, value_format, compression, expires_at
            FROM cache_items
            WHERE namespace = ? AND key = ?
            """,
            (ns, key),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            return None

        expires_at = int(row["expires_at"]) if row["expires_at"] is not None else 0
        if expires_at != 0 and expires_at < now:
            # expired: delete and return None
            await self.delete(key, namespace=ns)
            return None

        payload: bytes = row["value_blob"]
        compression: str = row["compression"]
        value_format: str = row["value_format"]
        if compression == "gzip":
            try:
                payload = gzip.decompress(payload)
            except Exception as e:
                wis_logger.warning(f"Failed to gunzip key={key}: {e}")
                return None
        try:
            value = _deserialize_value(payload, value_format)
            if include_expires_at:
                return (value, expires_at)
            return value
        except Exception as e:
            wis_logger.warning(f"Failed to decode value for key={key}: {e}")
            return None

    async def set(self, key: str, value: Any, expire_time: int, namespace: Optional[str] = None) -> None:
        """Set a value with TTL in minutes. If expire_time == 0, the entry never expires."""
        await self._ensure_open()
        ns = self._resolve_namespace(namespace)

        # Normalize empty-like values to a unified marker
        if not value:
            normalized_value = "**empty**"
        else:
            normalized_value = value

        payload, value_format = _serialize_value(normalized_value)
        if len(payload) > self.max_item_bytes:
            wis_logger.warning(
                f"Value size {len(payload)} exceeds max_item_bytes {self.max_item_bytes}, reject to save"
            )
            return

        compression = "none"
        raw_size = len(payload)
        if raw_size >= self.gzip_threshold_bytes:
            try:
                payload = gzip.compress(payload)
                compression = "gzip"
            except Exception as e:
                wis_logger.warning(f"gzip failed for key={key} (store uncompressed). Error: {e}")
                compression = "none"
        stored_size = len(payload)

        # TTL in minutes -> expires_at (seconds). 0 means never expire
        now = _utc_now_seconds()
        if expire_time and expire_time > 0:
            expires_at = now + int(expire_time) * 60
        else:
            expires_at = 0

        created_at = now

        assert self._connection is not None
        async with self._write_lock:
            await self._connection.execute(
                """
                INSERT INTO cache_items(namespace, key, value_blob, value_format, compression, size_bytes, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(namespace, key) DO UPDATE SET
                    value_blob=excluded.value_blob,
                    value_format=excluded.value_format,
                    compression=excluded.compression,
                    size_bytes=excluded.size_bytes,
                    expires_at=excluded.expires_at,
                    created_at=excluded.created_at
                """,
                (
                    ns,
                    key,
                    payload,
                    value_format,
                    compression,
                    stored_size,
                    expires_at,
                    created_at,
                ),
            )
            await self._connection.commit()

    async def delete(self, key: str, namespace: Optional[str] = None) -> None:
        await self._ensure_open()
        ns = self._resolve_namespace(namespace)
        assert self._connection is not None
        async with self._write_lock:
            await self._connection.execute(
                "DELETE FROM cache_items WHERE namespace = ? AND key = ?",
                (ns, key),
            )
            await self._connection.commit()

    async def keys(self, pattern: str = "*", namespace: Optional[str] = None) -> List[str]:
        """List keys matching pattern for non-expired entries only.

        Pattern supports '*' and '?' wildcards.
        """
        await self._ensure_open()
        ns = self._resolve_namespace(namespace)
        like = _to_sql_like(pattern)
        now = _utc_now_seconds()
        assert self._connection is not None
        cursor = await self._connection.execute(
            """
            SELECT key FROM cache_items
            WHERE namespace = ?
              AND (expires_at = 0 OR expires_at >= ?)
              AND key LIKE ?
            ORDER BY key
            """,
            (ns, now, like),
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return [row["key"] for row in rows]

    async def ttl(self, key: str, namespace: Optional[str] = None) -> int:
        """Return remaining TTL in minutes.

        Returns:
            -1 if the key does not exist or is expired,
            0 if the key has no expiration,
            otherwise remaining minutes (integer, ceil to the next minute if seconds remainder > 0).
        """
        await self._ensure_open()
        ns = self._resolve_namespace(namespace)
        now = _utc_now_seconds()
        assert self._connection is not None
        cursor = await self._connection.execute(
            "SELECT expires_at FROM cache_items WHERE namespace = ? AND key = ?",
            (ns, key),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            return -1
        expires_at = int(row["expires_at"]) if row["expires_at"] is not None else 0
        if expires_at == 0:
            return -1
        if expires_at < now:
            # best-effort cleanup of the single key
            await self.delete(key, namespace=ns)
            return -1
        remaining_seconds = expires_at - now
        # Convert to minutes, rounding up any remaining seconds
        minutes = (remaining_seconds + 59) // 60
        return int(minutes)

    async def update_ttl(self, key: str, expire_time: int, namespace: Optional[str] = None) -> bool:
        """Update TTL for an existing cache entry.
        
        Args:
            key: Cache key to update.
            expire_time: New TTL in minutes. 0 means never expires.
            namespace: Optional namespace; defaults to the cache's default namespace.
            
        Returns:
            True if the key existed and was updated, False if key was not found.
        """
        await self._ensure_open()
        ns = self._resolve_namespace(namespace)
        
        # Convert TTL in minutes to expires_at (seconds). 0 means never expire
        now = _utc_now_seconds()
        if expire_time and expire_time > 0:
            expires_at = now + int(expire_time) * 60
        else:
            expires_at = 0
            
        assert self._connection is not None
        async with self._write_lock:
            cursor = await self._connection.execute(
                """
                UPDATE cache_items 
                SET expires_at = ?
                WHERE namespace = ? AND key = ?
                """,
                (expires_at, ns, key),
            )
            await self._connection.commit()
            return (cursor.rowcount or 0) > 0

    # -------------- internals --------------
    async def _initialize_schema(self) -> None:
        assert self._connection is not None
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cache_items (
                namespace   TEXT NOT NULL,
                key         TEXT NOT NULL,
                value_blob  BLOB NOT NULL,
                value_format TEXT NOT NULL,
                compression  TEXT NOT NULL,
                size_bytes   INTEGER NOT NULL,
                expires_at   INTEGER NOT NULL,
                created_at   INTEGER NOT NULL,
                UNIQUE(namespace, key)
            )
            """
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_cache_expires_at ON cache_items(expires_at)"
        )

    async def _cleanup_expired_items_batch(self, batch_size: int = 1000) -> int:
        """Delete up to batch_size expired items.

        We use rowid IN (SELECT ...) form to support LIMIT in older SQLite versions.
        """
        assert self._connection is not None
        now = _utc_now_seconds()
        async with self._write_lock:
            cursor = await self._connection.execute(
                """
                DELETE FROM cache_items
                WHERE rowid IN (
                    SELECT rowid FROM cache_items
                    WHERE expires_at > 0 AND expires_at < ?
                    LIMIT ?
                )
                """,
                (now, batch_size),
            )
            await self._connection.commit()
            return cursor.rowcount or 0

    async def _cleanup_loop(self) -> None:
        try:
            while not self._closed:
                try:
                    # drain expired entries in small batches
                    total_deleted = 0
                    while True:
                        deleted = await self._cleanup_expired_items_batch()
                        total_deleted += deleted
                        if deleted == 0:
                            break
                    if total_deleted:
                        wis_logger.debug(
                            f"[SqliteCache.cleanup] default_namespace={self.default_namespace or '*'} deleted={total_deleted}"
                        )
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    wis_logger.warning(f"Background cleanup error: {e}")

                await asyncio.sleep(self.cleanup_interval_seconds)
        except asyncio.CancelledError:
            # graceful termination
            pass

    async def _ensure_open(self) -> None:
        if self._closed or self._connection is None:
            raise RuntimeError("SqliteCache is not open. Call 'await open()' or use 'async with'.")
