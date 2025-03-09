# -*- coding: utf-8 -*-
import asyncio
import os
import hashlib
import json
import sys
import psutil

core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(core_path)
from crawl4ai import AsyncWebCrawler, CacheMode
from scrapers import crawler_config
from scrapers import browser_cfg

save_dir = 'webpage_samples'
# which include some standard sites with different html structure
standard_sites = ["https://www.zhihu.com/topic/19552832/hot",
                  "https://mp.weixin.qq.com/s/y-YCGeYXv_T4bB48hn0UGw",
                  "https://news.bjx.com.cn/html/20241226/1419428.shtml",
                  "https://news.bjx.com.cn/rankinglist/qingneng/",
                  "http://search.people.cn/s?keyword=%E7%A4%BE%E5%8C%BA%E6%B2%BB%E7%90%86&st=0&_=1741317033197",
                  "https://www.gd121.cn/zx/qxzx/list.shtml",
                  "https://www.xuexi.cn/lgpage/detail/index.html?id=12812273746490421418&item_id=12812273746490421418",
                  "https://www.gzhu.edu.cn/",
                  "https://arxiv.org/list/cs/recent",
                  "https://www.shenmezhideting.com/app/homepage",
                  "https://tophub.today/",
                  "https://www.reuters.com/site-search/?query=tech&offset=0",
                  "https://www.reuters.com/business/autos-transportation/",
                  "https://d.aigclink.ai/?v=e3a86502f7ef495598705abe58e21848",
                  ]

crawler_config.cache_mode=CacheMode.DISABLED

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

    crawler = AsyncWebCrawler(config=browser_cfg)
    await crawler.start()
    crawler_config.cache_mode = CacheMode.DISABLED
    for site in sites:
        # Check memory usage prior to launching tasks
        log_memory(prefix="Before crawling: ")
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

    await crawler.close()
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
