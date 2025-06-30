# -*- coding: utf-8 -*-
import asyncio
import json
from typing import Callable, Dict, List, Optional, Union, cast
from urllib.parse import urlencode
import copy
import regex as re
import httpx
from httpx import Response
from tenacity import RetryError, retry, stop_after_attempt, wait_fixed
from ..config.mc_config import WEIBO_API_URL, PER_NOTE_MAX_COMMENTS_COUNT
from ..mc_commen.account_pool import *
from .exception import DataFetchError
from .field import SearchType
from urllib.parse import parse_qs, unquote, urlencode
import time


class WeiboClient:
    account_info: AccountWithIpModel
    _account_update_lock: asyncio.Lock

    def __init__(
        self,
        timeout: int = 10,
        # user_agent: str = None,
        account_with_ip_pool: AccountWithIpPoolManager = None,
    ):
        """
        weibo client constructor
        Args:
            timeout: 请求超时时间
            user_agent: 请求头中的 User-Agent
            account_with_ip_pool: 账号池管理器
        """
        self.timeout = timeout
        # self._user_agent = user_agent or utils.get_user_agent()
        self.account_with_ip_pool = account_with_ip_pool
        self._account_update_lock = asyncio.Lock()
        self._account_updated_at = None

    @property
    def headers(self):
        return {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Cookie": self._cookies,
            "origin": "https://m.weibo.cn/",
            "referer": "https://m.weibo.cn/",
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
        Args:
            force_login: 是否强制登录获取新账号
        Returns:
        """
        # Use async lock to ensure that only one account is being updated
        async with self._account_update_lock:
            if self._account_updated_at and time.time() - self._account_updated_at < 60:
                return

            if self.account_with_ip_pool.proxy_ip_pool:
                try:
                    await self.account_with_ip_pool.mark_ip_invalid(
                        cast(IpInfoModel, self.account_info.ip_info)
                    )
                    proxy_ip_pool: ProxyIpPool = cast(
                        ProxyIpPool, self.account_with_ip_pool.proxy_ip_pool
                    )
                    self.account_info.ip_info = await proxy_ip_pool.get_proxy()
                    if await self.pong():
                        wis_logger.info("update account by changing ip success, will continue the job")
                        self._account_updated_at = time.time()
                        return
                except Exception as e:
                    wis_logger.error(f"update IP failed, err:{e}")

            # in this case, we change ip and account together to ensure success -- follow ajiang's suggestion
            await self.mark_account_invalid(self.account_info)
            account_info = await self.account_with_ip_pool.get_account_with_ip_info(force_login=force_login)
            self.account_info = account_info
            if not await self.pong():
                raise DataFetchError("cannot get any valid account, we have to quit")

            wis_logger.info("update account by changing ip and account success, will continue the job")
            self._account_updated_at = time.time()

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
                f"[WeiboClient.request] current ip {self.account_info.ip_info.ip} is expired, "
                f"mark it invalid and try to get a new one"
            )
            await self.account_with_ip_pool.mark_ip_invalid(self.account_info.ip_info)
            self.account_info.ip_info = await cast(
                ProxyIpPool, self.account_with_ip_pool.proxy_ip_pool
            ).get_proxy()

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
        await self.check_ip_expired()
        need_return_ori_response = kwargs.get("return_response", False)
        if "return_response" in kwargs:
            del kwargs["return_response"]
        headers = kwargs.pop("headers", None) or self.headers
        
        async with httpx.AsyncClient(proxy=self._proxies) as client:
            response = await client.request(
                method, url, timeout=self.timeout, headers=headers, **kwargs
            )
        
        if not response.is_success:
            return {}

        if need_return_ori_response:
            return response

        data = response.json()
        if data.get("ok") not in [1, 0]:
            # 0和1是正常的返回码，其他的都是异常，0代表无数据，1代表有数据
            wis_logger.error(
                f"[WeiboClient.request] {method}:{url} err, res:{data}"
            )
            raise DataFetchError(data.get("msg", "unkonw error"))
        else:
            return cast(Dict, data.get("data", {}))

    async def get(self, uri: str, params=None, **kwargs) -> Union[Response, Dict]:
        """
        GET请求，对请求头签名
        Args:
            uri: 请求路由
            params: 请求参数

        Returns:

        """
        final_uri = uri
        if isinstance(params, dict):
            final_uri = f"{uri}?" f"{urlencode(params)}"

        try:
            res = await self.request(
                method="GET", url=f"{WEIBO_API_URL}{final_uri}", **kwargs
            )
            if res:
                return res
        except RetryError:
            wis_logger.debug(f"get uri:{uri} failed, will try to update account and IP proxy")

        await self.update_account_info(force_login=True)
        try:
            return await self.request(
                method="GET", url=f"{WEIBO_API_URL}{final_uri}", **kwargs
            )
        except Exception as e:
            wis_logger.warning(f"get uri:{uri} failed many times, account and ip proxy had been updated, however, still failed, have to quit, err:{e}")

    async def post(self, uri: str, data: Dict, **kwargs) -> Union[Response, Dict]:
        """
        POST请求，对请求头签名
        Args:
            uri: 请求路由
            data: 请求体参数

        Returns:

        """
        json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        try:
            res = await self.request(
                method="POST", url=f"{WEIBO_API_URL}{uri}", data=json_str, **kwargs
            )
            if res:
                return res
        except RetryError:
            wis_logger.debug(f"post uri:{uri} failed, will try to update account and IP proxy")

        await self.update_account_info(force_login=True)
        try:
            return await self.request(
                method="POST", url=f"{WEIBO_API_URL}{uri}", data=json_str, **kwargs
            )
        except Exception as e:
            wis_logger.warning(f"post uri:{uri} failed many times, account and ip proxy had been updated, however, still failed, have to quit, err:{e}")

    async def pong(self) -> bool:
        """get a note to check if login state is ok"""
        # wis_logger.debug(f"Begin to check account weibo login state...")
        ping_flag = False
        try:
            uri = "/api/config"
            async with httpx.AsyncClient(proxy=self._proxies) as client:
                response = await client.request(
                    method="GET",
                    url=f"{WEIBO_API_URL}{uri}",
                    headers=self.headers,
                )
            resp_data: Dict = cast(Dict, response.json())
            if resp_data and resp_data.get("data", {}).get("login"):
                ping_flag = True
            else:
                wis_logger.info(
                    f"[WeiboClient.pong] cookie may be invalid and again login..."
                )
        except Exception as e:
            wis_logger.warning(
                f"[WeiboClient.pong] Ping weibo failed: {e}"
            )
            ping_flag = False
        return ping_flag

    async def get_note_by_keyword(
        self, keyword: str, page: int = 1, search_type: SearchType = SearchType.DEFAULT
    ) -> Dict:
        """
        search note by keyword
        :param keyword: 微博搜搜的关键词
        :param page: 分页参数 -当前页码
        :param search_type: 搜索的类型，见 weibo/filed.py 中的枚举SearchType
        :return:
        """
        uri = "/api/container/getIndex"
        containerid = f"100103type={search_type.value}&q={keyword}"
        params = {
            "containerid": containerid,
            "page_type": "searchall",
            "page": page,
        }
        return cast(Dict, await self.get(uri, params))

    async def get_note_comments(
        self, mid_id: str, max_id: int, max_id_type: int = 0
    ) -> Dict:
        """get notes comments
        :param mid_id: 微博ID
        :param max_id: 分页参数ID
        :param max_id_type: 分页参数类型
        :return:
        """
        uri = "/comments/hotflow"
        params = {
            "id": mid_id,
            "mid": mid_id,
            "max_id_type": max_id_type,
        }
        if max_id > 0:
            params.update({"max_id": max_id})

        referer_url = f"https://m.weibo.cn/detail/{mid_id}"
        headers = copy.copy(self.headers)
        headers["Referer"] = referer_url

        return cast(Dict, await self.get(uri, params, headers=headers))

    async def get_note_all_comments(
        self,
        note_id: str,
        crawl_interval: float = 1.0,
        callback: Optional[Callable] = None,
    ) -> List[Dict]:
        """
        get note all comments include sub comments
        :param note_id:
        :param crawl_interval:
        :param callback:
        :return:
        """
        result = []
        is_end = False
        max_id = -1
        max_id_type = 0
        for _ in range(3):
            try:
                comments_res = await self.get_note_comments(note_id, max_id, max_id_type)
                if not comments_res:
                    break
            except Exception as e:
                wis_logger.warning(f"get note_id:{note_id} comments failed by error: {e}, will retry for max 3 times")
                continue
            max_id = comments_res.get("max_id", 0)
            max_id_type = comments_res.get("max_id_type", 0)
            comment_list: List[Dict] = comments_res.get("data", [])
            is_end = max_id == 0

            if callback:  # 如果有回调函数，就执行回调函数
                await callback(note_id, comment_list)

            result.extend(comment_list)
            if is_end:
                break
            if (
                PER_NOTE_MAX_COMMENTS_COUNT
                and len(result) >= PER_NOTE_MAX_COMMENTS_COUNT
            ):
                wis_logger.info(
                    f"The number of comments exceeds the limit: {PER_NOTE_MAX_COMMENTS_COUNT}"
                )
                break
            await asyncio.sleep(crawl_interval)
        return result

    async def get_note_info_by_id(self, note_id: str) -> Dict:
        """
        根据帖子ID获取详情
        :param note_id:
        :return:
        """
        uri = f"/detail/{note_id}"
        response = await self.get(uri, return_response=True)
        if not response or response.status_code != 200:
            raise DataFetchError(f"get weibo detail err: {response}")
        match = re.search(
            r"var \$render_data = (\[.*?\])\[0\]", response.text, re.DOTALL
        )
        if match:
            render_data_json = match.group(1)
            render_data_dict = json.loads(render_data_json)
            note_detail = render_data_dict[0].get("status")
            note_item = {"mblog": note_detail}
            return note_item
        else:
            wis_logger.info(
                f"[WeiboClient.get_note_info_by_id] 未找到$render_data的值"
            )
            return dict()

    async def get_creator_container_info(self, creator_id: str) -> Dict:
        """
        获取用户的容器ID, 容器信息代表着真实请求的API路径
            fid_container_id：用户的微博详情API的容器ID
            lfid_container_id：用户的微博列表API的容器ID
        Args:
            creator_id:

        Returns: {

        """
        response = await self.get(f"/u/{creator_id}", return_response=True)
        m_weibocn_params = response.cookies.get("M_WEIBOCN_PARAMS")
        if not m_weibocn_params:
            raise DataFetchError("get containerid failed")
        m_weibocn_params_dict = parse_qs(unquote(m_weibocn_params))
        return {
            "fid_container_id": m_weibocn_params_dict.get("fid", [""])[0],
            "lfid_container_id": m_weibocn_params_dict.get("lfid", [""])[0],
        }

    async def get_creator_info_by_id(self, creator_id: str) -> Dict:
        """
        根据用户ID获取用户详情
        Args:
            creator_id:

        Returns:

        """
        uri = "/api/container/getIndex"
        container_info = await self.get_creator_container_info(creator_id)
        params = {
            "jumpfrom": "weibocom",
            "type": "uid",
            "value": creator_id,
            "containerid": container_info["fid_container_id"]
            or container_info["lfid_container_id"],
        }

        user_res = await self.get(uri, params)

        if user_res.get("tabsInfo"):
            tabs: List[Dict] = user_res.get("tabsInfo", {}).get("tabs", [])
            for tab in tabs:
                if tab.get("tabKey") == "weibo":
                    container_info["lfid_container_id"] = tab.get("containerid")
                    break

        user_res.update(container_info)
        return user_res

    async def get_notes_by_creator(
        self,
        creator: str,
        container_id: str,
        since_id: str = "0",
    ) -> Dict:
        """
        获取博主的笔记
        Args:
            creator: 博主ID
            container_id: 容器ID
            since_id: 上一页最后一条笔记的ID
        Returns:

        """
        uri = "/api/container/getIndex"
        params = {
            "jumpfrom": "weibocom",
            "type": "uid",
            "value": creator,
            "containerid": container_id,
            "since_id": since_id,
        }
        return await self.get(uri, params)
