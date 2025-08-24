import regex as re
from typing import Dict, List

import httpx
from pydantic import BaseModel, Field

from wis.config.proxy_config import KDL_SECERT_ID, KDL_SIGNATURE, KDL_USER_NAME, KDL_USER_PWD
from ..base_proxy import IpCache, IpInfoModel, ProxyProvider
from ..types import ProviderNameEnum
from wis.mc.pkg.tools.utils import get_unix_timestamp
from async_logger import wis_logger as logger

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

    def __init__(self, kdl_user_name: str, kdl_user_pwd: str, kdl_secret_id: str, kdl_signature: str):
        """

        Args:
            kdl_user_name:
            kdl_user_pwd:
        """
        self.kdl_user_name = kdl_user_name
        self.kdl_user_pwd = kdl_user_pwd
        self.api_base = "https://dps.kdlapi.com/"
        self.secret_id = kdl_secret_id
        self.signature = kdl_signature
        self.ip_cache = IpCache()
        self.proxy_brand_name = ProviderNameEnum.KUAI_DAILI_PROVIDER.value
        self.params = {
            "secret_id": self.secret_id,
            "signature": self.signature,
            "pt": 1,
            "format": "json",
            "sep": 1,
            "f_et": 1,
        }

    async def get_proxies(self, num: int) -> List[IpInfoModel]:
        """
        快代理实现
        Args:
            num:

        Returns:

        """
        uri = "/api/getdps/"

        # 优先从缓存中拿 IP
        ip_cache_list = await self.ip_cache.load_all_ip(proxy_brand_name=self.proxy_brand_name)
        if len(ip_cache_list) >= num:
            return ip_cache_list[:num]

        # 如果缓存中的数量不够，从IP代理商获取补上，再存入缓存中
        need_get_count = num - len(ip_cache_list)
        self.params.update({"num": need_get_count})

        ip_infos: List[IpInfoModel] = []
        async with httpx.AsyncClient() as client:
            response = await client.get(self.api_base + uri, params=self.params)

            if response.status_code != 200:
                logger.warning(f"[KuaiDaiLiProxy.get_proxies] statuc code not 200 and response.txt:{response.text}")
                raise Exception("get ip error from proxy provider and status code not 200 ...")

            ip_response: Dict = response.json()
            if ip_response.get("code") != 0:
                logger.warning(f"[KuaiDaiLiProxy.get_proxies]  code not 0 and msg:{ip_response.get('msg')}")
                raise Exception("get ip error from proxy provider and  code not 0 ...")

            proxy_list: List[str] = ip_response.get("data", {}).get("proxy_list")
            for proxy in proxy_list:
                proxy_model = parse_kuaidaili_proxy(proxy)
                ip_info_model = IpInfoModel(
                    ip=proxy_model.ip,
                    port=proxy_model.port,
                    user=self.kdl_user_name,
                    password=self.kdl_user_pwd,
                    expired_time_ts=proxy_model.expire_ts + get_unix_timestamp() - DELTA_EXPIRED_SECOND,
                )
                ip_key = f"{self.proxy_brand_name}_{ip_info_model.ip}_{ip_info_model.port}"
                await self.ip_cache.set_ip(ip_key, ip_info_model.model_dump_json(), ex=proxy_model.expire_ts - DELTA_EXPIRED_SECOND)
                ip_infos.append(ip_info_model)

        return ip_cache_list + ip_infos

    async def mark_ip_invalid(self, ip_info: IpInfoModel) -> None:
        """
        标记IP为无效
        Args:
            ip_info:

        Returns:

        """
        ip_key = f"{self.proxy_brand_name}_{ip_info.ip}_{ip_info.port}"
        await self.ip_cache.delete_ip(ip_key)


def new_kuai_daili_proxy() -> KuaiDaiLiProxy:
    """
    构造快代理HTTP实例
    Returns:

    """
    return KuaiDaiLiProxy(
        kdl_secret_id=KDL_SECERT_ID,
        kdl_signature=KDL_SIGNATURE,
        kdl_user_name=KDL_USER_NAME,
        kdl_user_pwd=KDL_USER_PWD,
    )
