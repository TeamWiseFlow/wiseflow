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
import os

# 是否开启 IP 代理
ENABLE_IP_PROXY = False

# 代理IP池数量
IP_PROXY_POOL_COUNT = 2  # 一般情况下设置成2个就够了，程序会自动维护IP可用性

# 代理IP提供商名称
IP_PROXY_PROVIDER_NAME = "kuaidaili"

# 快代理配置
KDL_SECERT_ID = os.getenv("KDL_SECERT_ID", "")
KDL_SIGNATURE = os.getenv("KDL_SIGNATURE", "")
KDL_USER_NAME = os.getenv("KDL_USER_NAME", "")
KDL_USER_PWD = os.getenv("KDL_USER_PWD", "")
