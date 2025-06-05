import asyncio
import random
from typing import Dict, List, Optional, Tuple
from ..mc_commen.tools.time_util import rfc2822_to_timestamp, is_cacheup, rfc2822_to_china_datetime
from ..config.mc_config import (
    WEIBO_PLATFORM_NAME, 
    ENABLE_GET_COMMENTS, 
    START_PAGE, 
    CRAWLER_MAX_NOTES_COUNT, 
    WEIBO_SEARCH_TYPE, 
    SEARCH_UP_TIME, CREATOR_SEARCH_UP_TIME)
from ..mc_commen import AccountWithIpPoolManager, ProxyIpPool, wis_logger, create_ip_pool
from .store_impl import update_weibo_note, update_weibo_note_comment
from .client import WeiboClient
from .exception import DataFetchError
from .field import SearchType
from .help import filter_search_result_card
# from ..mc_commen.tools.utils import process_html_string
from ..basemodels import CrawlResult
import regex as re


class WeiboCrawler:
    def __init__(self, db_manager=None):
        self.wb_client = WeiboClient()
        self.db_manager = db_manager

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
                         creator_ids: List[str] = []) -> Tuple[str, dict]:
        try:
            await self.async_initialize()
        except Exception as e:
            wis_logger.error(f"initialize weibo crawler failed: {e}")
            return "", {}

        fresh_notes = []

        if creator_ids:
            creator_ids = set(creator_ids)
            creator_ids.discard("homefeed")
            fresh_notes.extend(await self.get_notes_by_creators(creator_ids, existings, CREATOR_SEARCH_UP_TIME))

        if keywords:
            if WEIBO_SEARCH_TYPE == "REAL_TIME":
                search_type = SearchType.REAL_TIME
            elif WEIBO_SEARCH_TYPE == "POPULAR":
                search_type = SearchType.POPULAR
            elif WEIBO_SEARCH_TYPE == "VIDEO":
                search_type = SearchType.VIDEO
            else:   
                search_type = SearchType.DEFAULT
            fresh_notes.extend(await self.search_notes(keywords, existings, SEARCH_UP_TIME, search_type))

        markdown = ""
        link_dict = {}

        for note in fresh_notes:
            content = note.get("content").replace("\n", " ")
            create_time = note.get("create_time")
            liked_count = note.get("liked_count")
            comments_count = note.get("comments_count")
            shared_count = note.get("shared_count")
            # ip_location = note.get("ip_location")
            # user_id = note.get("user_id")
            # nickname = note.get("nickname")
            # gender = note.get("gender")
            _key = f"[{len(link_dict)+1}]"
            link_dict[_key] = note.get("note_id")
            markdown += f"* {_key}{content} (发布时间： {create_time} 点赞量：{liked_count} 评论量：{comments_count} 转发量：{shared_count}) {_key}\n"

        return markdown.replace("#", ""), link_dict
    
    async def post_as_article(self, note_id: str) -> Optional[CrawlResult]:
        note_url = f"https://m.weibo.cn/detail/{note_id}"
        if self.db_manager:
            # 社交媒体url 相对固定
            cached_result = await self.db_manager.get_cached_url(note_url, days_threshold=365)
            if cached_result:
                return cached_result
            
        note_detail = await self.get_note_info(note_id)
        try:
            mblog: Dict = note_detail.get("mblog", {})
            content = mblog.get("text")
            title = mblog.get("status_title")
            user_info: Dict = mblog.get("user")
            create_time = str(rfc2822_to_china_datetime(mblog.get("created_at")))
            liked_count = mblog.get("attitudes_count", 0)
            comments_count = mblog.get("comments_count", 0)
            shared_count = mblog.get("reposts_count", 0)
            ip_location = mblog.get("region_name", "")
            user_id = user_info.get("id")
            nickname = user_info.get("screen_name", "")
            gender = '女' if user_info.get('gender') == "f" else '男'
        except Exception as e:
            wis_logger.error(f"get note_id:{note_id} detail failed: {e}")
            return None

        author = f"{nickname} ({user_id}) "
        if gender:
            author += f"({gender}) "
        if ip_location:
            author += f"{ip_location} "
        html = f"{content}\n\n点赞量：{liked_count} 评论量：{comments_count} 转发量：{shared_count}"

        comments = await self.get_note_comments(note_id)
        if comments:
            html += f"\n\n评论区：\n{comments}"

        pattern = r'<span class="url-icon">.*?</span>'
        html = re.sub(pattern, '', html, flags=re.DOTALL)

        result = CrawlResult(
            url=note_url,
            cleaned_html=html,
            author=author,
            publish_date=create_time,
            title=title,
        )

        if self.db_manager:
            await self.db_manager.cache_url(result)
        return result

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
        gender = '女' if user_info.get('gender') == "f" else '男'
        desc = user_info.get('description')
        ip_location = user_info.get("source", "")
        verify = user_info.get('verified_reason')
        fans = user_info.get('followers_count', '')

        markdown = f"昵称:{nickname}({creator_id})\n性别:{gender}\n"
        if verify:
            markdown += f"认证:{verify}\n"
        if ip_location:
            markdown += f"来自:{ip_location}\n"
        markdown += f"简介:{desc}\n粉丝量:{fans}"
        return markdown

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
            page = 1
            while (
                page - start_page + 1
            ) * weibo_limit_count <= CRAWLER_MAX_NOTES_COUNT:
                if page < start_page:
                    wis_logger.debug(f"Current search keyword: {keyword}, Skip page: {page} as setting")
                    page += 1
                    continue
                wis_logger.debug(
                    f"search weibo keyword: {keyword}, page: {page}"
                )

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
                    mblog: Dict = note_item.get("mblog", {})
                    if not mblog:
                        continue
                    note_id = mblog.get("id", "")
                    if not note_id or note_id in existings:
                        continue
                    # existings.add(note_id)  will add when llm extracting finished
                    # print("create_time", str(rfc2822_to_china_datetime(mblog.get("created_at"))))
                    if is_cacheup(rfc2822_to_timestamp(mblog.get("created_at")), limit_hours):
                        note = update_weibo_note(mblog, keyword)
                        if self.db_manager:
                            await self.db_manager.add_wb_cache(note)
                        notes.append(note)
                page += 1
        return notes

    async def get_note_info(self, note_id: str) -> Optional[Dict]:
        # todo should read first from db for cache
        try:
            return await self.wb_client.get_note_info_by_id(note_id)
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
 
    async def get_note_comments(self, note_id: str) -> str:
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
            return ""
        
        # todo should read first from db for cache
        wis_logger.debug(f"begin get note_id: {note_id} comments ...")
        results = await self.wb_client.get_note_all_comments(
            note_id=note_id,
            crawl_interval=random.randint(1, 3)
        )
        return update_weibo_note_comment(results)

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
        results = []
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
            
            since_id = ""
            crawler_total_count = 0
            for _ in range(3):
                try:
                    notes_res = await self.wb_client.get_notes_by_creator(
                        user_id, createor_info_res.get("lfid_container_id", ""), since_id
                    )
                except Exception as e:
                    wis_logger.warning(f"get user_id:{user_id} notes failed by error: {e}, will retry for max 3 times")
                    continue
                if not notes_res:
                    wis_logger.warning(
                        f"get user_id:{user_id} notes is empty, will retry for max 3 times"
                    )
                    continue

                since_id = notes_res.get("cardlistInfo", {}).get("since_id", "0")
                if "cards" not in notes_res:
                    wis_logger.warning(
                        f"get user_id:{user_id} notes no 'notes' key found in response: {notes_res}, will retry for max 3 times"
                    )
                    continue

                notes = notes_res["cards"]
                wis_logger.debug(
                    f"got user_id:{user_id} notes len : {len(notes)}"
                )
                notes = [note for note in notes if note.get("card_type") == 9]
                for idx, note in enumerate(notes):
                    mblog: Dict = note.get("mblog", {})
                    if not mblog:
                        continue
                    note_id = mblog.get("id", "")
                    if not note_id or note_id in existings:
                        continue
                    # existings.add(note_id)  will add when llm extracting finished
                    # print("create_time", str(rfc2822_to_china_datetime(mblog.get("created_at"))))
                    if is_cacheup(rfc2822_to_timestamp(mblog.get("created_at")), limit_hours):
                        note = update_weibo_note(mblog)
                        if self.db_manager:
                            await self.db_manager.add_wb_cache(note)
                        results.append(note)
                    else:
                        if idx >= 3:
                            wis_logger.debug("too old notes, will discard this and the rest...")
                            crawler_total_count += 10000
                            break
                    
                crawler_total_count += 10
                if notes_res.get("cardlistInfo", {}).get("total", 0) <= crawler_total_count:
                    break
                await asyncio.sleep(0.2)
        return results
