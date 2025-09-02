# __init__.py
import warnings
from .async_configs import BrowserConfig, CrawlerRunConfig, GeolocationConfig
from .async_webcrawler import AsyncWebCrawler
from .extraction_strategy import (
    NoExtractionStrategy,
    ExtractionStrategy,
    LLMExtractionStrategy,
    JsonCssExtractionStrategy,
    JsonXPathExtractionStrategy,
    JsonLxmlExtractionStrategy,
    RegexExtractionStrategy
)
from .chunking_strategy import ChunkingStrategy, RegexChunking, IdentityChunking, MaxLengthChunking

from .basemodels import CrawlResult
from .markdown_generation_strategy import (
    DefaultMarkdownGenerator, 
    WeixinArticleMarkdownGenerator,
)

from .async_dispatcher import (
    MemoryAdaptiveDispatcher,
    SemaphoreDispatcher,
    RateLimiter,
    BaseDispatcher,
)

from .kuaishou import *
from .weibo import *
from .config import WEIBO_PLATFORM_NAME, KUAISHOU_PLATFORM_NAME, ALL_PLATFORMS
from .searchengines import search_with_engine

__all__ = [
    "AsyncWebCrawler",
    "GeolocationConfig",
    "CrawlResult",
    "BrowserConfig",
    "CrawlerRunConfig",
    "ExtractionStrategy",
    "NoExtractionStrategy",
    "LLMExtractionStrategy",
    "JsonCssExtractionStrategy",
    "JsonXPathExtractionStrategy",
    "JsonLxmlExtractionStrategy",
    "RegexExtractionStrategy",
    "ChunkingStrategy",
    "RegexChunking",
    "IdentityChunking",
    "MaxLengthChunking",
    "BaseDispatcher",
    "MemoryAdaptiveDispatcher",
    "SemaphoreDispatcher",
    "KuaiShouCrawler",
    "WeiboCrawler",
    "WeiboSearchType",
    "WEIBO_PLATFORM_NAME",
    "KUAISHOU_PLATFORM_NAME",
    "DefaultMarkdownGenerator",
    "WeixinArticleMarkdownGenerator",
    "search_with_engine",
    "ALL_PLATFORMS",
]

# Disable all Pydantic warnings
warnings.filterwarnings("ignore", module="pydantic")
# pydantic_warnings.filter_warnings()
