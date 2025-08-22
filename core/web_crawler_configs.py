from wis.async_configs import CrawlerRunConfig


DEFAULT_CRAWLER_CONFIG = CrawlerRunConfig(
    # session_id="my_session123",
    delay_before_return_html=1.0,
    word_count_threshold=10,
    magic=True, 
    scan_full_page=True,
    scroll_delay=0.3,
    # check_robots_txt=True
    # locale=None,
    # timezone_id=None,
    # geolocation=None,
    # SSL Parameters
    # fetch_ssl_certificate=False,
    # page_timeout=30000,
    # wait_for=None,
    # js_code=None, # to execute some js code in the page
    # exclude_external_links=False, # if you want the info collection only in the site's domain, set this to True
    # excluded_tags = []  # 如果不配置默认移除所有非顶级的'script', 'style', 'noscript', 'iframe', 'canvas', 'svg', 'video', 'audio', 'source', 'track', 'map', 'area'
    # for internet codebug, you can capture the network requests and console messages
    # capture_network_requests=False,
    # capture_console_messages=False,
)

# for special domain, modify a custom crawler config and register it here
crawler_config_map = {'default': DEFAULT_CRAWLER_CONFIG}
