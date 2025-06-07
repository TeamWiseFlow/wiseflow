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
]


# def is_sync_version_installed():
#     try:
#         import selenium # noqa

#         return True
#     except ImportError:
#         return False


# if is_sync_version_installed():
#     try:
#         from .web_crawler import WebCrawler

#         __all__.append("WebCrawler")
#     except ImportError:
#         print(
#             "Warning: Failed to import WebCrawler even though selenium is installed. This might be due to other missing dependencies."
#         )
# else:
#     WebCrawler = None
#     # import warnings
#     # print("Warning: Synchronous WebCrawler is not available. Install crawl4ai[sync] for synchronous support. However, please note that the synchronous version will be deprecated soon.")

# Disable all Pydantic warnings
warnings.filterwarnings("ignore", module="pydantic")
# pydantic_warnings.filter_warnings()
