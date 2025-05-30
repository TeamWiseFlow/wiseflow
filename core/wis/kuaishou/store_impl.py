from ..mc_commen.tools import utils
from typing import Dict


def update_kuaishou_video(video_item: Dict, limit_hours: int = 48) -> Dict:
    photo_info: Dict = video_item.get("photo", {})
    video_id = photo_info.get("id")
    if not video_id:
        return None
    user_info = video_item.get("author", {})
    create_time = photo_info.get("timestamp")

    if not utils.is_cacheup(create_time, limit_hours):
        return None
    create_time = utils.get_date_str_from_unix_time(create_time)

    return {
        "video_id": video_id,
        "video_type": str(video_item.get("type")),
        "title": photo_info.get("caption", ""),
        "desc": photo_info.get("caption", ""),
        "create_time": create_time,
        "user_id": user_info.get("id"),
        "nickname": user_info.get("name"),
        # "avatar": user_info.get("headerUrl", ""),
        "liked_count": str(photo_info.get("realLikeCount")),
        "viewd_count": str(photo_info.get("viewCount")),
        # "last_modify_ts": utils.get_current_timestamp(),
        "video_url": f"https://www.kuaishou.com/short-video/{video_id}",
        # "video_cover_url": photo_info.get("coverUrl", ""),
        "video_play_url": photo_info.get("photoUrl", "")
    }

def update_ks_video_comment(comment_item: Dict):
    # comment_id = comment_item.get("commentId")
    return {
        # "comment_id": comment_id,
        "create_time": utils.get_date_str_from_unix_time(comment_item.get("timestamp")),
        # "video_id": video_id,
        "content": comment_item.get("content"),
        "user_id": comment_item.get("authorId"),
        "nickname": comment_item.get("authorName"),
        # "avatar": comment_item.get("headurl"),
        "sub_comment_count": str(comment_item.get("subCommentCount", 0)),
        # "last_modify_ts": utils.get_current_timestamp(),
        "like_count": (
            comment_item.get("realLikedCount")
            if comment_item.get("realLikedCount")
            else 0
        ),
    }