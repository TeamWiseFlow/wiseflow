from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional, Callable, Awaitable, Union, Any
from typing import AsyncGenerator
from typing import Generic, TypeVar
from enum import Enum
from dataclasses import dataclass
from .ssl_certificate import SSLCertificate
from datetime import datetime
from datetime import timedelta


###############################
# Dispatcher Models
###############################
@dataclass
class DomainState:
    last_request_time: float = 0
    current_delay: float = 0
    fail_count: int = 0


@dataclass
class CrawlerTaskResult:
    task_id: str
    url: str
    result: "CrawlResult"
    memory_usage: float
    peak_memory: float
    start_time: Union[datetime, float]
    end_time: Union[datetime, float]
    error_message: str = ""
    retry_count: int = 0
    wait_time: float = 0.0
    
    @property
    def success(self) -> bool:
        return self.result.success

class CrawlStatus(Enum):
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class CrawlStats:
    task_id: str
    url: str
    status: CrawlStatus
    start_time: Optional[Union[datetime, float]] = None
    end_time: Optional[Union[datetime, float]] = None
    memory_usage: float = 0.0
    peak_memory: float = 0.0
    error_message: str = ""
    wait_time: float = 0.0
    retry_count: int = 0
    counted_requeue: bool = False

    @property
    def duration(self) -> str:
        if not self.start_time:
            return "0:00"
            
        # Convert start_time to datetime if it's a float
        start = self.start_time
        if isinstance(start, float):
            start = datetime.fromtimestamp(start)
            
        # Get end time or use current time
        end = self.end_time or datetime.now()
        # Convert end_time to datetime if it's a float
        if isinstance(end, float):
            end = datetime.fromtimestamp(end)
            
        duration = end - start
        return str(timedelta(seconds=int(duration.total_seconds())))


###############################
# Crawler Models
###############################
@dataclass
class TokenUsage:
    completion_tokens: int = 0
    prompt_tokens: int = 0
    total_tokens: int = 0
    completion_tokens_details: Optional[dict] = None
    prompt_tokens_details: Optional[dict] = None

class UrlModel(BaseModel):
    url: HttpUrl
    forced: bool = False

@dataclass
class TraversalStats:
    """Statistics for the traversal process"""

    start_time: datetime = datetime.now()
    urls_processed: int = 0
    urls_failed: int = 0
    urls_skipped: int = 0
    total_depth_reached: int = 0
    current_depth: int = 0


class DispatchResult(BaseModel):
    task_id: str
    memory_usage: float
    peak_memory: float
    start_time: Union[datetime, float]
    end_time: Union[datetime, float]
    error_message: str = ""

   
class CrawlResult(BaseModel):
    url: str
    html: str
    success: Optional[bool] = True
    cleaned_html: Optional[str] = None
    downloaded_files: Optional[List[str]] = None
    js_execution_result: Optional[Dict[str, Any]] = None
    screenshot: Optional[str] = None
    pdf: Optional[bytes] = None
    mhtml: Optional[str] = None
    markdown: Optional[str] = ''
    link_dict: Optional[dict] = {}
    title: Optional[str] = ''
    author: Optional[str] = ''
    publish_date: Optional[str] = ''
    # extracted_content: Optional[List[Dict[str, Any]]] = None
    # metadata: Optional[dict] = None
    error_message: Optional[str] = ''
    session_id: Optional[str] = None
    response_headers: Optional[dict] = None
    status_code: Optional[int] = None
    ssl_certificate: Optional[SSLCertificate] = None
    dispatch_result: Optional[DispatchResult] = None
    redirected_url: Optional[str] = None
    network_requests: Optional[List[Dict[str, Any]]] = None
    console_messages: Optional[List[Dict[str, Any]]] = None

    class Config:
        arbitrary_types_allowed = True
    

class StringCompatibleMarkdown(str):
    """A string subclass that also provides access to MarkdownGenerationResult attributes"""
    def __new__(cls, markdown_result):
        return super().__new__(cls, markdown_result.raw_markdown)
    
    def __init__(self, markdown_result):
        self._markdown_result = markdown_result
    
    def __getattr__(self, name):
        return getattr(self._markdown_result, name)


CrawlResultT = TypeVar('CrawlResultT', bound=CrawlResult)


class CrawlResultContainer(Generic[CrawlResultT]):
    def __init__(self, results: Union[CrawlResultT, List[CrawlResultT]]):
        # Normalize to a list
        if isinstance(results, list):
            self._results = results
        else:
            self._results = [results]

    def __iter__(self):
        return iter(self._results)

    def __getitem__(self, index):
        return self._results[index]

    def __len__(self):
        return len(self._results)

    def __getattr__(self, attr):
        # Delegate attribute access to the first element.
        if self._results:
            return getattr(self._results[0], attr)
        raise AttributeError(f"{self.__class__.__name__} object has no attribute '{attr}'")

    def __repr__(self):
        return f"{self.__class__.__name__}({self._results!r})"

RunManyReturn = Union[
    CrawlResultContainer[CrawlResultT],
    AsyncGenerator[CrawlResultT, None]
]


# END of backward compatibility code for markdown/markdown_v2.
# When removing this code in the future, make sure to:
# 1. Replace the private attribute and property with a standard field
# 2. Update any serialization logic that might depend on the current behavior

class AsyncCrawlResponse(BaseModel):
    html: str
    response_headers: Dict[str, str]
    js_execution_result: Optional[Dict[str, Any]] = None
    status_code: int
    screenshot: Optional[str] = None
    pdf_data: Optional[bytes] = None
    mhtml_data: Optional[str] = None
    get_delayed_content: Optional[Callable[[Optional[float]], Awaitable[str]]] = None
    downloaded_files: Optional[List[str]] = None
    ssl_certificate: Optional[SSLCertificate] = None
    redirected_url: Optional[str] = None
    network_requests: Optional[List[Dict[str, Any]]] = None
    console_messages: Optional[List[Dict[str, Any]]] = None

    class Config:
        arbitrary_types_allowed = True

###############################
# Scraping Models
###############################
class MediaItem(BaseModel):
    src: Optional[str] = ""
    data: Optional[str] = ""
    alt: Optional[str] = ""
    desc: Optional[str] = ""
    score: Optional[int] = 0
    type: str = "image"
    group_id: Optional[int] = 0
    format: Optional[str] = None
    width: Optional[int] = None


class Link(BaseModel):
    href: Optional[str] = ""
    text: Optional[str] = ""
    title: Optional[str] = ""
    base_domain: Optional[str] = ""


class Media(BaseModel):
    images: List[MediaItem] = []
    videos: List[
        MediaItem
    ] = []  # Using MediaItem model for now, can be extended with Video model if needed
    audios: List[
        MediaItem
    ] = []  # Using MediaItem model for now, can be extended with Audio model if needed
    tables: List[Dict] = []  # Table data extracted from HTML tables


class Links(BaseModel):
    internal: List[Link] = []
    external: List[Link] = []
