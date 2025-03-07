from crawl4ai import CrawlerRunConfig, BrowserConfig, LXMLWebScrapingStrategy
from .customer_crawl4ai_md_generator import CustomMarkdownGenerator
from .mp_scraper import mp_scraper

custom_scrapers = {'mp.weixin.qq.com': mp_scraper}
custom_fetching_configs = {}

md_generator = CustomMarkdownGenerator(
        options={
            "skip_internal_links": True,
            "escape_html": True,
            "include_sup_sub": True
        }
    )

crawler_config = CrawlerRunConfig(
    # session_id="my_session123",
    delay_before_return_html=1.0,
    word_count_threshold=10,
    # keep_data_attributes=True,
    scraping_strategy=LXMLWebScrapingStrategy(),
    excluded_tags=['script', 'style'],
    # exclude_domains=[],
    # disable_cache=True,
    markdown_generator=md_generator, 
    wait_until='commit', 
    # simulate_user=True,
    magic=True, 
    scan_full_page=True,
    scroll_delay=0.5,
    # adjust_viewport_to_content=True,
    # verbose=False,
    # keep_data_attributes=True,
    # fetch_ssl_certificate=True,
    # image_score_threshold=3
)

browser_cfg = BrowserConfig(
    browser_type="chromium",
    headless=True,
    viewport_width=1920,
    viewport_height=1080,
    # proxy="http://user:pass@proxy:8080",
    # use_managed_browser=True,
    # If you need authentication storage or repeated sessions, consider use_persistent_context=True and specify user_data_dir.
    # use_persistent_context=True, # must be used with use_managed_browser=True
    # user_data_dir="/tmp/crawl4ai_chromium_profile",
    # java_script_enabled=True,
    # cookies=[]
    # headers={}
    user_agent_mode="random",
    # user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/116.0.0.0 Safari/537.36",
    light_mode=True,
    # text_mode=True,
    extra_args=["--disable-gpu", "--disable-extensions"]
)