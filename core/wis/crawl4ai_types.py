from typing import TYPE_CHECKING, Union


# Crawler core types
AsyncWebCrawler = Union['AsyncWebCrawlerType']
CacheMode = Union['CacheModeType']
CrawlResult = Union['CrawlResultType']

# Configuration types
BrowserConfig = Union['BrowserConfigType']
CrawlerRunConfig = Union['CrawlerRunConfigType']

# Proxy types
ProxyRotationStrategy = Union['ProxyRotationStrategyType']
RoundRobinProxyStrategy = Union['RoundRobinProxyStrategyType']

# Extraction types
ExtractionStrategy = Union['ExtractionStrategyType']
LLMExtractionStrategy = Union['LLMExtractionStrategyType']
JsonCssExtractionStrategy = Union['JsonCssExtractionStrategyType']
JsonXPathExtractionStrategy = Union['JsonXPathExtractionStrategyType']

# Chunking types
ChunkingStrategy = Union['ChunkingStrategyType']
RegexChunking = Union['RegexChunkingType']
MaxLengthChunking = Union['MaxLengthChunkingType']

# Markdown generation types
DefaultMarkdownGenerator = Union['DefaultMarkdownGeneratorType']
WeiXinMarkdownGenerator = Union['WeiXinMarkdownGeneratorType']

# Dispatcher types
BaseDispatcher = Union['BaseDispatcherType']
MemoryAdaptiveDispatcher = Union['MemoryAdaptiveDispatcherType']
SemaphoreDispatcher = Union['SemaphoreDispatcherType']
RateLimiter = Union['RateLimiterType']
CrawlerMonitor = Union['CrawlerMonitorType']
DisplayMode = Union['DisplayModeType']
RunManyReturn = Union['RunManyReturnType']

# Only import types during type checking to avoid circular imports
if TYPE_CHECKING:
    
    # Crawler core imports
    from .async_webcrawler import (
        AsyncWebCrawler as AsyncWebCrawlerType,
        CacheMode as CacheModeType,
    )
    from .basemodels import CrawlResult as CrawlResultType

    # Configuration imports
    from .async_configs import (
        BrowserConfig as BrowserConfigType,
        CrawlerRunConfig as CrawlerRunConfigType,
    )
    
    # Proxy imports
    from .proxy_strategy import (
        ProxyRotationStrategy as ProxyRotationStrategyType,
        RoundRobinProxyStrategy as RoundRobinProxyStrategyType,
    )
    
    # Extraction imports
    from .extraction_strategy import (
        ExtractionStrategy as ExtractionStrategyType,
        LLMExtractionStrategy as LLMExtractionStrategyType,
        JsonCssExtractionStrategy as JsonCssExtractionStrategyType,
        JsonXPathExtractionStrategy as JsonXPathExtractionStrategyType,
        RegexExtractionStrategy as RegexExtractionStrategyType,
    )

    # Chunking imports
    from .chunking_strategy import (
        ChunkingStrategy as ChunkingStrategyType,
        RegexChunking as RegexChunkingType,
        MaxLengthChunking as MaxLengthChunkingType,
    )

    # Markdown generation imports
    from .markdown_generation_strategy import (
        DefaultMarkdownGenerator as DefaultMarkdownGeneratorType,
        WeiXinMarkdownGenerator as WeiXinMarkdownGeneratorType,
    )

    # Dispatcher imports
    from .async_dispatcher import (
        BaseDispatcher as BaseDispatcherType,
        MemoryAdaptiveDispatcher as MemoryAdaptiveDispatcherType,
        SemaphoreDispatcher as SemaphoreDispatcherType,
        RateLimiter as RateLimiterType,
        CrawlerMonitor as CrawlerMonitorType,
        DisplayMode as DisplayModeType,
        RunManyReturn as RunManyReturnType,
    )
    