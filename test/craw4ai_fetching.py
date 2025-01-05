# -*- coding: utf-8 -*-
import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode
import os
import hashlib
import json


save_dir = 'webpage_samples'

async def main(sites: list):
    async with AsyncWebCrawler(headless=True, verbose=True) as crawler:
        for site in sites:
            result = await crawler.arun(url=site, delay_before_return_html=2.0, exclude_social_media_links=True,
                                        magic=True,
                                        scan_full_page=True,
                                        remove_overlay_elements=True, cache_mode=CacheMode.BYPASS)
            
            record_file = os.path.join(save_dir, f"{hashlib.sha256(site.encode()).hexdigest()[-6:]}.json")
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(result.model_dump(), f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sites', '-S', type=str)
    parser.add_argument('--save_dir', '-D', type=str, default=save_dir)
    args = parser.parse_args()

    sites = [site.strip() for site in args.sites.split(',')]
    save_dir = args.save_dir
    os.makedirs(save_dir, exist_ok=True)
    asyncio.run(main(sites))
