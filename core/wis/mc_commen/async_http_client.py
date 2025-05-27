# don't be evil
# for commercial use, please contact to get permission
# wiseflow opensouce do not support commercial use since 4.0

import httpx
from .account_pool import wis_logger


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
        wis_logger.debug(f"Request started: {method} {url}, kwargs:{kwargs}")
        try:
            response = await self.client.request(method, url, **kwargs)
            wis_logger.debug(f"Request completed with status {response.status_code}")
            return response
        except Exception as e:
            wis_logger.error(f"Request failed: {str(e)}")
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
