from core.wis.async_configs import CrawlerRunConfig, GeolocationConfig


DEFAULT_CRAWLER_CONFIG = CrawlerRunConfig(
    # session_id="my_session123",
    delay_before_return_html=1.0,
    scan_full_page=True,
    scroll_delay=0.3,
    max_scroll_steps=18,
    # locale=None,
    # timezone_id=None,
    # geolocation=None,
    # need_login=False,
    # SSL Parameters
    # fetch_ssl_certificate=False,
    # page_timeout=30000,
    # wait_for=None,
    # js_code=None, # to execute some js code in the page
    # c4a_script=None, # to robotexecute some c4a script in the page
    # excluded_tags = []  # leave it empty to remove all following tags: 'script', 'style', 'noscript', 'iframe', 'canvas', 'svg', 'video', 'audio', 'source', 'track', 'map', 'area'
    # for internet codebug, you can capture the network requests and console messages
    # capture_network_requests=True,
    # capture_console_messages=True,
)

# for domains need login
NEED_LOGIN_CRAWLER_CONFIG = CrawlerRunConfig(
    need_login=True,
    delay_before_return_html=1.0,
    scan_full_page=True,
    scroll_delay=0.3,
    max_scroll_steps=18,
    # proxy_provider=proxy_provider
)
