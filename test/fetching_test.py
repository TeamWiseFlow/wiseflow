# -*- coding: utf-8 -*-
import asyncio
import os
import hashlib
import json
import sys
import psutil

root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(root_path)
from core.wwd import AsyncWebCrawler, CacheMode, BrowserConfig
from core.scrapers.default_scraper import crawler_config


save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webpage_samples')
# which include some standard sites with different html structure
standard_sites = ['https://cg.shenzhenmc.com/zzbgg/83524.jhtml',
                  'https://www.jimei123.com/cn/news/plate-information',
                  'https://cg.shenzhenmc.com/zzzgg/85093.jhtml',
                  'https://www.mee.gov.cn/xxgk2018/xxgk/xxgk15/201809/t20180928_661943.html',
                  'https://www.stone365.com/news/channel-1.html']

base_directory=os.path.join(root_path, 'work_dir')

crawler_config.cache_mode = CacheMode.DISABLED
browser_cfg = BrowserConfig(
    # browser_type="chromium",
    # headless=True,
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

async def main(sites: list):
    print("\n=== Crawling Test with Memory Check ===")

    # We'll keep track of peak memory usage across all tasks
    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # in bytes
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        for site in sites:
            # Check memory usage prior to launching tasks
            log_memory(prefix="Before crawling: ")
            print(f"Crawling {site}")
            try:
                result = await crawler.arun(url=site, config=crawler_config)
            except Exception as e:
                print(e)
                continue
            if not result or not result.success:
                print(f'{site} failed to crawl, skip')
                continue
            record_file = os.path.join(save_dir, f"{hashlib.sha256(site.encode()).hexdigest()[-6:]}.json")
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(result.model_dump(), f, indent=4, ensure_ascii=False)
            print(f'saved to {record_file}')

            # Check memory usage after tasks complete
            # maybe we can use this to check memory usage, if exceed settings, we can close and restart the crawler...
            log_memory(prefix="After crawling: ")

    # Final memory log
    log_memory(prefix="Final: ")
    print(f"\nPeak memory usage (MB): {peak_memory // (1024 * 1024)}")

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sites', '-S', type=str, default='')
    parser.add_argument('--save_dir', '-D', type=str, default=save_dir)
    args = parser.parse_args()

    sites = [site.strip() for site in args.sites.split(',')] if args.sites else standard_sites

    save_dir = args.save_dir
    os.makedirs(save_dir, exist_ok=True)

    asyncio.run(main(sites))
