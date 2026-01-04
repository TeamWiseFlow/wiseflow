import warnings
import importlib
from typing import Any, Dict, Tuple

#
# Lazy exports to reduce import-time overhead and avoid side effects under spawn.
# Accessing attributes will import the corresponding submodules on demand and cache them.
#

CRAWLER_MAP = {}

__all__ = [
    # Core runtime
    "AsyncWebCrawler",
    "BrowserConfig",
    "CrawlerRunConfig",
    "GeolocationConfig",
    "CrawlResult",
    # Extraction and chunking
    "ExtractionStrategy",
    "NoExtractionStrategy",
    "JsonCssExtractionStrategy",
    "JsonXPathExtractionStrategy",
    "JsonLxmlExtractionStrategy",
    "RegexExtractionStrategy",
    "ChunkingStrategy",
    "RegexChunking",
    "IdentityChunking",
    "MaxLengthChunking",
    # Dispatchers
    "BaseDispatcher",
    "MemoryAdaptiveDispatcher",
    "SemaphoreDispatcher",
    "RateLimiter",
    # Other utilities
    "DefaultMarkdownGenerator",
    "WeixinArticleMarkdownGenerator",
    "search_with_engine",
    "ExtractManager",
    "SqliteCache",
    "MAIN_CACHE_FILE",
    # Dynamic mapping
    "CRAWLER_MAP",
]

_LAZY_ATTRS: Dict[str, Tuple[str, str]] = {
    # Core runtime
    "AsyncWebCrawler": ("core.wis.async_webcrawler", "AsyncWebCrawler"),
    "BrowserConfig": ("core.wis.async_configs", "BrowserConfig"),
    "CrawlerRunConfig": ("core.wis.async_configs", "CrawlerRunConfig"),
    "GeolocationConfig": ("core.wis.async_configs", "GeolocationConfig"),
    "CrawlResult": ("core.wis.basemodels", "CrawlResult"),
    # Extraction and chunking
    "ExtractionStrategy": ("core.wis.extraction_strategy", "ExtractionStrategy"),
    "NoExtractionStrategy": ("core.wis.extraction_strategy", "NoExtractionStrategy"),
    "JsonCssExtractionStrategy": ("core.wis.extraction_strategy", "JsonCssExtractionStrategy"),
    "JsonXPathExtractionStrategy": ("core.wis.extraction_strategy", "JsonXPathExtractionStrategy"),
    "JsonLxmlExtractionStrategy": ("core.wis.extraction_strategy", "JsonLxmlExtractionStrategy"),
    "RegexExtractionStrategy": ("core.wis.extraction_strategy", "RegexExtractionStrategy"),
    "ChunkingStrategy": ("core.wis.chunking_strategy", "ChunkingStrategy"),
    "RegexChunking": ("core.wis.chunking_strategy", "RegexChunking"),
    "IdentityChunking": ("core.wis.chunking_strategy", "IdentityChunking"),
    "MaxLengthChunking": ("core.wis.chunking_strategy", "MaxLengthChunking"),
    # Dispatchers
    "BaseDispatcher": ("core.wis.async_dispatcher", "BaseDispatcher"),
    "MemoryAdaptiveDispatcher": ("core.wis.async_dispatcher", "MemoryAdaptiveDispatcher"),
    "SemaphoreDispatcher": ("core.wis.async_dispatcher", "SemaphoreDispatcher"),
    "RateLimiter": ("core.wis.async_dispatcher", "RateLimiter"),
    # Other utilities
    "DefaultMarkdownGenerator": ("core.wis.markdown_generation_strategy", "DefaultMarkdownGenerator"),
    "WeixinArticleMarkdownGenerator": ("core.wis.markdown_generation_strategy", "WeixinArticleMarkdownGenerator"),
    "search_with_engine": ("core.wis.searchengines", "search_with_engine"),
    "ExtractManager": ("core.wis.extractor", "ExtractManager"),
    "SqliteCache": ("core.wis.async_cache", "SqliteCache"),
    "MAIN_CACHE_FILE": ("core.wis.async_cache", "MAIN_CACHE_FILE"),
}

def _resolve(name: str) -> Any:
    module_path, attr = _LAZY_ATTRS[name]
    mod = importlib.import_module(module_path)
    value = getattr(mod, attr)
    globals()[name] = value  # cache for future access
    return value

# Disable all Pydantic warnings
warnings.filterwarnings("ignore", module="pydantic")

def __getattr__(name: str) -> Any:
    if name in _LAZY_ATTRS:
        return _resolve(name)
    raise AttributeError(f"module {__name__} has no attribute {name}")

def __dir__() -> list[str]:
    return sorted(__all__)
