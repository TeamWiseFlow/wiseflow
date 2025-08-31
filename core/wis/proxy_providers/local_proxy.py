import json
import os
from typing import List
from .base_proxy import IpInfoModel, ProxyProvider, base_directory
import time

DEFAULT_LOCAL_PROXY_FILE = os.path.join(base_directory, "proxy_setting.json")
"""
You Must give a json file as following format:
[
    {
        "ip": "http://127.0.0.1",
        "port": 8080,
        "user": "user",
        "password": "password",
        "life_time": 17  # in minutes, 0 means never expire
    }
    ...
]
"""

class LocalProxy(ProxyProvider):

    def __init__(self, 
                 uni_name: str,
                 ip_pool_count: int, 
                 enable_validate_ip: bool,
                 local_proxy_file: str = DEFAULT_LOCAL_PROXY_FILE):
        
        super().__init__(uni_name, ip_pool_count, enable_validate_ip)
        self.local_proxy_file = local_proxy_file
    
    async def _supply_new_proxies(self):
        try:
            with open(self.local_proxy_file, "r", encoding="utf-8") as f:
                proxy_list = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load local proxy file: {e}")
            raise Exception(f"Failed to load local proxy file: {e}")
        
        self.clear_all()
        self.ip_pool = []
        for proxy in proxy_list:
            if "ip" not in proxy or "port" not in proxy:
                continue
            if "://" in proxy["ip"]:
                protocol, ip = proxy["ip"].split("://")
            else:
                protocol = "https"
                ip = proxy["ip"]

            port = proxy.get("port")
            user = proxy.get("user", "")
            password = proxy.get("password", "")
            expired_time_ts = proxy.get("life_time", 0) * 60
            if expired_time_ts == 0:
                expired_time_ts = 0
            else:
                expired_time_ts = int(expired_time_ts) + int(time.time())

            ip_info = IpInfoModel(ip=ip, port=port, user=user, password=password, protocol=f"{protocol}://", expired_time_ts=expired_time_ts)
            self.ip_pool.append(ip_info)

        self.cache_ip_infos(self.ip_pool)
