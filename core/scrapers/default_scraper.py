from ..wwd import CrawlerRunConfig

"""
refer this to modify a custom scraper(actully is a CrawlerRunConfig)
1. config the extractor
2. config the md_generator
3. config the filter strategy: target_elements, exclude_all_images, remove_comments, excluded_tags, excluded_selector, remove_forms, exclude_domains, only_text
4. config other base options, particularly the proxy
"""

crawler_config = CrawlerRunConfig(
    # session_id="my_session123",
    delay_before_return_html=1.0,
    word_count_threshold=10,
    magic=True, 
    scan_full_page=True,
    # locale=None,
    # timezone_id=None,
    # geolocation=None,
    # SSL Parameters
    # fetch_ssl_certificate=False,
    # page_timeout=30000,
    # wait_for=None,
    # check_robots_txt=False,
    # exclude_external_links=False, # if you want the info collection only in the site's domain, set this to True
    # excluded_tags = []  # 唯一可以在 preprocess 阶段配置的，如果不配置默认移除所有非顶级的'script', 'style', 'noscript', 'iframe', 'canvas', 'svg', 'video', 'audio', 'source', 'track', 'map', 'area'
    extraction_strategy=None # 使用自定义 scraper config需要配置的地方，default 会自动在主进程使用 LLMExtractionStrategy， 并填入 focuspoint
    # for internet codebug, you can capture the network requests and console messages
    # capture_network_requests=False,
    # capture_console_messages=False,
)
