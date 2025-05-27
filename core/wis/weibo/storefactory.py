from typing import List
from .store_impl import WeiboDbStoreImplement
from ..base.mc_crawler import AbstractStore
from ..mc_commen import wis_logger, base_directory
from ..mc_commen.tools import utils
import asyncio
import json
import os
from typing import Dict
import aiofiles
import regex as re


def calculate_number_of_files(file_store_path: str) -> int:
    """计算数据保存文件的前部分排序数字，支持每次运行代码不写到同一个文件中
    Args:
        file_store_path;
    Returns:
        file nums
    """
    if not os.path.exists(file_store_path):
        return 1
    try:
        return max([int(file_name.split("_")[0]) for file_name in os.listdir(file_store_path)]) + 1
    except ValueError:
        return 1


class WeiboJsonStoreImplement(AbstractStore):
    json_store_path = os.path.join(base_directory, "mc_data", "weibo")
    lock = asyncio.Lock()
    file_count: int = calculate_number_of_files(json_store_path)

    def make_save_file_name(self, store_type: str) -> str:
        """
        make save file name by platform_save_data type
        Args:
            store_type: Save type contains content and comments（contents | comments）

        Returns:

        """
        os.makedirs(self.json_store_path, exist_ok=True)
        return os.path.join(self.json_store_path, f"{store_type}_{utils.get_current_date()}.json")

    async def save_data_to_json(self, save_item: Dict, store_type: str):
        """
        Below is a simple way to save it in json format.
        Args:
            save_item: save content dict info
            store_type: Save type contains content and comments（contents | comments）

        Returns:

        """
        save_file_name = self.make_save_file_name(store_type=store_type)
        save_data = []

        async with self.lock:
            if os.path.exists(save_file_name):
                async with aiofiles.open(save_file_name, 'r', encoding='utf-8') as file:
                    save_data = json.loads(await file.read())

            save_data.append(save_item)
            async with aiofiles.open(save_file_name, 'w', encoding='utf-8') as file:
                await file.write(json.dumps(save_data, ensure_ascii=False))

    async def store_content(self, content_item: Dict):
        """
        content JSON storage implementation
        Args:
            content_item:

        Returns:

        """
        await self.save_data_to_json(content_item, "contents")

    async def store_comment(self, comment_item: Dict):
        """
        comment JSON storage implementatio
        Args:
            comment_item:

        Returns:

        """
        await self.save_data_to_json(comment_item, "comments")

    async def store_creator(self, creator: Dict):
        """
        creator JSON storage implementation
        Args:
            creator:

        Returns:

        """
        await self.save_data_to_json(creator, "creator")


class WeibostoreFactory:
    def __init__(self, test_mode: bool = False):
        if test_mode:
            self.store = WeiboJsonStoreImplement()
        else:
            self.store = WeiboDbStoreImplement()

    async def batch_update_weibo_notes(self, note_list: List[Dict]):
        if not note_list:
            return
        for note_item in note_list:
            await self.store.update_weibo_note(note_item)


    async def update_weibo_note(self, note_item: Dict, keywords: List[str] = []):
        mblog: Dict = note_item.get("mblog")
        user_info: Dict = mblog.get("user")
        note_id = mblog.get("id")
        content_text = mblog.get("text")
        clean_text = re.sub(r"<.*?>", "", content_text)
        save_content_item = {
            # 微博信息
            "note_id": note_id,
            "content": clean_text,
            "create_time": utils.rfc2822_to_timestamp(mblog.get("created_at")),
            "create_date_time": str(utils.rfc2822_to_china_datetime(mblog.get("created_at"))),
            "liked_count": str(mblog.get("attitudes_count", 0)),
            "comments_count": str(mblog.get("comments_count", 0)),
            "shared_count": str(mblog.get("reposts_count", 0)),
            "last_modify_ts": utils.get_current_timestamp(),
            "note_url": f"https://m.weibo.cn/detail/{note_id}",
            "ip_location": mblog.get("region_name", "").replace("发布于 ", ""),

            # 用户信息
            "user_id": str(user_info.get("id")),
            "nickname": user_info.get("screen_name", ""),
            "gender": user_info.get("gender", ""),
            "profile_url": user_info.get("profile_url", ""),
            "avatar": user_info.get("profile_image_url", ""),
            "source_keyword": keywords,
        }
        wis_logger.info(
            f"[store.weibo.update_weibo_note] weibo note id:{note_id}, title:{save_content_item.get('content')[:24]} ...")
        await self.store.store_content(content_item=save_content_item)


    async def batch_update_weibo_note_comments(self, note_id: str, comments: List[Dict]):
        if not comments:
            return
        for comment_item in comments:
            await self.store.update_weibo_note_comment(note_id, comment_item)


    async def update_weibo_note_comment(self, note_id: str, comment_item: Dict):
        comment_id = str(comment_item.get("id"))
        user_info: Dict = comment_item.get("user")
        content_text = comment_item.get("text")
        clean_text = re.sub(r"<.*?>", "", content_text)
        save_comment_item = {
            "comment_id": comment_id,
            "create_time": utils.rfc2822_to_timestamp(comment_item.get("created_at")),
            "create_date_time": str(utils.rfc2822_to_china_datetime(comment_item.get("created_at"))),
            "note_id": note_id,
            "content": clean_text,
            "sub_comment_count": str(comment_item.get("total_number", 0)),
            "like_count": comment_item.get("like_count") if comment_item.get("like_count") else 0,
            "last_modify_ts": utils.get_current_timestamp(),
            "ip_location": comment_item.get("source", "").replace("来自", ""),
            "parent_comment_id": comment_item.get("rootid", ""),

            # 用户信息
            "user_id": str(user_info.get("id")),
            "nickname": user_info.get("screen_name", ""),
            "gender": user_info.get("gender", ""),
            "profile_url": user_info.get("profile_url", ""),
            "avatar": user_info.get("profile_image_url", ""),
        }
        wis_logger.info(
            f"[store.weibo.update_weibo_note_comment] Weibo note comment: {comment_id}, content: {save_comment_item.get('content', '')[:24]} ...")
        await self.store.store_comment(comment_item=save_comment_item)

    async def save_creator(self, user_id: str, user_info: Dict):
        local_db_item = {
            'user_id': user_id,
            'nickname': user_info.get('screen_name'),
            'gender': '女' if user_info.get('gender') == "f" else '男',
            'avatar': user_info.get('avatar_hd'),
            'desc': user_info.get('description'),
            'ip_location': user_info.get("source", "").replace("来自", ""),
            'follows': user_info.get('follow_count', ''),
            'fans': user_info.get('followers_count', ''),
            'tag_list': '',
            "last_modify_ts": utils.get_current_timestamp(),
        }
        wis_logger.info(f"[store.weibo.save_creator] creator:{local_db_item}")
        await self.store.store_creator(local_db_item)
