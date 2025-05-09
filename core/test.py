from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
import asyncio

# Create browser config with builtin mode
browser_config = BrowserConfig(
    browser_mode="builtin",  # This is the key setting!
    headless=True            # Can be headless or not
)


# Create the crawler
crawler = AsyncWebCrawler(config=browser_config)


# Use it - no need to explicitly start()
result = asyncio.run(crawler.arun("https://mp.weixin.qq.com/s/t0aXokWLyKZFu7LpnUBU7w"))
if result.success:
    print(result.cleaned_html)
else:
    print(result.error_message)
