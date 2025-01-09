# -*- coding: utf-8 -*-
import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
import os
import hashlib
import json


save_dir = 'webpage_samples'

md_generator = DefaultMarkdownGenerator(
        options={
            "skip_internal_links": True,
            "escape_html": True
        }
    )

crawler_config = CrawlerRunConfig(delay_before_return_html=2.0, markdown_generator=md_generator,
                                wait_until='commit', magic=True, scan_full_page=True,
                                cache_mode=CacheMode.BYPASS)


async def main(sites: list):
    async with AsyncWebCrawler(headless=True, verbose=True) as crawler:
        for site in sites:
            result = await crawler.arun(url=site, config=crawler_config)
            if not result or not result.success:
                print(f'{site} failed to crawl, skip')
                continue
            
            print('raw_markdown:')
            print(result.markdown_v2.raw_markdown)
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
