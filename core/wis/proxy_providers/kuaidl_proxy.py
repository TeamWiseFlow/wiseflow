import regex as re
from typing import Dict, List

import httpx
from pydantic import BaseModel, Field

from .base_proxy import IpInfoModel, ProxyProvider
import time

# 快代理的IP代理过期时间向前推移5秒
DELTA_EXPIRED_SECOND = 5

class KuaidailiProxyModel(BaseModel):
    ip: str = Field("ip")
    port: int = Field("端口")
    expire_ts: int = Field("过期时间,单位秒，多少秒后过期")


def parse_kuaidaili_proxy(proxy_info: str) -> KuaidailiProxyModel:
    """
    解析快代理的IP信息
    Args:
        proxy_info:

    Returns:

    """
    proxies: List[str] = proxy_info.split(":")
    if len(proxies) != 2:
        raise Exception("not invalid kuaidaili proxy info")

    pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5}),(\d+)'
    match = re.search(pattern, proxy_info)
    if not match.groups():
        raise Exception("not match kuaidaili proxy info")

    return KuaidailiProxyModel(
        ip=match.groups()[0],
        port=int(match.groups()[1]),
        expire_ts=int(match.groups()[2])
    )


class KuaiDaiLiProxy(ProxyProvider):

    def __init__(self, 
                 uni_name: str,
                 ip_pool_count: int, 
                 enable_validate_ip: bool,
                 kdl_user_name: str, 
                 kdl_user_pwd: str, 
                 kdl_secret_id: str, 
                 kdl_signature: str,
                 clear_all_cache: bool = False):

        self.kdl_user_name = kdl_user_name
        self.kdl_user_pwd = kdl_user_pwd
        self.api_base = "https://dps.kdlapi.com/"
        self.secret_id = kdl_secret_id
        self.signature = kdl_signature
        self.params = {
            "secret_id": self.secret_id,
            "signature": self.signature,
            "pt": 1,
            "format": "json",
            "sep": 1,
            "f_et": 1,
        }
        # Call parent class constructor
        super().__init__(uni_name, ip_pool_count, enable_validate_ip, clear_all_cache)

    async def _supply_new_proxies(self):
        """
        快代理实现
        Args:
            num:

        Returns:

        """
        # 先清理过期和无效的IP
        self._clear()

        uri = "/api/getdps/"
        self.params.update({"num": self.ip_pool_count})
        new_ip_infos: List[IpInfoModel] = []
        async with httpx.AsyncClient() as client:
            response = await client.get(self.api_base + uri, params=self.params)

            if response.status_code != 200:
                self.logger.warning(f"[KuaiDaiLiProxy.get_proxies] statuc code not 200 and response.txt:{response.text}")
                raise Exception("get ip error from proxy provider and status code not 200 ...")

            ip_response: Dict = response.json()
            if ip_response.get("code") != 0:
                self.logger.warning(f"[KuaiDaiLiProxy.get_proxies]  code not 0 and msg:{ip_response.get('msg')}")
                raise Exception("get ip error from proxy provider and  code not 0 ...")
        
            proxy_list: List[str] = ip_response.get("data", {}).get("proxy_list")
            for proxy in proxy_list:
                proxy_model = parse_kuaidaili_proxy(proxy)
                ip_info_model = IpInfoModel(
                    protocol="http",  # 快代理的IP代理协议都是http
                    ip=proxy_model.ip,
                    port=proxy_model.port,
                    user=self.kdl_user_name,
                    password=self.kdl_user_pwd,
                    expired_time_ts=proxy_model.expire_ts + int(time.time()) - DELTA_EXPIRED_SECOND,
                )
                new_ip_infos.append(ip_info_model)

        # Cache the newly obtained IPs
        if new_ip_infos:
            self.cache_ip_infos(new_ip_infos)
            
        self.ip_pool.extend(new_ip_infos)
