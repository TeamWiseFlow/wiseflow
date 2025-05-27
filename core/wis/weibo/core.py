import asyncio
import random
from asyncio import Task
from typing import Dict, List, Optional

import config
from ..config.mc_config import *
from ..base.mc_crawler import AbstractCrawler
from ..mc_commen import AccountWithIpPoolManager, ProxyIpPool, wis_logger, create_ip_pool
from ..mc_commen.tools import utils
from .storefactory import WeiboStoreFactory

from .client import WeiboClient
from .exception import DataFetchError
from .field import SearchType
from .help import filter_search_result_card


class WeiboCrawler(AbstractCrawler):

    def __init__(self, test_mode: bool = False):
        self.wb_client = WeiboClient()
        self.store = WeiboStoreFactory(test_mode=test_mode)

    async def async_initialize(self) -> None:
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
            platform_name=WEIBO_PLATFORM_NAME,
            proxy_ip_pool=proxy_ip_pool,
        )
        await account_with_ip_pool.async_initialize()

        self.wb_client.account_with_ip_pool = account_with_ip_pool
        await self.wb_client.update_account_info()

    async def search(self, keywords: List[str]):
        """
        search weibo note with keywords
        :return:
        """
        wis_logger.info("[WeiboCrawler.search] Begin search weibo keywords")
        weibo_limit_count = 10  # weibo limit page fixed value
        if CRAWLER_MAX_NOTES_COUNT < weibo_limit_count:
            CRAWLER_MAX_NOTES_COUNT = weibo_limit_count
        start_page = START_PAGE
        for keyword in keywords:
            wis_logger.info(
                f"[WeiboCrawler.search] Current search keyword: {keyword}"
            )
            page = 1
            while (
                page - start_page + 1
            ) * weibo_limit_count <= config.CRAWLER_MAX_NOTES_COUNT:
                if page < start_page:
                    wis_logger.info(f"[WeiboCrawler.search] Skip page: {page}")
                    page += 1
                    continue
                try:
                    wis_logger.debug(
                        f"[WeiboCrawler.search] search weibo keyword: {keyword}, page: {page}"
                    )
                    search_res = await self.wb_client.get_note_by_keyword(
                        keyword=keyword, page=page, search_type=SearchType.DEFAULT
                    )
                    note_id_list: List[str] = []
                    note_list = filter_search_result_card(search_res.get("cards", []))
                    for note_item in note_list:
                        if note_item:
                            mblog: Dict = note_item.get("mblog", {})
                            if mblog:
                                note_id_list.append(mblog.get("id", ""))
                                await self.store.update_weibo_note(note_item)

                    page += 1
                    await self.batch_get_notes_comments(note_id_list)

                except Exception as ex:
                    wis_logger.error(
                        f"[WeiboCrawler.search] Search note  error: {ex}"
                    )
                    # 发生异常了，则打印当前爬取的关键词和页码，用于后续继续爬取
                    wis_logger.info(
                        "------------------------------------------记录当前爬取的关键词和页码------------------------------------------"
                    )
                    for i in range(10):
                        wis_logger.error(
                            f"[WeiboCrawler.search] Current keyword: {keyword}, page: {page}"
                        )
                    wis_logger.info(
                        "------------------------------------------记录当前爬取的关键词和页码---------------------------------------------------"
                    )
                    return

    async def get_specified_notes(self, note_ids: List[str]):
        """
        get specified notes info
        Returns:

        """
        semaphore = asyncio.Semaphore(MAX_CONCURRENCY_NUM)
        task_list = [
            self.get_note_info_task(note_id=note_id, semaphore=semaphore)
            for note_id in note_ids
        ]
        video_details = await asyncio.gather(*task_list)
        for note_item in video_details:
            if note_item:
                await self.store.update_weibo_note(note_item)
        await self.batch_get_notes_comments(note_ids)

    async def get_note_info_task(
        self, note_id: str, semaphore: asyncio.Semaphore
    ) -> Optional[Dict]:
        """
        get note detail task
        Args:
            note_id:
            semaphore:

        Returns:

        """
        async with semaphore:
            try:
                result = await self.wb_client.get_note_info_by_id(note_id)
                return result
            except DataFetchError as ex:
                wis_logger.error(
                    f"[WeiboCrawler.get_note_info_task] Get note detail error: {ex}"
                )
                return None
            except KeyError as ex:
                wis_logger.error(
                    f"[WeiboCrawler.get_note_info_task] have not fund note detail note_id:{note_id}, err: {ex}"
                )
                return None

    async def batch_get_notes_comments(self, note_id_list: List[str]):
        """
        batch get notes comments
        Args:
            note_id_list:

        Returns:

        """
        if not ENABLE_GET_COMMENTS:
            wis_logger.info(
                f"[WeiboCrawler.batch_get_note_comments] Crawling comment mode is not enabled"
            )
            return

        wis_logger.debug(
            f"[WeiboCrawler.batch_get_notes_comments] note ids:{note_id_list}"
        )
        semaphore = asyncio.Semaphore(MAX_CONCURRENCY_NUM)
        task_list: List[Task] = []
        for note_id in note_id_list:
            task = asyncio.create_task(
                self.get_note_comments(note_id, semaphore), name=note_id
            )
            task_list.append(task)
        await asyncio.gather(*task_list)

    async def get_note_comments(self, note_id: str, semaphore: asyncio.Semaphore):
        """
        get note comments by note id
        Args:
            note_id:
            semaphore:

        Returns:

        """
        async with semaphore:
            try:
                wis_logger.debug(
                    f"[WeiboCrawler.get_note_comments] begin get note_id: {note_id} comments ..."
                )
                await self.wb_client.get_note_all_comments(
                    note_id=note_id,
                    crawl_interval=random.randint(
                        1, 3
                    ),  # 微博对API的限流比较严重，所以延时提高一些
                    callback=self.store.batch_update_weibo_note_comments,
                )
            except DataFetchError as ex:
                wis_logger.error(
                    f"[WeiboCrawler.get_note_comments] get note_id: {note_id} comment error: {ex}"
                )
            except Exception as e:
                wis_logger.error(
                    f"[WeiboCrawler.get_note_comments] may be been blocked, err:{e}"
                )

    async def get_creators_and_notes(self, creator_ids: List[str]) -> None:
        """
        Get creator's information and their notes and comments
        Returns:

        """
        wis_logger.info(
            "[WeiboCrawler.get_creators_and_notes] Begin get weibo creators"
        )
        for user_id in creator_ids:
            createor_info_res: Dict = await self.wb_client.get_creator_info_by_id(
                creator_id=user_id
            )
            if createor_info_res:
                createor_info: Dict = createor_info_res.get("userInfo", {})
                wis_logger.info(
                    f"[WeiboCrawler.get_creators_and_notes] creator info: {createor_info}"
                )
                if not createor_info:
                    raise DataFetchError("Get creator info error")
                await self.store.save_creator(user_id, user_info=createor_info)

                # Get all note information of the creator
                all_notes_list = await self.wb_client.get_all_notes_by_creator_id(
                    creator_id=user_id,
                    container_id=createor_info_res.get("lfid_container_id"),
                    crawl_interval=0,
                    callback=self.store.batch_update_weibo_notes,
                )

                note_ids = [
                    note_item.get("mblog", {}).get("id")
                    for note_item in all_notes_list
                    if note_item.get("mblog", {}).get("id")
                ]
                await self.batch_get_notes_comments(note_ids)

            else:
                wis_logger.error(
                    f"[WeiboCrawler.get_creators_and_notes] get creator info error, creator_id:{user_id}"
                )
