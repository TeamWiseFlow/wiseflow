# -*- coding: utf-8 -*-
import asyncio
import os
import hashlib
import json
import sys

root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(root_path)
from wis import AsyncWebCrawler
from web_crawler_configs import crawler_config_map


save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webpage_samples')
# which include some standard sites with different html structure
standard_sites = ['https://cg.shenzhenmc.com/zzbgg/83524.jhtml',
                  'https://www.jimei123.com/cn/news/plate-information',
                  'https://cg.shenzhenmc.com/zzzgg/85093.jhtml',
                  'https://www.mee.gov.cn/xxgk2018/xxgk/xxgk15/201809/t20180928_661943.html',
                  'https://www.stone365.com/news/channel-1.html']

async def main(sites: list):
    async with AsyncWebCrawler(crawler_config_map=crawler_config_map) as crawler:
        async for result in await crawler.arun_many(sites):
            if result and result.success:
                record_file = os.path.join(save_dir, f"{hashlib.sha256(result.url.encode()).hexdigest()[-6:]}.json")
                with open(record_file, 'w', encoding='utf-8') as f:
                    json.dump(result.model_dump(), f, indent=4, ensure_ascii=False)
                print(f'saved to {record_file}')
            else:
                print(f'{result.url} failed to crawl: {result.error_message}')


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
