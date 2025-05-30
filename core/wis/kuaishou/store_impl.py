from ..mc_commen.tools import utils
from typing import Dict


def update_kuaishou_video(video_item: Dict, limit_hours: int = 48, keyword: str = "") -> Dict:
    photo_info: Dict = video_item.get("photo", {})
    video_id = photo_info.get("id")
    if not video_id:
        return None
    user_info = video_item.get("author", {})
    create_time = photo_info.get("timestamp")

    if not utils.is_cacheup(create_time, limit_hours):
        return None
    create_time = utils.get_date_str_from_unix_time(create_time)

    # todo should save to db first

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
        "video_play_url": photo_info.get("photoUrl", ""),
        "source_keyword": keyword,
        "commnets": ""
    }

def update_ks_video_comment(comment_item: Dict) -> str:
    create_time = utils.get_date_str_from_unix_time(comment_item.get("timestamp"))
    content = comment_item.get("content")
    sub_comment_count = comment_item.get("subCommentCount") if comment_item.get("subCommentCount") else 0
    like_count = comment_item.get("realLikedCount") if comment_item.get("realLikedCount") else 0
    user_id = comment_item.get("authorId")
    # nickname = comment_item.get("authorName")

    comment_str = f"用户 {user_id} 于 {create_time} 发表评论:\n{content}\n获赞：{like_count}, 回复：{sub_comment_count}\n"
    sub_comments = comment_item.get('subComments', [])
    for sub_comment in sub_comments:
        create_time = utils.get_date_str_from_unix_time(sub_comment.get("timestamp"))
        content = sub_comment.get("content")
        like_count = sub_comment.get("realLikedCount") if sub_comment.get("realLikedCount") else 0
        user_id = sub_comment.get("authorId")
        # nickname = sub_comment.get("authorName")
        replyto = sub_comment.get("replyTo")
        comment_str += f"\t用户 {user_id} 于 {create_time} 回复 用户 {replyto} :\n\t{content}\n\t获赞：{like_count}\n"
    if len(sub_comments) < sub_comment_count:
        comment_str += f"\t还有 {sub_comment_count - len(sub_comments)} 条回复未显示...\n"
    
    # todo should save to db first
    return comment_str
