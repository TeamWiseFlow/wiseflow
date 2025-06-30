from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import os, sys
import regex as re
from wis.utils import params_to_remove, url_pattern
from loguru import logger
from wis.__version__ import __version__
from pydantic import BaseModel


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
    verbose = os.environ.get("VERBOSE", "").lower() in ["true", "1"]
    # level = 'DEBUG' if verbose else 'INFO'
    
    os.makedirs(logger_file_path, exist_ok=True)
    logger_file = os.path.join(logger_file_path, f"{logger_name}.log")
    
    # 如果该 logger 已经存在，先移除其所有处理器
    if logger_name in _logger_handlers:
        for handler_id in _logger_handlers[logger_name]:
            try:
                logger.remove(handler_id)
            except ValueError:
                pass  # 处理器可能已经被移除
    
    # 如果是第一次创建 logger，移除默认的控制台处理器
    if logger_name not in _logger_handlers:
        try:
            logger.remove(0)  # 移除默认控制台处理器
        except ValueError:
            pass  # 默认处理器可能已经被移除
    
    # 创建过滤器，只处理当前 logger_name 的消息
    logger_filter = lambda record: record.get("extra", {}).get("name") == logger_name
    # 添加文件处理器
    file_handler_id = logger.add(
        logger_file,
        level='INFO',
        backtrace=True,  # 始终启用，主要在异常时显示堆栈信息
        diagnose=verbose,
        rotation="12 MB",
        enqueue=True,  # 启用异步文件写入
        encoding="utf-8",
        filter=logger_filter
    )
    
    # 添加控制台处理器（使用默认彩色格式）
    console_handler_id = logger.add(
        sys.stderr,
        level='DEBUG',
        filter=logger_filter,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>"
    )
    
    # 记录处理器 ID（存储为列表）
    _logger_handlers[logger_name] = [file_handler_id, console_handler_id]

    if logger_name == 'wiseflow_info_scraper':
        print(f"\n{CYAN}{'#' * 50}{RESET}")
        print(f"{GREEN}Wiseflow Info Scraper {__version__}{RESET}")
        print(f"{YELLOW}Modified by bigbrother666sh based on:{RESET}")
        print(f"{BLUE}Crawl4ai 0.6.3 (https://github.com/unclecode/crawl4ai)")
        print(f"{BLUE}MediaCrawler (https://github.com/NanmiCoder/MediaCrawler)")
        print(f"{BLUE}with enhanced by NoDriver (https://github.com/ultrafunkamsterdam/nodriver)")
        print(f"{MAGENTA}2025-06-30{RESET}")
        print(f"{CYAN}{'#' * 50}{RESET}\n")
    
    # 返回绑定了名称的 logger 实例
    return logger.bind(name=logger_name)

class Recorder(BaseModel):
    # source status
    rss_source: int = 0
    web_source: int = 0
    mc_count: dict[str, int] = {}
    item_source: dict[str, int] = {}

    # to do list
    url_queue: set[str] = set()
    article_queue: list[str] = []

    # working status
    total_processed: int = 0
    crawl_failed: int = 0
    scrap_failed: int = 0
    successed: int = 0
    info_added: int = 0

    # general
    focus_id: str = ""
    max_urls_per_task: int = 0
    processed_urls: set[str] = set()

    def finished(self) -> bool:
        if not self.url_queue and not self.article_queue:
            return True
        if self.total_processed >= self.max_urls_per_task:
            return True
        return False
    
    def add_url(self, url: str | set[str], source: str):
        if isinstance(url, str):
            if url in self.processed_urls:
                return
            self.url_queue.add(url)
            if source not in self.item_source:
                self.item_source[source] = 0
            self.item_source[source] += 1
        elif isinstance(url, set):
            more_urls = url - self.processed_urls
            self.url_queue.update(more_urls)
            if source not in self.item_source:
                self.item_source[source] = 0
            self.item_source[source] += len(more_urls)

    def source_summary(self) -> str:
        from_str = f"From"
        if self.rss_source:
            from_str += f"\n- RSS: {self.rss_source}"
        if self.web_source:
            from_str += f"\n- Sites: {self.web_source}"
        if self.mc_count:
            for source, count in self.mc_count.items():
                from_str += f"\n- {source} : {count} Videos/Notes"
        
        url_str = f"Found Total: {len(self.url_queue) + len(self.article_queue)} items worth to explore (after existings filtered)"
        for source, count in self.item_source.items():
            url_str += f"\n- from {source} : {count}"
        
        self.processed_urls.update({article.url for article in self.article_queue})
        
        return "\n".join([f"=== Focus: {self.focus_id:.10}... Source Finding Summary ===", from_str, url_str])

    def scrap_summary(self) -> str:
        proce_status_str = f"=== Focus: {self.focus_id:.10}... Scraping Summary ===\nProcessed {self.total_processed} items till now"
        proce_status_str += f"\n- Crawl Failed: {self.crawl_failed}"
        proce_status_str += f"\n- Scrap Failed: {self.scrap_failed}"
        proce_status_str += f"\n- Successed: {self.successed}"
        proce_status_str += f"\n- Finally find valid infos: {self.info_added}"
        if self.article_queue:
            proce_status_str += f"\n\nWe Still have {len(self.article_queue)} more items to explore"
            if 'article' in self.item_source:
                proce_status_str += f" ({self.item_source['article']} new items added from articles since source finding)"
            left_url_count = self.max_urls_per_task - self.total_processed
            if left_url_count > 0:
                proce_status_str += f"\nHowever after {left_url_count} items be proccessed, we have to quit by config setting limit."
            else:
                proce_status_str += f"\nHowever we have to quit by config setting limit."
        return proce_status_str
    