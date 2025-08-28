import regex as re
from typing import Dict, List

import httpx
from pydantic import BaseModel, Field

from ..config.proxy_config import KDL_SECERT_ID, KDL_SIGNATURE, KDL_USER_NAME, KDL_USER_PWD
from .base_proxy import IpInfoModel, ProxyProvider
import time

class UseInputProxy(ProxyProvider):

    def __init__(self, 
                 uni_name: str,
                 ip_pool_count: int, 
                 enable_validate_ip: bool):
        
        super().__init__(uni_name, ip_pool_count, enable_validate_ip)
    
    async def _supply_new_proxies(self):
        # 先清理过期和无效的IP
        self._clear()
        new_ip_infos: List[IpInfoModel] = []
        for i in range(self.ip_pool_count):
            print(f"请输入第{i+1}个代理IP信息")
            ip = input("请输入IP（仅 ip 地址）: ")
            port = input("请输入端口（没有请回车）: ")
            user = input("请输入用户名（没有请回车）: ")
            password = input("请输入密码（没有请回车）: ")
            protocol = input("请输入协议（没有请回车）: ")
            if protocol == "":
                protocol = "https://"
            expired_time_ts = input("请输入代理生命周期（单位秒，没有请回车）: ")
            if expired_time_ts == "":
                expired_time_ts = 0
            else:
                expired_time_ts = int(expired_time_ts) + int(time.time())
            ip_info = IpInfoModel(ip=ip, port=port, user=user, password=password, protocol=protocol, expired_time_ts=expired_time_ts)
            new_ip_infos.append(ip_info)

        self.cache_ip_infos(new_ip_infos)
        self.ip_pool = new_ip_infos
