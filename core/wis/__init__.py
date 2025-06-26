# __init__.py
import warnings

from .async_webcrawler import AsyncWebCrawler
from .async_configs import BrowserConfig, CrawlerRunConfig, ProxyConfig, GeolocationConfig

from .proxy_strategy import (
    ProxyRotationStrategy,
    RoundRobinProxyStrategy,
)

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
    markdown_generation_hub
)

from .async_dispatcher import (
    MemoryAdaptiveDispatcher,
    SemaphoreDispatcher,
    RateLimiter,
    BaseDispatcher,
)

from .kuaishou import *
from .weibo import *
from .config.mc_config import WEIBO_PLATFORM_NAME, KUAISHOU_PLATFORM_NAME
from .searchengines import search_with_engine

__all__ = [
    "AsyncWebCrawler",
    "GeolocationConfig",
    "CrawlResult",
    "CacheMode",
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
    "RateLimiter",
    "ProxyRotationStrategy",
    "RoundRobinProxyStrategy",
    "ProxyConfig",
    "KuaiShouCrawler",
    "WeiboCrawler",
    "WeiboSearchType",
    "WEIBO_PLATFORM_NAME",
    "KUAISHOU_PLATFORM_NAME",
    "markdown_generation_hub",
    "DefaultMarkdownGenerator",
    "WeixinArticleMarkdownGenerator",
    "search_with_engine",
]

# Disable all Pydantic warnings
warnings.filterwarnings("ignore", module="pydantic")
# pydantic_warnings.filter_warnings()
