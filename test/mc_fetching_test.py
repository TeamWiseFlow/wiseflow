# -*- coding: utf-8 -*-
import asyncio
import os
import hashlib
import json
import sys

root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(root_path)
from core.wis import AsyncWebCrawler, CacheMode
from core.crawler_configs import default_browser_config, default_crawler_config
from core.async_database import init_database, cleanup_database

save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webpage_samples')

async def main(sites: list):
        # 爬取类型，search(关键词搜索) | detail(帖子详情)| creator(创作者主页数据) | homefeed(首页推荐)
"search":
            # Search for videos and retrieve their comment information.
            await self.search()
 "detail":
            # Get the information and comments of the specified post
            await self.get_specified_videos()
"creator":
            # Get creator's information and their videos and comments
            await self.get_creators_and_videos()
 "homefeed":
            await self.get_homefeed_videos()



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
