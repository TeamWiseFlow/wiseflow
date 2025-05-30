# -*- coding: utf-8 -*-
import asyncio
import json
import traceback
from typing import Callable, Dict, List, Optional, Union
from urllib.parse import urlencode

import httpx
from httpx import Response
from tenacity import RetryError, retry, stop_after_attempt, wait_fixed

from ..config.mc_config import KUAISHOU_API, PER_NOTE_MAX_COMMENTS_COUNT, ENABLE_GET_SUB_COMMENTS
from ..mc_commen.account_pool import *
from .exception import DataFetchError
from .graphql import KuaiShouGraphQL


class KuaiShouApiClient:
    def __init__(
        self,
        timeout: int = 10,
        # user_agent: str = None,
        account_with_ip_pool: AccountWithIpPoolManager = None,
    ):
        """
        kuaishou client constructor
        Args:
            timeout: 请求超时时间配置
            user_agent: 自定义的User-Agent
            account_with_ip_pool: 账号池管理器
        """
        self.timeout = timeout
        # self._user_agent = user_agent or utils.get_user_agent()
        # self._sign_client = SignServerClient()
        self._graphql = KuaiShouGraphQL()
        self.account_with_ip_pool = account_with_ip_pool
        self.account_info: Optional[AccountWithIpModel] = None

    @property
    def headers(self):
        return {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Cookie": self._cookies,
            "origin": "https://www.kuaishou.com",
            "referer": "https://www.kuaishou.com/",
            "user-agent": self.account_info.account.user_agent,
            # "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }

    @property
    def _proxies(self):
        return (
            self.account_info.ip_info.format_httpx_proxy()
            if self.account_info.ip_info
            else None
        )

    @property
    def _cookies(self):
        return self.account_info.account.cookies

    async def update_account_info(self, force_login: bool = False):
        """
        更新客户端的账号信息, 该方法会一直尝试获取新的账号信息，直到获取到一个有效的账号信息
        Returns:

        """
        have_account = False
        wis_logger.debug("try to get a new account")
        account_info = await self.account_with_ip_pool.get_account_with_ip_info(force_login)
        self.account_info = account_info
        have_account = await self.pong()
        if have_account:
            return
        wis_logger.info(f"current account {account_info.account.account_name} is invalid, try to get a new one")
        await self.mark_account_invalid(account_info)
        account_info = await self.account_with_ip_pool.get_account_with_ip_info(force_login=True)
        self.account_info = account_info
        have_account = await self.pong()
        if not have_account:
            raise DataFetchError("cannot get any valid account, we have to quit")

    async def mark_account_invalid(self, account_with_ip: AccountWithIpModel):
        """
        标记账号为无效
        Args:
            account_with_ip:

        Returns:

        """
        if self.account_with_ip_pool:
            await self.account_with_ip_pool.mark_account_invalid(
                account_with_ip.account
            )
            await self.account_with_ip_pool.mark_ip_invalid(account_with_ip.ip_info)

    async def check_ip_expired(self):
        """
        检查IP是否过期, 由于IP的过期时间在运行中是不确定的，所以每次请求都需要验证下IP是否过期
        如果过期了，那么需要重新获取一个新的IP，赋值给当前账号信息
        Returns:

        """
        if (
            self.account_with_ip_pool.proxy_ip_pool
            and self.account_info.ip_info
            and self.account_info.ip_info.is_expired
        ):
            wis_logger.info(
                f"[KuaiShouApiClient.request] current ip {self.account_info.ip_info.ip} is expired, "
                f"mark it invalid and try to get a new one"
            )
            await self.account_with_ip_pool.mark_ip_invalid(self.account_info.ip_info)
            self.account_info.ip_info = (
                await self.account_with_ip_pool.proxy_ip_pool.get_proxy()
            )

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
    async def request(self, method, url, **kwargs) -> Union[Response, Dict]:
        """
        封装httpx的公共请求方法，对请求响应做一些处理
        Args:
            method: 请求方法
            url: 请求的URL
            **kwargs: 其他请求参数，例如请求头、请求体等

        Returns:

        """
        async with httpx.AsyncClient(proxy=self._proxies) as client:
            response = await client.request(method, url, timeout=self.timeout, **kwargs)
        data: Dict = response.json()
        if data.get("errors"):
            raise DataFetchError(data.get("errors", "unkonw error"))
        else:
            return data.get("data", {})

    async def get(self, uri: str, params=None, **kwargs) -> Dict:
        """
        get请求
        Args:
            uri: 请求路由
            params: 请求参数
            **kwargs: 其他请求参数

        Returns:

        """
        final_uri = uri
        if isinstance(params, dict):
            final_uri = f"{uri}?" f"{urlencode(params)}"
        try:
            return await self.request(
                method="GET", url=f"{KUAISHOU_API}{final_uri}", **kwargs
            )
        except RetryError as e:
            # 获取原始异常
            original_exception = e.last_attempt.exception()
            traceback.print_exception(
                type(original_exception),
                original_exception,
                original_exception.__traceback__,
            )
            wis_logger.error(
                f"请求uri:{uri} 重试均失败了，尝试更换账号与IP再次发起重试"
            )
            try:
                wis_logger.info(
                    f"请求uri:{uri} 尝试更换IP再次发起重试..."
                )
                await self.account_with_ip_pool.mark_ip_invalid(
                    self.account_info.ip_info
                )
                self.account_info.ip_info = (
                    await self.account_with_ip_pool.proxy_ip_pool.get_proxy()
                )
                return await self.request(
                    method="GET", url=f"{KUAISHOU_API}{final_uri}", **kwargs
                )
            except Exception as e:
                # 获取原始异常
                """
                # in version 4.0, we do not have ip proxy yet
                original_exception = ee.last_attempt.exception()
                traceback.print_exception(
                    type(original_exception),
                    original_exception,
                    original_exception.__traceback__,
                )
                """
                wis_logger.error(
                    f"请求uri:{uri}，IP更换后还是失败，尝试更换账号与IP再次发起重试"
                )
                await self.mark_account_invalid(self.account_info)
                await self.update_account_info(force_login=True)
                return await self.request(
                    method="GET", url=f"{KUAISHOU_API}{final_uri}", **kwargs
                )

    async def post(self, uri: str, data: dict, **kwargs) -> Dict:
        """
        post请求
        Args:
            uri: 请求路由
            data: 请求体参数
            **kwargs: 其他请求参数

        Returns:

        """
        json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        try:
            return await self.request(
                method="POST",
                url=f"{KUAISHOU_API}{uri}",
                data=json_str,
                headers=self.headers,
            )
        except RetryError as e:
            # 获取原始异常
            original_exception = e.last_attempt.exception()
            traceback.print_exception(
                type(original_exception),
                original_exception,
                original_exception.__traceback__,
            )

            wis_logger.error(
                f"请求uri:{uri} 重试均失败了，尝试更换账号与IP再次发起重试"
            )
            try:
                wis_logger.info(
                    f"请求uri:{uri} 尝试更换IP再次发起重试..."
                )
                await self.account_with_ip_pool.mark_ip_invalid(
                    self.account_info.ip_info
                )
                self.account_info.ip_info = (
                    await self.account_with_ip_pool.proxy_ip_pool.get_proxy()
                )

                return await self.request(
                    method="POST",
                    url=f"{KUAISHOU_API}{uri}",
                    data=json_str,
                    **kwargs,
                )
            except Exception as ee:
                # 获取原始异常
                """
                # in version 4.0, we do not have ip proxy yet
                original_exception = ee.last_attempt.exception()
                traceback.print_exception(
                    type(original_exception),
                    original_exception,
                    original_exception.__traceback__,
                )
                """
                wis_logger.error(
                    "no IP proxy available, try to get a new account"
                )
                await self.mark_account_invalid(self.account_info)
                await self.update_account_info(force_login=True)
                return await self.request(
                    method="POST", url=f"{KUAISHOU_API}{uri}", data=json_str, **kwargs
                )

    async def pong(self) -> bool:
        """
        快手登录态检测
        Returns:

        """
        wis_logger.debug("Begin pong kuaishou...")
        ping_flag = False
        try:
            post_data = {
                "operationName": "visionProfileUserList",
                "variables": {
                    "ftype": 1,
                },
                "query": self._graphql.get("vision_profile_user_list"),
            }

            async with httpx.AsyncClient(proxy=self._proxies) as client:
                response = await client.post(
                    f"{KUAISHOU_API}", json=post_data, headers=self.headers
                )
            res = response.json()
            # print(res)
            vision_profile_user_list = res.get("data", {}).get("visionProfileUserList")
            if vision_profile_user_list and vision_profile_user_list.get("result") == 1:
                # wis_logger.debug(f"pong kuaishou success as user: {vision_profile_user_list.get('fols')[0]['user_name']}")
                ping_flag = True
        except Exception as e:
            wis_logger.error(
                f"Pong kuaishou failed: {e}, and try to login again..."
            )
            ping_flag = False
        return ping_flag

    async def search_info_by_keyword(
        self, keyword: str, pcursor: str, search_session_id: str = ""
    ) -> Dict:
        """
        关键词搜索接口
        Args:
            keyword: 关键词
            pcursor: 分页游标
            search_session_id: 搜索会话ID

        Returns:

        """
        post_data = {
            "operationName": "visionSearchPhoto",
            "variables": {
                "keyword": keyword,
                "pcursor": pcursor,
                "page": "search",
                "searchSessionId": search_session_id,
            },
            "query": self._graphql.get("search_query"),
        }
        return await self.post("", post_data)

    async def get_video_info(self, photo_id: str) -> Dict:
        """
        获取视频详情
        Args:
            photo_id: 视频id

        Returns:

        """
        post_data = {
            "operationName": "visionVideoDetail",
            "variables": {"photoId": photo_id, "page": "search"},
            "query": self._graphql.get("video_detail"),
        }
        return await self.post("", post_data)

    async def get_video_comments(self, photo_id: str, pcursor: str = "") -> Dict:
        """
        获取视频一级评论
        Args:
            photo_id: 视频id
            pcursor: 分页游标

        Returns:

        """
        post_data = {
            "operationName": "commentListQuery",
            "variables": {"photoId": photo_id, "pcursor": pcursor},
            "query": self._graphql.get("comment_list"),
        }
        return await self.post("", post_data)

    async def get_video_sub_comments(
        self, photo_id: str, root_comment_id: str, pcursor: str = ""
    ) -> Dict:
        """
        获取视频二级评论
        Args:
            photo_id: 视频ID
            root_comment_id: 一级评论ID
            pcursor:

        Returns:

        """
        post_data = {
            "operationName": "visionSubCommentList",
            "variables": {
                "photoId": photo_id,
                "pcursor": pcursor,
                "root_comment_id": root_comment_id,
            },
            "query": self._graphql.get("vision_sub_comment_list"),
        }
        return await self.post("", post_data)

    async def get_creator_profile(self, user_id: str) -> Dict:
        """
        获取创作者主页信息
        Args:
            user_id: 用户ID

        Returns:

        """
        post_data = {
            "operationName": "visionProfile",
            "variables": {"userId": user_id},
            "query": self._graphql.get("vision_profile"),
        }
        return await self.post("", post_data)

    async def get_video_by_creater(self, user_id: str, pcursor: str = "") -> Dict:
        """
        获取用户发布的所有视频
        Args:
            user_id: 用户ID
            pcursor: 分页游标

        Returns:

        """
        post_data = {
            "operationName": "visionProfilePhotoList",
            "variables": {"page": "profile", "pcursor": pcursor, "userId": user_id},
            "query": self._graphql.get("vision_profile_photo_list"),
        }
        return await self.post("", post_data)

    async def get_video_all_comments(
        self,
        photo_id: str,
        crawl_interval: float = 1.0,
        callback: Optional[Callable] = None,
    ) -> List[Dict]:
        """
        获取视频所有评论，包括一级评论和二级评论
        Args:
            photo_id:
            crawl_interval:
            callback:

        Returns:

        """
        result = []
        pcursor = ""
        for _ in range(3):
            try:
                comments_res = await self.get_video_comments(photo_id, pcursor)
                vision_commen_list = comments_res.get("visionCommentList", {})
                pcursor = vision_commen_list.get("pcursor", "")
                comments = vision_commen_list.get("rootComments", [])

                if not comments:
                    continue

                if callback:
                    await callback(photo_id, comments)

                await self.get_comments_all_sub_comments(
                    comments, photo_id, crawl_interval, callback
                )

                result.extend(comments)
                if (
                    PER_NOTE_MAX_COMMENTS_COUNT
                    and len(result) >= PER_NOTE_MAX_COMMENTS_COUNT
                ):
                    wis_logger.debug(
                        f"The number of comments exceeds the limit: {PER_NOTE_MAX_COMMENTS_COUNT}"
                    )
                    break

                if pcursor == "no_more":
                    break

                await asyncio.sleep(crawl_interval)
            except Exception as e:
                wis_logger.error(
                    f"get video_id:{photo_id} comments not finished, but paused by error: {e}"
                )
                break

        return result

    async def get_comments_all_sub_comments(
        self,
        comments: List[Dict],
        photo_id,
        crawl_interval: float = 1.0,
        callback: Optional[Callable] = None,
    ):
        """
        获取指定一级评论下的所有二级评论, 该方法会一直查找一级评论下的所有二级评论信息
        Args:
            comments: 评论列表
            photo_id: 视频id
            crawl_interval: 爬取一次评论的延迟单位（秒）
            callback: 一次评论爬取结束后
        Returns:

        """
        if not ENABLE_GET_SUB_COMMENTS:
            wis_logger.info(
                f"Crawling sub_comment mode is not enabled"
            )
            return

        for comment in comments:
            # print("root comment", comment)
            sub_comments = []
            sub_comment_pcursor = comment.get("subCommentsPcursor")
            if not sub_comment_pcursor or sub_comment_pcursor == "no_more":
                continue
            root_comment_id = comment.get("commentId")
            for _ in range(3):
                # print("sub comments pcursor", sub_comment_pcursor)
                # print("root comment id", root_comment_id)
                # print("photo id", photo_id)
                comments_res = await self.get_video_sub_comments(
                    photo_id, root_comment_id, sub_comment_pcursor
                )
                # print("sub comments response", comments_res)
                # print('-'*10)
                vision_sub_comment_list = comments_res.get("visionSubCommentList", {})
                sub_comment_pcursor = vision_sub_comment_list.get("pcursor", "no_more")
                subs = vision_sub_comment_list.get("subComments", [])
                if callback and subs:
                    await callback(photo_id, subs)
                if subs:
                    sub_comments.extend(subs)
                if not sub_comment_pcursor or sub_comment_pcursor == "no_more":
                    break
            if sub_comments:
                comment["subComments"] = sub_comments
            await asyncio.sleep(crawl_interval)

    async def get_creator_info(self, user_id: str) -> Dict:
        """
        获取用户主页信息
        eg: https://www.kuaishou.com/profile/3x4jtnbfter525a
        Args:
            user_id:

        Returns:

        """
        vision_res = await self.get_creator_profile(user_id)
        vision_profile = vision_res.get("visionProfile", {})
        return vision_profile.get("userProfile")

    async def get_all_videos_by_creator(
        self,
        user_id: str,
        crawl_interval: float = 1.0,
        callback: Optional[Callable] = None,
    ) -> List[Dict]:
        """
        获取指定用户下的所有发过的帖子，该方法会一直查找一个用户下的所有帖子信息
        Args:
            user_id: 用户ID
            crawl_interval: 爬取一次的延迟单位（秒）
            callback: 一次分页爬取结束后的更新回调函数
        Returns:

        """
        result = []
        pcursor = ""

        while pcursor != "no_more":
            videos_res = await self.get_video_by_creater(user_id, pcursor)
            if not videos_res:
                wis_logger.error(
                    f"The current creator may have been banned by ks, so they cannot access the data."
                )
                break

            vision_profile_photo_list = videos_res.get("visionProfilePhotoList", {})
            pcursor = vision_profile_photo_list.get("pcursor", "")

            videos = vision_profile_photo_list.get("feeds", [])
            wis_logger.debug(
                f"got user_id:{user_id} videos len : {len(videos)}"
            )

            if callback:
                await callback(videos)
            await asyncio.sleep(crawl_interval)
            result.extend(videos)
        return result

    async def get_homefeed_videos(self, pcursor: str = "") -> Dict:
        """
        获取快手首页视频

        Args:
            pcursor: 分页游标

        Returns:

        """
        post_data = {
            "operationName": "brilliantTypeDataQuery",
            "variables": {
                "pcursor": pcursor,
                "hotChannelId": "00",
                "page": "brilliant",
            },
            "query": self._graphql.get("homefeed_videos"),
        }
        return await self.post("", post_data)
