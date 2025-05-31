from ..mc_commen.tools.time_util import rfc2822_to_china_datetime
from typing import Dict, List
import regex as re


def update_weibo_note(mblog: Dict, keyword: str = "") -> Dict:
    user_info: Dict = mblog.get("user")
    note_id = mblog.get("id")
    content_text = mblog.get("text")
    clean_text = re.sub(r"<.*?>", "", content_text)
    save_content_item = {
        # 微博信息
        "note_id": note_id,
        "content": clean_text,
        "create_time": str(rfc2822_to_china_datetime(mblog.get("created_at"))),
        "liked_count": str(mblog.get("attitudes_count", 0)),
        "comments_count": str(mblog.get("comments_count", 0)),
        "shared_count": str(mblog.get("reposts_count", 0)),
        # "last_modify_ts": utils.get_current_timestamp(),
        "note_url": f"https://m.weibo.cn/detail/{note_id}",
        "ip_location": mblog.get("region_name", ""),
        "comments": "",
        # 用户信息
        "user_id": str(user_info.get("id")),
        "nickname": user_info.get("screen_name", ""),
        "gender": '女' if user_info.get('gender') == "f" else '男',
        "profile_url": user_info.get("profile_url", ""),
        # "avatar": user_info.get("profile_image_url", ""),
        "source_keyword": keyword,
        }
    
    # todo should save to db first
    return save_content_item

def update_weibo_note_comment(comment_items: List[Dict]) -> str:
    comment_str = ""
    for comment_item in comment_items:
        # print("comment_item", comment_item)
        user_info: Dict = comment_item.get("user")
        content = comment_item.get("text")
        create_time = str(rfc2822_to_china_datetime(comment_item.get("created_at")))
        sub_comment_count = str(comment_item.get("total_number", 0))
        like_count = comment_item.get("like_count") if comment_item.get("like_count") else 0
        ip_location = comment_item.get("source", "")
        # 用户信息
        user_id = str(user_info.get("id"))
        # nickname = user_info.get("screen_name", "")
        gender = '女' if user_info.get('gender') == "f" else '男'
        comment_str += f"用户 {user_id} "
        if gender:
            comment_str += f"({gender}) "
        if ip_location:
            comment_str += f"({ip_location}) "
        comment_str += f"于 {create_time} 发表评论:\n{content}\n获赞：{like_count}, 回复：{sub_comment_count}\n"
        sub_comments = comment_item.get('comments')
        if sub_comments and isinstance(sub_comments, list):
            for sub_comment in sub_comments:
                user_info: Dict = sub_comment.get("user")
                content = sub_comment.get("text")
                create_time = str(rfc2822_to_china_datetime(sub_comment.get("created_at")))
                like_count = sub_comment.get("like_count") if sub_comment.get("like_count") else 0
                ip_location = sub_comment.get("source", "")
                # 用户信息
                user_id = str(user_info.get("id"))
                # nickname = user_info.get("screen_name", "")
                gender = '女' if user_info.get('gender') == "f" else '男'
                comment_str += f"\t用户 {user_id} "
                if gender:
                    comment_str += f"({gender}) "
                if ip_location:
                    comment_str += f"({ip_location}) "
                comment_str += f"于 {create_time} 回复评论:\n\t{content}\n\t获赞：{like_count}\n"
    # todo should save to db first(update note_id comments)
    return comment_str
