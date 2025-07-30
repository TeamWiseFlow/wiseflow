# -*- coding: utf-8 -*-
import asyncio
import os
import random
import json
import sys
from datetime import datetime

root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(root_path)
from wis import KuaiShouCrawler, WeiboCrawler, WeiboSearchType, WEIBO_PLATFORM_NAME, KUAISHOU_PLATFORM_NAME


save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webpage_samples')

async def main(keywords: list, 
               existings: set[str] = set(), 
               limit_hours: int = 48, 
               creator_ids: set[str] = set(),
               platform: str = KUAISHOU_PLATFORM_NAME,
               search_type: WeiboSearchType = WeiboSearchType.DEFAULT):
    if platform == KUAISHOU_PLATFORM_NAME:
        crawler = KuaiShouCrawler()
    elif platform == WEIBO_PLATFORM_NAME:
        crawler = WeiboCrawler()
    try:
        await crawler.async_initialize()
    except Exception as e:
        print(e)
        return
    albums, posts = await crawler.posts_list(keywords=keywords, creator_ids=creator_ids, existings=existings)
    print(albums)
    time_stamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    albums_json = {
        "markdown": albums,
        "link_dict": posts
    }
    with open(os.path.join(save_dir, f'{platform}_albums_{time_stamp}.json'), 'w', encoding='utf-8') as f:
        json.dump(albums_json, f, ensure_ascii=False, indent=4)

    # 从 posts 的值中随机选择一个
    post_values = list(posts.values())
    if post_values:
        selected_post = random.choice(post_values)
    else:
        print("\n--- No posts found in posts to select from ---")
        return
    
    article, ref = await crawler.as_article(selected_post)
    print(article)
    print(ref)
    creator_info = await crawler.as_creator(selected_post.get("user_id"))
    print(creator_info)
    article_json = {
        "article": article,
        "ref": ref,
        "creator_info": creator_info
    }
    with open(os.path.join(save_dir, f'{platform}_article_{time_stamp}.json'), 'w', encoding='utf-8') as f:
        json.dump(article_json, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--keywords', '-K', type=str, default='')
    parser.add_argument('--creator_ids', '-C', type=str, default='')
    parser.add_argument('--save_dir', '-D', type=str, default=save_dir)
    parser.add_argument('--platform', '-P', type=str, default=WEIBO_PLATFORM_NAME)
    parser.add_argument('--limit_hours', '-L', type=int, default=48)
    parser.add_argument('--search_type', '-S', type=str, default='default')
    args = parser.parse_args()

    keywords = [keyword.strip() for keyword in args.keywords.split(',')] if args.keywords else []
    creator_ids = {creator_id.strip() for creator_id in args.creator_ids.split(',')} if args.creator_ids else set()

    save_dir = args.save_dir
    os.makedirs(save_dir, exist_ok=True)
    if args.search_type == 'default':
        search_type = WeiboSearchType.DEFAULT
    elif args.search_type == 'real_time':
        search_type = WeiboSearchType.REAL_TIME
    elif args.search_type == 'popular':
        search_type = WeiboSearchType.POPULAR
    elif args.search_type == 'video':
        search_type = WeiboSearchType.VIDEO

    asyncio.run(main(keywords=keywords, creator_ids=creator_ids, platform=args.platform, limit_hours=args.limit_hours, search_type=search_type))
