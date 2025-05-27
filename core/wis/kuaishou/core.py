import asyncio
import random
from asyncio import Task
from typing import Dict, List, Optional
from ..config.mc_config import *
from ..base.mc_crawler import AbstractCrawler
from ..mc_commen import AccountWithIpPoolManager, ProxyIpPool, wis_logger, create_ip_pool
from ..mc_commen.tools import utils
from .storefactory import KuaishouStoreFactory

from .client import KuaiShouApiClient
from .exception import DataFetchError


class KuaiShouCrawler(AbstractCrawler):
    def __init__(self, test_mode: bool = False):
        self.ks_client = KuaiShouApiClient()
        self.store = KuaishouStoreFactory(test_mode=test_mode)

    async def async_initialize(self):
        """
        Asynchronous Initialization
        Returns:
        """
        proxy_ip_pool: Optional[ProxyIpPool] = None
        """
        if config.ENABLE_IP_PROXY:
            # weibo对代理验证中等，可以选择长时长的IP，比如1-5分钟一个IP
            # 快代理：私密代理->按IP付费->专业版->IP有效时长为1-5分钟, 购买地址：https://www.kuaidaili.com/?ref=ldwkjqipvz6c
            proxy_ip_pool = await create_ip_pool(
                config.IP_PROXY_POOL_COUNT, enable_validate_ip=True
            )
        """
        # 初始化账号池
        account_with_ip_pool = AccountWithIpPoolManager(
            platform_name=KUAISHOU_PLATFORM_NAME,
            proxy_ip_pool=proxy_ip_pool,
        )
        await account_with_ip_pool.async_initialize()

        self.ks_client.account_with_ip_pool = account_with_ip_pool
        await self.ks_client.update_account_info()

    async def search(self, keywords: List[str]):
        """
        Search for videos and retrieve their comment information.
        Returns:

        """
        utils.logger.info("[KuaiShouCrawler.search] Begin search kuaishou keywords")
        ks_limit_count = 20  # kuaishou limit page fixed value
        if CRAWLER_MAX_NOTES_COUNT < ks_limit_count:
            CRAWLER_MAX_NOTES_COUNT = ks_limit_count
        start_page = START_PAGE
        for keyword in keywords:
            search_session_id = ""
            wis_logger.info(
                f"[KuaiShouCrawler.search] Current search keyword: {keyword}"
            )
            page = 1
            while (
                page - start_page + 1
            ) * ks_limit_count <= CRAWLER_MAX_NOTES_COUNT:
                if page < start_page:
                    wis_logger.info(f"[KuaiShouCrawler.search] Skip page: {page}")
                    page += 1
                    continue
                wis_logger.debug(
                    f"[KuaiShouCrawler.search] search kuaishou keyword: {keyword}, page: {page}"
                )
                video_id_list: List[str] = []
                videos_res = await self.ks_client.search_info_by_keyword(
                    keyword=keyword,
                    pcursor=str(page),
                    search_session_id=search_session_id,
                )
                if not videos_res:
                    wis_logger.error(
                        f"[KuaiShouCrawler.search] search info by keyword:{keyword} not found data"
                    )
                    continue

                vision_search_photo: Dict = videos_res.get("visionSearchPhoto")
                if vision_search_photo.get("result") != 1:
                    wis_logger.error(
                        f"[KuaiShouCrawler.search] search info by keyword:{keyword} not found data "
                    )
                    continue
                search_session_id = vision_search_photo.get("searchSessionId", "")
                for video_detail in vision_search_photo.get("feeds"):
                    video_id_list.append(video_detail.get("photo", {}).get("id"))
                    await self.store.update_kuaishou_video(video_item=video_detail)

                # batch fetch video comments
                page += 1
                await self.batch_get_video_comments(video_id_list)

    async def get_specified_videos(self, video_ids: List[str]):
        """
        Get the information and comments of the specified post
        Returns:

        """
        semaphore = asyncio.Semaphore(MAX_CONCURRENCY_NUM)
        task_list = [
            self.get_video_info_task(video_id=video_id, semaphore=semaphore)
            for video_id in video_ids
        ]
        video_details = await asyncio.gather(*task_list)
        for video_detail in video_details:
            if video_detail is not None:
                await self.store.update_kuaishou_video(video_detail)
        await self.batch_get_video_comments(video_ids)

    async def get_video_info_task(
        self, video_id: str, semaphore: asyncio.Semaphore
    ) -> Optional[Dict]:
        """
        Get video detail task
        Args:
            video_id:
            semaphore:

        Returns:

        """
        async with semaphore:
            try:
                result = await self.ks_client.get_video_info(video_id)
                wis_logger.debug(
                    f"[KuaiShouCrawler.get_video_info_task] Get video_id:{video_id} info result: {result} ..."
                )
                return result.get("visionVideoDetail")
            except DataFetchError as ex:
                wis_logger.error(
                    f"[KuaiShouCrawler.get_video_info_task] Get video detail error: {ex}"
                )
                return None
            except KeyError as ex:
                wis_logger.error(
                    f"[KuaiShouCrawler.get_video_info_task] have not fund video detail video_id:{video_id}, err: {ex}"
                )
                return None

    async def batch_get_video_comments(self, video_id_list: List[str]):
        """
        Batch get video comments
        Args:
            video_id_list:

        Returns:

        """
        if not ENABLE_GET_COMMENTS:
            wis_logger.info(
                f"[KuaiShouCrawler.batch_get_video_comments] Crawling comment mode is not enabled"
            )
            return

        wis_logger.debug(
            f"[KuaiShouCrawler.batch_get_video_comments] video ids:{video_id_list}"
        )
        semaphore = asyncio.Semaphore(MAX_CONCURRENCY_NUM)
        task_list: List[Task] = []
        for video_id in video_id_list:
            task = asyncio.create_task(
                self.get_comments_async_task(video_id, semaphore), name=video_id
            )
            task_list.append(task)

        await asyncio.gather(*task_list)

    async def get_comments_async_task(
        self, video_id: str, semaphore: asyncio.Semaphore
    ):
        """
        Get comment for video id
        Args:
            video_id:
            semaphore:

        Returns:

        """
        async with semaphore:
            try:
                wis_logger.debug(
                    f"[KuaiShouCrawler.get_comments_async_task] begin get video_id: {video_id} comments ..."
                )
                await self.ks_client.get_video_all_comments(
                    photo_id=video_id,
                    crawl_interval=random.random(),
                    callback=self.store.batch_update_ks_video_comments,
                )
            except DataFetchError as ex:
                wis_logger.error(
                    f"[KuaiShouCrawler.get_comments_async_task] get video_id: {video_id} comment error: {ex}"
                )
            except Exception as e:
                wis_logger.error(
                    f"[KuaiShouCrawler.get_comments_async_task] may be been blocked, err:{e}"
                )

    async def get_creators_and_videos(self, creator_ids: List[str]) -> None:
        """
        Get creator's information and their videos and comments
        Returns:

        """
        wis_logger.debug(
            "[KuaiShouCrawler.get_creators_and_videos] Begin get kuaishou creators"
        )
        for user_id in creator_ids:
            # get creator detail info from web html content
            createor_info: Dict = await self.ks_client.get_creator_info(user_id=user_id)
            if not createor_info:
                wis_logger.error(
                    f"[KuaiShouCrawler.get_creators_and_videos] get creator: {user_id} info error: {createor_info}"
                )
                continue

            await self.store.save_creator(user_id, creator=createor_info)
            # Get all video information of the creator
            all_video_list = await self.ks_client.get_all_videos_by_creator(
                user_id=user_id,
                crawl_interval=random.random(),
                callback=self.fetch_creator_video_detail,
            )

            video_ids = [
                video_item.get("photo", {}).get("id") for video_item in all_video_list
            ]
            await self.batch_get_video_comments(video_ids)

    async def fetch_creator_video_detail(self, video_list: List[Dict]):
        """
        Fetch creator video detail
        Args:
            video_list:

        Returns:

        """
        semaphore = asyncio.Semaphore(MAX_CONCURRENCY_NUM)
        task_list = [
            self.get_video_info_task(post_item.get("photo", {}).get("id"), semaphore)
            for post_item in video_list
        ]

        video_details = await asyncio.gather(*task_list)
        for video_detail in video_details:
            if video_detail is not None:
                await self.store.update_kuaishou_video(video_detail)

    async def get_homefeed_videos(self):
        """
        Get homefeed videos and comments
        """
        wis_logger.debug(
            "[KuaiShouCrawler.get_homefeed_videos] Begin get kuaishou homefeed videos"
        )
        pcursor = ""
        saved_video_count = 0
        while saved_video_count <= CRAWLER_MAX_NOTES_COUNT:
            homefeed_videos_res = await self.ks_client.get_homefeed_videos(pcursor)
            if not homefeed_videos_res:
                wis_logger.debug(
                    "[KuaiShouCrawler.get_homefeed_videos] No more content!"
                )
                break

            brilliant_type_data: Dict = homefeed_videos_res.get("brilliantTypeData")
            pcursor = brilliant_type_data.get("pcursor", "")
            videos_list: List[Dict] = brilliant_type_data.get("feeds", [])
            if not videos_list:
                wis_logger.debug(
                    "[KuaiShouCrawler.get_homefeed_videos] No more content!"
                )
                break

            video_id_list = []
            for video_detail in videos_list:
                video_id_list.append(video_detail.get("photo", {}).get("id"))
                await self.store.update_kuaishou_video(video_item=video_detail)
            saved_video_count += len(videos_list)

            # batch fetch video comments
            await self.batch_get_video_comments(video_id_list)
            wis_logger.debug(
                f"[KuaiShouCrawler.get_homefeed_videos] Get homefeed videos, saved_video_count: {saved_video_count}"
            )

        wis_logger.info(
            "[KuaiShouCrawler.get_homefeed_videos] Kuaishou homefeed videos crawler finished ..."
        )
