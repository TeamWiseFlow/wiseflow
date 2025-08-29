import asyncio
import time
import os
from patchright.async_api import async_playwright
from patchright.async_api import ProxySettings
from .config import DOWNLOAD_PAGE_TIMEOUT
from .async_configs import BrowserConfig, CrawlerRunConfig
from async_logger import base_directory


PERSISTENT_CONTEXT_DIR = os.path.join(base_directory, ".crawl4ai", "contexts")

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

        # Browser state
        self.contexts = {}
        self.playwright = None

        # Session management
        self.sessions = {}
        self.session_ttl = 1800  # 30 minutes

        self._contexts_lock = asyncio.Lock()

    async def start(self):

        if self.playwright is not None:
            await self.close()

        self.playwright = await async_playwright().start()

    def _build_stealth_args(self) -> list:
        """构建隐蔽启动参数"""
        stealth_args = [
            "--no-sandbox",
            # "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=VizDisplayCompositor",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-background-timer-throttling",
            "--disable-hang-monitor",
            "--disable-client-side-phishing-detection",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-sync",
            "--no-first-run",
            "--no-default-browser-check",
            "--password-store=basic",
            "--use-mock-keychain",
            "--disable-extensions",
            "--disable-default-apps",
            "--disable-component-extensions-with-background-pages",
            "--disable-gpu",
            "--disable-gpu-compositing", 
            "--disable-software-rasterizer",
            "--mute-audio",
            "--ignore-certificate-errors",
            "--ignore-ssl-errors",
            "--ignore-certificate-errors-spki-list",
            "--ignore-certificate-errors-skip-list",
            "--allow-running-insecure-content",
            "--disable-web-security",
            f"--window-size={self.config.viewport_width},{self.config.viewport_height}"
        ]
        if self.config.text_mode:
            stealth_args.extend(
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
            stealth_args.extend(self.config.extra_args)
        return list(set(stealth_args))

    def _build_browser_args(self, config: CrawlerRunConfig, proxy:ProxySettings = None) -> dict:

        args = self._build_stealth_args()

        browser_args = {
            "user_data_dir": os.path.join(PERSISTENT_CONTEXT_DIR, config.context_marker),
            "channel": "chrome",
            "headless": self.config.headless,
            "no_viewport": True,
            "ignore_https_errors": True,
            "java_script_enabled": True,
            "args": args,
        }
        if os.environ.get('BROWSER_EXECUTABLE_PATH'):
            browser_args['browser_executable_path'] = os.environ.get('BROWSER_EXECUTABLE_PATH')

        if self.config.text_mode:
            text_mode_settings = {
                "has_touch": False,
                "is_mobile": False,
            }
            # Update context settings with text mode settings
            browser_args.update(text_mode_settings)

        if self.config.accept_downloads:
            browser_args["accept_downloads"] = True
            if not self.config.downloads_path:
                self.config.downloads_path = os.path.join(base_directory, "downloads")
            browser_args["downloads_path"] = self.config.downloads_path
            os.makedirs(browser_args["downloads_path"], exist_ok=True)
            # Set download-related timeouts at browser level
            browser_args["navigation_timeout"] = DOWNLOAD_PAGE_TIMEOUT
            browser_args["timeout"] = DOWNLOAD_PAGE_TIMEOUT

        if proxy:
            browser_args["proxy"] = proxy

        # inject locale / tz / geo if user provided them
        if config.locale:
            browser_args["locale"] = config.locale
        if config.timezone_id:
            browser_args["timezone_id"] = config.timezone_id
        if config.geolocation:
            browser_args["geolocation"] = {
                "latitude": config.geolocation.latitude,
                "longitude": config.geolocation.longitude,
                "accuracy": config.geolocation.accuracy,
            }
            # ensure geolocation permission
            browser_args["permissions"] = ["geolocation"]

        return browser_args
    
    async def create_context(self, crawlerRunConfig: CrawlerRunConfig):
        """
        Create a new context for the given crawlerRunConfig.
        """
        if not self.playwright:
            await self.start()

        if crawlerRunConfig.proxy_provider:
            proxy_info = await crawlerRunConfig.proxy_provider.get_proxy()
            proxy = ProxySettings(
                server=f"{proxy_info.protocol}://{proxy_info.ip}:{proxy_info.port}",
                username=proxy_info.user,
                password=proxy_info.password,
            )
        else:
            proxy = None

        context = await self.playwright.chromium.launch_persistent_context(
            **self._build_browser_args
            (config = crawlerRunConfig, proxy = proxy))

        if self.config.text_mode:
            # Create and apply route patterns for each extension
            for ext in self._blocked_extensions:
                await context.route(f"**/*.{ext}", lambda route: route.abort())
        # await context.add_init_script(load_js_script("navigator_overrider_enhanced"))
        self.contexts[crawlerRunConfig.context_marker] = context
        return context

    async def get_page(self, crawlerRunConfig: CrawlerRunConfig, refresh: bool = False):
        """
        Get a page for the given session ID, creating a new one if needed.

        Args:
            crawlerRunConfig (CrawlerRunConfig): Configuration object containing all browser settings

        Returns:
            (page, context): The Page and its BrowserContext
        """
        async with self._contexts_lock:
            self._cleanup_expired_sessions()

            if not refresh:
                # If a session_id is provided and we already have it, reuse that page + context
                if crawlerRunConfig.session_id and crawlerRunConfig.session_id in self.sessions:
                    context, page, _, _ = self.sessions[crawlerRunConfig.session_id]
                    # Update last-used timestamp
                    self.sessions[crawlerRunConfig.session_id] = (context, page, time.time(), crawlerRunConfig.context_marker)
                    return page, context

            context = self.contexts.get(crawlerRunConfig.context_marker)
        
            if context and refresh:
                for session_id, (_, _, _, context_marker) in self.sessions.items():
                    if context_marker == crawlerRunConfig.context_marker:
                        del self.sessions[session_id]
                await context.close()
                del self.contexts[crawlerRunConfig.context_marker]
                context = None
            if not context:
                context = await self.create_context(crawlerRunConfig)

        page = await context.new_page()

        # If a session_id is specified, store this session so we can reuse later
        if crawlerRunConfig.session_id:
            self.sessions[crawlerRunConfig.session_id] = (context, page, time.time(), crawlerRunConfig.context_marker)

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
            # await context.close()
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
        if self.config.sleep_on_close:
            await asyncio.sleep(0.5)

        for context in self.contexts.values():
            await context.close()
        self.contexts.clear()
        self.sessions.clear()

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
