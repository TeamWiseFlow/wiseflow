import os
import time
from typing import Optional, List
import asyncio

from .utils import configure_windows_event_loop
configure_windows_event_loop()

# from contextlib import nullcontext, asynccontextmanager
from contextlib import asynccontextmanager
from .basemodels import (
    CrawlResult,
    DispatchResult,
    CrawlResultContainer,
    RunManyReturn
)
from async_logger import wis_logger, base_directory
from .async_crawler_strategy import (
    AsyncCrawlerStrategy,
    AsyncPlaywrightCrawlerStrategy,
    AsyncCrawlResponse,
)
from .async_configs import BrowserConfig, CrawlerRunConfig, ProxyConfig
from .async_dispatcher import BaseDispatcher, MemoryAdaptiveDispatcher, RateLimiter
from .utils import (
    sanitize_input_encode,
    RobotsParser,
    get_base_domain,
    preprocess_html_for_schema,
    get_content_of_website,
    extract_metadata,
    extract_metadata_using_lxml,
    common_file_exts,
)
from tools.general_utils import isURL


# for 99% of the cases, you don't need to change these configs
DEFAULT_BROWSER_CONFIG = BrowserConfig(
    viewport_width=1920,
    viewport_height=1080,
    user_agent_mode="random",
    light_mode=True
)

class AsyncWebCrawler:
    def __init__(
        self,
        config: BrowserConfig = DEFAULT_BROWSER_CONFIG,
        crawler_strategy: AsyncCrawlerStrategy = None,
        thread_safe: bool = False,
        crawler_config_map: dict = {},
        db_manager = None
    ):
        """
        Initialize the AsyncWebCrawler.

        Args:
            crawler_strategy: Strategy for crawling web pages. Default AsyncPlaywrightCrawlerStrategy
            config: Configuration object for browser settings. Default BrowserConfig()
            base_directory: Base directory for storing cache
            thread_safe: Whether to use thread-safe operations
            **kwargs: Additional arguments for backwards compatibility
        """
        # Handle browser configuration
        self.browser_config = config

        # Initialize crawler strategy
        self.crawler_strategy = crawler_strategy or AsyncPlaywrightCrawlerStrategy(
            browser_config=self.browser_config,
            logger=wis_logger,
        )

        # Thread safety setup
        self._lock = asyncio.Lock() if thread_safe else None

        # Initialize directories
        self.crawl4ai_folder = os.path.join(base_directory, ".crawl4ai")
        # os.makedirs(self.crawl4ai_folder, exist_ok=True)
        os.makedirs(os.path.join(self.crawl4ai_folder, "cache"), exist_ok=True)

        # Initialize robots parser
        self.robots_parser = RobotsParser(cache_dir=self.crawl4ai_folder)
        self.db_manager = db_manager
        self.crawler_config_map = crawler_config_map
        self.ready = False

    async def start(self):
        """
        Start the crawler explicitly without using context manager.
        This is equivalent to using 'async with' but gives more control over the lifecycle.
        Returns:
            AsyncWebCrawler: The initialized crawler instance
        """
        await self.crawler_strategy.__aenter__()
        self.ready = True
        return self

    async def close(self):
        """
        Close the crawler explicitly without using context manager.
        This should be called when you're done with the crawler if you used start().

        This method will:
        1. Clean up browser resources
        2. Close any open pages and contexts
        """
        await self.crawler_strategy.__aexit__(None, None, None)

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @asynccontextmanager
    async def nullcontext(self):
        """异步空上下文管理器"""
        yield

    async def arun(self, url: str, config: CrawlerRunConfig = None, session_id: str = None) -> Optional[RunManyReturn]:
        if self.db_manager:
            cached_result = await self.db_manager.get_cached_url(url, days_threshold=30)
            if cached_result and cached_result.html:
                wis_logger.debug(f"Get {url} from db cache")
                cached_result.session_id = session_id
                return CrawlResultContainer(cached_result)
            
        # Auto-start if not ready
        if not self.ready:
            await self.start()

        if not isinstance(url, str) or not url:
            wis_logger.info(f"Invalid URL, make sure the URL is a non-empty string")
            return None
        if not isURL(url):
            wis_logger.info(f"Invalid URL formate {url}")
            return None
        has_common_ext = any(url.lower().endswith(ext) for ext in common_file_exts)
        if has_common_ext:
            wis_logger.debug(f'{url} is a common file, skip')
            return None

        async with self._lock or self.nullcontext():
            try:
                # Initialize processing variables
                async_response: AsyncCrawlResponse = None
                screenshot_data = None
                pdf_data = None
                config = config or self.crawler_config_map.get(get_base_domain(url), self.crawler_config_map['default'])

                # Update proxy configuration from rotation strategy if available
                if config and config.proxy_rotation_strategy:
                    next_proxy: ProxyConfig = await config.proxy_rotation_strategy.get_next_proxy()
                    if next_proxy:
                        wis_logger.info(f"[PROXY] Switching to {next_proxy.server}")
                        config.proxy_config = next_proxy
                        # config = config.clone(proxy_config=next_proxy)

                t1 = time.perf_counter()
                # Check robots.txt if enabled
                if config and config.check_robots_txt:
                    if not await self.robots_parser.can_fetch(
                        url, self.browser_config.user_agent
                    ):
                        wis_logger.info(f"Access denied by robots.txt")
                        return None

                ##############################
                # Call CrawlerStrategy.crawl #
                ##############################
                async_response = await self.crawler_strategy.crawl(
                    url,
                    config=config,  # Pass the entire config object
                )

                html = "" if async_response.status_code in [403, 404, 429] else sanitize_input_encode(async_response.html)
                last_modified = async_response.response_headers.get("last-modified", "")
                screenshot_data = async_response.screenshot
                pdf_data = async_response.pdf_data
                js_execution_result = async_response.js_execution_result
                success = bool(html)
                t2 = time.perf_counter()
                if success:
                    wis_logger.debug(f"[FETCH] ✓ {url:.30}... | ⏱: {t2 - t1:.2f}s")
                else:
                    wis_logger.info(f"[FETCH] ✗ {url} | ⏱: {t2 - t1:.2f}s")
            except Exception as e:
                error_message = f"[Crawl Failed] {url}\n{str(e)}"
                wis_logger.warning(error_message)
                return CrawlResultContainer(
                    CrawlResult(
                        url=url, html="", success=False, error_message=error_message
                    )
                )
            if success:
                try:
                    metadata = extract_metadata_using_lxml(html)  # Using same function as BeautifulSoup version
                except Exception as e:
                    wis_logger.warning(f"when extracting metadata, error: {str(e)}\ntry to use beatifulsoup method")
                    try:
                        metadata = extract_metadata(html)
                    except Exception as e:
                        wis_logger.error(
                            f"when extracting metadata by beatifulsoup, error: {str(e)}\nfallback to empty metadata")
                        metadata = {}
            
                cleaned_html = preprocess_html_for_schema(html_content=html, tags_to_remove=config.excluded_tags)
                if not cleaned_html:
                    wis_logger.warning(f"Failed to clean html by fit html method, try to use beatifulsoup method")
                    cleaned_html = get_content_of_website(html, tags_to_remove=config.excluded_tags)
                if not cleaned_html:
                    wis_logger.error(f"Failed to clean html, fallback to raw html")
                    cleaned_html = ''
            else:
                cleaned_html = ''
                metadata = {}

            crawl_result = CrawlResult(
                url=url,
                html=html,
                cleaned_html=cleaned_html,
                screenshot=screenshot_data,
                pdf=pdf_data,
                publish_date=metadata.get("publish_date") or last_modified,
                title=metadata.get("title") or "",
                author=metadata.get("author") or "",
                success=success,
                error_message="",
                redirected_url=async_response.redirected_url,
                response_headers=async_response.response_headers,
                downloaded_files=async_response.downloaded_files,
                js_execution_result=js_execution_result,
                mhtml=async_response.mhtml_data,
                ssl_certificate=async_response.ssl_certificate,
                network_requests=async_response.network_requests,
                console_messages=async_response.console_messages,
                session_id=session_id,
            )
            if self.db_manager and success:
                await self.db_manager.cache_url(crawl_result)
            return CrawlResultContainer(crawl_result)

    async def arun_many(
        self,
        urls: List[str],
        dispatcher: Optional[BaseDispatcher] = None,
        stream: bool = True,
    ) -> RunManyReturn:
        """
        Runs the crawler for multiple URLs concurrently using a configurable dispatcher strategy.

        Args:
        urls: List of URLs to crawl
        config: Configuration object controlling crawl behavior for all URLs
        dispatcher: The dispatcher strategy instance to use. Defaults to MemoryAdaptiveDispatcher
        [other parameters maintained for backwards compatibility]

        Returns:
        Union[List[CrawlResult], AsyncGenerator[CrawlResult, None]]:
            Either a list of all results or an async generator yielding results

        Examples:

        # Batch processing (default)
        results = await crawler.arun_many(
            urls=["https://example1.com", "https://example2.com"],
            config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        )
        for result in results:
            print(f"Processed {result.url}: {len(result.markdown)} chars")

        # Streaming results
        async for result in await crawler.arun_many(
            urls=["https://example1.com", "https://example2.com"],
            config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=True),
        ):
            print(f"Processed {result.url}: {len(result.markdown)} chars")
        """

        if dispatcher is None:
            dispatcher = MemoryAdaptiveDispatcher(
                rate_limiter=RateLimiter(
                    base_delay=(1.0, 3.0), max_delay=60.0, max_retries=3
                ),
            )

        def transform_result(task_result):
            wis_logger.debug(
                f"[SYS STATUS] memory_usage: {task_result.memory_usage}MB, peak_memory: {task_result.peak_memory}MB, retry_count: {task_result.retry_count}")
            return (
                setattr(
                    task_result.result,
                    "dispatch_result",
                    DispatchResult(
                        task_id=task_result.task_id,
                        memory_usage=task_result.memory_usage,
                        peak_memory=task_result.peak_memory,
                        start_time=task_result.start_time,
                        end_time=task_result.end_time,
                        error_message=task_result.error_message,
                    ),
                )
                or task_result.result
            )

        # stream = config.stream
        if stream:
            async def result_transformer():
                async for task_result in dispatcher.run_urls_stream(
                    crawler=self, urls=urls
                ):
                    yield transform_result(task_result)

            return result_transformer()
        else:
            _results = await dispatcher.run_urls(crawler=self, urls=urls)
            return [transform_result(res) for res in _results]
