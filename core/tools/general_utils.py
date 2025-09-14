import os, sys
import regex
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from loguru import logger
from pydantic import BaseModel, Field
from wis.utils import params_to_remove, url_pattern
from wis.__version__ import __version__


# ANSI color codes
CYAN = '\033[36m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
RED = '\033[31m'
MAGENTA = '\033[35m'
RESET = '\033[0m'


def isURL(string: str) -> bool:
    if string.startswith("www."):
        string = f"https://{string}"
    result = urlparse(string)
    return bool(result.scheme and result.netloc)


def extract_urls(text: str) -> set[str]:
    urls = regex.findall(url_pattern, text)
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


def isChinesePunctuation(char: str) -> bool:
    chinese_punctuations = set(range(0x3000, 0x303F)) | set(range(0xFF00, 0xFFEF))
    return ord(char) in chinese_punctuations


def is_chinese(string: str) -> bool:
    if not string:
        return False
    pattern = regex.compile(r'[^\u4e00-\u9fa5]')
    non_chinese_count = len(pattern.findall(string))
    return (non_chinese_count / len(string)) < 0.68


def extract_and_convert_dates(input_string: str) -> str:
    if not isinstance(input_string, str) or len(input_string) < 8:
        return ''

    patterns = [
        r'(\d{4})-(\d{2})-(\d{2})',
        r'(\d{4})/(\d{2})/(\d{2})',
        r'(\d{4})\.(\d{2})\.(\d{2})',
        r'(\d{4})\\(\d{2})\\(\d{2})',
        r'(\d{4})(\d{2})(\d{2})',
        r'(\d{4})年(\d{2})月(\d{2})日'
    ]

    for pattern in patterns:
        matches = regex.findall(pattern, input_string)
        if matches:
            return '-'.join(matches[0])
    return ''


# Track created logger handlers
_logger_handlers = {}


def get_logger(logger_file_path: str, logger_name: str):
    verbose = os.environ.get("VERBOSE", "").lower() in ["true", "1"]

    os.makedirs(logger_file_path, exist_ok=True)
    logger_file = os.path.join(logger_file_path, f"{logger_name}.log")

    if logger_name in _logger_handlers:
        for handler_id in _logger_handlers[logger_name]:
            try:
                logger.remove(handler_id)
            except ValueError:
                pass
    else:
        try:
            logger.remove(0)
        except ValueError:
            pass

    logger_filter = lambda record: record.get("extra", {}).get("name") == logger_name

    file_handler_id = logger.add(
        logger_file,
        level='INFO',
        backtrace=True,
        diagnose=verbose,
        rotation="12 MB",
        enqueue=True,
        encoding="utf-8",
        filter=logger_filter
    )

    console_handler_id = logger.add(
        sys.stderr,
        level='DEBUG',
        filter=logger_filter,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>"
    )

    _logger_handlers[logger_name] = [file_handler_id, console_handler_id]

    if logger_name == 'wiseflow_info_scraper':
        print(f"\n{CYAN}{'#' * 50}{RESET}")
        print(f"{GREEN}Wiseflow Info Scraper {__version__}{RESET}")
        print(f"{YELLOW}⚠️  Important Notice: This tool is only for fetching publicly released, non-intellectual property content.{RESET}")
        print(f"{RED}Intended Use: For bulletin boards, notice boards, news releases, etc. of corporate portals, government agencies, industry associations, and similar organizations.{RESET}")
        print(f"{RED}Strictly Prohibited: Bulk content retrieval from media platforms or trading platforms is not allowed.{RESET}")
        print(f"{MAGENTA}Disclaimer: You are solely responsible for the results of using this tool. Please evaluate carefully before use.{RESET}")
        print(f"{CYAN}{'#' * 50}{RESET}\n")

    return logger.bind(name=logger_name)


class Recorder(BaseModel):
    rss_source: int = 0
    web_source: int = 0
    mc_count: dict[str, int] = Field(default_factory=dict)
    item_source: dict[str, int] = Field(default_factory=dict)

    url_queue: set[str] = Field(default_factory=set)
    article_queue: list[object] = Field(default_factory=list)  # CrawlerResult objects

    total_processed: int = 0
    crawl_failed: int = 0
    scrap_failed: int = 0
    successed: int = 0
    info_added: int = 0

    focus_id: str = ""
    max_urls_per_task: int = 0
    processed_urls: set[str] = Field(default_factory=set)

    def finished(self) -> bool:
        return (not self.url_queue and not self.article_queue) or (
            self.total_processed >= self.max_urls_per_task
        )

    def add_url(self, url: str | set[str], source: str):
        if isinstance(url, str):
            if url in self.processed_urls:
                return
            self.url_queue.add(url)
            self.item_source[source] = self.item_source.get(source, 0) + 1
        elif isinstance(url, set):
            more_urls = url - self.processed_urls
            self.url_queue.update(more_urls)
            self.item_source[source] = self.item_source.get(source, 0) + len(more_urls)

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

        #  Fixed: correctly update with generator expression
        self.processed_urls.update(article.url for article in self.article_queue)

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
