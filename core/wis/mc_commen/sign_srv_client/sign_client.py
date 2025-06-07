# don't be evil
# for commercial use, please contact to get permission
# wiseflow opensouce do not support commercial use since 4.0


# -*- coding: utf-8 -*-
import asyncio
from typing import Any, Dict, Union
import aiohttp
from ..account_pool import wis_logger
import os

SIGN_SRV_HOST = os.getenv('SIGN_SRV_HOST', 'localhost')
SIGN_SRV_PORT = os.getenv('SIGN_SRV_PORT', '8989')
from .sign_model import (BilibliSignRequest,
                         BilibliSignResponse,
                         DouyinSignRequest,
                         DouyinSignResponse,
                         XhsSignRequest,
                         XhsSignResponse,
                         ZhihuSignRequest,
                         ZhihuSignResponse)

SIGN_SERVER_URL = f"http://{SIGN_SRV_HOST}:{SIGN_SRV_PORT}"


class SignServerClient:
    def __init__(self, endpoint: str = SIGN_SERVER_URL, timeout: int = 60):
        """
        SignServerClient constructor
        Args:
            endpoint: sign server endpoint
            timeout: request timeout
        """
        self._endpoint = endpoint
        self._timeout = timeout

    async def request(self, method: str, uri: str, **kwargs) -> Union[Dict, Any]:
        """
        send request
        Args:
            method: request method
            uri: request uri
            **kwargs: other request params

        Returns:

        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self._timeout)) as session:
                async with session.request(method, self._endpoint + uri, **kwargs) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        wis_logger.error(
                            f"[XhsSignClient.request] response status code {response.status} response content: {response_text}")
                        raise Exception(f"请求签名服务器失败，状态码：{response.status}")

                    data = await response.json()
                    return data
        except Exception as e:
            raise Exception(f"请求签名服务器失败, error: {e}")

    async def xiaohongshu_sign(self, sign_req: XhsSignRequest) -> XhsSignResponse:
        """
        xiaohongshu sign request to sign server
        Args:
            sign_req:

        Returns:

        """
        sign_server_uri = "/signsrv/v1/xhs/sign"
        res_json = await self.request(method="POST", uri=sign_server_uri, json=sign_req.model_dump())
        if not res_json:
            raise Exception(f"从签名服务器:{SIGN_SERVER_URL}{sign_server_uri} 获取签名失败")

        xhs_sign_response = XhsSignResponse(**res_json)
        if xhs_sign_response.isok:
            return xhs_sign_response
        raise Exception(
            f"从签名服务器:{SIGN_SERVER_URL}{sign_server_uri} 获取签名失败，原因：{xhs_sign_response.msg}, sign reponse: {xhs_sign_response}")

    async def douyin_sign(self, sign_req: DouyinSignRequest) -> DouyinSignResponse:
        """
        douyin sign request to sign server
        Args:
            sign_req: DouyinSignRequest object

        Returns:

        """
        sign_server_uri = "/signsrv/v1/douyin/sign"
        res_json = await self.request(method="POST", uri=sign_server_uri, json=sign_req.model_dump())
        if not res_json:
            raise Exception(f"从签名服务器:{SIGN_SERVER_URL}{sign_server_uri} 获取签名失败")

        sign_response = DouyinSignResponse(**res_json)
        if sign_response.isok:
            return sign_response
        raise Exception(
            f"从签名服务器:{SIGN_SERVER_URL}{sign_server_uri} 获取签名失败，原因：{sign_response.msg}, sign reponse: {sign_response}")

    async def bilibili_sign(self, sign_req: BilibliSignRequest) -> BilibliSignResponse:
        """
        bilibili sign request to sign server
        Args:
            sign_req:

        Returns:

        """
        sign_server_uri = "/signsrv/v1/bilibili/sign"
        res_json = await self.request(method="POST", uri=sign_server_uri, json=sign_req.model_dump())
        if not res_json:
            raise Exception(f"从签名服务器:{SIGN_SERVER_URL}{sign_server_uri} 获取签名失败")
        sign_response = BilibliSignResponse(**res_json)
        if sign_response.isok:
            return sign_response
        raise Exception(
            f"从签名服务器:{SIGN_SERVER_URL}{sign_server_uri} 获取签名失败，原因：{sign_response.msg}, sign reponse: {sign_response}")

    async def zhihu_sign(self, sign_req: ZhihuSignRequest) -> ZhihuSignResponse:
        """
        zhihu sign request to sign server
        Args:
            sign_req:

        Returns:

        """
        sign_server_uri = "/signsrv/v1/zhihu/sign"
        res_json = await self.request(method="POST", uri=sign_server_uri, json=sign_req.model_dump())
        if not res_json:
            raise Exception(f"从签名服务器:{SIGN_SERVER_URL}{sign_server_uri} 获取签名失败")
        sign_response = ZhihuSignResponse(**res_json)
        if sign_response.isok:
            return sign_response
        raise Exception(
            f"从签名服务器:{SIGN_SERVER_URL}{sign_server_uri} 获取签名失败，原因：{sign_response.msg}, sign reponse: {sign_response}")

    async def pong_sign_server(self):
        """
        test
        :return:
        """
        wis_logger.info("[XhsSignClient.pong_sign_server] test xhs sign server is alive")
        await self.request(method="GET", uri="/signsrv/pong")
        wis_logger.info("[XhsSignClient.pong_sign_server] xhs sign server is alive")


if __name__ == '__main__':
    sign_client = SignServerClient()
    asyncio.run(sign_client.pong_sign_server())
