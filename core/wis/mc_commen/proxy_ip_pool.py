# don't be evil
# for commercial use, please contact to get permission
# wiseflow opensouce do not support commercial use since 4.0

import random
from typing import List

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from .field import IpInfoModel
from .account_pool import wis_logger


class ProxyIpPool:
    def __init__(
        self, ip_pool_count: int, enable_validate_ip: bool
    ) -> None:
        """

        Args:
            ip_pool_count:
            enable_validate_ip:
            ip_provider:
        """
        self.valid_ip_url = "https://echo.apifox.cn/"  # 验证 IP 是否有效的地址
        self.ip_pool_count = ip_pool_count
        self.enable_validate_ip = enable_validate_ip
        self.proxy_list: List[IpInfoModel] = []

    async def load_proxies(self) -> None:
        """
        加载IP代理
        Returns:
        !!! here we will add the proxy serve in next version
        """
        # todo: load proxies from wiseflow server
        self.proxy_list = []

    async def _is_valid_proxy(self, proxy: IpInfoModel) -> bool:
        """
        验证代理IP是否有效
        :param proxy:
        :return:
        """
        wis_logger.info(
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
            wis_logger.warning(
                f"[ProxyIpPool._is_valid_proxy] testing {proxy.ip} err: {e}"
            )
            raise e

    async def mark_ip_invalid(self, proxy: IpInfoModel):
        """
        标记IP为无效
        :param proxy:
        :return:
        """
        wis_logger.info(f"[ProxyIpPool.mark_ip_invalid] mark {proxy.ip} invalid")
        # todo: mark ip invalid to server
        for p in self.proxy_list:
            if (
                p.ip == proxy.ip
                and p.port == proxy.port
                and p.protocol == proxy.protocol
                and p.user == proxy.user
                and p.password == proxy.password
            ):
                self.proxy_list.remove(p)
                break

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def get_proxy(self) -> IpInfoModel:
        """
        从代理池中随机提取一个代理IP
        :return:
        """
        if len(self.proxy_list) == 0:
            await self._reload_proxies()

        proxy = random.choice(self.proxy_list)
        self.proxy_list.remove(proxy)  # 取出来一个IP就应该移出掉
        if self.enable_validate_ip:
            if not await self._is_valid_proxy(proxy):
                raise Exception(
                    "[ProxyIpPool.get_proxy] current ip invalid and again get it"
                )
        return proxy

    async def _reload_proxies(self):
        """
        # 重新加载代理池
        :return:
        """
        self.proxy_list = []
        await self.load_proxies()


async def create_ip_pool(
    ip_pool_count: int,
    enable_validate_ip: bool,
) -> ProxyIpPool:
    """
     创建 IP 代理池
    :param ip_pool_count: ip池子的数量
    :param enable_validate_ip: 是否开启验证IP代理
    :param ip_provider: 代理IP提供商名称
    :return:
    """
    pool = ProxyIpPool(
        ip_pool_count=ip_pool_count,
        enable_validate_ip=enable_validate_ip
    )
    await pool.load_proxies()
    return pool


if __name__ == "__main__":
    pass
