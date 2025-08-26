import asyncio
import time
import os
import json
from patchright.async_api import BrowserContext
import hashlib
from .js_snippet import load_js_script
from .config import DOWNLOAD_PAGE_TIMEOUT
from .async_configs import BrowserConfig, CrawlerRunConfig
from patchright.async_api import async_playwright
from patchright.async_api import ProxySettings


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
    _blocked_extensions = [
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

    @classmethod
    async def get_playwright(cls):
        cls._playwright_instance = await async_playwright().start()
        return cls._playwright_instance

    def __init__(self, browser_config: BrowserConfig, logger=None):
        """
        Initialize the BrowserManager with a browser configuration.

        Args:
            browser_config (BrowserConfig): Configuration object containing all browser settings
            logger: Logger instance for recording events and errors
            use_undetected (bool): Whether to use undetected browser (Patchright)
        """
        self.config: BrowserConfig = browser_config
        self.logger = logger
        self.proxy = browser_config.proxy_config
        self.locale = None
        self.timezone_id = None
        self.geolocation = None

        # Browser state
        self.browser = None
        self.default_context = None
        self.managed_browser = None
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

    # modified by bigbrother to only use patchright to launch browser
    async def start(self):
        """
        Start the browser instance and set up the default context.

        How it works:
        1. Check if Playwright is already initialized.
        2. If not, initialize Playwright.
        3. Choose between launch() and launch_persistent_context() based on config
        4. Set up the appropriate browser instance and context.

        Note: This method should be called in a separate task to avoid blocking the main event loop.
        """
        if self.playwright is not None:
            await self.close()
            
        # Initialize playwright
        self.playwright = await async_playwright().start()
        browser_args = self._build_browser_args()
        
        # Choose launch strategy based on configuration
        if self.config.use_persistent_context and self.config.user_data_dir:
            # Use launch_persistent_context for better persistence
            self.default_context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.config.user_data_dir,
                **browser_args
            )
            # Apply text mode settings if enabled
            if self.config.text_mode:
                # Create and apply route patterns for each extension
                for ext in self._blocked_extensions:
                    await self.default_context.route(f"**/*.{ext}", lambda route: route.abort())
            self.browser = None  # No separate browser object in persistent mode
        else:
            # Use traditional launch + new_context approach
            self.browser = await self.playwright.chromium.launch(**browser_args)
            self.default_context = None  # Will be created dynamically
    
    # modified by bigbrother to  both for launch and launch_persistent_context
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
            # f"--window-size={self.config.viewport_width},{self.config.viewport_height}",
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
        args = list(set(args))
        
        browser_args = {"no_viewport":True,
                        "headless": self.config.headless,
                        "ignore_https_errors": self.config.ignore_https_errors,
                        "java_script_enabled": self.config.java_script_enabled,
                        "accept_downloads": self.config.accept_downloads,
                        "channel": self.config.channel,
                        "executable_path": self.config.executable_path,
                        "args": args}

        if self.config.text_mode:
            text_mode_settings = {
                "has_touch": False,
                "is_mobile": False,
            }
            browser_args.update(text_mode_settings)

        if self.config.accept_downloads:
            browser_args["downloads_path"] = self.config.downloads_path or os.path.join(
                os.getcwd(), "downloads"
            )
            os.makedirs(browser_args["downloads_path"], exist_ok=True)
            browser_args["default_timeout"] = DOWNLOAD_PAGE_TIMEOUT
            browser_args["default_navigation_timeout"] = DOWNLOAD_PAGE_TIMEOUT

        if self.proxy:
            proxy_settings = ProxySettings(server=self.proxy.server,
                                           username=self.proxy.username,
                                           password=self.proxy.password)
            browser_args["proxy"] = proxy_settings
        if self.locale:
            browser_args["locale"] = self.locale
        if self.timezone_id:
            browser_args["timezone_id"] = self.timezone_id
        if self.geolocation:
            browser_args["geolocation"] = {
                "latitude": self.geolocation.latitude,
                "longitude": self.geolocation.longitude,
                "accuracy": self.geolocation.accuracy,
            }
            # ensure geolocation permission
            perms = browser_args.get("permissions", [])
            perms.append("geolocation")
            browser_args["permissions"] = perms

        return {k: v for k, v in browser_args.items() if v is not None}
        
    async def setup_context(
        self,
        context: BrowserContext,
        crawlerRunConfig: CrawlerRunConfig = None,
        is_default=False,
    ):
        """
        Set up a browser context with the configured options.
        
        For persistent contexts, most settings are already applied at startup, no need to use this function
        For non-persistent contexts, we apply the necessary configurations.

        Args:
            context (BrowserContext): The browser context to set up
            crawlerRunConfig (CrawlerRunConfig): Configuration object containing all browser settings
            is_default (bool): Flag indicating if this is the default context
        Returns:
            None
        only for traditional launch mode, not for persistent context
        """
        if not self.browser:
            self.logger.warning("You should not call this function for persistent context")
            return
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
        only for traditional launch mode, not for persistent context
        """
        if not self.browser:
            self.logger.warning("You should not call this function for persistent context")
            return
        # Common context settings
        context_settings = {}
        if crawlerRunConfig:
            # Check if there is value for crawlerRunConfig.proxy_config set add that to context
            if crawlerRunConfig.proxy_config:
                proxy_settings = ProxySettings(server=crawlerRunConfig.proxy_config.server,
                                               username=crawlerRunConfig.proxy_config.username,
                                               password=crawlerRunConfig.proxy_config.password)
                context_settings["proxy"] = proxy_settings

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

        if self.config.text_mode:
            text_mode_settings = {
                "has_touch": False,
                "is_mobile": False,
            }
            # Update context settings with text mode settings
            context_settings.update(text_mode_settings)

        context = await self.browser.new_context(**context_settings)

        # Apply text mode settings if enabled
        if self.config.text_mode:
            # Create and apply route patterns for each extension
            for ext in self._blocked_extensions:
                await context.route(f"**/*.{ext}", lambda route: route.abort())
        return context

    def _compare_proxy_config(self, proxy1, proxy2):
        """Compare two proxy configurations for equality."""
        # Both None
        if proxy1 is None and proxy2 is None:
            return True
        # One None, one not None
        if proxy1 is None or proxy2 is None:
            return False
        # Compare actual values
        return (
            proxy1.server == proxy2.server and
            getattr(proxy1, 'username', None) == getattr(proxy2, 'username', None) and
            getattr(proxy1, 'password', None) == getattr(proxy2, 'password', None)
        )
    
    def _compare_geolocation(self, geo1, geo2):
        """Compare two geolocation configurations for equality."""
        # Both None
        if geo1 is None and geo2 is None:
            return True
        # One None, one not None
        if geo1 is None or geo2 is None:
            return False
        # Compare actual values
        return (
            geo1.latitude == geo2.latitude and
            geo1.longitude == geo2.longitude and
            geo1.accuracy == geo2.accuracy
        )
    
    def _configs_match(self, crawlerRunConfig: CrawlerRunConfig) -> bool:
        """
        Check if crawlerRunConfig settings match current browser manager settings.
        
        Returns True if all configurations match, False otherwise.
        """
        # Compare proxy_config
        if not self._compare_proxy_config(crawlerRunConfig.proxy_config, self.proxy):
            return False
        
        # Compare locale (both None is considered equal)
        if (crawlerRunConfig.locale is None and self.locale is None) or \
           (crawlerRunConfig.locale == self.locale):
            pass  # Equal
        else:
            return False
            
        # Compare timezone_id (both None is considered equal)
        if (crawlerRunConfig.timezone_id is None and self.timezone_id is None) or \
           (crawlerRunConfig.timezone_id == self.timezone_id):
            pass  # Equal
        else:
            return False
            
        # Compare geolocation
        if not self._compare_geolocation(crawlerRunConfig.geolocation, self.geolocation):
            return False
            
        return True
    
    def _make_context_signature(self, crawlerRunConfig: CrawlerRunConfig) -> str:
        """
        Generate a signature for configurations that truly require different browser contexts.
        Only includes settings that fundamentally change browser behavior.
        
        Context-affecting configurations:
        - proxy_config: Different proxies require different contexts
        - locale: Language settings affect browser behavior  
        - timezone_id: Timezone affects JavaScript Date objects
        - geolocation: Geographic location for geolocation API
        """
        # Only include truly context-level configurations
        context_affecting_config = {}
        
        # Proxy configuration significantly affects context
        if crawlerRunConfig.proxy_config:
            context_affecting_config["proxy"] = {
                "server": crawlerRunConfig.proxy_config.server,
                "username": getattr(crawlerRunConfig.proxy_config, 'username', None),
                "password": getattr(crawlerRunConfig.proxy_config, 'password', None)
            }
        
        # Locale affects browser language and behavior
        if crawlerRunConfig.locale:
            context_affecting_config["locale"] = crawlerRunConfig.locale
            
        # Timezone affects JavaScript Date behavior
        if crawlerRunConfig.timezone_id:
            context_affecting_config["timezone_id"] = crawlerRunConfig.timezone_id
            
        # Geolocation affects geolocation API
        if crawlerRunConfig.geolocation:
            context_affecting_config["geolocation"] = {
                "latitude": crawlerRunConfig.geolocation.latitude,
                "longitude": crawlerRunConfig.geolocation.longitude,
                "accuracy": crawlerRunConfig.geolocation.accuracy
            }
        
        # Convert to canonical JSON string and hash
        signature_json = json.dumps(context_affecting_config, sort_keys=True, default=str)
        signature_hash = hashlib.sha256(signature_json.encode("utf-8")).hexdigest()
        
        return signature_hash

    async def get_page(self, crawlerRunConfig: CrawlerRunConfig):
        """
        Get a page for the given session ID, creating a new one if needed.
        
        Simplified strategy for better performance and persistent context support:
        - For persistent context: always reuse the same context
        - For non-persistent: create new context only when truly necessary

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

        # For persistent context, always reuse the same context
        if self.config.use_persistent_context:
            # Check if configurations have changed and need context restart
            if not self._configs_match(crawlerRunConfig):
                if self.logger:
                    self.logger.info("Configuration changed, updating browser settings and restarting context")
                
                # Update self configurations to match crawlerRunConfig
                self.proxy = crawlerRunConfig.proxy_config
                self.locale = crawlerRunConfig.locale
                self.timezone_id = crawlerRunConfig.timezone_id
                self.geolocation = crawlerRunConfig.geolocation
                
                # Close current default_context if exists
                if self.default_context:
                    await self.default_context.close()
                    self.default_context = None
                
                # Restart with new configuration
                await self.start()

            if not self.default_context:
                await self.start()
            
            context = self.default_context
            page = await context.new_page()
        else:
            # For non-persistent context, check if we need a new context
            # Only create new context for truly context-level differences
            context_signature = self._make_context_signature(crawlerRunConfig)
            
            async with self._contexts_lock:
                if context_signature in self.contexts_by_config:
                    context = self.contexts_by_config[context_signature]
                else:
                    # Create and setup a new context only when necessary
                    context = await self.create_browser_context(crawlerRunConfig)
                    await self.setup_context(context, crawlerRunConfig)
                    self.contexts_by_config[context_signature] = context

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
                self.logger.error(f"Error closing context: {str(e)}")
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
                        self.logger.error(f"Error closing stealth context: {str(e)}")
                self._stealth_cm = None
                self._stealth_instance = None
            else:
                await self.playwright.stop()
            self.playwright = None
