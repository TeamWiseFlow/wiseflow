from urllib.parse import urlparse
import regex as re
from pydantic import BaseModel
from loguru import logger
import os, sys, atexit
from pathlib import Path
from datetime import datetime, timedelta


# 全局字典，用于跟踪已创建的 logger 处理器
_logger_handlers = {}
_atexit_registered = False

def _env_to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    v = value.strip().lower()
    return v in {"1", "true", "yes", "y", "on"}

def get_logger(logger_file_path: Path, logger_name: str):
    """
    创建一个配置好的 loguru 日志记录器，包含文件和控制台输出
    
    :param logger_name: 日志记录器名称
    :param logger_file_path: 日志文件存储路径
    :return: 配置好的 logger 实例
    """
    verbose = _env_to_bool(os.environ.get("WISEFLOW_VERBOSE", "False"), False)
    
    logger_file = logger_file_path / f"{logger_name}.log"
    
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

    # 运行环境检测与配置
    is_frozen = bool(getattr(sys, "frozen", False))
    is_child = os.environ.get("WISEFLOW_CHILD_PROCESS") == "1"
    # 动态决定文件写入是否使用 enqueue（可通过环境变量覆盖）
    env_enqueue = os.environ.get("WISEFLOW_LOG_ENQUEUE")
    effective_enqueue = _env_to_bool(env_enqueue, default=(not (is_frozen and is_child)))

    # 文件保留与压缩策略（可通过环境变量调整）
    # 默认保留 14 天，压缩 zip；设置为 0 或 "none" 可关闭
    try:
        retention_days = int(os.environ.get("WISEFLOW_LOG_RETENTION_DAYS", "14"))
    except ValueError:
        retention_days = 14
    retention_arg = (f"{retention_days} days" if retention_days > 0 else None)
    compression_env = os.environ.get("WISEFLOW_LOG_COMPRESSION", "zip").strip().lower()
    compression_arg = (None if compression_env in {"", "none", "false", "0"} else compression_env)
    # 添加文件处理器
    file_handler_id = logger.add(
        logger_file,
        level='INFO',
        backtrace=True,  # 异常时显示堆栈信息
        diagnose=verbose,
        rotation="12 MB",
        retention=retention_arg,
        compression=compression_arg,
        enqueue=effective_enqueue,
        encoding="utf-8",
        filter=logger_filter
    )
    
    # 添加控制台处理器（使用默认彩色格式）
    console_handler_id = logger.add(
        sys.stderr,
        level=('DEBUG' if verbose else 'INFO'),
        filter=logger_filter,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>",
        enqueue=False  # 控制台同步输出，获得即时反馈
    )
    
    # 记录处理器 ID（存储为列表）
    _logger_handlers[logger_name] = [file_handler_id, console_handler_id]

    # 进程退出时确保刷新日志
    global _atexit_registered
    if not _atexit_registered:
        try:
            atexit.register(shutdown_logger)
            _atexit_registered = True
        except Exception:
            pass

    # 返回绑定了名称的 logger 实例
    return logger.bind(name=logger_name)


def shutdown_logger(logger_name: str | None = None):
    """
    Remove configured handlers to flush and stop background logging threads.
    If logger_name is None, remove all known handlers.
    """
    try:
        if logger_name is None:
            names = list(_logger_handlers.keys())
        else:
            names = [logger_name] if logger_name in _logger_handlers else []

        for name in names:
            handler_ids = _logger_handlers.get(name, [])
            for hid in handler_ids:
                try:
                    logger.remove(hid)
                except Exception:
                    pass
            _logger_handlers.pop(name, None)
    except Exception:
        # best-effort shutdown
        pass


def isURL(string):
    if string.startswith("www."):
        string = f"https://{string}"
    result = urlparse(string)
    return result.scheme != '' and result.netloc != ''

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
        proce_status_str += f"\n- Extract Failed: {self.scrap_failed}"
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

def normalize_publish_date(publish_time: str) -> str:
    """
    将各种日期格式统一转换为 YYYY-MM-DD 格式
    
    支持的格式（按处理顺序，运算量小的先处理）：
    1. 空值或非字符串 - 返回空字符串''
    2. 今天/today - 返回今天日期
    3. 昨天/yesterday - 返回昨天日期
    4. 分钟前/小时前 - 返回今天日期
    5. MM-DD - 月日格式（补充当前年份）
    6. YYYY-MM-DD - 标准格式（验证后直接返回）
    7. X天前 - 相对时间格式（2天前、3天前等）
    8. 从字符串中提取日期格式：
       - YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD, YYYY\\MM\\DD
       - YYYYMMDD, YYYY年MM月DD日
    
    Args:
        publish_time: 输入的时间字符串
    
    Returns:
        统一的 YYYY-MM-DD 格式字符串，如果解析失败则返回空字符串''
    """
    
    # 1. 空值检查（最快）
    if not publish_time or not isinstance(publish_time, str):
        return ''
    
    publish_time = publish_time.strip()
    if not publish_time:
        return ''
    
    # 2. 字符串包含检查（不需要正则，运算量小）
    try:
        # 今天/today
        if '今天' in publish_time or 'today' in publish_time.lower():
            return datetime.now().strftime('%Y-%m-%d')
        
        # 昨天/yesterday
        if '昨天' in publish_time or 'yesterday' in publish_time.lower():
            return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 分钟前/小时前（当前日期）
        if "天" not in publish_time and ('分钟前' in publish_time or '小时前' in publish_time):
            return datetime.now().strftime('%Y-%m-%d')
        
        # 相对时间格式（X天前）- 需要正则提取数字
        if '天前' in publish_time:
            days_match = re.search(r'(\d+)天', publish_time)
            if days_match:
                days_ago = int(days_match.group(1))
                target_date = datetime.now() - timedelta(days=days_ago)
                return target_date.strftime('%Y-%m-%d')
        
        # 3. 简单正则匹配（MM-DD格式）
        if re.match(r'^\d{2}-\d{2}$', publish_time):
            current_year = datetime.now().year
            return f"{current_year}-{publish_time}"
        
        # 4. 标准格式检查（YYYY-MM-DD）
        if re.match(r'^\d{4}-\d{2}-\d{2}$', publish_time):
            try:
                # 验证日期是否有效
                datetime.strptime(publish_time, '%Y-%m-%d')
                return publish_time
            except ValueError:
                pass

        # 6. 从字符串中提取日期格式（运算量较大，放在最后）
        # 定义匹配不同日期格式的正则表达式
        # 注意：YYYY-MM-DD 格式已在第4步处理，这里不再重复
        if len(publish_time) >= 8:
            patterns = [
                (r'(\d{4})/(\d{2})/(\d{2})', '-'),  # YYYY/MM/DD
                (r'(\d{4})\.(\d{2})\.(\d{2})', '-'),  # YYYY.MM.DD
                (r'(\d{4})\\(\d{2})\\(\d{2})', '-'),  # YYYY\MM\DD
                (r'(\d{4})(\d{2})(\d{2})', '-'),  # YYYYMMDD
                (r'(\d{4})年(\d{2})月(\d{2})日', '-')  # YYYY年MM月DD日
            ]
            
            for pattern, separator in patterns:
                match = re.search(pattern, publish_time)
                if match:
                    groups = match.groups()
                    try:
                        # 验证日期是否有效
                        date_str = f"{groups[0]}-{groups[1]}-{groups[2]}"
                        datetime.strptime(date_str, '%Y-%m-%d')
                        return date_str
                    except ValueError:
                        continue
        
        return ''
        
    except Exception:
        # 如果解析过程中出现任何错误，返回空字符串
        return ''
