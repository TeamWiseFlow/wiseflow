import json
from typing import Any, Dict, List
from core.async_logger import base_directory, wis_logger


custom_config_path = base_directory / "custom_config.json"

# 默认配置的副本，用于恢复
_default_config = {
    # 基础配置
    'BACKUP_SERVER': '',
    'MAX_URLS_PER_TASK': 200,
    'MAX_CHUNK_SIZE': 6000,
    'VIEWPORT_WIDTH': 1366,
    'VIEWPORT_HEIGHT': 768,
    'MaxSessionPermit': 6,
    'EXCLUDE_EXTERNAL_LINKS': True,
    'ALL_PLATFORMS': ["web", "rss"],
    'MC_PLATFORMS': ["ks", "wb", "bili", "dy", "xhs", "zhihu"],
    'NEED_LOGIN_DOMAINS': [],
    'FORBIDDEN_DOMAINS': [],
    # 调度起始时间（格式 HH:MM），后续时间段将以 +6 小时递进
    'TIME_SLOTS_START': '07:07',
    
    # Caching LifeTime Setting(in days)
    'WEB_ARTICLE_TTL': 15,
    'SocialMedia_TTL': 2,
    
    # Web 配置
    'CHUNK_TOKEN_THRESHOLD': 2**11,  # 2048 tokens
    'OVERLAP_RATE': 0.1,
    'WORD_TOKEN_RATE': 1.3,
    'MIN_WORD_THRESHOLD': 2,
    'IMAGE_DESCRIPTION_MIN_WORD_THRESHOLD': 5,
    'IMAGE_SCORE_THRESHOLD': 0.5,
    'IMPORTANT_ATTRS': ["src", "href", "alt", "title", "width", "height", "data-src"],
    'ONLY_TEXT_ELIGIBLE_TAGS': [
        "b", "i", "u", "span", "del", "ins", "sub", "sup", "strong", "em",
        "code", "kbd", "var", "s", "q", "abbr", "cite", "dfn", "time", "small", "mark"
    ],
    'SOCIAL_MEDIA_DOMAINS': [
        "facebook.com", "twitter.com", "x.com", "linkedin.com", "instagram.com",
        "pinterest.com", "tiktok.com", "snapchat.com", "reddit.com", "weibo.com",
        "m.weibo.cn", "m.weibo.com", "service.weibo.com", "zhihu.com",
        "zhuanlan.zhihu.com", "douyin.com", "bilibili.com", "xiaohongshu.com", "kuaishou.com"
    ],
    'MAX_METRICS_HISTORY': 1000,
    'URL_LOG_SHORTEN_LENGTH': 30,
    'SHOW_DEPRECATION_WARNINGS': True,
    'SCREENSHOT_HEIGHT_TRESHOLD': 10000,
    'PAGE_TIMEOUT': 60000,
    'DOWNLOAD_PAGE_TIMEOUT': 60000,
}

# 使用默认配置的副本来初始化config
config = _default_config.copy()


def _is_type_compatible(value: Any, expected_type: type) -> bool:
    """
    检查值的类型是否与期望类型兼容
    支持的类型包括：str, int, float, bool, list, dict
    注意：JSON 会将数字统一解析，int 和 float 需要特殊处理
    """
    if expected_type == str:
        return isinstance(value, str)
    elif expected_type == int:
        # JSON 中没有区分 int 和 float，但我们可以检查是否为整数
        return isinstance(value, int) or (isinstance(value, float) and value.is_integer())
    elif expected_type == float:
        return isinstance(value, (int, float))
    elif expected_type == bool:
        return isinstance(value, bool)
    elif expected_type == list:
        return isinstance(value, list)
    elif expected_type == dict:
        return isinstance(value, dict)
    else:
        return isinstance(value, expected_type)


def _validate_config_item(key: str, value: Any) -> bool:
    """
    校验单个配置项
    返回 True 表示通过校验，False 表示不符合要求
    """
    # 1. 检查 key 是否在 _default_config 中
    if key not in _default_config:
        wis_logger.warning(f"配置项 '{key}' 不在默认配置中，已跳过")
        return False
    
    # 2. 检查 value 的类型是否与 _default_config 中对应值的类型一致
    expected_value = _default_config[key]
    expected_type = type(expected_value)
    
    if not _is_type_compatible(value, expected_type):
        wis_logger.info(
            f"配置项 '{key}' 的值类型不匹配: 期望 {expected_type.__name__}, "
            f"实际 {type(value).__name__}, 已跳过"
        )
        return False
    
    return True


def load_runtime_overrides() -> None:
    """
    加载运行时配置覆盖，直接更新配置字典
    会校验 payload 中的每一项，只更新符合要求的配置项
    """
    
    if not custom_config_path.exists():
        return

    try:
        with open(custom_config_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        
        if not isinstance(payload, dict):
            wis_logger.warning(f"配置文件格式错误，期望字典类型，已跳过")
            return
        
        # 校验并过滤 payload
        valid_updates: Dict[str, Any] = {}
        skipped_count = 0
        
        for key, value in payload.items():
            if _validate_config_item(key, value):
                valid_updates[key] = value
            else:
                skipped_count += 1
        
        # 只更新通过校验的配置项
        if valid_updates:
            config.update(valid_updates)

    except Exception as e:
        wis_logger.warning(f"加载配置文件失败 {custom_config_path}: {e}, 使用默认配置")

load_runtime_overrides()
