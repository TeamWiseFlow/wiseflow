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
    preprocess_html_for_schema,
    get_content_of_website,
    extract_metadata,
    get_base_domain,
)


class AsyncWebCrawler:
    """
    Asynchronous web crawler with flexible caching capabilities.

    There are two ways to use the crawler:

    1. Using context manager (recommended for simple cases):
        ```python
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url="https://example.com")
        ```

    2. Using explicit lifecycle management (recommended for long-running applications):
        ```python
        crawler = AsyncWebCrawler()
        await crawler.start()

        # Use the crawler multiple times
        result1 = await crawler.arun(url="https://example.com")
        result2 = await crawler.arun(url="https://another.com")

        await crawler.close()
        ```

    Attributes:
        browser_config (BrowserConfig): Configuration object for browser settings.
        crawler_strategy (AsyncCrawlerStrategy): Strategy for crawling web pages.
        logger (AsyncLogger): Logger instance for recording events and errors.
        crawl4ai_folder (str): Directory for storing cache.
        base_directory (str): Base directory for storing cache.
        ready (bool): Whether the crawler is ready for use.

    Methods:
        start(): Start the crawler explicitly without using context manager.
        close(): Close the crawler explicitly without using context manager.
        arun(): Run the crawler for a single source: URL (web, local file, or raw HTML).
        awarmup(): Perform warmup sequence.
        arun_many(): Run the crawler for multiple sources.
        aprocess_html(): Process HTML content.

    Typical Usage:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url="https://example.com")
            print(result.markdown)

        Using configuration:
        browser_config = BrowserConfig(browser_type="chromium", headless=True)
        async with AsyncWebCrawler(config=browser_config) as crawler:
            crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS
            )
            result = await crawler.arun(url="https://example.com", config=crawler_config)
            print(result.markdown)
    """


    def __init__(
        self,
        config: BrowserConfig = None,
        crawler_strategy: AsyncCrawlerStrategy = None,
        verbose: bool = False,
        thread_safe: bool = False,
        **kwargs,
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
        self.browser_config = config or BrowserConfig(verbose=verbose)

        # Initialize logger first since other components may need it
        self.logger = wis_logger

        # Initialize crawler strategy
        self.crawler_strategy = crawler_strategy or AsyncPlaywrightCrawlerStrategy(
            browser_config=self.browser_config,
            logger=self.logger,
        )

        # Thread safety setup
        self._lock = asyncio.Lock() if thread_safe else None

        # Initialize directories
        self.crawl4ai_folder = os.path.join(base_directory, ".crawl4ai")
        # os.makedirs(self.crawl4ai_folder, exist_ok=True)
        os.makedirs(os.path.join(self.crawl4ai_folder, "cache"), exist_ok=True)

        # Initialize robots parser
        self.robots_parser = RobotsParser()

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

    async def arun(
        self,
        url: str,
        config: CrawlerRunConfig = None,
        **kwargs,
    ) -> RunManyReturn:
        """
        Runs the crawler for a single source: URL (web, local file, or raw HTML).

        Migration Guide:
        Old way (deprecated):
            result = await crawler.arun(
                url="https://example.com",
                word_count_threshold=200,
                screenshot=True,
                ...
            )

        New way (recommended):
            config = CrawlerRunConfig(
                word_count_threshold=200,
                screenshot=True,
                ...
            )
            result = await crawler.arun(url="https://example.com", crawler_config=config)

        Args:
            url: The URL to crawl (http://, https://, file://, or raw:)
            crawler_config: Configuration object controlling crawl behavior
            [other parameters maintained for backwards compatibility]

        Returns:
            CrawlResult: The result of crawling and processing
        """
        # Auto-start if not ready
        if not self.ready:
            await self.start()

        config = config or CrawlerRunConfig()
        if not isinstance(url, str) or not url:
            raise ValueError(
                "Invalid URL, make sure the URL is a non-empty string")

        async with self._lock or self.nullcontext():
            try:
                # Initialize processing variables
                async_response: AsyncCrawlResponse = None
                cached_result: CrawlResult = None
                screenshot_data = None
                pdf_data = None
                start_time = time.perf_counter()

                # important: here the crawler cache do not contain the extracted_content,
                # extracted_content is related with the focus point, and stored in the infos table
                # here we only got the html, markdown, link_dict, metadata, updated_at
                # for the use case of same url and different focus point
                if cached_result:
                    html = sanitize_input_encode(cached_result.html)
                    markdown = cached_result.markdown or ""
                    link_dict = cached_result.link_dict or {}
                    metadata = cached_result.metadata or {}
                    publish_date = metadata.get("publish_date", "")
                    screenshot_data = cached_result.screenshot
                    pdf_data = cached_result.pdf
                    # if config.screenshot and not screenshot or config.pdf and not pdf:
                    if config.screenshot and not screenshot_data:
                        cached_result = None

                    if config.pdf and not pdf_data:
                        cached_result = None
                        
                if cached_result:  # 只有在缓存仍然有效时才记录
                    status_marker = "✓" if bool(html) else "✗"
                    self.logger.debug(f"[CACHE FETCH] {status_marker} {url} | ⏱: {time.perf_counter() - start_time:.2f}s")

                # Update proxy configuration from rotation strategy if available
                if config and config.proxy_rotation_strategy:
                    next_proxy: ProxyConfig = await config.proxy_rotation_strategy.get_next_proxy()
                    if next_proxy:
                        self.logger.info(f"[PROXY] Switching to {next_proxy.server}")
                        config.proxy_config = next_proxy
                        # config = config.clone(proxy_config=next_proxy)

                # Fetch fresh content if needed
                if not cached_result or not html:
                    t1 = time.perf_counter()

                    # Check robots.txt if enabled
                    if config and config.check_robots_txt:
                        if not await self.robots_parser.can_fetch(
                            url, self.browser_config.user_agent
                        ):
                            return CrawlResult(
                                url=url,
                                html="",
                                success=False,
                                status_code=403,
                                error_message="Access denied by robots.txt",
                                response_headers={
                                    "X-Robots-Status": "Blocked by robots.txt"
                                },
                            )

                    ##############################
                    # Call CrawlerStrategy.crawl #
                    ##############################
                    async_response = await self.crawler_strategy.crawl(
                        url,
                        config=config,  # Pass the entire config object
                    )

                    html = "" if async_response.status_code == 403 else sanitize_input_encode(async_response.html)
                    publish_date = async_response.response_headers.get("last-modified", "")
                    screenshot_data = async_response.screenshot
                    pdf_data = async_response.pdf_data
                    js_execution_result = async_response.js_execution_result

                    t2 = time.perf_counter()
                    status_marker = "✓" if bool(html) else "✗"
                    self.logger.debug(f"[FETCH] {status_marker} {url} | ⏱: {t2 - t1:.2f}s")
                    # 要把解析 metadate 过程放这里
                    crawl_result: CrawlResult = await self.aprocess_html(
                        url=url,
                        html=html,
                        config=config,  # Pass the config object instead of individual parameters
                        screenshot_data=screenshot_data,
                        pdf_data=pdf_data,
                        publish_date=publish_date,
                        verbose=config.verbose,
                        is_raw_html=True if url.startswith("raw:") else False,
                        redirected_url=async_response.redirected_url, 
                        **kwargs,
                    )

                    crawl_result.status_code = async_response.status_code
                    crawl_result.redirected_url = async_response.redirected_url or url
                    crawl_result.response_headers = async_response.response_headers
                    crawl_result.downloaded_files = async_response.downloaded_files
                    crawl_result.js_execution_result = js_execution_result
                    crawl_result.mhtml = async_response.mhtml_data
                    crawl_result.ssl_certificate = async_response.ssl_certificate
                    # Add captured network and console data if available
                    crawl_result.network_requests = async_response.network_requests
                    crawl_result.console_messages = async_response.console_messages
                    # crawl_result.success = bool(html)
                    crawl_result.session_id = getattr(
                        config, "session_id", None)

                    status_marker = "✓" if crawl_result.success else "✗"
                    self.logger.debug(
                        f"[COMPLETE] {status_marker} {url:.30}... | ⏱: {time.perf_counter() - start_time:.2f}s")
                    return CrawlResultContainer(crawl_result)
                else:
                    crawl_result: CrawlResult = await self.aprocess_html(
                        url=cached_result.url,
                        html=html,
                        markdown=markdown,
                        link_dict=link_dict,
                        config=config,  # Pass the config object instead of individual parameters
                        screenshot_data=screenshot_data,
                        metadata=metadata,
                        pdf_data=pdf_data,
                        publish_date=publish_date,
                        verbose=config.verbose,
                        **kwargs,
                    )
                    status_marker = "✓" if crawl_result.success else "✗"
                    self.logger.debug(
                        f"[COMPLETE] {status_marker} {url:.30}... | ⏱: {time.perf_counter() - start_time:.2f}s")
                    cached_result.session_id = getattr(
                        config, "session_id", None)
                    # cached_result.redirected_url = cached_result.redirected_url or url
                    return CrawlResultContainer(cached_result)

            except Exception as e:
                error_message = f"[Unexpected Error] {url}\n{str(e)}"
                self.logger.error(error_message)
                return CrawlResultContainer(
                    CrawlResult(
                        url=url, html="", success=False, error_message=error_message
                    )
                )

    async def aprocess_html(
        self,
        url: str,
        html: str,
        config: CrawlerRunConfig,
        markdown: str = "",
        link_dict: dict = {},
        screenshot_data: str = "",
        pdf_data: str = "",
        metadata: dict = {},
        publish_date: str = "",
        **kwargs,
    ) -> CrawlResult:
        """
        Process HTML content using the provided configuration.
        Returns:
            CrawlResult: Processed result containing extracted and formatted content
        """
        _url = url if not kwargs.get("is_raw_html", False) else "Raw HTML"

        if not html:
            # Return complete crawl result
            return CrawlResult(
                url=url,
                html=html,
                cleaned_html='',
                metadata=metadata,
                screenshot=screenshot_data,
                pdf=pdf_data,
                # extracted_content=[],
                success=False,
                error_message="null html, can do nothing",
            )
        
        if not metadata:
            try:
                metadata = extract_metadata_using_lxml(html)  # Using same function as BeautifulSoup version
            except Exception as e:
                self.logger.warning(f"when extracting metadata, error: {str(e)}\ntry to use beatifulsoup method")
                try:
                    metadata = extract_metadata(html)
                except Exception as e:
                    self.logger.error(
                        f"when extracting metadata by beatifulsoup, error: {str(e)}\nfallback to empty metadata")
                    metadata = {}
        
        t1 = time.perf_counter()
        cleaned_html = preprocess_html_for_schema(html_content=html, tags_to_remove=config.excluded_tags)
        if not cleaned_html:
            self.logger.warning(f"Failed to clean html by fit html method, try to use beatifulsoup method")
            cleaned_html = get_content_of_website(html, tags_to_remove=config.excluded_tags)
        if not cleaned_html:
            self.logger.error(f"Failed to clean html, fallback to raw html")
            cleaned_html = html

        # Log processing completion
        self.logger.debug(f"[PREPROCESS] {_url:.30}... | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")





        # post process for default extraction task --- sellection related links and infos

        # Return complete crawl result
        return CrawlResult(
            url=url,
            html=html,
            cleaned_html=cleaned_html,
            markdown=markdown,
            link_dict=link_dict,
            metadata=metadata,
            screenshot=screenshot_data,
            pdf=pdf_data,
            # extracted_content=extracted_content,
            success=True if not error_msg else False,
            error_message=error_msg,
        )

    async def arun_many(
        self,
        urls: List[str],
        config: Optional[CrawlerRunConfig] = None,
        dispatcher: Optional[BaseDispatcher] = None,
        stream: bool = True,
        **kwargs,
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
        config = config or CrawlerRunConfig()
        if dispatcher is None:
            dispatcher = MemoryAdaptiveDispatcher(
                rate_limiter=RateLimiter(
                    base_delay=(1.0, 3.0), max_delay=60.0, max_retries=3
                ),
            )

        def transform_result(task_result):
            self.logger.debug(
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
                    crawler=self, urls=urls, config=config
                ):
                    yield transform_result(task_result)

            return result_transformer()
        else:
            _results = await dispatcher.run_urls(crawler=self, urls=urls, config=config)
            return [transform_result(res) for res in _results]
