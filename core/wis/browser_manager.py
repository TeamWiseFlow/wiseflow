import asyncio
import time
import os
from playwright.async_api import BrowserContext
import hashlib
from .js_snippet import load_js_script
from .config import DOWNLOAD_PAGE_TIMEOUT
from .async_configs import BrowserConfig, CrawlerRunConfig


BROWSER_DISABLE_OPTIONS = [
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-breakpad",
    "--disable-client-side-phishing-detection",
    "--disable-component-extensions-with-background-pages",
    "--disable-default-apps",
    "--disable-extensions",
    "--disable-features=TranslateUI",
    "--disable-hang-monitor",
    "--disable-ipc-flooding-protection",
    "--disable-popup-blocking",
    "--disable-prompt-on-repost",
    "--disable-sync",
    "--force-color-profile=srgb",
    "--metrics-recording-only",
    "--no-first-run",
    "--password-store=basic",
    "--use-mock-keychain",
]


async def clone_runtime_state(
    src: BrowserContext,
    dst: BrowserContext,
    crawlerRunConfig: CrawlerRunConfig | None = None,
    browserConfig: BrowserConfig | None = None,
) -> None:
    """
    Bring everything that *can* be changed at runtime from `src` → `dst`.

    1. Cookies
    2. localStorage (and sessionStorage, same API)
    3. Extra headers, permissions, geolocation if supplied in configs
    """

    # ── 1. cookies ────────────────────────────────────────────────────────────
    cookies = await src.cookies()
    if cookies:
        await dst.add_cookies(cookies)

    # ── 2. localStorage / sessionStorage ──────────────────────────────────────
    state = await src.storage_state()
    for origin in state.get("origins", []):
        url = origin["origin"]
        kvs = origin.get("localStorage", [])
        if not kvs:
            continue

        page = dst.pages[0] if dst.pages else await dst.new_page()
        await page.goto(url, wait_until="domcontentloaded")
        for k, v in kvs:
            await page.evaluate("(k,v)=>localStorage.setItem(k,v)", k, v)

    # ── 3. runtime-mutable extras from configs ────────────────────────────────
    # headers
    if browserConfig and browserConfig.headers:
        await dst.set_extra_http_headers(browserConfig.headers)

    # geolocation
    if crawlerRunConfig and crawlerRunConfig.geolocation:
        await dst.grant_permissions(["geolocation"])
        await dst.set_geolocation(
            {
                "latitude": crawlerRunConfig.geolocation.latitude,
                "longitude": crawlerRunConfig.geolocation.longitude,
                "accuracy": crawlerRunConfig.geolocation.accuracy,
            }
        )
        
    return dst



class BrowserManager:
    """
    Manages the browser instance and context.

    Attributes:
        config (BrowserConfig): Configuration object containing all browser settings
        logger: Logger instance for recording events and errors
        browser (Browser): The browser instance
        default_context (BrowserContext): The default browser context
        managed_browser (ManagedBrowser): The managed browser instance
        playwright (Playwright): The Playwright instance
        sessions (dict): Dictionary to store session information
        session_ttl (int): Session timeout in seconds
    """

    _playwright_instance = None
    
    @classmethod
    async def get_playwright(cls, use_undetected: bool = False):
        if use_undetected:
            from patchright.async_api import async_playwright
        else:
            from playwright.async_api import async_playwright
        cls._playwright_instance = await async_playwright().start()
        return cls._playwright_instance    

    def __init__(self, browser_config: BrowserConfig, logger=None, use_undetected: bool = False):
        """
        Initialize the BrowserManager with a browser configuration.

        Args:
            browser_config (BrowserConfig): Configuration object containing all browser settings
            logger: Logger instance for recording events and errors
            use_undetected (bool): Whether to use undetected browser (Patchright)
        """
        self.config: BrowserConfig = browser_config
        self.logger = logger
        self.use_undetected = use_undetected

        # Browser state
        self.browser = None
        self.default_context = None
        self.playwright = None

        # Session management
        self.sessions = {}
        self.session_ttl = 1800  # 30 minutes

        # Keep track of contexts by a "config signature," so each unique config reuses a single context
        self.contexts_by_config = {}
        self._contexts_lock = asyncio.Lock()
        
        # Serialize context.new_page() across concurrent tasks to avoid races
        # when using a shared persistent context (context.pages may be empty
        # for all racers). Prevents 'Target page/context closed' errors.
        self._page_lock = asyncio.Lock()
        
        # Stealth-related attributes
        self._stealth_instance = None
        self._stealth_cm = None 

    async def start(self):
        """
        Start the browser instance and set up the default context.

        How it works:
        1. Check if Playwright is already initialized.
        2. If not, initialize Playwright.
        3. If managed browser is used, start it and connect to the CDP endpoint.
        4. If managed browser is not used, launch the browser and set up the default context.

        Note: This method should be called in a separate task to avoid blocking the main event loop.
        """
        if self.playwright is not None:
            await self.close()
            
        if self.use_undetected:
            from patchright.async_api import async_playwright
        else:
            from playwright.async_api import async_playwright

        # Initialize playwright with or without stealth
        if self.config.enable_stealth and not self.use_undetected:
            # Import stealth only when needed
            from playwright_stealth import Stealth
            # Use the recommended stealth wrapper approach
            self._stealth_instance = Stealth()
            self._stealth_cm = self._stealth_instance.use_async(async_playwright())
            self.playwright = await self._stealth_cm.__aenter__()
        else:
            self.playwright = await async_playwright().start()


        browser_args = self._build_browser_args()

        # Launch appropriate browser type
        if self.config.browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(**browser_args)
        elif self.config.browser_type == "webkit":
            self.browser = await self.playwright.webkit.launch(**browser_args)
        else:
            self.browser = await self.playwright.chromium.launch(**browser_args)

        self.default_context = self.browser


    def _build_browser_args(self) -> dict:
        """Build browser launch arguments from config."""
        args = [
            "--disable-gpu",
            "--disable-gpu-compositing",
            "--disable-software-rasterizer",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-infobars",
            "--window-position=0,0",
            "--ignore-certificate-errors",
            "--ignore-certificate-errors-spki-list",
            "--disable-blink-features=AutomationControlled",
            "--window-position=400,0",
            "--disable-renderer-backgrounding",
            "--disable-ipc-flooding-protection",
            "--force-color-profile=srgb",
            "--mute-audio",
            "--disable-background-timer-throttling",
            # "--single-process",
            f"--window-size={self.config.viewport_width},{self.config.viewport_height}",
        ]

        if self.config.light_mode:
            args.extend(BROWSER_DISABLE_OPTIONS)

        if self.config.text_mode:
            args.extend(
                [
                    "--blink-settings=imagesEnabled=false",
                    "--disable-remote-fonts",
                    "--disable-images",
                    "--disable-javascript",
                    "--disable-software-rasterizer",
                    "--disable-dev-shm-usage",
                ]
            )

        if self.config.extra_args:
            args.extend(self.config.extra_args)

        # Deduplicate args
        args = list(dict.fromkeys(args))
        
        browser_args = {"headless": self.config.headless, "args": args}

        if self.config.chrome_channel:
            browser_args["channel"] = self.config.chrome_channel

        if self.config.accept_downloads:
            browser_args["downloads_path"] = self.config.downloads_path or os.path.join(
                os.getcwd(), "downloads"
            )
            os.makedirs(browser_args["downloads_path"], exist_ok=True)

        if self.config.proxy or self.config.proxy_config:
            from playwright.async_api import ProxySettings

            proxy_settings = (
                ProxySettings(server=self.config.proxy)
                if self.config.proxy
                else ProxySettings(
                    server=self.config.proxy_config.server,
                    username=self.config.proxy_config.username,
                    password=self.config.proxy_config.password,
                )
            )
            browser_args["proxy"] = proxy_settings

        return browser_args

    async def setup_context(
        self,
        context: BrowserContext,
        crawlerRunConfig: CrawlerRunConfig = None,
        is_default=False,
    ):
        """
        Set up a browser context with the configured options.

        How it works:
        1. Set extra HTTP headers if provided.
        2. Add cookies if provided.
        3. Load storage state if provided.
        4. Accept downloads if enabled.
        5. Set default timeouts for navigation and download.
        6. Set user agent if provided.
        7. Set browser hints if provided.
        8. Set proxy if provided.
        9. Set downloads path if provided.
        10. Set storage state if provided.
        11. Set cache if provided.
        12. Set extra HTTP headers if provided.
        13. Add cookies if provided.
        14. Set default timeouts for navigation and download if enabled.
        15. Set user agent if provided.
        16. Set browser hints if provided.

        Args:
            context (BrowserContext): The browser context to set up
            crawlerRunConfig (CrawlerRunConfig): Configuration object containing all browser settings
            is_default (bool): Flag indicating if this is the default context
        Returns:
            None
        """
        if self.config.headers:
            await context.set_extra_http_headers(self.config.headers)

        if self.config.cookies:
            await context.add_cookies(self.config.cookies)

        if self.config.storage_state:
            await context.storage_state(path=None)

        if self.config.accept_downloads:
            context.set_default_timeout(DOWNLOAD_PAGE_TIMEOUT)
            context.set_default_navigation_timeout(DOWNLOAD_PAGE_TIMEOUT)
            if self.config.downloads_path:
                context._impl_obj._options["accept_downloads"] = True
                context._impl_obj._options[
                    "downloads_path"
                ] = self.config.downloads_path

        # Handle user agent and browser hints
        if self.config.user_agent:
            combined_headers = {
                "User-Agent": self.config.user_agent,
                "sec-ch-ua": self.config.browser_hint,
            }
            combined_headers.update(self.config.headers)
            await context.set_extra_http_headers(combined_headers)

        # Add default cookie
        await context.add_cookies(
            [
                {
                    "name": "cookiesEnabled",
                    "value": "true",
                    "url": crawlerRunConfig.url
                    if crawlerRunConfig and crawlerRunConfig.url
                    else "https://crawl4ai.com/",
                }
            ]
        )

        # Handle navigator overrides
        if crawlerRunConfig:
            if (
                crawlerRunConfig.override_navigator
                or crawlerRunConfig.simulate_user
                or crawlerRunConfig.magic
            ):
                await context.add_init_script(load_js_script("navigator_overrider"))        

    async def create_browser_context(self, crawlerRunConfig: CrawlerRunConfig = None):
        """
        Creates and returns a new browser context with configured settings.
        Applies text-only mode settings if text_mode is enabled in config.

        Returns:
            Context: Browser context object with the specified configurations
        """
        # Base settings
        user_agent = self.config.headers.get("User-Agent", self.config.user_agent) 
        viewport_settings = {
            "width": self.config.viewport_width,
            "height": self.config.viewport_height,
        }
        proxy_settings = {"server": self.config.proxy} if self.config.proxy else None

        blocked_extensions = [
            # Images
            "jpg",
            "jpeg",
            "png",
            "gif",
            "webp",
            "svg",
            "ico",
            "bmp",
            "tiff",
            "psd",
            # Fonts
            "woff",
            "woff2",
            "ttf",
            "otf",
            "eot",
            # Styles
            # 'css', 'less', 'scss', 'sass',
            # Media
            "mp4",
            "webm",
            "ogg",
            "avi",
            "mov",
            "wmv",
            "flv",
            "m4v",
            "mp3",
            "wav",
            "aac",
            "m4a",
            "opus",
            "flac",
            # Documents
            "pdf",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "ppt",
            "pptx",
            # Archives
            "zip",
            "rar",
            "7z",
            "tar",
            "gz",
            # Scripts and data
            "xml",
            "swf",
            "wasm",
        ]

        # Common context settings
        context_settings = {
            "user_agent": user_agent,
            "viewport": viewport_settings,
            "proxy": proxy_settings,
            "accept_downloads": self.config.accept_downloads,
            "storage_state": self.config.storage_state,
            "ignore_https_errors": self.config.ignore_https_errors,
            "device_scale_factor": 1.0,
            "java_script_enabled": self.config.java_script_enabled,
        }
        
        if crawlerRunConfig:
            # Check if there is value for crawlerRunConfig.proxy_config set add that to context
            if crawlerRunConfig.proxy_config:
                proxy_settings = {
                    "server": crawlerRunConfig.proxy_config.server,
                }
                if crawlerRunConfig.proxy_config.username:
                    proxy_settings.update({
                        "username": crawlerRunConfig.proxy_config.username,
                        "password": crawlerRunConfig.proxy_config.password,
                    })
                context_settings["proxy"] = proxy_settings

        if self.config.text_mode:
            text_mode_settings = {
                "has_touch": False,
                "is_mobile": False,
            }
            # Update context settings with text mode settings
            context_settings.update(text_mode_settings)

        # inject locale / tz / geo if user provided them
        if crawlerRunConfig:
            if crawlerRunConfig.locale:
                context_settings["locale"] = crawlerRunConfig.locale
            if crawlerRunConfig.timezone_id:
                context_settings["timezone_id"] = crawlerRunConfig.timezone_id
            if crawlerRunConfig.geolocation:
                context_settings["geolocation"] = {
                    "latitude": crawlerRunConfig.geolocation.latitude,
                    "longitude": crawlerRunConfig.geolocation.longitude,
                    "accuracy": crawlerRunConfig.geolocation.accuracy,
                }
                # ensure geolocation permission
                perms = context_settings.get("permissions", [])
                perms.append("geolocation")
                context_settings["permissions"] = perms

        # Create and return the context with all settings
        context = await self.browser.new_context(**context_settings)

        # Apply text mode settings if enabled
        if self.config.text_mode:
            # Create and apply route patterns for each extension
            for ext in blocked_extensions:
                await context.route(f"**/*.{ext}", lambda route: route.abort())
        return context

    def _make_config_signature(self, crawlerRunConfig: CrawlerRunConfig) -> str:
        """
        Converts the crawlerRunConfig into a dict, excludes ephemeral fields,
        then returns a hash of the sorted JSON. This yields a stable signature
        that identifies configurations requiring a unique browser context.
        """
        import json

        config_dict = crawlerRunConfig.__dict__.copy()
        # Exclude items that do not affect browser-level setup.
        # Expand or adjust as needed, e.g. chunking_strategy is purely for data extraction, not for browser config.
        ephemeral_keys = [
            "session_id",
            "js_code",
            "scraping_strategy",
            "extraction_strategy",
            "chunking_strategy",
            "cache_mode",
            "content_filter",
            "semaphore_count",
            "url"
        ]
        
        # Do NOT exclude locale, timezone_id, or geolocation as these DO affect browser context
        # and should cause a new context to be created if they change
        
        for key in ephemeral_keys:
            if key in config_dict:
                del config_dict[key]
        # Convert to canonical JSON string
        signature_json = json.dumps(config_dict, sort_keys=True, default=str)

        # Hash the JSON so we get a compact, unique string
        signature_hash = hashlib.sha256(signature_json.encode("utf-8")).hexdigest()
        return signature_hash

    async def get_page(self, crawlerRunConfig: CrawlerRunConfig):
        """
        Get a page for the given session ID, creating a new one if needed.

        Args:
            crawlerRunConfig (CrawlerRunConfig): Configuration object containing all browser settings

        Returns:
            (page, context): The Page and its BrowserContext
        """
        self._cleanup_expired_sessions()

        # If a session_id is provided and we already have it, reuse that page + context
        if crawlerRunConfig.session_id and crawlerRunConfig.session_id in self.sessions:
            context, page, _ = self.sessions[crawlerRunConfig.session_id]
            # Update last-used timestamp
            self.sessions[crawlerRunConfig.session_id] = (context, page, time.time())
            return page, context

        # If using a managed browser, just grab the shared default_context
        if self.config.use_managed_browser:
            if self.config.storage_state:
                context = await self.create_browser_context(crawlerRunConfig)
                ctx = self.default_context        # default context, one window only
                ctx = await clone_runtime_state(context, ctx, crawlerRunConfig, self.config)
                # Avoid concurrent new_page on shared persistent context
                # See GH-1198: context.pages can be empty under races
                async with self._page_lock:
                    page = await ctx.new_page()
            else:
                context = self.default_context
                pages = context.pages
                page = next((p for p in pages if p.url == crawlerRunConfig.url), None)
                if not page:
                    if pages:
                        page = pages[0]
                    else:
                        # Double-check under lock to avoid TOCTOU and ensure only
                        # one task calls new_page when pages=[] concurrently
                        async with self._page_lock:
                            pages = context.pages
                            if pages:
                                page = pages[0]
                            else:
                                page = await context.new_page()
        else:
            # Otherwise, check if we have an existing context for this config
            config_signature = self._make_config_signature(crawlerRunConfig)

            async with self._contexts_lock:
                if config_signature in self.contexts_by_config:
                    context = self.contexts_by_config[config_signature]
                else:
                    # Create and setup a new context
                    context = await self.create_browser_context(crawlerRunConfig)
                    await self.setup_context(context, crawlerRunConfig)
                    self.contexts_by_config[config_signature] = context

            # Create a new page from the chosen context
            page = await context.new_page()

        # If a session_id is specified, store this session so we can reuse later
        if crawlerRunConfig.session_id:
            self.sessions[crawlerRunConfig.session_id] = (context, page, time.time())

        return page, context

    async def kill_session(self, session_id: str):
        """
        Kill a browser session and clean up resources.

        Args:
            session_id (str): The session ID to kill.
        """
        if session_id in self.sessions:
            context, page, _ = self.sessions[session_id]
            await page.close()
            if not self.config.use_managed_browser:
                await context.close()
            del self.sessions[session_id]

    def _cleanup_expired_sessions(self):
        """Clean up expired sessions based on TTL."""
        current_time = time.time()
        expired_sessions = [
            sid
            for sid, (_, _, last_used) in self.sessions.items()
            if current_time - last_used > self.session_ttl
        ]
        for sid in expired_sessions:
            asyncio.create_task(self.kill_session(sid))

    async def close(self):
        """Close all browser resources and clean up."""
        if self.config.cdp_url:
            return
        
        if self.config.sleep_on_close:
            await asyncio.sleep(0.5)

        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            await self.kill_session(session_id)

        # Now close all contexts we created. This reclaims memory from ephemeral contexts.
        for ctx in self.contexts_by_config.values():
            try:
                await ctx.close()
            except Exception as e:
                self.logger.error(
                    message="Error closing context: {error}",
                    tag="ERROR",
                    params={"error": str(e)}
                )
        self.contexts_by_config.clear()

        if self.browser:
            await self.browser.close()
            self.browser = None

        if self.playwright:
            # Handle stealth context manager cleanup if it exists
            if hasattr(self, '_stealth_cm') and self._stealth_cm is not None:
                try:
                    await self._stealth_cm.__aexit__(None, None, None)
                except Exception as e:
                    if self.logger:
                        self.logger.error(
                            message="Error closing stealth context: {error}",
                            tag="ERROR", 
                            params={"error": str(e)}
                        )
                self._stealth_cm = None
                self._stealth_instance = None
            else:
                await self.playwright.stop()
            self.playwright = None
