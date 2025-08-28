import os
from .config import (
    SCREENSHOT_HEIGHT_TRESHOLD,
    PAGE_TIMEOUT,
)

from .proxy_providers import ProxyProvider
from typing import Union, List
import inspect
from typing import Any, Dict, Optional
from enum import Enum

from .c4a_scripts import compile


def to_serializable_dict(obj: Any, ignore_default_value : bool = False) -> Dict:
    """
    Recursively convert an object to a serializable dictionary using {type, params} structure
    for complex objects.
    """
    if obj is None:
        return None

    # Handle basic types
    if isinstance(obj, (str, int, float, bool)):
        return obj

    # Handle Enum
    if isinstance(obj, Enum):
        return {"type": obj.__class__.__name__, "params": obj.value}

    # Handle datetime objects
    if hasattr(obj, "isoformat"):
        return obj.isoformat()

    # Handle lists, tuples, and sets, and basically any iterable
    if isinstance(obj, (list, tuple, set)) or hasattr(obj, '__iter__') and not isinstance(obj, dict):
        return [to_serializable_dict(item) for item in obj]

    # Handle frozensets, which are not iterable
    if isinstance(obj, frozenset):
        return [to_serializable_dict(item) for item in list(obj)]

    # Handle dictionaries - preserve them as-is
    if isinstance(obj, dict):
        return {
            "type": "dict",  # Mark as plain dictionary
            "value": {str(k): to_serializable_dict(v) for k, v in obj.items()},
        }

    _type = obj.__class__.__name__

    # Handle class instances
    if hasattr(obj, "__class__"):
        # Get constructor signature
        sig = inspect.signature(obj.__class__.__init__)
        params = sig.parameters

        # Get current values
        current_values = {}
        for name, param in params.items():
            if name == "self":
                continue

            value = getattr(obj, name, param.default)

            # Only include if different from default, considering empty values
            if not (is_empty_value(value) and is_empty_value(param.default)):
                if value != param.default and not ignore_default_value:
                    current_values[name] = to_serializable_dict(value)
        
        if hasattr(obj, '__slots__'):
            for slot in obj.__slots__:
                if slot.startswith('_'):  # Handle private slots
                    attr_name = slot[1:]  # Remove leading '_'
                    value = getattr(obj, slot, None)
                    if value is not None:
                        current_values[attr_name] = to_serializable_dict(value)

            
        
        return {
            "type": obj.__class__.__name__,
            "params": current_values
        }
        
    return str(obj)


def from_serializable_dict(data: Any) -> Any:
    """
    Recursively convert a serializable dictionary back to an object instance.
    """
    if data is None:
        return None

    # Handle basic types
    if isinstance(data, (str, int, float, bool)):
        return data

    # Handle typed data
    if isinstance(data, dict) and "type" in data:
        # Handle plain dictionaries
        if data["type"] == "dict" and "value" in data:
            return {k: from_serializable_dict(v) for k, v in data["value"].items()}

    # Handle lists
    if isinstance(data, list):
        return [from_serializable_dict(item) for item in data]

    # Handle raw dictionaries (legacy support)
    if isinstance(data, dict):
        return {k: from_serializable_dict(v) for k, v in data.items()}

    return data


def is_empty_value(value: Any) -> bool:
    """Check if a value is effectively empty/null."""
    if value is None:
        return True
    if isinstance(value, (list, tuple, set, dict, str)) and len(value) == 0:
        return True
    return False


class GeolocationConfig:
    def __init__(
        self,
        latitude: float,
        longitude: float,
        accuracy: Optional[float] = 0.0
    ):
        """Configuration class for geolocation settings.
        
        Args:
            latitude: Latitude coordinate (e.g., 37.7749)
            longitude: Longitude coordinate (e.g., -122.4194)
            accuracy: Accuracy in meters. Default: 0.0
        """
        self.latitude = latitude
        self.longitude = longitude
        self.accuracy = accuracy
    
    @staticmethod
    def from_dict(geo_dict: Dict) -> "GeolocationConfig":
        """Create a GeolocationConfig from a dictionary."""
        return GeolocationConfig(
            latitude=geo_dict.get("latitude"),
            longitude=geo_dict.get("longitude"),
            accuracy=geo_dict.get("accuracy", 0.0)
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracy": self.accuracy
        }
    
    def clone(self, **kwargs) -> "GeolocationConfig":
        """Create a copy of this configuration with updated values.

        Args:
            **kwargs: Key-value pairs of configuration options to update

        Returns:
            GeolocationConfig: A new instance with the specified updates
        """
        config_dict = self.to_dict()
        config_dict.update(kwargs)
        return GeolocationConfig.from_dict(config_dict)


class BrowserConfig:
    """
    Configuration class for setting up a browser instance and its context in AsyncPlaywrightCrawlerStrategy.

    This class centralizes all parameters that affect browser and context creation. Instead of passing
    scattered keyword arguments, users can instantiate and modify this configuration object. The crawler
    code will then reference these settings to initialize the browser in a consistent, documented manner.

    Attributes:
        browser_type (str): The type of browser to launch. Supported values: "chromium", "firefox", "webkit".
                            Default: "chromium".
        headless (bool): Whether to run the browser in headless mode (no visible GUI).
                         Default: True.
        browser_mode (str): Determines how the browser should be initialized:
                           "builtin" - use the builtin CDP browser running in background
                           "dedicated" - create a new dedicated browser instance each time
                           "cdp" - use explicit CDP settings provided in cdp_url
                           "docker" - run browser in Docker container with isolation
                           Default: "dedicated"
        use_managed_browser (bool): Launch the browser using a managed approach (e.g., via CDP), allowing
                                    advanced manipulation. Default: False.
        cdp_url (str): URL for the Chrome DevTools Protocol (CDP) endpoint. Default: "ws://localhost:9222/devtools/browser/".
        debugging_port (int): Port for the browser debugging protocol. Default: 9222.
        use_persistent_context (bool): Use a persistent browser context (like a persistent profile).
                                       Automatically sets use_managed_browser=True. Default: False.
        user_data_dir (str or None): Path to a user data directory for persistent sessions. If None, a
                                     temporary directory may be used. Default: None.
        chrome_channel (str): The Chrome channel to launch (e.g., "chrome", "msedge"). Only applies if browser_type
                              is "chromium". Default: "chromium".
        channel (str): The channel to launch (e.g., "chromium", "chrome", "msedge"). Only applies if browser_type
                              is "chromium". Default: "chromium".
        proxy (Optional[str]): Proxy server URL (e.g., "http://username:password@proxy:port"). If None, no proxy is used.
                             Default: None.
        proxy_config (ProxyConfig or dict or None): Detailed proxy configuration, e.g. {"server": "...", "username": "..."}.
                                     If None, no additional proxy config. Default: None.
        viewport_width (int): Default viewport width for pages. Default: 1080.
        viewport_height (int): Default viewport height for pages. Default: 600.
        viewport (dict): Default viewport dimensions for pages. If set, overrides viewport_width and viewport_height.
                         Default: None.
        verbose (bool): Enable verbose logging.
                        Default: True.
        accept_downloads (bool): Whether to allow file downloads. If True, requires a downloads_path.
                                 Default: False.
        downloads_path (str or None): Directory to store downloaded files. If None and accept_downloads is True,
                                      a default path will be created. Default: None.
        storage_state (str or dict or None): An in-memory storage state (cookies, localStorage).
                                             Default: None.
        ignore_https_errors (bool): Ignore HTTPS certificate errors. Default: True.
        java_script_enabled (bool): Enable JavaScript execution in pages. Default: True.
        cookies (list): List of cookies to add to the browser context. Each cookie is a dict with fields like
                        {"name": "...", "value": "...", "url": "..."}.
                        Default: [].
        headers (dict): Extra HTTP headers to apply to all requests in this context.
                        Default: {}.
        user_agent (str): Custom User-Agent string to use. Default: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36".
        user_agent_mode (str or None): Mode for generating the user agent (e.g., "random"). If None, use the provided
                                       user_agent as-is. Default: None.
        user_agent_generator_config (dict or None): Configuration for user agent generation if user_agent_mode is set.
                                                    Default: None.
        text_mode (bool): If True, disables images and other rich content for potentially faster load times.
                          Default: False.
        light_mode (bool): Disables certain background features for performance gains. Default: False.
        extra_args (list): Additional command-line arguments passed to the browser.
                           Default: [].
        enable_stealth (bool): If True, applies playwright-stealth to bypass basic bot detection.
                              Cannot be used with use_undetected browser mode. Default: False.
    """

    def __init__(
        self,
        headless: bool = False,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        accept_downloads: bool = False,
        downloads_path: str = None,
        ignore_https_errors: bool = True,
        java_script_enabled: bool = True,
        sleep_on_close: bool = False,
        verbose: bool = False,
        text_mode: bool = False,
        extra_args: list = None,
    ):
        self.headless = headless 
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.accept_downloads = accept_downloads
        self.downloads_path = downloads_path
        self.ignore_https_errors = ignore_https_errors
        self.java_script_enabled = java_script_enabled
        self.text_mode = text_mode
        self.extra_args = extra_args if extra_args is not None else []
        self.sleep_on_close = sleep_on_close
        self.verbose = verbose

    @staticmethod
    def from_kwargs(kwargs: dict) -> "BrowserConfig":
        return BrowserConfig(
            headless=kwargs.get("headless", True),
            viewport_width=kwargs.get("viewport_width", 1920),
            viewport_height=kwargs.get("viewport_height", 1080),
            accept_downloads=kwargs.get("accept_downloads", False),
            downloads_path=kwargs.get("downloads_path"),
            ignore_https_errors=kwargs.get("ignore_https_errors", True),
            java_script_enabled=kwargs.get("java_script_enabled", True),
            sleep_on_close=kwargs.get("sleep_on_close", False),
            verbose=kwargs.get("verbose", False),
            text_mode=kwargs.get("text_mode", False),
            extra_args=kwargs.get("extra_args", []),
        )

    def to_dict(self):
        result = {
            "headless": self.headless,
            "viewport_width": self.viewport_width,
            "viewport_height": self.viewport_height,
            "accept_downloads": self.accept_downloads,
            "downloads_path": self.downloads_path,
            "ignore_https_errors": self.ignore_https_errors,
            "java_script_enabled": self.java_script_enabled,
            "text_mode": self.text_mode,
            "extra_args": self.extra_args,
            "sleep_on_close": self.sleep_on_close,
            "verbose": self.verbose,
        }

        return result

    def clone(self, **kwargs):
        """Create a copy of this configuration with updated values.

        Args:
            **kwargs: Key-value pairs of configuration options to update

        Returns:
            BrowserConfig: A new instance with the specified updates
        """
        config_dict = self.to_dict()
        config_dict.update(kwargs)
        return BrowserConfig.from_kwargs(config_dict)

    # Create a funciton returns dict of the object
    def dump(self) -> dict:
        # Serialize the object to a dictionary
        return to_serializable_dict(self)

    @staticmethod
    def load(data: dict) -> "BrowserConfig":
        # Deserialize the object from a dictionary
        config = from_serializable_dict(data)
        if isinstance(config, BrowserConfig):
            return config
        return BrowserConfig.from_kwargs(config)

class VirtualScrollConfig:
    """Configuration for virtual scroll handling.
    
    This config enables capturing content from pages with virtualized scrolling
    (like Twitter, Instagram feeds) where DOM elements are recycled as user scrolls.
    """
    
    def __init__(
        self,
        container_selector: str,
        scroll_count: int = 10,
        scroll_by: Union[str, int] = "container_height",
        wait_after_scroll: float = 0.5,
    ):
        """
        Initialize virtual scroll configuration.
        
        Args:
            container_selector: CSS selector for the scrollable container
            scroll_count: Maximum number of scrolls to perform
            scroll_by: Amount to scroll - can be:
                - "container_height": scroll by container's height
                - "page_height": scroll by viewport height  
                - int: fixed pixel amount
            wait_after_scroll: Seconds to wait after each scroll for content to load
        """
        self.container_selector = container_selector
        self.scroll_count = scroll_count
        self.scroll_by = scroll_by
        self.wait_after_scroll = wait_after_scroll
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "container_selector": self.container_selector,
            "scroll_count": self.scroll_count,
            "scroll_by": self.scroll_by,
            "wait_after_scroll": self.wait_after_scroll,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VirtualScrollConfig":
        """Create instance from dictionary."""
        return cls(**data)

class LinkPreviewConfig:
    """Configuration for link head extraction and scoring."""
    
    def __init__(
        self,
        include_internal: bool = True,
        include_external: bool = False,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        concurrency: int = 10,
        timeout: int = 5,
        max_links: int = 100,
        query: Optional[str] = None,
        score_threshold: Optional[float] = None,
        verbose: bool = False
    ):
        """
        Initialize link extraction configuration.
        
        Args:
            include_internal: Whether to include same-domain links
            include_external: Whether to include different-domain links  
            include_patterns: List of glob patterns to include (e.g., ["*/docs/*", "*/api/*"])
            exclude_patterns: List of glob patterns to exclude (e.g., ["*/login*", "*/admin*"])
            concurrency: Number of links to process simultaneously
            timeout: Timeout in seconds for each link's head extraction
            max_links: Maximum number of links to process (prevents overload)
            query: Query string for BM25 contextual scoring (optional)
            score_threshold: Minimum relevance score to include links (0.0-1.0, optional)
            verbose: Show detailed progress during extraction
        """
        self.include_internal = include_internal
        self.include_external = include_external
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns
        self.concurrency = concurrency
        self.timeout = timeout
        self.max_links = max_links
        self.query = query
        self.score_threshold = score_threshold
        self.verbose = verbose
        
        # Validation
        if concurrency <= 0:
            raise ValueError("concurrency must be positive")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if max_links <= 0:
            raise ValueError("max_links must be positive")
        if score_threshold is not None and not (0.0 <= score_threshold <= 1.0):
            raise ValueError("score_threshold must be between 0.0 and 1.0")
        if not include_internal and not include_external:
            raise ValueError("At least one of include_internal or include_external must be True")
    
    @staticmethod
    def from_dict(config_dict: Dict[str, Any]) -> "LinkPreviewConfig":
        """Create LinkPreviewConfig from dictionary (for backward compatibility)."""
        if not config_dict:
            return None
        
        return LinkPreviewConfig(
            include_internal=config_dict.get("include_internal", True),
            include_external=config_dict.get("include_external", False),
            include_patterns=config_dict.get("include_patterns"),
            exclude_patterns=config_dict.get("exclude_patterns"),
            concurrency=config_dict.get("concurrency", 10),
            timeout=config_dict.get("timeout", 5),
            max_links=config_dict.get("max_links", 100),
            query=config_dict.get("query"),
            score_threshold=config_dict.get("score_threshold"),
            verbose=config_dict.get("verbose", False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "include_internal": self.include_internal,
            "include_external": self.include_external,
            "include_patterns": self.include_patterns,
            "exclude_patterns": self.exclude_patterns,
            "concurrency": self.concurrency,
            "timeout": self.timeout,
            "max_links": self.max_links,
            "query": self.query,
            "score_threshold": self.score_threshold,
            "verbose": self.verbose
        }
    
    def clone(self, **kwargs) -> "LinkPreviewConfig":
        """Create a copy with updated values."""
        config_dict = self.to_dict()
        config_dict.update(kwargs)
        return LinkPreviewConfig.from_dict(config_dict)


class CrawlerRunConfig:

    """
    Configuration class for controlling how the crawler runs each crawl operation.
    This includes parameters for content extraction, page manipulation, waiting conditions,
    caching, and other runtime behaviors.

    This centralizes parameters that were previously scattered as kwargs to `arun()` and related methods.
    By using this class, you have a single place to understand and adjust the crawling options.

    Attributes:

        # Content Processing Parameters
        word_count_threshold (int): Minimum word count threshold before processing content.
                                    Default: MIN_WORD_THRESHOLD (typically 200).
        extraction_strategy (ExtractionStrategy or None): Strategy to extract structured data from crawled pages.
                                                          Default: None (NoExtractionStrategy is used if None).

        excluded_tags (list of str or None): List of HTML tags to exclude from processing.
                                             Default: None.
        proxy_config (ProxyConfig or dict or None): Detailed proxy configuration, e.g. {"server": "...", "username": "..."}.
                                     If None, no additional proxy config. Default: None.

        # Browser Location and Identity Parameters
        locale (str or None): Locale to use for the browser context (e.g., "en-US").
                             Default: None.
        timezone_id (str or None): Timezone identifier to use for the browser context (e.g., "America/New_York").
                                  Default: None.
        geolocation (GeolocationConfig or None): Geolocation configuration for the browser.
                                                Default: None.

        # SSL Parameters
        fetch_ssl_certificate: bool = False,
        # Caching Parameters
        shared_data (dict or None): Shared data to be passed between hooks.
                                     Default: None.

        # Page Navigation and Timing Parameters
        wait_until (str): The condition to wait for when navigating, e.g. "domcontentloaded".
                          Default: "domcontentloaded".
        page_timeout (int): Timeout in ms for page operations like navigation.
                            Default: 60000 (60 seconds).
        wait_for (str or None): A CSS selector or JS condition to wait for before extracting content.
                                Default: None.
        wait_for_images (bool): If True, wait for images to load before extracting content.
                                Default: False.
        delay_before_return_html (float): Delay in seconds before retrieving final HTML.
                                          Default: 0.1.
        mean_delay (float): Mean base delay between requests when calling arun_many.
                            Default: 0.1.
        max_range (float): Max random additional delay range for requests in arun_many.
                           Default: 0.3.
        semaphore_count (int): Number of concurrent operations allowed.
                               Default: 5.

        # Page Interaction Parameters
        js_code (str or list of str or None): JavaScript code/snippets to run on the page.
                                              Default: None.
        js_only (bool): If True, indicates subsequent calls are JS-driven updates, not full page loads.
                        Default: False.
        ignore_body_visibility (bool): If True, ignore whether the body is visible before proceeding.
                                       Default: True.
        scan_full_page (bool): If True, scroll through the entire page to load all content.
                               Default: False.
        scroll_delay (float): Delay in seconds between scroll steps if scan_full_page is True.
                              Default: 0.2.
        process_iframes (bool): If True, attempts to process and inline iframe content.
                                Default: False.
        remove_overlay_elements (bool): If True, remove overlays/popups before extracting HTML.
                                        Default: False.
        simulate_user (bool): If True, simulate user interactions (mouse moves, clicks) for anti-bot measures.
                              Default: False.
        override_navigator (bool): If True, overrides navigator properties for more human-like behavior.
                                   Default: False.
        magic (bool): If True, attempts automatic handling of overlays/popups.
                      Default: False.
        adjust_viewport_to_content (bool): If True, adjust viewport according to the page content dimensions.
                                           Default: False.

        # Media Handling Parameters
        screenshot (bool): Whether to take a screenshot after crawling.
                           Default: False.
        screenshot_wait_for (float or None): Additional wait time before taking a screenshot.
                                             Default: None.
        screenshot_height_threshold (int): Threshold for page height to decide screenshot strategy.
                                           Default: SCREENSHOT_HEIGHT_TRESHOLD (from config, e.g. 20000).
        pdf (bool): Whether to generate a PDF of the page.
                    Default: False.
        image_description_min_word_threshold (int): Minimum words for image description extraction.
                                                    Default: IMAGE_DESCRIPTION_MIN_WORD_THRESHOLD (e.g., 50).
        image_score_threshold (int): Minimum score threshold for processing an image.
                                     Default: IMAGE_SCORE_THRESHOLD (e.g., 3).
        exclude_external_images (bool): If True, exclude all external images from processing.
                                         Default: False.
        table_score_threshold (int): Minimum score threshold for processing a table.
                                     Default: 7.

        # Link and Domain Handling Parameters
        exclude_social_media_domains (list of str): List of domains to exclude for social media links.
                                                    Default: SOCIAL_MEDIA_DOMAINS (from config).
        exclude_external_links (bool): If True, exclude all external links from the results.
                                       Default: False.
        exclude_internal_links (bool): If True, exclude internal links from the results.
                                       Default: False.
        exclude_social_media_links (bool): If True, exclude links pointing to social media domains.
                                           Default: False.
        exclude_domains (list of str): List of specific domains to exclude from results.
                                       Default: [].
        exclude_internal_links (bool): If True, exclude internal links from the results.
                                       Default: False.

        # Debugging and Logging Parameters
        verbose (bool): Enable verbose logging.
                        Default: True.
        log_console (bool): If True, log console messages from the page.
                            Default: False.

        # HTTP Crwler Strategy Parameters
        method (str): HTTP method to use for the request, when using AsyncHTTPCrwalerStrategy.
                        Default: "GET".
        data (dict): Data to send in the request body, when using AsyncHTTPCrwalerStrategy.
                        Default: None.
        json (dict): JSON data to send in the request body, when using AsyncHTTPCrwalerStrategy.

        # Connection Parameters
        stream (bool): If True, enables streaming of crawled URLs as they are processed when used with arun_many.
                      Default: False.

        check_robots_txt (bool): Whether to check robots.txt rules before crawling. Default: False
                                 Default: False.
        user_agent (str): Custom User-Agent string to use.
                          Default: None.
        user_agent_mode (str or None): Mode for generating the user agent (e.g., "random"). If None, use the provided user_agent as-is.
                                       Default: None.
        user_agent_generator_config (dict or None): Configuration for user agent generation if user_agent_mode is set.
                                                    Default: None.

        # Experimental Parameters
        experimental (dict): Dictionary containing experimental parameters that are in beta phase.
                            This allows passing temporary features that are not yet fully integrated 
                            into the main parameter set.
                            Default: None.

        url: str = None  # This is not a compulsory parameter
    """

    def __init__(
        self,
        # Content Processing Parameters
        excluded_tags: list = None,
        proxy_provider: ProxyProvider = None,
        # Browser Location and Identity Parameters
        locale: Optional[str] = None,
        timezone_id: Optional[str] = None,
        geolocation: Optional[GeolocationConfig] = None,
        # SSL Parameters
        fetch_ssl_certificate: bool = False,
        # Caching Parameters
        session_id: str = None,
        shared_data: dict = None,
        # Page Navigation and Timing Parameters
        wait_until: str = "domcontentloaded",
        page_timeout: int = PAGE_TIMEOUT,
        wait_for: str = None,
        wait_for_images: bool = False,
        delay_before_return_html: float = 0.1,
        mean_delay: float = 0.1,
        max_range: float = 0.3,
        semaphore_count: int = 5,
        css_selector: str = None,
        # Page Interaction Parameters
        js_code: Union[str, List[str]] = None,
        c4a_script: Union[str, List[str]] = None,
        js_only: bool = False,
        ignore_body_visibility: bool = True,
        scan_full_page: bool = False,
        scroll_delay: float = 0.2,
        process_iframes: bool = False,
        remove_overlay_elements: bool = False,
        override_navigator: bool = False,
        adjust_viewport_to_content: bool = False,
        # Media Handling Parameters
        screenshot: bool = False,
        screenshot_wait_for: float = None,
        screenshot_height_threshold: int = SCREENSHOT_HEIGHT_TRESHOLD,
        pdf: bool = False,
        capture_mhtml: bool = False,
        # image_description_min_word_threshold: int = IMAGE_DESCRIPTION_MIN_WORD_THRESHOLD,
        # image_score_threshold: int = IMAGE_SCORE_THRESHOLD,
        table_score_threshold: int = 7,
        # exclude_external_images: bool = False,
        exclude_all_images: bool = False,
        # Debugging and Logging Parameters
        log_console: bool = False,
        # Network and Console Capturing Parameters
        capture_network_requests: bool = False,
        capture_console_messages: bool = False,
        # Connection Parameters
        method: str = "GET",
        stream: bool = False,
        url: str = None,
        check_robots_txt: bool = False,
        user_agent: str = None,
        user_agent_mode: str = None,
        user_agent_generator_config: dict = {},
        # Experimental Parameters
        experimental: Dict[str, Any] = None,
        wait_for_timeout: int = None,
        max_scroll_steps: Optional[int] = None,
        virtual_scroll_config: Union[VirtualScrollConfig, Dict[str, Any]] = None,
    ):
        # TODO: Planning to set properties dynamically based on the __init__ signature
        self.url = url
        self.excluded_tags = excluded_tags
        self.proxy_provider = proxy_provider
        
        # Browser Location and Identity Parameters
        self.locale = locale
        self.timezone_id = timezone_id
        self.geolocation = geolocation

        # SSL Parameters
        self.fetch_ssl_certificate = fetch_ssl_certificate

        # Caching Parameters
        self.session_id = session_id
        self.shared_data = shared_data

        # Page Navigation and Timing Parameters
        self.wait_until = wait_until
        self.page_timeout = page_timeout
        self.wait_for = wait_for
        self.wait_for_images = wait_for_images
        self.delay_before_return_html = delay_before_return_html
        self.mean_delay = mean_delay
        self.max_range = max_range
        self.semaphore_count = semaphore_count
        self.wait_for_timeout = wait_for_timeout
        self.css_selector = css_selector
        # Page Interaction Parameters
        self.js_code = js_code
        self.c4a_script = c4a_script
        self.js_only = js_only
        self.ignore_body_visibility = ignore_body_visibility
        self.scan_full_page = scan_full_page
        self.scroll_delay = scroll_delay
        self.process_iframes = process_iframes  
        self.remove_overlay_elements = remove_overlay_elements
        self.override_navigator = override_navigator
        self.adjust_viewport_to_content = adjust_viewport_to_content

        # Media Handling Parameters
        self.screenshot = screenshot
        self.screenshot_wait_for = screenshot_wait_for
        self.screenshot_height_threshold = screenshot_height_threshold
        self.pdf = pdf
        self.capture_mhtml = capture_mhtml
        # self.image_description_min_word_threshold = image_description_min_word_threshold
        # self.image_score_threshold = image_score_threshold
        # self.exclude_external_images = exclude_external_images
        self.exclude_all_images = exclude_all_images
        self.table_score_threshold = table_score_threshold

        # Debugging and Logging Parameters
        self.log_console = log_console
        
        # Network and Console Capturing Parameters
        self.capture_network_requests = capture_network_requests
        self.capture_console_messages = capture_console_messages

        # Connection Parameters
        self.stream = stream
        self.method = method

        # Robots.txt Handling Parameters
        self.check_robots_txt = check_robots_txt
        # User Agent Parameters
        self.user_agent = user_agent
        self.user_agent_mode = user_agent_mode
        self.user_agent_generator_config = user_agent_generator_config

        # Experimental Parameters
        self.experimental = experimental or {}
        self.max_scroll_steps = max_scroll_steps
        self.virtual_scroll_config = virtual_scroll_config

        # Virtual Scroll Parameters
        if virtual_scroll_config is None:
            self.virtual_scroll_config = None
        elif isinstance(virtual_scroll_config, VirtualScrollConfig):
            self.virtual_scroll_config = virtual_scroll_config
        elif isinstance(virtual_scroll_config, dict):
            # Convert dict to config object for backward compatibility
            self.virtual_scroll_config = VirtualScrollConfig.from_dict(virtual_scroll_config)
        else:
            raise ValueError("virtual_scroll_config must be VirtualScrollConfig object or dict")

        # Compile C4A scripts if provided
        if self.c4a_script and not self.js_code:
            self._compile_c4a_script()

    def _compile_c4a_script(self):
        """Compile C4A script to JavaScript"""
        try: 
            # Handle both string and list inputs
            if isinstance(self.c4a_script, str):
                scripts = [self.c4a_script]
            else:
                scripts = self.c4a_script
                
            # Compile each script
            compiled_js = []
            for i, script in enumerate(scripts):
                result = compile(script)
                
                if result.success:
                    compiled_js.extend(result.js_code)
                else:
                    # Format error message following existing patterns
                    error = result.first_error
                    error_msg = (
                        f"C4A Script compilation error (script {i+1}):\n"
                        f"  Line {error.line}, Column {error.column}: {error.message}\n"
                        f"  Code: {error.source_line}"
                    )
                    if error.suggestions:
                        error_msg += f"\n  Suggestion: {error.suggestions[0].message}"
                        
                    raise ValueError(error_msg)
                    
            self.js_code = compiled_js
            
        except Exception as e:
            # Re-raise with context
            if "compilation error" not in str(e).lower():
                raise ValueError(f"Failed to compile C4A script: {str(e)}")
            raise

    @staticmethod
    def from_kwargs(kwargs: dict) -> "CrawlerRunConfig":
        return CrawlerRunConfig(
            # Content Processing Parameters
            excluded_tags=kwargs.get("excluded_tags", []),
            proxy_provider=kwargs.get("proxy_provider"),
            # Browser Location and Identity Parameters
            locale=kwargs.get("locale", None),
            timezone_id=kwargs.get("timezone_id", None),
            geolocation=kwargs.get("geolocation", None),
            # SSL Parameters
            fetch_ssl_certificate=kwargs.get("fetch_ssl_certificate", False),
            # Caching Parameters
            session_id=kwargs.get("session_id"),
            shared_data=kwargs.get("shared_data", None),
            # Page Navigation and Timing Parameters
            wait_until=kwargs.get("wait_until", "domcontentloaded"),
            page_timeout=kwargs.get("page_timeout", 60000),
            wait_for=kwargs.get("wait_for"),
            wait_for_images=kwargs.get("wait_for_images", False),
            delay_before_return_html=kwargs.get("delay_before_return_html", 0.1),
            mean_delay=kwargs.get("mean_delay", 0.1),
            max_range=kwargs.get("max_range", 0.3),
            semaphore_count=kwargs.get("semaphore_count", 5),
            css_selector=kwargs.get("css_selector"),
            # Page Interaction Parameters
            js_code=kwargs.get("js_code"),
            c4a_script=kwargs.get("c4a_script"),
            js_only=kwargs.get("js_only", False),
            ignore_body_visibility=kwargs.get("ignore_body_visibility", True),
            scan_full_page=kwargs.get("scan_full_page", False),
            scroll_delay=kwargs.get("scroll_delay", 0.2),
            process_iframes=kwargs.get("process_iframes", False),
            remove_overlay_elements=kwargs.get("remove_overlay_elements", False),
            override_navigator=kwargs.get("override_navigator", False),
            adjust_viewport_to_content=kwargs.get("adjust_viewport_to_content", False),
            # Media Handling Parameters
            screenshot=kwargs.get("screenshot", False),
            screenshot_wait_for=kwargs.get("screenshot_wait_for"),
            screenshot_height_threshold=kwargs.get(
                "screenshot_height_threshold", SCREENSHOT_HEIGHT_TRESHOLD
            ),
            pdf=kwargs.get("pdf", False),
            capture_mhtml=kwargs.get("capture_mhtml", False),
            table_score_threshold=kwargs.get("table_score_threshold", 7),
            exclude_all_images=kwargs.get("exclude_all_images", False),
            # Debugging and Logging Parameters
            log_console=kwargs.get("log_console", False),
            # Network and Console Capturing Parameters
            capture_network_requests=kwargs.get("capture_network_requests", False),
            capture_console_messages=kwargs.get("capture_console_messages", False),
            # Connection Parameters
            method=kwargs.get("method", "GET"),
            stream=kwargs.get("stream", False),
            check_robots_txt=kwargs.get("check_robots_txt", False),
            user_agent=kwargs.get("user_agent"),
            user_agent_mode=kwargs.get("user_agent_mode"),
            user_agent_generator_config=kwargs.get("user_agent_generator_config", {}),
            url=kwargs.get("url"),
            wait_for_timeout=kwargs.get("wait_for_timeout"),
            # Experimental Parameters 
            experimental=kwargs.get("experimental"),
            max_scroll_steps=kwargs.get("max_scroll_steps"),
            virtual_scroll_config=kwargs.get("virtual_scroll_config"),
        )

    # Create a funciton returns dict of the object
    def dump(self) -> dict:
        # Serialize the object to a dictionary
        return to_serializable_dict(self)

    @staticmethod
    def load(data: dict) -> "CrawlerRunConfig":
        # Deserialize the object from a dictionary
        return CrawlerRunConfig.from_kwargs(data)

    def to_dict(self):
        return {
            "excluded_tags": self.excluded_tags,
            "proxy_provider": self.proxy_provider,
            "locale": self.locale,
            "timezone_id": self.timezone_id,
            "geolocation": self.geolocation,
            "fetch_ssl_certificate": self.fetch_ssl_certificate,
            "session_id": self.session_id,
            "shared_data": self.shared_data,
            "wait_until": self.wait_until,
            "page_timeout": self.page_timeout,
            "wait_for": self.wait_for,
            "wait_for_images": self.wait_for_images,
            "delay_before_return_html": self.delay_before_return_html,
            "mean_delay": self.mean_delay,
            "max_range": self.max_range,
            "semaphore_count": self.semaphore_count,
            "css_selector": self.css_selector,
            "js_code": self.js_code,
            "c4a_script": self.c4a_script,
            "js_only": self.js_only,
            "ignore_body_visibility": self.ignore_body_visibility,
            "scan_full_page": self.scan_full_page,
            "scroll_delay": self.scroll_delay,
            "process_iframes": self.process_iframes,
            "remove_overlay_elements": self.remove_overlay_elements,
            "override_navigator": self.override_navigator,
            "adjust_viewport_to_content": self.adjust_viewport_to_content,
            "screenshot": self.screenshot,
            "screenshot_wait_for": self.screenshot_wait_for,
            "screenshot_height_threshold": self.screenshot_height_threshold,
            "pdf": self.pdf,
            "capture_mhtml": self.capture_mhtml,
            "table_score_threshold": self.table_score_threshold,
            "exclude_all_images": self.exclude_all_images,
            "log_console": self.log_console,
            "capture_network_requests": self.capture_network_requests,
            "capture_console_messages": self.capture_console_messages,
            "method": self.method,
            "stream": self.stream,
            "check_robots_txt": self.check_robots_txt,
            "user_agent": self.user_agent,
            "user_agent_mode": self.user_agent_mode,
            "user_agent_generator_config": self.user_agent_generator_config,
            "url": self.url,
            "wait_for_timeout": self.wait_for_timeout,
            "experimental": self.experimental,
            "max_scroll_steps": self.max_scroll_steps,
            "virtual_scroll_config": self.virtual_scroll_config,
        }

    def clone(self, **kwargs):
        """Create a copy of this configuration with updated values.

        Args:
            **kwargs: Key-value pairs of configuration options to update

        Returns:
            CrawlerRunConfig: A new instance with the specified updates

        Example:
            ```python
            # Create a new config with streaming enabled
            stream_config = config.clone(stream=True)

            # Create a new config with multiple updates
            new_config = config.clone(
                stream=True,
                cache_mode=CacheMode.BYPASS,
                verbose=True
            )
            ```
        """
        config_dict = self.to_dict()
        config_dict.update(kwargs)
        return CrawlerRunConfig.from_kwargs(config_dict)
    