# copied from crawl4ai 0.6.3
# modified by bigbrother666sh 2025-05-24

import os
import aiosqlite
import asyncio
from typing import Optional, Dict
from contextlib import asynccontextmanager
import json  
from .wis.base.crawl4ai_models import CrawlResult
import aiofiles
from .tools.general_utils import get_logger
from .wis.utils import ensure_content_dirs, generate_content_hash


base_directory = os.path.join(
    os.getenv("PROJECT_DIR", "work_dir"), ".wis"
)
os.makedirs(base_directory, exist_ok=True)
wis_logger = get_logger(base_directory, "wiseflow_info_scraper")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "pb", "pb_data")

class AsyncDatabaseManager:
    def __init__(self, pool_size: int = 12, max_retries: int = 3):
        self.content_paths = ensure_content_dirs(DB_PATH)
        self.db_path = os.path.join(DB_PATH, "wiseflow_info_scraper.db")
        self.pool_size = pool_size
        self.max_retries = max_retries
        self.connection_pool: Dict[int, aiosqlite.Connection] = {}
        self.pool_lock = asyncio.Lock()
        self.init_lock = asyncio.Lock()
        self.connection_semaphore = asyncio.Semaphore(pool_size)
        self._initialized = False


    async def initialize(self):
        """Initialize the database and connection pool"""
        try:
            wis_logger.debug("Initializing database")

            # Always ensure base table exists
            await self.ainit_db()

            # Verify the table exists
            async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
                async with db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='crawled_data'"
                ) as cursor:
                    result = await cursor.fetchone()
                    if not result:
                        # todo try to create the table
                        raise Exception("crawled_data table was not created")
            """
            if needs_update:
                self.logger.info("New version detected, running updates", tag="INIT")
                await self.update_db_schema()
                from .wis.migrations import (
                    run_migration,
                )  # Import here to avoid circular imports

                await run_migration()
                self.version_manager.update_version()  # Update stored version after successful migration
                self.logger.success(
                    "Version update completed successfully", tag="COMPLETE"
                )
            else:
                self.logger.success(
                    "Database initialization completed successfully", tag="COMPLETE"
                )
            """
        except Exception as e:
            wis_logger.error(f"Database initialization error: {str(e)}")
            wis_logger.info("Database will be initialized on first use")
            raise

    async def cleanup(self):
        """Cleanup connections when shutting down"""
        async with self.pool_lock:
            for conn in self.connection_pool.values():
                await conn.close()
            self.connection_pool.clear()

    @asynccontextmanager
    async def get_connection(self):
        """Connection pool manager with enhanced error handling"""
        if not self._initialized:
            async with self.init_lock:
                if not self._initialized:
                    try:
                        await self.initialize()
                        self._initialized = True
                    except Exception as e:
                        wis_logger.error(f"Database initialization failed: {str(e)}")
                        raise

        await self.connection_semaphore.acquire()
        task_id = id(asyncio.current_task())

        try:
            async with self.pool_lock:
                if task_id not in self.connection_pool:
                    try:
                        conn = await aiosqlite.connect(self.db_path, timeout=30.0)
                        await conn.execute("PRAGMA journal_mode = WAL")
                        await conn.execute("PRAGMA busy_timeout = 5000")

                        # Verify database structure
                        async with conn.execute(
                            "PRAGMA table_info(crawled_data)"
                        ) as cursor:
                            columns = await cursor.fetchall()
                            column_names = [col[1] for col in columns]
                            expected_columns = {
                                "url",
                                "html",
                                "cleaned_html",
                                "markdown",
                                "extracted_content",
                                "success",
                                "link_dict",
                                "metadata",
                                "screenshot",
                                "response_headers",
                                "downloaded_files",
                                "redirected_url"
                            }
                            missing_columns = expected_columns - set(column_names)
                            if missing_columns:
                                raise ValueError(
                                    f"Database missing columns: {missing_columns}"
                                )
                        self.connection_pool[task_id] = conn
                    except Exception as e:
                        error_message = f"Unexpected error in db get_connection: {str(e)}"
                        wis_logger.error(error_message)
                        raise

            yield self.connection_pool[task_id]

        except Exception as e:
            error_message = f"Unexpected error in db get_connection: {str(e)}"
            wis_logger.error(error_message)
            raise
        finally:
            async with self.pool_lock:
                if task_id in self.connection_pool:
                    await self.connection_pool[task_id].close()
                    del self.connection_pool[task_id]
            self.connection_semaphore.release()

    async def execute_with_retry(self, operation, *args):
        """Execute database operations with retry logic"""
        for attempt in range(self.max_retries):
            try:
                async with self.get_connection() as db:
                    result = await operation(db, *args)
                    await db.commit()
                    return result
            except Exception as e:
                if attempt == self.max_retries - 1:
                    wis_logger.error(f"Operation failed after {self.max_retries} attempts: {str(e)}")
                    raise
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff

    async def ainit_db(self):
        """Initialize database schema"""
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS crawled_data (
                    url TEXT PRIMARY KEY,
                    html TEXT,
                    cleaned_html TEXT,
                    markdown TEXT,
                    extracted_content TEXT,
                    success BOOLEAN,
                    link_dict TEXT DEFAULT "{}",
                    metadata TEXT DEFAULT "{}",
                    screenshot TEXT DEFAULT "",
                    response_headers TEXT DEFAULT "{}",
                    downloaded_files TEXT DEFAULT "{}",
                    redirected_url TEXT DEFAULT ""
                )
            """
            )
            await db.commit()

    async def update_db_schema(self):
        """Update database schema if needed"""
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            cursor = await db.execute("PRAGMA table_info(crawled_data)")
            columns = await cursor.fetchall()
            column_names = [column[1] for column in columns]

            # List of new columns to add
            new_columns = [
                "link_dict",
                "metadata",
                "screenshot",
                "response_headers",
                "downloaded_files",
                "redirected_url"
            ]

            for column in new_columns:
                if column not in column_names:
                    await self.aalter_db_add_column(column, db)
            await db.commit()

    async def aalter_db_add_column(self, new_column: str, db):
        """Add new column to the database"""
        if new_column == "response_headers":
            await db.execute(
                f'ALTER TABLE crawled_data ADD COLUMN {new_column} TEXT DEFAULT "{{}}"'
            )
        else:
            await db.execute(
                f'ALTER TABLE crawled_data ADD COLUMN {new_column} TEXT DEFAULT ""'
            )
        wis_logger.info(f"Added column '{new_column}' to the database")

    async def aget_cached_url(self, url: str) -> Optional[CrawlResult]:
        """Retrieve cached URL data as CrawlResult"""

        async def _get(db):
            async with db.execute(
                "SELECT * FROM crawled_data WHERE url = ?", (url,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None

                # Get column names
                columns = [description[0] for description in cursor.description]
                # Create dict from row data
                row_dict = dict(zip(columns, row))

                # Load content from files using stored hashes
                content_fields = {
                    "html": row_dict["html"],
                    "cleaned_html": row_dict["cleaned_html"],
                    "markdown": row_dict["markdown"],
                    "link_dict": row_dict["link_dict"],
                    "redirected_url": row_dict["redirected_url"],
                    "extracted_content": row_dict["extracted_content"],
                    "screenshot": row_dict["screenshot"],
                }

                for field, hash_value in content_fields.items():
                    if hash_value:
                        content = await self._load_content(
                            hash_value,
                            field.split("_")[0],  # Get content type from field name
                        )
                        row_dict[field] = content or ""
                    else:
                        row_dict[field] = ""

                # Parse JSON fields
                json_fields = [
                    "link_dict",
                    "metadata",
                    "response_headers",
                ]
                for field in json_fields:
                    try:
                        row_dict[field] = (
                            json.loads(row_dict[field]) if row_dict[field] else {}
                        )
                    except json.JSONDecodeError:
                        row_dict[field] = {}

                # Parse downloaded_files
                try:
                    row_dict["downloaded_files"] = (
                        json.loads(row_dict["downloaded_files"])
                        if row_dict["downloaded_files"]
                        else []
                    )
                except json.JSONDecodeError:
                    row_dict["downloaded_files"] = []

                # Remove any fields not in CrawlResult model
                valid_fields = CrawlResult.__annotations__.keys()
                filtered_dict = {k: v for k, v in row_dict.items() if k in valid_fields}
                # filtered_dict["markdown"] = row_dict["markdown"]
                return CrawlResult(**filtered_dict)

        try:
            return await self.execute_with_retry(_get)
        except Exception as e:
            wis_logger.error(f"Error retrieving cached URL: {str(e)}")
            return None

    async def acache_url(self, result: CrawlResult):
        """Cache CrawlResult data"""
        # Store content files and get hashes
        content_map = {
            "html": (result.html, "html"),
            "cleaned_html": (result.cleaned_html or "", "cleaned"),
            "markdown": (result.markdown or "", "markdown"),
            "link_dict": (result.link_dict or {}, "link_dict"),
            "extracted_content": (result.extracted_content or "", "extracted"),
            "screenshot": (result.screenshot or "", "screenshots"),
        }

        content_hashes = {}
        for field, (content, content_type) in content_map.items():
            content_hashes[field] = await self._store_content(content, content_type)

        async def _cache(db):
            await db.execute(
                """
                INSERT INTO crawled_data (
                    url, html, cleaned_html, markdown,
                    extracted_content, success, link_dict, metadata,
                    screenshot, response_headers, downloaded_files, redirected_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    html = excluded.html,
                    cleaned_html = excluded.cleaned_html,
                    markdown = excluded.markdown,
                    extracted_content = excluded.extracted_content,
                    success = excluded.success,
                    link_dict = excluded.link_dict,
                    metadata = excluded.metadata,
                    screenshot = excluded.screenshot,
                    response_headers = excluded.response_headers,
                    downloaded_files = excluded.downloaded_files,
                    redirected_url = excluded.redirected_url
            """,
                (
                    result.url,
                    content_hashes["html"],
                    content_hashes["cleaned_html"],
                    content_hashes["markdown"],
                    content_hashes["extracted_content"],
                    result.success,
                    content_hashes["link_dict"],
                    json.dumps(result.metadata or {}),
                    content_hashes["screenshot"],
                    json.dumps(result.response_headers or {}),
                    json.dumps(result.downloaded_files or []),
                    result.redirected_url or ""
                ),
            )

        try:
            await self.execute_with_retry(_cache)
        except Exception as e:
            wis_logger.error(f"Error caching URL: {str(e)}")

    async def aget_total_count(self) -> int:
        """Get total number of cached URLs"""

        async def _count(db):
            async with db.execute("SELECT COUNT(*) FROM crawled_data") as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0

        try:
            return await self.execute_with_retry(_count)
        except Exception as e:
            wis_logger.error(f"Error getting total count: {str(e)}")
            return 0

    async def aclear_db(self):
        """Clear all data from the database"""

        async def _clear(db):
            await db.execute("DELETE FROM crawled_data")

        try:
            await self.execute_with_retry(_clear)
        except Exception as e:
            wis_logger.error(f"Error clearing database: {str(e)}")

    async def aflush_db(self):
        """Drop the entire table"""

        async def _flush(db):
            await db.execute("DROP TABLE IF EXISTS crawled_data")

        try:
            await self.execute_with_retry(_flush)
        except Exception as e:
            wis_logger.error(f"Error flushing database: {str(e)}")

    async def _store_content(self, content: str, content_type: str) -> str:
        """Store content in filesystem and return hash"""
        if not content:
            return ""

        content_hash = generate_content_hash(content)
        file_path = os.path.join(self.content_paths[content_type], content_hash)

        # Only write if file doesn't exist
        if not os.path.exists(file_path):
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(content)

        return content_hash

    async def _load_content(
        self, content_hash: str, content_type: str
    ) -> Optional[str]:
        """Load content from filesystem by hash"""
        if not content_hash:
            return None

        file_path = os.path.join(self.content_paths[content_type], content_hash)
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                return await f.read()
        except:
            wis_logger.error(f"Failed to load content: {file_path}")
            return None

# Create a singleton instance
async_db_manager = AsyncDatabaseManager()
