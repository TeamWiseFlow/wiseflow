from wis.async_configs import CrawlerRunConfig, GeolocationConfig
from wis.proxy_providers import KuaiDaiLiProxy, LocalProxy, ProxyProvider
import wis.config.proxy_config as proxy_config


proxy_provider = None
if hasattr(proxy_config, 'WEB_PROXY'):
    proxy_name = getattr(proxy_config, 'WEB_PROXY')
    if proxy_name == 'local':
        proxy_provider = LocalProxy(uni_name="local_proxy", ip_pool_count=1, enable_validate_ip=False)
    elif proxy_name.startswith('kdl_') and hasattr(proxy_config, proxy_name) and isinstance(getattr(proxy_config, proxy_name), dict):
        proxy_settings = getattr(proxy_config, proxy_name)
        proxy_provider = KuaiDaiLiProxy(uni_name=proxy_name, 
                                        ip_pool_count=2, 
                                        enable_validate_ip=False, 
                                        kdl_secret_id=proxy_settings.get("SECERT_ID", ""), 
                                        kdl_signature=proxy_settings.get("SIGNATURE", ""), 
                                        kdl_user_name=proxy_settings.get("USER_NAME", ""), 
                                        kdl_user_pwd=proxy_settings.get("USER_PWD", ""))



DEFAULT_CRAWLER_CONFIG = CrawlerRunConfig(
    # session_id="my_session123",
    delay_before_return_html=1.0,
    scan_full_page=True,
    scroll_delay=0.3,
    max_scroll_steps=18,
    proxy_provider=proxy_provider,
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

# for domains need proxy
PROXY_CRAWLER_CONFIG = CrawlerRunConfig(
    proxy_provider=proxy_provider,
    delay_before_return_html=1.0,
    scan_full_page=True,
    scroll_delay=0.3,
    max_scroll_steps=18
)