# -*- coding: utf-8 -*-
import asyncio
import os
import hashlib
import json
import sys
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(root_path)
from wis import AsyncWebCrawler
from custom_processes import crawler_config_map
from tools.rss_parsor import fetch_rss

save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webpage_samples')
# which include some standard sites with different html structure
standard_sites = ['https://qn.bjx.com.cn/',
                  'https://huanbao.bjx.com.cn/news/20250730/1453496.shtml',
                  'https://hr.bjx.com.cn/companys/50208/jobs_0_1/',
                  'https://mp.weixin.qq.com/s/jBWc1tK8_XasfmCGNo93Xg',
                  'https://www.liugong.com/',
                  "https://www.xcmg.com/aboutus/news.htm",
                  "https://www.komatsu.com/en/",
                  "https://www.putzmeister.com/",
                  "https://www.cat.com/",
                  "https://www.zoomlion.com/news/industry.html",
                  'https://www.justice.gov/news',
                  'https://www.wsj.com/news/latest-headlines?mod=nav_top_section',
                  'https://www.wsj.com/tech/openai-elon-musk-mark-zuckerberg-meta-be2ee198',
                  'https://www.bloomberg.com/latest?utm_source=homepage&utm_medium=web&utm_campaign=latest',
                  'https://www.bloomberg.com/news/articles/2025-08-21/trump-aims-to-win-majority-on-fed-board-with-attempt-to-oust-lisa-cook?srnd=phx-economics-v2',
                  'https://www.producthunt.com/products/qoder',
                  'https://www.producthunt.com/products/lumi-new-2',
                  'https://www.producthunt.com/products/jogg-ai/launches/joggai-avatarx',
                  'https://mp.weixin.qq.com/s/WY1sDXV41ABrJWtLj0v6EA'
                  ]


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

async def rss(sites: list):
    for site in sites:
        articles, markdown, link_dict = await fetch_rss(site)
        if articles:
            for i, a in enumerate(articles): 
                record_file = os.path.join(save_dir, f"{hashlib.sha256(site.encode()).hexdigest()[-6:]}_{i}.json")
                with open(record_file, 'w', encoding='utf-8') as f:
                    json.dump(a.model_dump(), f, indent=4, ensure_ascii=False)
                print(f'saved to {record_file}')
        elif markdown:
            print(f'markdown: \n{markdown}')
            record_file = os.path.join(save_dir, f"{hashlib.sha256(site.encode()).hexdigest()[-6:]}_processed.json")
            result = {
                'url': site,
                'markdown': markdown,
                'link_dict': link_dict,
                'title': "",
                'author': "",
                'published_date': ""
            }
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            print(f'\nsaved to {record_file}\n')
        else:
            print(f'fetching {site} failed or no result')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sites', '-S', type=str, default='')
    parser.add_argument('--mode', '-M', type=str, default='web')
    parser.add_argument('--save_dir', '-D', type=str, default=save_dir)
    args = parser.parse_args()

    sites = [site.strip() for site in args.sites.split(',')] if args.sites else standard_sites

    save_dir = args.save_dir
    os.makedirs(save_dir, exist_ok=True)
    if args.mode == 'rss':
        asyncio.run(rss(sites))
    else:
        asyncio.run(main(sites))
