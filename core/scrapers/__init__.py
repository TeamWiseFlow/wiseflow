from crawl4ai import CrawlerRunConfig
# from .xxx import xx_config

custom_scrapers = {}
custom_fetching_configs = {}


crawler_config = CrawlerRunConfig(delay_before_return_html=2.0, markdown_generator=md_generator,
                                wait_until='commit', magic=True, scan_full_page=True)
