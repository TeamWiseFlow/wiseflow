import asyncio
import random
from asyncio import Task
from typing import Dict, List, Optional, Tuple
from ..config.mc_config import CRAWLER_MAX_NOTES_COUNT, START_PAGE, MAX_CONCURRENCY_NUM, ENABLE_GET_COMMENTS, KUAISHOU_PLATFORM_NAME
# from ..base.mc_crawler import AbstractCrawler
from ..mc_commen import AccountWithIpPoolManager, ProxyIpPool, wis_logger, create_ip_pool
from .store_impl import *
from .client import KuaiShouApiClient
from .exception import DataFetchError


class KuaiShouCrawler:
    def __init__(self):
        self.ks_client = KuaiShouApiClient()

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

    async def posts_list(self,
                         keywords: List[str],
                         existings: set[str] = set(),
                         limit_hours: int = 48,
                         creator_ids: set[str] = set()) -> Tuple[str, dict]:

        fresh_videos = []
        if "homefeed" in creator_ids:
            creator_ids.remove("homefeed")
            fresh_videos.extend(await self.get_homefeed_videos(existings, limit_hours))

        if creator_ids:
            fresh_videos.extend(await self.get_videos_by_creators(creator_ids, existings, limit_hours))

        if keywords:
            fresh_videos.extend(await self.search_videos(keywords, existings, limit_hours))

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
        # get creator detail info from web html content
        try:
            createor_info: Dict = await self.ks_client.get_creator_info(creator_id)
        except Exception as e:
            wis_logger.error(
                f"get creator: {creator_id} info error: {e}"
            )
            return None
        
        if not createor_info:
            wis_logger.warning(
                f"get creator: {creator_id} info error: {createor_info}"
            )
            return None
        
        owner_count = createor_info.get("ownerCount", {})
        profile = createor_info.get("profile", {})
        if not profile and not owner_count:
            wis_logger.warning(
                f"get creator: {creator_id} info error: {createor_info}"
            )
            return None
        
        nickname = profile.get("user_name")
        gender = "女" if profile.get("gender") == "F" else "男"
        desc = profile.get("user_text")
        # follows = owner_count.get("follow")
        fans = owner_count.get("fan")
        videos_count = owner_count.get("photo_public")
        return f"昵称:{nickname}\n性别:{gender}\n简介:{desc}\n粉丝量:{fans}\n已发布视频数量:{videos_count}"

    async def search_videos(self, keywords: List[str], existings: set[str] = set(), limit_hours: int = 48) -> List[Dict]:
        """
        Search for videos and retrieve their comment information.
        Returns:

        """
        wis_logger.debug("Begin search kuaishou keywords")
        ks_limit_count = 20  # kuaishou limit page fixed value
        start_page = START_PAGE
        videos = []
        for keyword in keywords:
            search_session_id = ""
            wis_logger.debug(
                f"Current search keyword: {keyword}"
            )
            page = 1
            while (
                page - start_page + 1
            ) * ks_limit_count <= CRAWLER_MAX_NOTES_COUNT:
                if page < start_page:
                    wis_logger.debug(f"Skip page: {page}")
                    page += 1
                    continue
                wis_logger.debug(
                    f"search kuaishou keyword: {keyword}, page: {page}"
                )
                # todo should read first from db for cache
                try:
                    videos_res = await self.ks_client.search_info_by_keyword(
                        keyword=keyword,
                        pcursor=str(page),
                        search_session_id=search_session_id,
                    )
                except Exception as e:
                    wis_logger.error(
                        f"search info by keyword:{keyword} not finished, but paused by error: {e}"
                    )
                    break

                if not videos_res:
                    wis_logger.warning(
                        f"search info by keyword:{keyword} not found data"
                    )
                    break

                vision_search_photo: Dict = videos_res.get("visionSearchPhoto")
                if vision_search_photo.get("result") != 1:
                    wis_logger.warning(
                        f"search info by keyword:{keyword} not found data "
                    )
                    break
                search_session_id = vision_search_photo.get("searchSessionId", "")
                for video_detail in vision_search_photo.get("feeds", []):
                    _video_id = video_detail.get("photo", {}).get("id")
                    if not _video_id or _video_id in existings:
                        continue
                    existings.add(_video_id)
                    _video = update_kuaishou_video(video_item=video_detail, limit_hours=limit_hours, keyword=keyword)
                    if _video:
                        videos.append(_video)
                page += 1

        return videos

    async def get_specified_videos(self, video_ids: List[str], limit_hours: int = 48):
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
        videos = []
        for video_detail in video_details:
            if video_detail is not None:
                _video = update_kuaishou_video(video_item=video_detail, limit_hours=limit_hours)
                if _video:
                    videos.append(_video)
        return videos

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
            # todo should read first from db for cache
            try:
                result = await self.ks_client.get_video_info(video_id)
                if not result:
                    wis_logger.debug(f"Get video_id:{video_id} info result is None")
                    return None
                if result.get('result', 0) == 400002:
                    wis_logger.debug(f"Get video_id:{video_id} info result: {result} ...")
                    wis_logger.debug("will call user verify")
                    await self.ks_client.mark_account_invalid(self.ks_client.account_info)
                    await self.ks_client.update_account_info(force_login=True)
                    result = await self.ks_client.get_video_info(video_id)
                    if not result:
                        wis_logger.debug(f"Get video_id:{video_id} info result is None")
                        return None
                    if result.get('result', 0) == 400002:
                        wis_logger.debug(f"Get video_id:{video_id} info result: {result} ...")
                        wis_logger.info("user accnout has been banned... give out, try tomorrow")
                        return None
                return result.get("visionVideoDetail")
            except DataFetchError as ex:
                wis_logger.error(
                    f"Get video detail error: {ex}"
                )
                return None
            except KeyError as ex:
                wis_logger.error(
                    f"have not fund video detail video_id:{video_id}, err: {ex}"
                )
                return None

    async def get_videos_by_creators(self, creator_ids: set[str], existings: set[str] = set(), limit_hours: int = 48) -> List[Dict]:
        """
        Get creator's information and their videos and comments
        Args:
            creator_ids: creator ids for getting videos
            existings: existing video ids for skipping
            limit_hours: limit hours for getting videos(default 48 hours means get videos in the last 48 hours)
        Returns:
            set[Dict]: crawl results
        """
        wis_logger.debug("Begin get kuaishou creators' videos")
        video_ids = set()
        for user_id in creator_ids:
            # Get all video information of the creator
            pcursor = ""
            # 最多获取前三页
            for _ in range(3):
                try:
                    videos_res = await self.ks_client.get_video_by_creater(user_id, pcursor)
                except Exception as e:
                    wis_logger.error(
                        f"get user_id:{user_id} videos not finished, but paused by error: {e}"
                    )
                    break
                
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
                for video in videos:
                    _video_id = video.get("photo", {}).get("id")
                    if not _video_id or _video_id in existings:
                        continue
                    existings.add(_video_id)
                    video_ids.add(_video_id)
                if pcursor == "no_more":
                    break
                await asyncio.sleep(random.random())

        semaphore = asyncio.Semaphore(MAX_CONCURRENCY_NUM)
        task_list = [
            self.get_video_info_task(video_id, semaphore)
            for video_id in video_ids]
        # Process tasks as they complete (stream-like)
        videos = []
        for task in asyncio.as_completed(task_list):
            video_detail = await task
            if not video_detail:
                continue
            _video = update_kuaishou_video(video_item=video_detail, limit_hours=limit_hours)
            if _video:
                videos.append(_video)
        return videos

    async def get_homefeed_videos(self, existings: set[str] = set(), limit_hours: int = 48) -> List[Dict]:
        """
        Get homefeed videos and comments
        """
        wis_logger.debug("Begin get kuaishou homefeed videos")
        pcursor = ""
        saved_video_count = 0
        videos = []
        while saved_video_count <= CRAWLER_MAX_NOTES_COUNT:
            try:
                homefeed_videos_res = await self.ks_client.get_homefeed_videos(pcursor)
            except Exception as e:
                wis_logger.error(
                    f"get homefeed not finished, but paused by error: {e}"
                )
                break
            
            if not homefeed_videos_res:
                wis_logger.debug("No more content!")
                break

            brilliant_type_data: Dict = homefeed_videos_res.get("brilliantTypeData")
            pcursor = brilliant_type_data.get("pcursor", "")
            videos_list: List[Dict] = brilliant_type_data.get("feeds", [])
            if not videos_list:
                wis_logger.debug("No more content!")
                break

            for video_detail in videos_list:
                _video_id = video_detail.get("photo", {}).get("id")
                if not _video_id or _video_id in existings:
                    continue
                existings.add(_video_id)
                _video = update_kuaishou_video(video_item=video_detail, limit_hours=limit_hours)
                if _video:
                    videos.append(_video)
                    saved_video_count += 1

        wis_logger.debug(f"Kuaishou homefeed videos crawler finished, saved_video_count: {saved_video_count}")

        return videos

    async def get_video_comments(self, video_id: str) -> List[str]:
        if not ENABLE_GET_COMMENTS:
            wis_logger.info("Crawling comment mode is not enabled")
            return []
        
        # todo should read first from db for cache
        wis_logger.debug(f"begin get video_id: {video_id} comments ...")
        results =  await self.ks_client.get_video_all_comments(photo_id=video_id, crawl_interval=random.random())
        return [update_ks_video_comment(comment_item) for comment_item in results]
