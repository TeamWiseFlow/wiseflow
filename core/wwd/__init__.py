# __init__.py
import warnings

from .async_webcrawler import AsyncWebCrawler, CacheMode
from .async_configs import BrowserConfig, CrawlerRunConfig, ProxyConfig, GeolocationConfig

from .content_scraping_strategy import (
    ContentScrapingStrategy,
    WebScrapingStrategy,
    LXMLWebScrapingStrategy,
)
from .async_logger import (
    AsyncLoggerBase,
    AsyncLogger,
)
from .proxy_strategy import (
    ProxyRotationStrategy,
    RoundRobinProxyStrategy,
)
"""
from .extraction_strategy import (
    ExtractionStrategy,
    LLMExtractionStrategy,
    JsonCssExtractionStrategy,
    JsonXPathExtractionStrategy,
    JsonLxmlExtractionStrategy
)
from .chunking_strategy import ChunkingStrategy, RegexChunking
"""
from .markdown_generation_strategy import DefaultMarkdownGenerator

from .base.crawl4ai_models import CrawlResult, MarkdownGenerationResult, DisplayMode
from .components.crawler_monitor import CrawlerMonitor
from .async_dispatcher import (
    MemoryAdaptiveDispatcher,
    SemaphoreDispatcher,
    RateLimiter,
    BaseDispatcher,
)

from .hub import CrawlerHub


__all__ = [
    "AsyncLoggerBase",
    "AsyncLogger",
    "AsyncWebCrawler",
    "GeolocationConfig",
    "CrawlResult",
    "CrawlerHub",
    "CacheMode",
    "ContentScrapingStrategy",
    "WebScrapingStrategy",
    "LXMLWebScrapingStrategy",
    "BrowserConfig",
    "CrawlerRunConfig",
    "ExtractionStrategy",
    "LLMExtractionStrategy",
    "JsonCssExtractionStrategy",
    "JsonXPathExtractionStrategy",
    "JsonLxmlExtractionStrategy",
    "ChunkingStrategy",
    "RegexChunking",
    "DefaultMarkdownGenerator",
    "BaseDispatcher",
    "MemoryAdaptiveDispatcher",
    "SemaphoreDispatcher",
    "RateLimiter",
    "CrawlerMonitor",
    "DisplayMode",
    "MarkdownGenerationResult",
    "ProxyRotationStrategy",
    "RoundRobinProxyStrategy",
    "ProxyConfig"
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
