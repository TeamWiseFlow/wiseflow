# -*- coding: utf-8 -*-
from async_database import base_directory, wis_logger, db_manager
from tools.general_utils import extract_and_convert_dates, is_chinese, isURL
import time
import regex as re
import asyncio
from crawler_configs import *
from tools.jina_search import search_with_jina
from datetime import datetime
from tools.rss_parsor import fetch_rss
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from wis import (
    AsyncWebCrawler,
    LLMExtractionStrategy,
    KUAISHOU_PLATFORM_NAME,
    WEIBO_PLATFORM_NAME,
    KuaiShouCrawler,
    WeiboCrawler,
    MaxLengthChunking,
    WeiboSearchType
)



"""
async def info_process(url: str, 
                       url_title: str, 
                       author: str, 
                       publish_date: str, 
                       contents: list[str], 
                       link_dict: dict, 
                       focus_id: str,
                       get_info_prompts: list[str]):
    wis_logger.debug('info summarising by llm...')

    for info in infos:
        info['url'] = url
        info['url_title'] = url_title
        info['tag'] = focus_id
        _ = pb.add(collection_name='infos', body=info)
"""

async def main_process(focus: dict, sites: list, platforms: dict):
    # 0. prepare the work
    wis_logger.debug('new task initializing...')
    focus_id = focus["id"]
    focuspoint = focus["focuspoint"].strip()
    restrictions = focus["restrictions"].strip() if focus["restrictions"] else ''
    # TODO: use a llm to generate the query
    query = focuspoint if not restrictions else f"{focuspoint}({restrictions})"

    wis_logger.debug(f'focus_id: {focus_id}, focus_point: {focuspoint}, restrictions: {restrictions}, search_engine: {focus["search_engine"]}')
    # TODO: read from the database
    # existing_urls = {url['url'] for url in db_manager.get_cached_url(url=url, days_threshold=30)}
    existing_urls = set()
    to_crawl_urls = set()
    extractor = LLMExtractionStrategy(
        focus_point=focuspoint,
        restrictions=restrictions,
        verbose=os.getenv("VERBOSE", "False"),
        logger=wis_logger
    )

    # 1. get the posts list from the sources (to parse more related urls)
    tasks = set()
    def wrap_task(coro, meta):
        async def wrapper():
            result = await coro
            return meta, result
        return asyncio.create_task(wrapper())
    # Add RSS feed tasks
    for site in sites:
        if site.get('type', 'web') == 'rss':
            tasks.add(wrap_task(fetch_rss(site['url']), ('rss', site['url'])))
        else:
            if site['url'] not in existing_urls and isURL(site['url']):
                to_crawl_urls.add(site['url'])
    
    # Add Kuaishou tasks
    if KUAISHOU_PLATFORM_NAME in platforms:
        ks_crawler = KuaiShouCrawler()
        try:
            await ks_crawler.async_initialize()
            if focus.get('search_engine', False):
                kwags = {"keywords": [query], "existings": existing_urls, **platforms[KUAISHOU_PLATFORM_NAME]}
            else:
                kwags = {"existings": existing_urls, **platforms[KUAISHOU_PLATFORM_NAME]}
            tasks.add(wrap_task(ks_crawler.posts_list(**kwags), (KUAISHOU_PLATFORM_NAME, KUAISHOU_PLATFORM_NAME)))
        except Exception as e:
            wis_logger.error(f"initialize kuaishou crawler failed: {e}, will abort all the sources for kuaishou platform")
            
    # Add Weibo tasks
    if WEIBO_PLATFORM_NAME in platforms:
        wb_crawler = WeiboCrawler()
        try:
            await wb_crawler.async_initialize()
            if focus.get('search_engine', False):
                kwags = {"keywords": [query], "existings": existing_urls, **platforms[WEIBO_PLATFORM_NAME]}
            else:
                kwags = {"existings": existing_urls, **platforms[WEIBO_PLATFORM_NAME]}
            tasks.add(wrap_task(wb_crawler.posts_list(**kwags), (WEIBO_PLATFORM_NAME, WEIBO_PLATFORM_NAME)))
        except Exception as e:
            wis_logger.error(f"initialize weibo crawler failed: {e}, will abort all the sources for weibo platform")

    # Add search engine task
    if focus.get('search_engine', False):
        tasks.add(wrap_task(search_with_jina(query), ('search', 'Jina Search Engine')))
    
    to_scrap_articles = []
    posts = []
    t1 = time.perf_counter()
    # 使用 as_completed 并发执行所有任务
    for coro in asyncio.as_completed(tasks):
        (task_type, source_name), result = await coro
        wis_logger.debug(f'from {task_type} source: {source_name}')
        if task_type == 'rss':
            results, markdown, link_dict = result
            if results:
                wis_logger.debug(f'get {len(results)} articles, add to to_scrap_articles')
                to_scrap_articles.extend(results)
                for result in results:
                    print(result)
                    print('-'*100)
            if markdown:
                wis_logger.debug(f'get {len(link_dict)} articles, add to posts list')
                posts.append((markdown, link_dict, 'web'))
                # TODO: LLM extract the posts
        elif task_type == 'search':
            markdown, link_dict = result
            wis_logger.debug(f'get {len(link_dict)} items, add to posts list')
            posts.append((markdown, link_dict, 'web'))
            # TODO: LLM extract the posts
        else:
            markdown, link_dict = result
            wis_logger.debug(f'get {len(link_dict)} items, add to posts list')
            posts.append((markdown, link_dict, source_name))
            # TODO: LLM extract the posts
    
    wis_logger.debug(f"scource parsing finished, time cost: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
    
    # 2. fetching mediacrawler posts and analyzing search engine results
    chunking = MaxLengthChunking()
    def wrap_post_task(post):
        def wrapper():
            markdown, link_dict, source_name = post
            sections = chunking.chunk(markdown)
            result = extractor.run(sections=sections, mode='only_link', link_dict=link_dict)
            return source_name, result
        return wrapper
        
    t1 = time.perf_counter()
    tasks = set()
    with ThreadPoolExecutor(max_workers=min(os.getenv("CONCURRENT_NUMBER", 12), len(posts))) as executor:
        futures = [executor.submit(wrap_post_task(post)) for post in posts]
        for future in as_completed(futures):
            source_name, result = future.result()
            if source_name == 'web':
                for more in result:
                    to_crawl_urls.update(more['links'])
            elif source_name == WEIBO_PLATFORM_NAME:
                for more in result:
                    for note in more['links']:
                        tasks.add(asyncio.create_task(wb_crawler.post_as_article(note)))
            elif source_name == KUAISHOU_PLATFORM_NAME:
                for more in result:
                    for video in more['links']:
                        tasks.add(asyncio.create_task(ks_crawler.post_as_article(video)))

    for coro in asyncio.as_completed(tasks):
        article = await coro
        if article:
            to_scrap_articles.append(article)

    wis_logger.debug(f"Posts fetching finished, time cost: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")

    # 3. tik-tok style processing: 
    # use multiple threads to scrape the articles -- get more related urls add to to_crawl_urls...
    # use asyncio loop to crawl the urls -- get articles -- add to to_scrap_articles...

    """
    web_crawler = AsyncWebCrawler(config=default_browser_config, verbose=os.getenv("VERBOSE", "False"))
    await web_crawler.start()
    """



if __name__ == "__main__":
    import asyncio
    focus_point = "流行趋势花型设计"
    restrictions = "适用于家纺产业"
    focus = {"id": "1", "focuspoint": focus_point, "restrictions": restrictions, "search_engine": False}
    sites = [{"url": "http://jxjyxy.hunnu.edu.cn/xsxw.htm", "type": "web"}, {"url": "https://www.tmtpost.com/feed", "type": "rss"}]
    platforms = {KUAISHOU_PLATFORM_NAME: {"limit_hours": 48}, 
                 WEIBO_PLATFORM_NAME: {"creator_ids": ("1896456970",), "search_type": WeiboSearchType.DEFAULT, "limit_hours": 48}}
    asyncio.run(main_process(focus, sites, platforms))

    """         
    date_stamp = datetime.now().strftime('%Y-%m-%d')
    working_list = set()

    while working_list:
        url = working_list.pop()
        existing_urls.add(url)
        wiseflow_logger.debug(f'process new url, still {len(working_list)} urls in working list')
        has_common_ext = any(url.lower().endswith(ext) for ext in common_file_exts)
        if has_common_ext:
            wiseflow_logger.debug(f'{url} is a common file, skip')
            continue

        parsed_url = urlparse(url)
        existing_urls.add(f"{parsed_url.scheme}://{parsed_url.netloc}")
        existing_urls.add(f"{parsed_url.scheme}://{parsed_url.netloc}/")
        domain = parsed_url.netloc
            
        crawler_config.cache_mode = CacheMode.WRITE_ONLY if url in sites_urls else CacheMode.ENABLED
        result = await crawler.arun(url=url, config=crawler_config)
        if not result.success:
            wiseflow_logger.warning(f'{url} failed to crawl')
            continue
        metadata_dict = result.metadata if result.metadata else {}

        if domain in custom_scrapers:
            result = custom_scrapers[domain](result)
            raw_markdown = result.content
            used_img = result.images
            title = result.title
            if title == 'maybe a new_type_article':
                wiseflow_logger.warning(f'we found a new type here,{url}\n{result}')
            base_url = result.base
            author = result.author
            publish_date = result.publish_date
        else:
            raw_markdown = result.markdown
            media_dict = result.media if result.media else {}
            used_img = [d['src'] for d in media_dict.get('images', [])]
            title = ''
            base_url = ''
            author = ''
            publish_date = ''
        if not raw_markdown:
            wiseflow_logger.warning(f'{url} no content\n{result}\nskip')
            continue
        wiseflow_logger.debug('data preprocessing...')
        if not title:
            title = metadata_dict.get('title', '')
        if not base_url:
            base_url = metadata_dict.get('base', '')
        if not base_url:
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        if not author:
            author = metadata_dict.get('author', '')
        if not publish_date:
            publish_date = metadata_dict.get('publish_date', '')

        link_dict, links_parts, contents, recognized_img_cache = await pre_process(raw_markdown, base_url, used_img, recognized_img_cache, existing_urls)

        if link_dict and links_parts:
            wiseflow_logger.debug('links_parts exists, more links detecting...')
            links_texts = []
            for _parts in links_parts:
                links_texts.extend(_parts.split('\n\n'))
            more_url = await get_more_related_urls(links_texts, link_dict, get_link_prompts, _logger=wiseflow_logger)
            if more_url:
                wiseflow_logger.debug(f'get {len(more_url)} more related urls, will add to working list')
                working_list.update(more_url - existing_urls)
            
        if not contents:
            continue

        if not author or author.lower() == 'na' or not publish_date or publish_date.lower() == 'na':
            wiseflow_logger.debug('no author or publish date from metadata, will try to get by llm')
            main_content_text = re.sub(r'!\[.*?]\(.*?\)', '', raw_markdown)
            main_content_text = re.sub(r'\[.*?]\(.*?\)', '', main_content_text)
            alt_author, alt_publish_date = await get_author_and_publish_date(main_content_text, model, _logger=wiseflow_logger)
            if not author or author.lower() == 'na':
                author = alt_author if alt_author else parsed_url.netloc
            if not publish_date or publish_date.lower() == 'na':
                publish_date = alt_publish_date if alt_publish_date else ''

        publish_date = extract_and_convert_dates(publish_date)

        await info_process(url, title, author, publish_date, contents, link_dict, focus_id, get_info_prompts)

    await crawler.close()
    wiseflow_logger.debug(f'task finished, focus_id: {focus_id}')
    """  