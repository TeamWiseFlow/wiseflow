# __init__.py
import warnings

from .async_webcrawler import AsyncWebCrawler
from .async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from .content_scraping_strategy import (
    ContentScrapingStrategy,
    WebScrapingStrategy,
    LXMLWebScrapingStrategy,
)

from .markdown_generation_strategy import DefaultMarkdownGenerator
from .models import CrawlResult, MarkdownGenerationResult


__all__ = [
    "AsyncWebCrawler",
    "CrawlResult",
    "CacheMode",
    "ContentScrapingStrategy",
    "WebScrapingStrategy",
    "LXMLWebScrapingStrategy",
    "BrowserConfig",
    "CrawlerRunConfig",
    "DefaultMarkdownGenerator",
    "MarkdownGenerationResult",
]


# Disable all Pydantic warnings
warnings.filterwarnings("ignore", module="pydantic")
# pydantic_warnings.filter_warnings()
