import asyncio
import random
from typing import Dict, List, Optional, Tuple

from ..config.mc_config import WEIBO_PLATFORM_NAME, ENABLE_GET_COMMENTS, MAX_CONCURRENCY_NUM, START_PAGE, CRAWLER_MAX_NOTES_COUNT
from ..mc_commen import AccountWithIpPoolManager, ProxyIpPool, wis_logger, create_ip_pool
from .store_impl import update_weibo_note, update_weibo_note_comment
from .client import WeiboClient
from .exception import DataFetchError
from .field import SearchType
from .help import filter_search_result_card


class WeiboCrawler:
    def __init__(self):
        self.wb_client = WeiboClient()

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

    async def posts_list(self,
                         keywords: List[str],
                         existings: set[str] = set(),
                         limit_hours: int = 48,
                         creator_ids: set[str] = set(),
                         search_type: SearchType = SearchType.DEFAULT) -> Tuple[str, dict]:

        fresh_notes = []

        if creator_ids:
            fresh_notes.extend(await self.get_notes_by_creators(creator_ids, existings, limit_hours))

        if keywords:
            fresh_notes.extend(await self.search_notes(keywords, existings, limit_hours, search_type))

        markdown = ""
        link_dict = {}

        for video in fresh_videos:
            title = video.get("title").replace("\n", "  ")
            desc = video.get("desc").replace("\n", " ")
            create_time = video.get("create_time")
            liked_count = video.get("liked_count")
            viewd_count = video.get("viewd_count")
            _key = f"[{len(link_dict)+1}]"
            link_dict[_key] = video
            markdown += f"* 标题：{title} 发布时间：{create_time} 点赞量：{liked_count} 播放量：{viewd_count} 描述：{desc} {_key}\n\n"

        return markdown.replace("#", ""), link_dict
    
    async def post_as_article(self, video: Dict) -> Tuple[str, Dict]:
        article = f"{video.get('title')}\n作者：{video.get('nickname')}(id: {video.get('user_id')}) 发布时间：{video.get('create_time')}\n{video.get('desc')}\n点赞量：{video.get('liked_count')} 播放量：{video.get('viewd_count')}\n\n"
        ref = {"video_url": video.get("video_url"), "video_play_url": video.get("video_play_url")}

        comments = await self.get_video_comments(video.get("video_id"))
        if not comments:
            return article, ref

        article += "评论区：\n"
        article += "\n\n".join(comments)
        return article, ref

    async def creator_as_article(self, creator_id: str) -> Optional[str]:
        try:
            createor_info_res: Dict = await self.wb_client.get_creator_info_by_id(
                creator_id=creator_id
            )
        except Exception as e:
            wis_logger.error(
                f"get creator: {creator_id} info error: {e}"
            )
            return None
        
        if not createor_info_res:
            wis_logger.warning(
                f"get creator: {creator_id} createor_info_res failed"
            )
            return None
        
        user_info: Dict = createor_info_res.get("userInfo", {})
        if not user_info:
            wis_logger.warning(
                f"get creator: {creator_id} userInfo from createor_info_res failed"
            )
            return None
        
        nickname = user_info.get('screen_name')
        gender = '女' if user_info.get('gender') == "f" else '男',
        desc = user_info.get('description')
        ip_location = user_info.get("source", "")
        follows = user_info.get('follow_count', '')
        fans = user_info.get('followers_count', '')

        return f"昵称:{nickname}\n性别:{gender}\n来自:{ip_location}\n简介:{desc}\n粉丝量:{fans} {follows}"

    async def search_notes(self, 
                           keywords: List[str], 
                           existings: set[str] = set(), 
                           limit_hours: int = 48, 
                           search_type: SearchType = SearchType.DEFAULT) -> List[Dict]:
        """
        search weibo note with keywords
        Returns:
            List[Dict]: List of note items
        """
        wis_logger.debug("Begin search weibo notes")
        weibo_limit_count = 10  # weibo limit page fixed value
        start_page = START_PAGE
        notes = []
        for keyword in keywords:
            wis_logger.debug(
                f"Current search keyword: {keyword}"
            )
            page = 1
            while (
                page - start_page + 1
            ) * weibo_limit_count <= CRAWLER_MAX_NOTES_COUNT:
                if page < start_page:
                    wis_logger.debug(f"Skip page: {page}")
                    page += 1
                    continue
                wis_logger.debug(
                    f"search weibo keyword: {keyword}, page: {page}"
                )
                # todo should read first from db for cache
                try:
                    search_res = await self.wb_client.get_note_by_keyword(
                        keyword=keyword, page=page, search_type=search_type
                    )
                except Exception as e:
                    wis_logger.error(
                        f"search weibo keyword: {keyword} not finished, but paused by error: {e}"
                    )
                    break
                
                note_list = filter_search_result_card(search_res.get("cards", []))
                for note_item in note_list:
                    if note_item:
                        mblog: Dict = note_item.get("mblog", {})
                        if mblog:
                            note_id = mblog.get("id", "")
                            if note_id and note_id not in existings:
                                existings.add(note_id)
                                note_item = update_weibo_note(note_item, limit_hours=limit_hours, keyword=keyword)
                                if note_item:
                                    notes.append(note_item)
                page += 1
        return notes

    async def get_specified_notes(self, note_ids: List[str], limit_hours: int = 48):
        """
        get specified notes info
        Returns:

        """
        semaphore = asyncio.Semaphore(MAX_CONCURRENCY_NUM)
        task_list = [
            self.get_note_info_task(note_id=note_id, semaphore=semaphore)
            for note_id in note_ids
        ]
        # Process tasks as they complete (stream-like)
        notes = []
        for task in asyncio.as_completed(task_list):
            note_detail = await task
            if not note_detail:
                continue
            note_item = update_weibo_note(note_item=note_detail, limit_hours=limit_hours)
            if note_item:
                notes.append(note_item)
        return notes

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
            # todo should read first from db for cache
            try:
                result = await self.wb_client.get_note_info_by_id(note_id)
                return result
            except DataFetchError as ex:
                wis_logger.error(
                    f"Get note detail error: {ex}"
                )
                return None
            except KeyError as ex:
                wis_logger.error(
                    f"have not fund note detail note_id:{note_id}, err: {ex}"
                )
                return None
 
    async def get_note_comments(self, note_id: str) -> List[str]:
        """
        get note comments by note id
        Args:
            note_id:
            semaphore:

        Returns:

        """
        if not ENABLE_GET_COMMENTS:
            wis_logger.info(
                f"Crawling comment mode is not enabled"
            )
            return []
        
        # todo should read first from db for cache
        wis_logger.debug(f"begin get note_id: {note_id} comments ...")
        results = await self.wb_client.get_note_all_comments(
            note_id=note_id,
            crawl_interval=random.randint(1, 3)
        )
        return [update_weibo_note_comment(comment_item) for comment_item in results]

    async def get_notes_by_creators(self, creator_ids: List[str], existings: set[str] = set(), limit_hours: int = 48) -> List[Dict]:
        """
        Get creator's information and their notes and comments
        Args:
            creator_ids: creator ids for getting notes
            existings: existing note ids for skipping
            limit_hours: limit hours for getting notes(default 48 hours means get notes in the last 48 hours)
        Returns:
            List[Dict]: crawl results
        """
        wis_logger.debug("Begin get weibo creators' notes")
        note_ids = set()
        for user_id in creator_ids:
            # Get all note information of the creator
            try:
                createor_info_res: Dict = await self.wb_client.get_creator_info_by_id(
                    creator_id=user_id
                )
            except Exception as e:
                wis_logger.error(
                    f"get creator: {user_id} info error: {e}"
                )
                continue
            
            if not createor_info_res or not createor_info_res.get("lfid_container_id", ""):
                wis_logger.error(
                    f"get creator: {user_id} lfid_container_id failed"
                )
                continue
            
            try:
                # Get all note information of the creator
                all_notes_list = await self.wb_client.get_all_notes_by_creator_id(
                    creator_id=user_id,
                    container_id=createor_info_res.get("lfid_container_id"),
                    crawl_interval=0,
                )
            except Exception as e:
                wis_logger.error(
                    f"get creator: {user_id} all_notes_list error: {e}"
                )
                continue

