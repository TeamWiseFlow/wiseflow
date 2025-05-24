from .__version__ import __version__
import os
import time
from typing import Optional, List
import asyncio

from .utils import configure_windows_event_loop
configure_windows_event_loop()

# from contextlib import nullcontext, asynccontextmanager
from contextlib import asynccontextmanager
from .base.crawl4ai_models import (
    CrawlResult,
    DispatchResult,
    CrawlResultContainer,
    RunManyReturn
)
from ..async_database import async_db_manager
from .chunking_strategy import *  # noqa: F403
from .chunking_strategy import IdentityChunking, MaxLengthChunking
from .extraction_strategy import *  # noqa: F403
from .extraction_strategy import NoExtractionStrategy
from .async_crawler_strategy import (
    AsyncCrawlerStrategy,
    AsyncPlaywrightCrawlerStrategy,
    AsyncCrawlResponse,
)
from .cache_context import CacheMode, CacheContext
from .markdown_generation_strategy import *
markdown_generation_hub = {'mp.weixin.qq.com': WeixinArticleMarkdownGenerator}

from .async_configs import BrowserConfig, CrawlerRunConfig, ProxyConfig
from .async_dispatcher import *  # noqa: F403
from .async_dispatcher import BaseDispatcher, MemoryAdaptiveDispatcher, RateLimiter
from ..tools.general_utils import get_logger
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

    _domain_last_hit = {}

    def __init__(
        self,
        config: BrowserConfig = None,
        crawler_strategy: AsyncCrawlerStrategy = None,
        verbose: bool = False,
        base_directory: str = '.',
        thread_safe: bool = False,
        logger = None,
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
        self.logger = logger or get_logger("AsyncWebCrawler", os.path.join(base_directory, "WiseflowWebDriver.log"))

        # Initialize crawler strategy
        self.crawler_strategy = crawler_strategy or AsyncPlaywrightCrawlerStrategy(
            browser_config=self.browser_config,
            logger=self.logger,
        )

        # Thread safety setup
        self._lock = asyncio.Lock() if thread_safe else None

        # Initialize directories
        self.crawl4ai_folder = os.path.join(base_directory, ".crawl4ai")
        os.makedirs(self.crawl4ai_folder, exist_ok=True)
        os.makedirs(f"{self.crawl4ai_folder}/cache", exist_ok=True)

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
        self.logger.info(f"WiseflowInfoScraper {__version__}")
        self.logger.info("Modified by bigbrother666sh based on:") 
        self.logger.info("Crawl4ai 0.6.4 (https://github.com/unclecode/crawl4ai)")
        self.logger.info("MediaCrawler(https://github.com/NanmiCoder/MediaCrawler)")
        self.logger.info("with enhanced by NoDriver(https://github.com/ultrafunkamsterdam/nodriver)")
        self.logger.info("2025-05-23")
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
                # self.logger.verbose = config.verbose

                # Default to ENABLED if no cache mode specified
                if config.cache_mode is None:
                    config.cache_mode = CacheMode.ENABLED

                # Create cache context
                cache_context = CacheContext(url, config.cache_mode, False)

                # Initialize processing variables
                async_response: AsyncCrawlResponse = None
                cached_result: CrawlResult = None
                screenshot_data = None
                pdf_data = None
                extracted_content = None
                start_time = time.perf_counter()

                # Try to get cached result if appropriate
                if cache_context.should_read():
                    cached_result = await async_db_manager.aget_cached_url(url)

                if cached_result:
                    html = sanitize_input_encode(cached_result.html)
                    publish_date = cached_result.response_headers.get("last-modified", "")
                    extracted_content = sanitize_input_encode(
                        cached_result.extracted_content or ""
                    )
                    extracted_content = (
                        None
                        if not extracted_content or extracted_content == "[]"
                        else extracted_content
                    )
                    # If screenshot is requested but its not in cache, then set cache_result to None
                    screenshot_data = cached_result.screenshot
                    pdf_data = cached_result.pdf
                    # if config.screenshot and not screenshot or config.pdf and not pdf:
                    if config.screenshot and not screenshot_data:
                        cached_result = None

                    if config.pdf and not pdf_data:
                        cached_result = None
                    
                    status_marker = "✓" if bool(html) else "✗"
                    self.logger.debug(f"[CACHE FETCH] {status_marker} {cache_context.display_url} | ⏱: {time.perf_counter() - start_time:.2f}s")

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

                    html = sanitize_input_encode(async_response.html)
                    publish_date = async_response.response_headers.get("last-modified", "")
                    screenshot_data = async_response.screenshot
                    pdf_data = async_response.pdf_data
                    js_execution_result = async_response.js_execution_result

                    t2 = time.perf_counter()
                    status_marker = "✓" if bool(html) else "✗"
                    self.logger.debug(f"[FETCH] {status_marker} {cache_context.display_url} | ⏱: {t2 - t1:.2f}s")

                    ###############################################################
                    # Process the HTML content, Call CrawlerStrategy.process_html #
                    ###############################################################
                    crawl_result: CrawlResult = await self.aprocess_html(
                        url=url,
                        html=html,
                        extracted_content=extracted_content,
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

                    crawl_result.success = bool(html)
                    crawl_result.session_id = getattr(
                        config, "session_id", None)

                    status_marker = "✓" if crawl_result.success else "✗"
                    self.logger.debug(f"[COMPLETE] {status_marker} {cache_context.display_url} | ⏱: {time.perf_counter() - start_time:.2f}s")

                    # Update cache if appropriate
                    if cache_context.should_write() and not bool(cached_result):
                        await async_db_manager.acache_url(crawl_result)

                    return CrawlResultContainer(crawl_result)

                else:
                    self.logger.debug(f"[COMPLETE From Cache] {cache_context.display_url} | ⏱: {time.perf_counter() - start_time:.2f}s")
                    cached_result.success = True
                    cached_result.session_id = getattr(
                        config, "session_id", None)
                    cached_result.redirected_url = cached_result.redirected_url or url
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
        extracted_content: str,
        config: CrawlerRunConfig,
        screenshot_data: str,
        pdf_data: str,
        publish_date: str = "",
        **kwargs,
    ) -> CrawlResult:
        """
        Process HTML content using the provided configuration.

        Args:
            url: The URL being processed
            html: Raw HTML content
            extracted_content: Previously extracted content (if any)
            config: Configuration object controlling processing behavior
            screenshot_data: Screenshot data (if any)
            pdf_data: PDF data (if any)
            verbose: Whether to enable verbose logging
            **kwargs: Additional parameters for backwards compatibility

        Returns:
            CrawlResult: Processed result containing extracted and formatted content
        """
        _url = url if not kwargs.get("is_raw_html", False) else "Raw HTML"

        try:
            metadata = extract_metadata_using_lxml(html)  # Using same function as BeautifulSoup version
        except Exception as e:
            self.logger.warning(f"when extracting metadata, error: {str(e)}\ntry to use beatifulsoup method")
            try:
                metadata = extract_metadata(html)
            except Exception as e:
                self.logger.error(f"when extracting metadata by beatifulsoup, error: {str(e)}\nfallback to empty metadata")
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
        self.logger.debug(f"[PREPROCESS] {_url} | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")

        if (
            extracted_content 
            or not config.extraction_strategy 
            or isinstance(config.extraction_strategy, NoExtractionStrategy)
        ):
            # Return complete crawl result
            return CrawlResult(
                url=url,
                html=html,
                cleaned_html=cleaned_html,
                metadata=metadata,
                screenshot=screenshot_data,
                pdf=pdf_data,
                extracted_content=extracted_content,
                success=True,
                error_message="",
            )

        ################################
        # Structured Content Extraction#
        ################################
        t1 = time.perf_counter()
        if not isinstance(config.extraction_strategy, LLMExtractionStrategy):
            # Choose content based on input_format
            content_format = config.extraction_strategy.input_format
            if content_format in ["fit_html", "cleaned_html"]:
                content = cleaned_html
            else:
                content = html

            chunking = IdentityChunking()
            sections = chunking.chunk(content)
            extracted_content = config.extraction_strategy.run(url, sections)

            # Log extraction completion
            self.logger.debug(f"[EXTRACT] {_url} | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
            return CrawlResult(
                url=url,
                html=html,
                cleaned_html=cleaned_html,
                extracted_content=extracted_content,
                success=True,
                error_message="",
            )
        
        # if use LLMExtractionStrategy, then we need to generate markdown
        ################################
        # Generate Markdown            #
        ################################
        domain = get_base_domain(url)
        markdown_generator = markdown_generation_hub.get(domain, DefaultMarkdownGenerator)()
        error_msg, title, author, publish, markdown, link_dict = (
            await markdown_generator.generate_markdown(
                raw_html=html,
                cleaned_html=cleaned_html,
                base_url=kwargs.get("redirected_url", url),
                metadata=metadata,
                exclude_external_links=config.exclude_external_links,
            )
        )
        self.logger.debug(f"[HTML TO MARKDOWN] {_url} | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")

        t1 = time.perf_counter()
        if error_msg:
            self.logger.error(f"[HTML TO MARKDOWN] FAILED {_url}\n{error_msg}")
            extracted_content = ""
        else:
            content_date = publish or publish_date
            chunking = config.chunking_strategy or MaxLengthChunking()
            sections = chunking.chunk(markdown)
            extracted_content = config.extraction_strategy.run(url, sections, title, author, content_date)

        self.logger.debug(f"[EXTRACT] {_url} | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
        # post process for default extraction task --- sellection related links and infos
        if link_dict and not config.extraction_strategy.schema_mode:
            more_links = set()
            infos = []
            info_prefix = f'//{author} {content_date}//' if (author or content_date) else ''
            hallucination_times = 0
            total_parsed = 0
            for block in extracted_content:
                results = block.get("links", [])
                for result in results:
                    links = re.findall(r'\[\d+]', result)
                    total_parsed += len(links)
                    for link in links:
                        if link not in link_dict:
                            hallucination_times += 1
                            continue
                        more_links.add(link_dict[link])

                results = block.get("info", [])
                for res in results:
                    res = res.strip()
                    if len(res) < 3:
                        continue
                    url_tags = re.findall(r'\[\d+]', res)
                    refences = {}
                    for _tag in url_tags:
                        total_parsed += 1
                        if _tag in link_dict:
                            refences[_tag] = link_dict[_tag]
                        else:
                            if _tag not in markdown:
                                hallucination_times += 1
                                res = res.replace(_tag, '') 
                            # case:original text contents, eg [2025]文
                        infos.append({'content': f'{info_prefix}{res}', 'references': refences})
            hallucination_rate = round((hallucination_times / total_parsed) * 100, 2) if total_parsed > 0 else 'NA'
            self.logger.info(f"[QualityAssessment] task: link and info extraction, hallucination times: {hallucination_times}, hallucination rate: {hallucination_rate} %")
            extracted_content = [{'infos': infos, 'links': more_links}]
        
        if config.extraction_strategy.schema_mode:
            hallucination_times = 0
            total_parsed = 0
            schema_keys = config.extraction_strategy.schema.keys()
            plained_extracted_content = []
            for blocks in extracted_content:
                for block in blocks:
                    total_parsed += len(block)
                    for key in block.keys():
                        if key not in schema_keys:
                            hallucination_times += 1
                            del block[key]
                    for key in schema_keys:
                        if key not in block:
                            hallucination_times += 1
                            block[key] = None
                    plained_extracted_content.append(block)
            extracted_content = plained_extracted_content
            hallucination_rate = round((hallucination_times / total_parsed) * 100, 2) if total_parsed > 0 else 'NA'
            self.logger.info(f"[QualityAssessment] task: schema extraction, hallucination times: {hallucination_times}, hallucination rate: {hallucination_rate} %")

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
            extracted_content=extracted_content,
            success=True,
            error_message="",
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
            self.logger.debug(f"[SYS STATUS] memory_usage: {task_result.memory_usage}MB, peak_memory: {task_result.peak_memory}MB, retry_count: {task_result.retry_count}")
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
