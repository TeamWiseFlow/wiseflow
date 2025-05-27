from ..wis import BrowserConfig
from .default_config import crawler_config as default_crawler_config


# do use get_base_domain to get the base domain of the url, and then use the custom_scrapers to scrape the url
# custom_scrapers = {'mp.weixin.qq.com': mp_scraper}
custom_fetching_configs = {}

# for 99.9% of the cases, no need to change the default browser config
# if some domain need to be treated differently, you should modify a customer CrawlerRunConfig first
default_browser_config = BrowserConfig(
    viewport_width=1920,
    viewport_height=1080,
    user_agent_mode="random",
    light_mode=True
)