# -*- coding: utf-8 -*-
import asyncio
import os
import random
import json
import sys

root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(root_path)
from core.wis.kuaishou import KuaiShouCrawler


save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webpage_samples')

async def main(keywords: list, existings: set[str] = set(), limit_hours: int = 48, creator_ids: set[str] = set()):
    crawler = KuaiShouCrawler()
    try:
        await crawler.async_initialize()
    except Exception as e:
        print(e)
        return
    albums, posts = await crawler.get_new_videos(keywords=keywords, creator_ids=creator_ids, existings=existings, limit_hours=limit_hours)
    print(albums)
    albums_json = {
        "markdown": albums,
        "link_dict": posts
    }
    with open(os.path.join(save_dir, 'albums.json'), 'w', encoding='utf-8') as f:
        json.dump(albums_json, f, ensure_ascii=False, indent=4)

    # 从 posts 的值中随机选择一个
    post_values = list(posts.values())
    if post_values:
        selected_video = random.choice(post_values)
    else:
        print("\n--- No videos found in posts to select from ---")
        return
    
    article, ref = await crawler.get_video_as_article(selected_video)
    print(article)
    print(ref)
    creator_info = await crawler.get_creators_info(selected_video.get("user_id"))
    print(creator_info)
    article_json = {
        "article": article,
        "ref": ref,
        "creator_info": creator_info
    }
    with open(os.path.join(save_dir, 'article.json'), 'w', encoding='utf-8') as f:
        json.dump(article_json, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--keywords', '-K', type=str, default='')
    parser.add_argument('--creator_ids', '-C', type=str, default='')
    parser.add_argument('--save_dir', '-D', type=str, default=save_dir)
    args = parser.parse_args()

    keywords = [keyword.strip() for keyword in args.keywords.split(',')] if args.keywords else []
    creator_ids = {creator_id.strip() for creator_id in args.creator_ids.split(',')} if args.creator_ids else set()

    save_dir = args.save_dir
    os.makedirs(save_dir, exist_ok=True)

    asyncio.run(main(keywords=keywords, creator_ids=creator_ids))
