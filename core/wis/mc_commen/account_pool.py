# -*- coding: utf-8 -*-
from typing import List, Optional
from pathlib import Path
import json
from .field import AccountInfoModel, AccountStatusEnum, AccountWithIpModel, IpInfoModel
from .tools import utils
from ..nodriver_helper import NodriverHelper, wis_logger, base_directory
import random
from typing import List

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed


class AccountPoolManager:
    def __init__(self, platform_name: str):
        """
        account pool manager class constructor
        Args:
            platform_name:
        """
        self._platform_name = platform_name
        self._account_list: List[AccountInfoModel] = []

    async def async_initialize(self):
        """
        async init
        Returns:

        """
        existing_platform_login_token_file = Path(base_directory) / "nodriver_exported" / self._platform_name / "login_token.json"
        if existing_platform_login_token_file.exists():
            wis_logger.debug("found saved login token, load it")
            with open(existing_platform_login_token_file, "r") as f:
                login_token_data = json.load(f)
            self.add_account(AccountInfoModel(
                id=1,
                account_name=f"{self._platform_name}_account_1",
                cookies=login_token_data.get("cookies"),
                user_agent=login_token_data.get("user_agent"),
                status=AccountStatusEnum.NORMAL.value,
                platform_name=self._platform_name,
            ))

    async def get_active_account(self, force_login: bool = False) -> AccountInfoModel:
        """
        get active account
        Returns:
            AccountInfoModel: account info model
        """
        while len(self._account_list) > 0:
            account = self._account_list.pop(0)
            if account.status.value == AccountStatusEnum.NORMAL.value:
                wis_logger.debug(
                    f"from account pool get active account {account}"
                )
                return account

        async with NodriverHelper(self._platform_name) as nodriver_helper:
            cookies, user_agent = await nodriver_helper.for_mc_login(force_login=force_login)

        new_account = AccountInfoModel(
            id=len(self._account_list) + 1,
            account_name=f"{self._platform_name}_account_{len(self._account_list) + 1}",
            cookies=cookies,
            user_agent=user_agent,
            status=AccountStatusEnum.NORMAL.value,
            platform_name=self._platform_name,
        )
        self.add_account(new_account)
        return new_account

    def add_account(self, account: AccountInfoModel):
        """
        add account
        Args:
            account: account info model
        """
        self._account_list.append(account)

    async def update_account_status(
        self, account: AccountInfoModel, status: AccountStatusEnum
    ):
        """
        update account status
        Args:
            account: account info model
            status: account status enum
        """

        account.status = status
        account.invalid_timestamp = utils.get_current_timestamp()
        return


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
        wis_logger.debug(
            f"testing {proxy.ip} is it valid "
        )
        try:
            proxy_url = proxy.format_httpx_proxy()
            async with httpx.AsyncClient(proxy=proxy_url) as client:
                response = await client.get(self.valid_ip_url)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            wis_logger.warning(
                f"testing {proxy.ip} err: {e}"
            )
            raise e

    async def mark_ip_invalid(self, proxy: IpInfoModel):
        """
        标记IP为无效
        :param proxy:
        :return:
        """
        wis_logger.debug(f"mark {proxy.ip} invalid")
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


class AccountWithIpPoolManager(AccountPoolManager):
    def __init__(
        self,
        platform_name: str,
        proxy_ip_pool: Optional[ProxyIpPool] = None,
    ):
        """
        account with ip pool manager class constructor
        if proxy_ip_pool is None, then the account pool manager will not use proxy ip
        It will only use account pool
        Args:
            platform_name: platform name, defined in constant/base_constant.py
            work_dir: work directory, defined in constant/base_constant.py
            proxy_ip_pool: proxy ip pool, defined in proxy/proxy_ip_pool.py
        """
        super().__init__(platform_name)
        self.proxy_ip_pool = proxy_ip_pool

    async def async_initialize(self):
        """
        async init
        Returns:

        """
        await super().async_initialize()

    async def get_account_with_ip_info(self, force_login: bool = False) -> AccountWithIpModel:
        """
        get account with ip, if proxy_ip_pool is None, then return account only
        Returns:

        """
        ip_info: Optional[IpInfoModel] = None
        account: AccountInfoModel = await self.get_active_account(force_login)
        if self.proxy_ip_pool:
            ip_info = await self.proxy_ip_pool.get_proxy()
            wis_logger.info(
                f"enable proxy ip pool, get proxy ip: {ip_info}"
            )
        return AccountWithIpModel(account=account, ip_info=ip_info)

    async def mark_account_invalid(self, account: AccountInfoModel):
        """
        mark account invalid
        Args:
            account:

        Returns:

        """
        await self.update_account_status(account, AccountStatusEnum.INVALID)

    async def mark_ip_invalid(self, ip_info: Optional[IpInfoModel]):
        """
        mark ip invalid
        Args:
            ip_info:

        Returns:

        """
        if not ip_info or not self.proxy_ip_pool:
            return
        await self.proxy_ip_pool.mark_ip_invalid(ip_info)


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
