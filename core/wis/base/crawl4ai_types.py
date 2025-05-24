from typing import TYPE_CHECKING, Union

# Logger types
AsyncLoggerBase = Union['AsyncLoggerBaseType']
AsyncLogger = Union['AsyncLoggerType']

# Crawler core types
AsyncWebCrawler = Union['AsyncWebCrawlerType']
CacheMode = Union['CacheModeType']
CrawlResult = Union['CrawlResultType']
CrawlerHub = Union['CrawlerHubType']
BrowserProfiler = Union['BrowserProfilerType']

# Configuration types
BrowserConfig = Union['BrowserConfigType']
CrawlerRunConfig = Union['CrawlerRunConfigType']
HTTPCrawlerConfig = Union['HTTPCrawlerConfigType']
LLMConfig = Union['LLMConfigType']

# Content scraping types
ContentScrapingStrategy = Union['ContentScrapingStrategyType']
WebScrapingStrategy = Union['WebScrapingStrategyType']
LXMLWebScrapingStrategy = Union['LXMLWebScrapingStrategyType']

# Proxy types
ProxyRotationStrategy = Union['ProxyRotationStrategyType']
RoundRobinProxyStrategy = Union['RoundRobinProxyStrategyType']
"""
# Extraction types
ExtractionStrategy = Union['ExtractionStrategyType']
LLMExtractionStrategy = Union['LLMExtractionStrategyType']
JsonCssExtractionStrategy = Union['JsonCssExtractionStrategyType']
JsonXPathExtractionStrategy = Union['JsonXPathExtractionStrategyType']

# Chunking types
ChunkingStrategy = Union['ChunkingStrategyType']
RegexChunking = Union['RegexChunkingType']
"""
# Markdown generation types
DefaultMarkdownGenerator = Union['DefaultMarkdownGeneratorType']
MarkdownGenerationResult = Union['MarkdownGenerationResultType']

# Dispatcher types
BaseDispatcher = Union['BaseDispatcherType']
MemoryAdaptiveDispatcher = Union['MemoryAdaptiveDispatcherType']
SemaphoreDispatcher = Union['SemaphoreDispatcherType']
RateLimiter = Union['RateLimiterType']
CrawlerMonitor = Union['CrawlerMonitorType']
DisplayMode = Union['DisplayModeType']
RunManyReturn = Union['RunManyReturnType']

# Docker client
Crawl4aiDockerClient = Union['Crawl4aiDockerClientType']

# Only import types during type checking to avoid circular imports
if TYPE_CHECKING:
    # Logger imports
    from ..async_logger import (
        AsyncLoggerBase as AsyncLoggerBaseType,
        AsyncLogger as AsyncLoggerType,
    )
    
    # Crawler core imports
    from ..async_webcrawler import (
        AsyncWebCrawler as AsyncWebCrawlerType,
        CacheMode as CacheModeType,
    )
    from .crawl4ai_models import CrawlResult as CrawlResultType
    from ..hub import CrawlerHub as CrawlerHubType
    from ..browser_profiler import BrowserProfiler as BrowserProfilerType
    
    # Configuration imports
    from ..async_configs import (
        BrowserConfig as BrowserConfigType,
        CrawlerRunConfig as CrawlerRunConfigType,
    )
    
    # Content scraping imports
    from ..content_scraping_strategy import (
        ContentScrapingStrategy as ContentScrapingStrategyType,
        WebScrapingStrategy as WebScrapingStrategyType,
        LXMLWebScrapingStrategy as LXMLWebScrapingStrategyType,
    )
    
    # Proxy imports
    from ..proxy_strategy import (
        ProxyRotationStrategy as ProxyRotationStrategyType,
        RoundRobinProxyStrategy as RoundRobinProxyStrategyType,
    )
    
    # Extraction imports
    """
    from .extraction_strategy import (
        ExtractionStrategy as ExtractionStrategyType,
        LLMExtractionStrategy as LLMExtractionStrategyType,
        JsonCssExtractionStrategy as JsonCssExtractionStrategyType,
        JsonXPathExtractionStrategy as JsonXPathExtractionStrategyType,
    )

    # Chunking imports
    from .chunking_strategy import (
        ChunkingStrategy as ChunkingStrategyType,
        RegexChunking as RegexChunkingType,
    )
    """
    # Markdown generation imports
    from ..markdown_generation_strategy import (
        DefaultMarkdownGenerator as DefaultMarkdownGeneratorType,
    )
    from .crawl4ai_models import MarkdownGenerationResult as MarkdownGenerationResultType
    
    # Dispatcher imports
    from ..async_dispatcher import (
        BaseDispatcher as BaseDispatcherType,
        MemoryAdaptiveDispatcher as MemoryAdaptiveDispatcherType,
        SemaphoreDispatcher as SemaphoreDispatcherType,
        RateLimiter as RateLimiterType,
        CrawlerMonitor as CrawlerMonitorType,
        DisplayMode as DisplayModeType,
        RunManyReturn as RunManyReturnType,
    )
    
    # Docker client
    from ..docker_client import Crawl4aiDockerClient as Crawl4aiDockerClientType
"""
def create_llm_config(*args, **kwargs) -> 'LLMConfigType':
    from ..async_configs import LLMConfig
    return LLMConfig(*args, **kwargs)
"""
