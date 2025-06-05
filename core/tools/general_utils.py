from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import os
import regex as re
from wis.utils import params_to_remove, url_pattern
from loguru import logger
from wis.__version__ import __version__


# ANSI color codes
CYAN = '\033[36m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
RESET = '\033[0m'

def isURL(string):
    if string.startswith("www."):
        string = f"https://{string}"
    result = urlparse(string)
    return result.scheme != '' and result.netloc != ''

def extract_urls(text):
    # Regular expression to match http, https, and www URLs
    urls = re.findall(url_pattern, text)
    # urls = {quote(url.rstrip('/'), safe='/:?=&') for url in urls}
    cleaned_urls = set()
    for url in urls:
        if url.startswith("www."):
            url = f"https://{url}"

        try:
            parsed = urlparse(url)
            if not parsed.netloc or not parsed.scheme:
                continue

            query_params = parse_qs(parsed.query)
    
            for param in params_to_remove:
                query_params.pop(param, None)
        
            new_query = urlencode(query_params, doseq=True)
    
            cleaned_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
            cleaned_urls.add(cleaned_url)
        except Exception:
            continue

    return cleaned_urls


def isChinesePunctuation(char):
    # Define the Unicode encoding range for Chinese punctuation marks
    chinese_punctuations = set(range(0x3000, 0x303F)) | set(range(0xFF00, 0xFFEF))
    # Check if the character is within the above range
    return ord(char) in chinese_punctuations


def is_chinese(string):
    """
    :param string: {str} The string to be detected
    :return: {bool} Returns True if most are Chinese, False otherwise
    """
    pattern = re.compile(r'[^\u4e00-\u9fa5]')
    non_chinese_count = len(pattern.findall(string))
    # It is easy to misjudge strictly according to the number of bytes less than half.
    # English words account for a large number of bytes, and there are punctuation marks, etc
    return (non_chinese_count/len(string)) < 0.68


def extract_and_convert_dates(input_string):
    # 定义匹配不同日期格式的正则表达式
    if not isinstance(input_string, str) or len(input_string) < 8:
        return ''

    patterns = [
        r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        r'(\d{4})/(\d{2})/(\d{2})',  # YYYY/MM/DD
        r'(\d{4})\.(\d{2})\.(\d{2})',  # YYYY.MM.DD
        r'(\d{4})\\(\d{2})\\(\d{2})',  # YYYY\MM\DD
        r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
        r'(\d{4})年(\d{2})月(\d{2})日'  # YYYY年MM月DD日
    ]

    matches = []
    for pattern in patterns:
        matches = re.findall(pattern, input_string)
        if matches:
            break
    if matches:
        return '-'.join(matches[0])
    return ''


# 全局字典，用于跟踪已创建的 logger 处理器
_logger_handlers = {}

def get_logger(logger_file_path: str, logger_name: str):
    """
    创建一个配置好的 loguru 日志记录器，包含文件和控制台输出
    
    :param logger_name: 日志记录器名称
    :param logger_file_path: 日志文件存储路径
    :return: 配置好的 logger 实例
    """
    level = 'DEBUG' if os.environ.get("VERBOSE", "").lower() in ["true", "1"] else 'INFO'
    
    os.makedirs(logger_file_path, exist_ok=True)
    logger_file = os.path.join(logger_file_path, f"{logger_name}.log")
    
    # 如果该 logger 已经存在，先移除其所有处理器
    if logger_name in _logger_handlers:
        for handler_id in _logger_handlers[logger_name]:
            try:
                logger.remove(handler_id)
            except ValueError:
                pass  # 处理器可能已经被移除
    
    # 创建过滤器，只处理当前 logger_name 的消息
    logger_filter = lambda record: record.get("extra", {}).get("name") == logger_name
    
    # 添加文件处理器
    file_handler_id = logger.add(
        logger_file,
        level=level,
        backtrace=True,
        diagnose=True,
        rotation="12 MB",
        enqueue=True,  # 启用异步文件写入
        encoding="utf-8",
        filter=logger_filter,
        # format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[name]} | {function}:{line} | {message}\n{exception}"
    )
    
    # 添加控制台处理器
    """
    console_handler_id = logger.add(
        lambda msg: print(msg, end=""),  # 使用 lambda 避免重复输出
        level=level,
        backtrace=True,
        diagnose=True,
        filter=logger_filter,
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{extra[name]}</cyan> | <yellow>{function}:{line}</yellow> | {message}\n{exception}",
        colorize=True
    )
    """
    # 记录处理器 ID（存储为列表）
    _logger_handlers[logger_name] = file_handler_id

    if logger_name == 'wiseflow_info_scraper':
        print(f"\n{CYAN}{'#' * 50}{RESET}")
        print(f"{GREEN}Wiseflow Info Scraper {__version__}{RESET}")
        print(f"{YELLOW}Modified by bigbrother666sh based on:{RESET}")
        print(f"{BLUE}Crawl4ai 0.6.3 (https://github.com/unclecode/crawl4ai)")
        print(f"{BLUE}MediaCrawler (https://github.com/NanmiCoder/MediaCrawler)")
        print(f"{BLUE}with enhanced by NoDriver (https://github.com/ultrafunkamsterdam/nodriver)")
        print(f"{MAGENTA}2025-06-06{RESET}")
        print(f"{CYAN}{'#' * 50}{RESET}\n")
    
    # 返回绑定了名称的 logger 实例
    return logger.bind(name=logger_name)
