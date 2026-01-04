import json
from typing import Any, Dict, List
from core.tools.general_utils import get_logger
from core.async_database import base_directory


logger = get_logger(base_directory, "wiseflow_backend")
custom_config_path = base_directory / "custom_config.json"

# 默认配置的副本，用于恢复
_default_config = {
    # 基础配置
    'BACKUP_SERVER': '',
    'MAX_URLS_PER_TASK': 200,
    'MAX_CHUNK_SIZE': 10000,
    'VIEWPORT_WIDTH': 1366,
    'VIEWPORT_HEIGHT': 768,
    'MaxSessionPermit': 6,
    'EXCLUDE_EXTERNAL_LINKS': True,
    'ALL_PLATFORMS': [],
    'MC_PLATFORMS': ["ks", "wb", "bili", "dy", "xhs", "zhihu"],
    'NEED_LOGIN_DOMAINS': [],
    'FORBIDDEN_DOMAINS': [],
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
    'DOWNLOAD_PAGE_TIMEOUT': 60000
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
        logger.warning(f"配置项 '{key}' 不在默认配置中，已跳过")
        return False
    
    # 2. 检查 value 的类型是否与 _default_config 中对应值的类型一致
    expected_value = _default_config[key]
    expected_type = type(expected_value)
    
    if not _is_type_compatible(value, expected_type):
        logger.info(
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
            logger.warning(f"配置文件格式错误，期望字典类型，已跳过")
            return
        
        # 校验并过滤 payload
        valid_updates: Dict[str, Any] = {}
        
        for key, value in payload.items():
            if _validate_config_item(key, value):
                valid_updates[key] = value
        
        # 只更新通过校验的配置项
        if valid_updates:
            config.update(valid_updates)
 
    except Exception as e:
        logger.warning(f"加载配置文件失败 {custom_config_path}: {e}, 使用默认配置")

def save_config(config_updates: dict) -> bool:
    """
    保存配置更新到自定义配置文件
    会校验 config_updates 中的每一项，只保存符合要求的配置项
    
    Args:
        config_updates: 要更新的配置字典
        
    Returns:
        bool: 操作是否成功
    """

    try:
        # 校验并过滤配置更新
        valid_updates: Dict[str, Any] = {}
        
        for key, value in config_updates.items():
            if _validate_config_item(key, value):
                valid_updates[key] = value
        
        if not valid_updates:
            logger.warning("没有有效的配置项可保存")
            return False
        
        # 读取现有配置（如果存在）
        existing_config = {}
        if custom_config_path.exists():
            try:
                with open(custom_config_path, "r", encoding="utf-8") as f:
                    existing_config = json.load(f)
            except Exception as e:
                logger.warning(f"读取现有配置失败，将创建新配置: {e}")
        
        # 合并新配置（只合并通过校验的配置项）
        existing_config.update(valid_updates)

        # 写入配置文件
        with open(custom_config_path, "w", encoding="utf-8") as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"更新配置已保存到: {custom_config_path}")
        return True
        
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        return False


def restore_default_config() -> bool:
    """
    恢复配置为默认值，并清除自定义配置文件
    
    Returns:
        bool: 操作是否成功
    """
    try:
        # 清除自定义配置文件
        if custom_config_path.exists():
            custom_config_path.unlink()
            logger.info(f"已删除自定义配置文件: {custom_config_path}")
        return True
        
    except Exception as e:
        logger.error(f"恢复默认配置失败: {e}")
        return False

load_runtime_overrides()
