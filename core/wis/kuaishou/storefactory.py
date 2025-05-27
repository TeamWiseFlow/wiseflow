from typing import List
from .store_impl import KuaishouDbStoreImplement
from ..base.mc_crawler import AbstractStore
from ..mc_commen import wis_logger, base_directory
from ..mc_commen.tools import utils
import asyncio
import json
import os
from typing import Dict
import aiofiles


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
        return (
            max(
                [
                    int(file_name.split("_")[0])
                    for file_name in os.listdir(file_store_path)
                ]
            )
            + 1
        )
    except ValueError:
        return 1


class KuaishouJsonStoreImplement(AbstractStore):
    json_store_path = os.path.join(base_directory, "mc_data", "kuaishou")
    lock = asyncio.Lock()
    file_count: int = calculate_number_of_files(json_store_path)

    def make_save_file_name(self, store_type: str) -> str:
        """
        make save file name by store type
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
                async with aiofiles.open(save_file_name, "r", encoding="utf-8") as file:
                    save_data = json.loads(await file.read())

            save_data.append(save_item)
            async with aiofiles.open(save_file_name, "w", encoding="utf-8") as file:
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
        Kuaishou content JSON storage implementation
        Args:
            creator: creator dict

        Returns:

        """
        await self.save_data_to_json(creator, "creator")


class KuaishouStoreFactory:

    def __init__(self, test_mode: bool = False):
        if test_mode:
            self.store = KuaishouJsonStoreImplement()
        else:
            self.store = KuaishouDbStoreImplement()

    async def update_kuaishou_video(self, video_item: Dict, keywords: List[str] = []):
        photo_info: Dict = video_item.get("photo", {})
        video_id = photo_info.get("id")
        if not video_id:
            return
        user_info = video_item.get("author", {})
        save_content_item = {
            "video_id": video_id,
            "video_type": str(video_item.get("type")),
            "title": photo_info.get("caption", "")[:500],
            "desc": photo_info.get("caption", "")[:500],
            "create_time": photo_info.get("timestamp"),
            "user_id": user_info.get("id"),
            "nickname": user_info.get("name"),
            "avatar": user_info.get("headerUrl", ""),
            "liked_count": str(photo_info.get("realLikeCount")),
            "viewd_count": str(photo_info.get("viewCount")),
            "last_modify_ts": utils.get_current_timestamp(),
            "video_url": f"https://www.kuaishou.com/short-video/{video_id}",
            "video_cover_url": photo_info.get("coverUrl", ""),
            "video_play_url": photo_info.get("photoUrl", ""),
            "source_keyword": keywords,
        }
        wis_logger.debug(
            f"[store.kuaishou.update_kuaishou_video] Kuaishou video id:{video_id}, title:{save_content_item.get('title')}"
        )
        await self.store.store_content(
            content_item=save_content_item
        )


    async def batch_update_ks_video_comments(self, video_id: str, comments: List[Dict]):
        if not comments:
            return
        wis_logger.debug(
            f"[store.kuaishou.batch_update_ks_video_comments] video_id:{video_id}, comments:{comments}"
        )
        for comment_item in comments:
            await self.update_ks_video_comment(video_id, comment_item)


    async def update_ks_video_comment(self, video_id: str, comment_item: Dict):
        comment_id = comment_item.get("commentId")
        save_comment_item = {
            "comment_id": comment_id,
            "create_time": comment_item.get("timestamp"),
            "video_id": video_id,
            "content": comment_item.get("content"),
            "user_id": comment_item.get("authorId"),
            "nickname": comment_item.get("authorName"),
            "avatar": comment_item.get("headurl"),
            "sub_comment_count": str(comment_item.get("subCommentCount", 0)),
            "last_modify_ts": utils.get_current_timestamp(),
            "like_count": (
                comment_item.get("realLikedCount")
                if comment_item.get("realLikedCount")
                else 0
            ),
        }
        wis_logger.debug(
            f"[store.kuaishou.update_ks_video_comment] Kuaishou video comment: {comment_id}, content: {save_comment_item.get('content')}"
        )
        await self.store.store_comment(
            comment_item=save_comment_item
        )


    async def save_creator(self, user_id: str, creator: Dict):
        owner_count = creator.get("ownerCount", {})
        profile = creator.get("profile", {})

        local_db_item = {
            "user_id": user_id,
            "nickname": profile.get("user_name"),
            "gender": "女" if profile.get("gender") == "F" else "男",
            "avatar": profile.get("headurl"),
            "desc": profile.get("user_text"),
            "ip_location": "",
            "follows": owner_count.get("follow"),
            "fans": owner_count.get("fan"),
            "videos_count": owner_count.get("photo_public"),
            "last_modify_ts": utils.get_current_timestamp(),
        }
        wis_logger.debug(f"[store.kuaishou.save_creator] creator:{local_db_item}")
        await self.store.store_creator(local_db_item)
