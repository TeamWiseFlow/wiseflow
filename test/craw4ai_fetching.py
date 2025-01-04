# -*- coding: utf-8 -*-
import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
import os
import hashlib
import json


sites = [
    "https://www.lejucaijing.com/news-7280844510992200941.html"
]

save_dir = 'webpage_samples'

async def main(sites: list):
    config = CrawlerRunConfig(
        delay_before_return_html=2.0,
        exclude_social_media_links=True,
        magic=True,
        scan_full_page=True,
        remove_overlay_elements=True
        )
    async with AsyncWebCrawler(headless=True, verbose=True) as crawler:
        for site in sites:
            # 排除社交媒体 todo 后续要用特定爬虫
            # 排除自动爬虫
            # 排除已经爬过的
            result = await crawler.arun(url=site, crawler_config=config, cache_mode=CacheMode.BYPASS)
            
            record_file = os.path.join(save_dir, f"{hashlib.sha256(site.encode()).hexdigest()[-6:]}.json")
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(result.model_dump(), f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    asyncio.run(main(sites))
