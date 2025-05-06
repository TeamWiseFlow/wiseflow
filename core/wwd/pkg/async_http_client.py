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
import logging

import httpx

logger = logging.getLogger(__name__)


class AsyncHTTPClient:
    def __init__(self, base_url: str = ""):
        self.client = httpx.AsyncClient()
        self.base_uri = base_url

    async def __aenter__(self):
        """
        在进入异步上下文管理器时调用。
        返回实例自身，允许在'async with'块中使用。
        :return:
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        在退出异步上下文管理器时调用。
        无论是否发生异常，都将关闭HTTP客户端。
        :param exc_type: 异常类型
        :param exc_val: 异常值
        :param exc_tb: 异常的回溯对象
        :return:
        """
        await self.close()

    async def fetch(self, method: str, url: str, **kwargs):
        """
        执行HTTP请求。
        :param method: HTTP方法，如'GET'或'POST'。
        :param url: 请求的URL。
        :param kwargs: 传递给httpx请求的额外参数。
        :return:
        """
        if self.base_uri:
            url = self.base_uri + url
        logger.info(f"Request started: {method} {url}, kwargs:{kwargs}")
        try:
            response = await self.client.request(method, url, **kwargs)
            logger.info(f"Request completed with status {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    async def get(self, url: str, **kwargs):
        """
        发送GET请求。
        :param url: 请求的URL
        :param kwargs: 传递给httpx请求的额外参数。
        :return:
        """
        return await self.fetch('GET', url, **kwargs)

    async def post(self, url, data=None, json=None, **kwargs):
        """
        发送POST请求。
        :param url: 请求的URL。
        :param data: 用于表单数据的字典。
        :param json: 用于JSON数据的字典。
        :param kwargs: 传递给httpx请求的额外参数。
        :return:
        """
        if json is not None:
            kwargs['json'] = json
        elif data is not None:
            kwargs['data'] = data
        return await self.fetch('POST', url, **kwargs)

    async def close(self):
        """
        关闭HTTP客户端。
        :return:
        """
        await self.client.aclose()
