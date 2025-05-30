from ..mc_commen.tools import utils
from typing import Dict
import regex as re


def update_weibo_note(note_item: Dict, keyword: str = "") -> Dict:
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
        # "last_modify_ts": utils.get_current_timestamp(),
        "note_url": f"https://m.weibo.cn/detail/{note_id}",
        "ip_location": mblog.get("region_name", "").replace("发布于 ", ""),

        # 用户信息
        "user_id": str(user_info.get("id")),
        "nickname": user_info.get("screen_name", ""),
        "gender": user_info.get("gender", ""),
        "profile_url": user_info.get("profile_url", ""),
        # "avatar": user_info.get("profile_image_url", ""),
        "source_keyword": keyword,
        }
    
    # todo should save to db first
    return save_content_item

def update_weibo_note_comment(note_id: str, comment_item: Dict) -> str:
    comment_id = str(comment_item.get("id"))
    user_info: Dict = comment_item.get("user")
    content_text = comment_item.get("text")
    clean_text = re.sub(r"<.*?>", "", content_text)

    create_time = utils.rfc2822_to_timestamp(comment_item.get("created_at"))
    create_date_time = str(utils.rfc2822_to_china_datetime(comment_item.get("created_at")))
    sub_comment_count = str(comment_item.get("total_number", 0))
    like_count = comment_item.get("like_count") if comment_item.get("like_count") else 0
    ip_location = comment_item.get("source", "").replace("来自", "")
    parent_comment_id = comment_item.get("rootid", "")

    # 用户信息
    user_id = str(user_info.get("id"))
    nickname = user_info.get("screen_name", "")
    gender = user_info.get("gender", "")
    profile_url = user_info.get("profile_url", "")

    comment_str = f"用户 {user_id} 于 {create_date_time} 发表评论:\n{clean_text}\n获赞：{like_count}, 回复：{sub_comment_count}\n"
    sub_comments = comment_item.get('sub_comments', [])
