# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。


# -*- coding: utf-8 -*-
from typing import List, Optional
from pathlib import Path
import json
from .field import AccountInfoModel, AccountStatusEnum, AccountWithIpModel, IpInfoModel
from .proxy_ip_pool import ProxyIpPool
from .tools import utils
from ..nodriver_helper import NodriverHelper, wis_logger, base_directory


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
                wis_logger.info(
                    f"[AccountPoolManager.get_active_account] get active account {account}"
                )
                return account

        with NodriverHelper(self._platform_name) as nodriver_helper:
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
                f"[AccountWithIpPoolManager.get_account_with_ip] enable proxy ip pool, get proxy ip: {ip_info}"
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
        if not ip_info:
            return
        await self.proxy_ip_pool.mark_ip_invalid(ip_info)
