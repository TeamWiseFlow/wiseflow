import random
from typing import Dict, List
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed
import os
import time
import sqlite3
from async_logger import wis_logger, base_directory
from pathlib import Path
from .types import IpInfoModel
from abc import ABC, abstractmethod


class ProxyProvider(ABC):

    cache_db_file = Path(base_directory) / "proxy_cache.db"

    def __init__(
        self, 
        uni_name: str,
        ip_pool_count: int, 
        enable_validate_ip: bool) -> None:

        self.valid_ip_url = "https://echo.apifox.cn/"  # 验证 IP 是否有效的地址
        self.ip_pool_count = ip_pool_count
        self.enable_validate_ip = enable_validate_ip
        self.uni_name = uni_name
        self.ip_pool: List[IpInfoModel] = []
        self.invalid_ips: List[str] = []
        self.logger = wis_logger
        os.makedirs(base_directory, exist_ok=True)
        self._init_db()
        self._load_cached_ips()
    
    def _init_db(self):
        """Initialize the cache database"""
        # Use WAL mode for better concurrency and performance
        with sqlite3.connect(self.cache_db_file) as conn:
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
        with sqlite3.connect(self.cache_db_file) as conn:
            # Use INSERT OR REPLACE to handle both insert and update cases
            conn.execute(
                """INSERT OR REPLACE INTO ip_cache 
                   (provider_name, ip, port, user, password, protocol, expired_time_ts)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (self.uni_name, ip_info.ip, ip_info.port, ip_info.user, 
                 ip_info.password, ip_info.protocol, ip_info.expired_time_ts)
            )

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
        self.logger.debug(f"[{self.uni_name}] Cached {len(ip_infos)} IP infos to database")

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
        deleted_count = 0
        with sqlite3.connect(self.cache_db_file) as conn:
            cursor = conn.execute(
                "DELETE FROM ip_cache WHERE provider_name = ? AND expired_time_ts > 0 AND expired_time_ts < ?", 
                (self.uni_name, current_time)
            )
            deleted_count = cursor.rowcount
            conn.execute("DELETE FROM ip_cache WHERE provider_name = ? AND ip IN ?", (self.uni_name, tuple(self.invalid_ips)))
            deleted_count += conn.rowcount
        
        self.logger.info(f"[{self.uni_name}] Removed {deleted_count} expired and invalid IPs from cache")

    async def _is_valid_proxy(self, proxy: IpInfoModel) -> bool:
        """
        验证代理IP是否有效
        :param proxy:
        :return:
        """
        self.logger.debug(
            f"[ProxyIpPool._is_valid_proxy] testing {proxy.ip} is it valid "
        )
        try:
            httpx_proxy = {
                f"{proxy.protocol}": f"http://{proxy.user}:{proxy.password}@{proxy.ip}:{proxy.port}"
            }
            async with httpx.AsyncClient(proxies=httpx_proxy) as client:
                response = await client.get(self.valid_ip_url)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            self.logger.info(
                f"[ProxyIpPool._is_valid_proxy] testing {proxy.ip} err: {e}"
            )
            raise e

    async def mark_ip_invalid(self, proxy: IpInfoModel):
        """
        标记IP为无效
        :param proxy:
        :return:
        """
        self.logger.info(f"[ProxyIpPool.mark_ip_invalid] mark {proxy.ip} invalid")
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

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def get_proxy(self) -> IpInfoModel:
        """
        从代理池中随机提取一个代理IP
        :return:
        """
        if len(self.ip_pool) < 1:
            await self._supply_new_proxies()

        proxy = random.choice(self.ip_pool)
        self.ip_pool.remove(proxy)  # 取出来一个IP就应该移出掉
        if self.enable_validate_ip:
            if not await self._is_valid_proxy(proxy):
                raise Exception(
                    "[ProxyIpPool.get_proxy] current ip invalid and again get it"
                )
        return proxy
    
    @abstractmethod
    async def _supply_new_proxies(self):
        """
        # Abstract method for obtaining IPs. Different HTTP proxy providers need to implement this method.
        # Each time, fetch self.ip_pool_count new IPs, as this method is only called when ip_pool is empty.
        # Directly add the new IPs to ip_pool and cache them in the database.
        # :return: None
        """
        pass
