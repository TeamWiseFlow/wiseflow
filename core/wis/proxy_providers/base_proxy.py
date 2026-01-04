import random
from typing import List
import httpx
import asyncio
import time
import sqlite3
from core.async_logger import wis_logger, base_directory
from .types import IpInfoModel
from abc import ABC, abstractmethod
from ..ws_connect import notify_user


class ProxyProvider(ABC):

    cache_db_file = base_directory / "proxy_cache.db"

    def __init__(
        self, 
        uni_name: str,
        ip_pool_count: int, 
        enable_validate_ip: bool,
        clear_all_cache: bool = False) -> None:

        self.valid_ip_url = "https://shouxiqingbaoguan.com/"  # 验证 IP 是否有效的地址
        self.ip_pool_count = ip_pool_count
        self.enable_validate_ip = enable_validate_ip
        self.uni_name = uni_name
        self.ip_pool: List[IpInfoModel] = []
        self.invalid_ips: List[str] = []
        self.logger = wis_logger
        self._init_db()
        self._load_cached_ips()
        if clear_all_cache:
            self.clear_all()
    
    def _init_db(self):
        """Initialize the cache database"""
        # Use WAL mode for better concurrency and performance
        with sqlite3.connect(self.cache_db_file, timeout=10.0) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ip_cache (
                    provider_name TEXT NOT NULL,
                    ip TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    user TEXT NOT NULL,
                    password TEXT NOT NULL,
                    protocol TEXT NOT NULL,
                    expired_time_ts INTEGER NOT NULL,
                    PRIMARY KEY (provider_name, ip, port, user)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expired_time ON ip_cache(expired_time_ts)")

    def _cache_ipinfo(self, ip_info: IpInfoModel):
        """Cache IpInfoModel to database"""
        for attempt in range(3):
            try:
                with sqlite3.connect(self.cache_db_file, timeout=10.0) as conn:
                    # Use INSERT OR REPLACE to handle both insert and update cases
                    conn.execute(
                        """INSERT OR REPLACE INTO ip_cache 
                           (provider_name, ip, port, user, password, protocol, expired_time_ts)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (self.uni_name, ip_info.ip, ip_info.port, ip_info.user, 
                         ip_info.password, ip_info.protocol, ip_info.expired_time_ts)
                    )
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < 2:
                    time.sleep(0.1 * (attempt + 1))  # 递增等待时间
                    continue
                else:
                    self.logger.warning(f"Database operation failed: {e}")
                    # raise

    def _load_cached_ips(self):
        """Load cached IPs from database, remove expired ones, and add valid ones to ip_pool"""
        current_time = int(time.time())
        
        with sqlite3.connect(self.cache_db_file) as conn:
            # Delete expired entries (expired_time_ts=0 means never expire)
            conn.execute(
                "DELETE FROM ip_cache WHERE expired_time_ts > 0 AND expired_time_ts < ?",
                (current_time,)
            )
            
            # Load valid IPs for this provider (expired_time_ts=0 means never expire)
            cursor = conn.execute(
                """SELECT ip, port, user, password, protocol, expired_time_ts 
                   FROM ip_cache 
                   WHERE provider_name = ? AND (expired_time_ts = 0 OR expired_time_ts > ?)""",
                (self.uni_name, current_time)
            )
            
            for row in cursor.fetchall():
                ip_info = IpInfoModel(
                    ip=row[0],
                    port=row[1], 
                    user=row[2],
                    password=row[3],
                    protocol=row[4],
                    expired_time_ts=row[5]
                )
                self.ip_pool.append(ip_info)
        
        self.logger.debug(f"[{self.uni_name}] Loaded {len(self.ip_pool)} cached IPs from database")

    def cache_ip_infos(self, ip_infos: List[IpInfoModel]):
        """Cache multiple IpInfoModel instances to database"""
        for ip_info in ip_infos:
            self._cache_ipinfo(ip_info)

    def clear_all(self):
        """Clear all cached IPs for this provider"""
        with sqlite3.connect(self.cache_db_file) as conn:
            conn.execute("DELETE FROM ip_cache WHERE provider_name = ?", (self.uni_name,))
        self.logger.info(f"[{self.uni_name}] Cleared all cached IPs")

    def _clear(self):
        """
        1. Remove only expired entries from cache (expired_time_ts=0 means never expire)
        2. Remove invalid ips from database
        """
        current_time = int(time.time())
        with sqlite3.connect(self.cache_db_file) as conn:
            cursor = conn.execute(
                "DELETE FROM ip_cache WHERE provider_name = ? AND expired_time_ts > 0 AND expired_time_ts < ?", 
                (self.uni_name, current_time)
            )
            
            # Handle invalid IPs deletion only if there are any invalid IPs
            if self.invalid_ips:
                # Create placeholders for the IN clause
                placeholders = ','.join('?' * len(self.invalid_ips))
                query = f"DELETE FROM ip_cache WHERE provider_name = ? AND ip IN ({placeholders})"
                cursor = conn.execute(query, (self.uni_name, *self.invalid_ips))

    async def _is_valid_proxy(self, proxy: IpInfoModel) -> bool:
        """
        验证代理IP是否有效
        :param proxy:
        :return:
        """
        self.logger.debug(
            f"[ProxyIpPool._is_valid_proxy] testing {proxy.ip}:{proxy.port} is it valid "
        )
        try:
            httpx_proxy = f"{proxy.protocol}://{proxy.user}:{proxy.password}@{proxy.ip}:{proxy.port}"
            async with httpx.AsyncClient(proxy=httpx_proxy) as client:
                response = await client.get(self.valid_ip_url)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            self.logger.info(
                f"[ProxyIpPool._is_valid_proxy] testing {proxy.ip}:{proxy.port} err: {e}"
            )
            return False

    async def mark_ip_invalid(self, proxy: IpInfoModel):
        """
        标记IP为无效
        :param proxy:
        :return:
        """
        self.logger.info(f"[ProxyIpPool.mark_ip_invalid] mark {proxy.ip}:{proxy.port} invalid")
        for p in self.ip_pool:
            if (
                p.ip == proxy.ip
                and p.port == proxy.port
                and p.protocol == proxy.protocol
                and p.user == proxy.user
                and p.password == proxy.password
            ):
                self.ip_pool.remove(p)
                self.invalid_ips.append(p.ip)
                break

    # 这里错误全部内部处理、通知用户，不反馈上层 （这都属于不影响大 loop 的执行层）
    async def get_proxy(self) -> IpInfoModel | None:
        """
        从代理池中随机提取一个代理IP
        :return: IpInfoModel if successful, None if all 3 attempts failed
        fall back to None
        """
        for attempt in range(3):
            try:
                if len(self.ip_pool) < 1:
                    await self._supply_new_proxies()

                proxy = random.choice(self.ip_pool)
                self.ip_pool.remove(proxy)  # 取出来一个IP就应该移出掉
                
                if self.enable_validate_ip:
                    if not await self._is_valid_proxy(proxy):
                        await self.mark_ip_invalid(proxy)
                        self.logger.info(
                            f"[ProxyIpPool.get_proxy] Attempt {attempt + 1}/3: "
                            f"proxy {proxy.ip}:{proxy.port} is invalid, retrying..."
                        )
                        if attempt < 2:  # 不是最后一次尝试，等待1秒
                            await asyncio.sleep(1)
                        continue
                
                return proxy
                
            except Exception as e:
                self.logger.info(
                    f"[ProxyIpPool.get_proxy] Attempt {attempt + 1}/3 failed: {e}"
                )
                if attempt < 2:  # 不是最后一次尝试，等待1秒
                    await asyncio.sleep(1)
                continue
        
        self.logger.warning("[ProxyIpPool.get_proxy] All 3 attempts failed")
        await notify_user(23, [self.uni_name])
        return None
    
    @abstractmethod
    async def _supply_new_proxies(self):
        """
        # Abstract method for obtaining IPs. Different HTTP proxy providers need to implement this method.
        # Each time, fetch self.ip_pool_count new IPs, as this method is only called when ip_pool is empty.
        # Directly add the new IPs to ip_pool and cache them in the database.
        # :return: None
        """
        pass
