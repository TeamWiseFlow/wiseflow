from wis.async_configs import CrawlerRunConfig, GeolocationConfig
from wis.proxy_providers import KuaiDaiLiProxy, LocalProxy, ProxyProvider

# proxy provider sample
# sample_proxy_provider = LocalProxy(uni_name="sample_local_proxy", ip_pool_count=1, enable_validate_ip=False)
# here we sue the default local proxy file, which means you need put a json file in base_directory/proxy_setting.json, as following format:
"""
You Must give a json file as following format:
[
    {
        "ip": "http://127.0.0.1",
        "port": 8080,
        "user": "user",
        "password": "password",
        "life_time": 17  # in minutes, 0 means never expire
    }
    ...
]
"""

# kuaidaili proxy provider sample
# from wis.config.proxy_config import KDL_SECERT_ID, KDL_SIGNATURE, KDL_USER_NAME, KDL_USER_PWD
# sample_kuaidaili_proxy_provider = KuaiDaiLiProxy(
#     uni_name="sample_kuaidaili_proxy",
#     ip_pool_count=2,
#     enable_validate_ip=True,
#     kdl_secret_id=KDL_SECERT_ID,
#     kdl_signature=KDL_SIGNATURE,
#     kdl_user_name=KDL_USER_NAME,
#     kdl_user_pwd=KDL_USER_PWD,
# )

DEFAULT_CRAWLER_CONFIG = CrawlerRunConfig(
    # session_id="my_session123",
    delay_before_return_html=1.0,
    scan_full_page=True,
    scroll_delay=0.3,
    max_scroll_steps=18,
    # proxy_provider=sample_proxy_provider,
    # check_robots_txt=True
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

NEED_LOGIN_CRAWLER_CONFIG = CrawlerRunConfig(
    need_login=True,
    delay_before_return_html=1.0,
    scan_full_page=True,
    scroll_delay=0.3,
    max_scroll_steps=18
)
