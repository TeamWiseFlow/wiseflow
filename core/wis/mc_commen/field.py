from enum import Enum
from typing import Optional
import time
from pydantic import BaseModel, Field

from ..config.mc_config import *


class IpInfoModel(BaseModel):
    """Unified IP model"""
    ip: str = Field(title="ip")
    port: int = Field(title="端口")
    user: str = Field(title="IP代理认证的用户名")
    protocol: str = Field(default="https://", title="代理IP的协议")
    password: str = Field(title="IP代理认证用户的密码")
    expired_time_ts: int = Field(title="IP过期时间时间戳，单位秒")

    def format_httpx_proxy(self) -> str:
        """
        Get the httpx proxy string for new httpx version
        Returns:
            str: proxy URL string like "http://user:password@ip:port"
        """
        return f"{self.protocol}://{self.user}:{self.password}@{self.ip}:{self.port}"

    @property
    def is_expired(self) -> bool:
        """
        Check if the IP is expired
        Returns:
            bool: True if the IP is expired, False otherwise
        """
        return self.expired_time_ts < int(time.time())


class AccountStatusEnum(Enum):
    """
    account status enum
    """
    NORMAL = 0
    INVALID = -1


class AccountPlatfromEnum(Enum):
    """
    account platform enum
    """
    # XHS = constant.XHS_PLATFORM_NAME
    WEIBO = WEIBO_PLATFORM_NAME
    # DOUYIN = constant.DOUYIN_PLATFORM_NAME
    KUAISHOU = KUAISHOU_PLATFORM_NAME
    # BILIBILI = constant.BILIBILI_PLATFORM_NAME
    # TIEBA = constant.TIEBA_PLATFORM_NAME
    # ZHIHU = constant.ZHIHU_PLATFORM_NAME


class AccountInfoModel(BaseModel):
    """
    account info model
    """
    id: int = Field(title="account id，primary key，auto increment")
    account_name: str = Field("", title="account name")
    cookies: str = Field("", title="account cookies")
    platform_name: AccountPlatfromEnum = Field("", title="platform name")
    status: AccountStatusEnum = Field(AccountStatusEnum.NORMAL.value, title="account status, 0: normal, -1: invalid")
    invalid_timestamp: int = Field(0, title="account invalid timestamp")
    user_agent: str = Field("", title="account user agent")
    
    def __repr__(self):
        # Customize how the instance is represented
        # Hide cookies but show the first 5 characters
        cookies_preview = f"{self.cookies[:5]}..." if self.cookies else "No cookies"
        return (f"AccountInfoModel(id={self.id}, "
                f"account_name='{self.account_name}', "
                f"cookies='{cookies_preview}', "
                f"platform_name={self.platform_name.value}, "
                f"status={self.status.value}, "
                f"invalid_timestamp={self.invalid_timestamp}, "
                f"user_agent='{self.user_agent}')")

    def __str__(self):
        # Custom __str__ method for other usages
        return self.__repr__()


class AccountWithIpModel(BaseModel):
    """
    account with ip model
    """
    account: AccountInfoModel
    ip_info: Optional[IpInfoModel] = None

    def __repr__(self):
        # Delegate repr customization to AccountInfoModel
        return f"AccountWithIpModel(account={repr(self.account)}, ip_info={self.ip_info})"


if __name__ == '__main__':
    aim = AccountInfoModel(
        id=1,
        account_name="account_name_test_1",
        cookies="account_cookies_test_1",
        status=AccountStatusEnum.NORMAL,
        invalid_timestamp=0,
        user_agent="user_agent_test_1",
        platform_name=AccountPlatfromEnum.XHS
    )
    print(aim)
    print(aim.model_dump())
    print(aim.model_dump_json())
