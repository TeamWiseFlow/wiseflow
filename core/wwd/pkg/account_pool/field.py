# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：  
# 1. 不得用于任何商业用途。  
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。  
# 3. 不得进行大规模爬取或对平台造成运营干扰。  
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。   
# 5. 不得用于任何非法或不当的用途。
#   
# 详细许可条款请参阅项目根目录下的LICENSE文件。  
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。  


from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

import constant
from pkg.proxy.types import IpInfoModel


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
    XHS = constant.XHS_PLATFORM_NAME
    WEIBO = constant.WEIBO_PLATFORM_NAME
    DOUYIN = constant.DOUYIN_PLATFORM_NAME
    KUAISHOU = constant.KUAISHOU_PLATFORM_NAME
    BILIBILI = constant.BILIBILI_PLATFORM_NAME
    TIEBA = constant.TIEBA_PLATFORM_NAME
    ZHIHU = constant.ZHIHU_PLATFORM_NAME


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

    def __repr__(self):
        # Customize how the instance is represented
        # Hide cookies but show the first 5 characters
        cookies_preview = f"{self.cookies[:5]}..." if self.cookies else "No cookies"
        return (f"AccountInfoModel(id={self.id}, "
                f"account_name='{self.account_name}', "
                f"cookies='{cookies_preview}', "
                f"platform_name={self.platform_name.value}, "
                f"status={self.status.value}, "
                f"invalid_timestamp={self.invalid_timestamp})")

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
        platform_name=AccountPlatfromEnum.XHS
    )
    print(aim)
    print(aim.model_dump())
    print(aim.model_dump_json())
