import sqlite3
import os
import time
import hashlib
from urllib.parse import urlparse
import aiohttp
from urllib.robotparser import RobotFileParser


class RobotsParser:
    # Default 7 days cache TTL
    CACHE_TTL = 7 * 24 * 60 * 60

    def __init__(self, cache_dir, cache_ttl=None):
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl or self.CACHE_TTL
        os.makedirs(self.cache_dir, exist_ok=True)
        self.db_path = os.path.join(self.cache_dir, "robots_cache.db")
        self._init_db()

    def _init_db(self):
        # Use WAL mode for better concurrency and performance
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS robots_cache (
                    domain TEXT PRIMARY KEY,
                    rules TEXT NOT NULL,
                    fetch_time INTEGER NOT NULL,
                    hash TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_domain ON robots_cache(domain)")

    def _get_cached_rules(self, domain: str) -> tuple[str, bool]:
        """Get cached rules. Returns (rules, is_fresh)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT rules, fetch_time, hash FROM robots_cache WHERE domain = ?", 
                (domain,)
            )
            result = cursor.fetchone()
            
            if not result:
                return None, False
                
            rules, fetch_time, _ = result
            # Check if cache is still fresh based on TTL
            return rules, (time.time() - fetch_time) < self.cache_ttl

    def _cache_rules(self, domain: str, content: str):
        """Cache robots.txt content with hash for change detection"""
        hash_val = hashlib.md5(content.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            # Check if content actually changed
            cursor = conn.execute(
                "SELECT hash FROM robots_cache WHERE domain = ?", 
                (domain,)
            )
            result = cursor.fetchone()
            
            # Only update if hash changed or no previous entry
            if not result or result[0] != hash_val:
                conn.execute(
                    """INSERT OR REPLACE INTO robots_cache 
                       (domain, rules, fetch_time, hash) 
                       VALUES (?, ?, ?, ?)""",
                    (domain, content, int(time.time()), hash_val)
                )

    async def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """
        Check if URL can be fetched according to robots.txt rules.
        
        Args:
            url: The URL to check
            user_agent: User agent string to check against (default: "*")
            
        Returns:
            bool: True if allowed, False if disallowed by robots.txt
        """
        # Handle empty/invalid URLs
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if not domain:
                return True
        except Exception as _ex:
            return True

        # Fast path - check cache first
        rules, is_fresh = self._get_cached_rules(domain)
        
        # If rules not found or stale, fetch new ones
        if not is_fresh:
            try:
                # Ensure we use the same scheme as the input URL
                scheme = parsed.scheme or 'http'
                robots_url = f"{scheme}://{domain}/robots.txt"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(robots_url, timeout=2) as response:
                        if response.status == 200:
                            rules = await response.text()
                            self._cache_rules(domain, rules)
                        else:
                            return True
            except Exception as _ex:
                # On any error (timeout, connection failed, etc), allow access
                return True

        if not rules:
            return True

        # Create parser for this check
        parser = RobotFileParser() 
        parser.parse(rules.splitlines())
        
        # If parser can't read rules, allow access
        if not parser.mtime():
            return True
            
        return parser.can_fetch(user_agent, url)

    def clear_cache(self):
        """Clear all cached robots.txt entries"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM robots_cache")

    def clear_expired(self):
        """Remove only expired entries from cache"""
        with sqlite3.connect(self.db_path) as conn:
            expire_time = int(time.time()) - self.cache_ttl
            conn.execute("DELETE FROM robots_cache WHERE fetch_time < ?", (expire_time,))