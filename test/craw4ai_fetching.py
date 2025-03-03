# -*- coding: utf-8 -*-
import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode
import os
import hashlib
import json
import sys

core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(core_path)

from scrapers import crawler_config as default_crawler_config
from scrapers import browser_cfg

save_dir = 'webpage_samples'

crawler_config = default_crawler_config.clone(cache_mode=CacheMode.DISABLED)
# crawler = AsyncWebCrawler(config=browser_cfg)

async def main(sites: list):
    for site in sites:
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            try:
                result = await crawler.arun(url=site, config=crawler_config)
            except Exception as e:
                print(e)
                continue
        if not result or not result.success:
            print(f'{site} failed to crawl, skip')
            continue
            
        print('raw_markdown:')
        print(result.markdown)
        print('-' * 24)

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
