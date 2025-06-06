# -*- coding: utf-8 -*-
from async_logger import wis_logger, base_directory
from typing import List, Dict, Tuple
from wis.utils import get_base_domain
import time, pickle
import asyncio
from custom_processes import *
from tools.jina_search import search_with_jina
from tools.rss_parsor import fetch_rss
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from wis import (
    AsyncWebCrawler,
    LLMExtractionStrategy,
    KUAISHOU_PLATFORM_NAME,
    WEIBO_PLATFORM_NAME,
    MAX_EPOCH,
    MaxLengthChunking,
    markdown_generation_hub,
    DefaultMarkdownGenerator,
    ExtractionStrategy,
    NoExtractionStrategy,
    LLMExtractionStrategy,
    ChunkingStrategy,
    IdentityChunking,
    MaxLengthChunking,
    CrawlResult,
)
from web_crawler_configs import crawler_config_map


def get_existings_for_focus(focus_id: str) -> dict:
    visited_record_dir = os.path.join(base_directory, ".wis", "visited_record", focus_id)
    if not os.path.exists(visited_record_dir):
        os.makedirs(visited_record_dir, exist_ok=True)
        return {"web": set(), KUAISHOU_PLATFORM_NAME: set(), WEIBO_PLATFORM_NAME: set()}
    
    existings = {}
    for name in ["web", KUAISHOU_PLATFORM_NAME, WEIBO_PLATFORM_NAME]:
        file_path = os.path.join(visited_record_dir, f"{name}.pkl")
        if not os.path.exists(file_path):
            existings[name] = set()
            continue
        with open(file_path, "rb") as f:
            existings[name] = pickle.load(f)

    return existings

def save_existings_for_focus(focus_id: str, existings: dict) -> None:
    """
    Save existings data to local files using thread pool
    
    Args:
        focus_id: The focus ID
        existings: Dictionary containing platform names as keys and sets as values
    """
    if not existings:
        return
    
    visited_record_dir = os.path.join(base_directory, ".wis", "visited_record", focus_id)
    if not os.path.exists(visited_record_dir):
        os.makedirs(visited_record_dir, exist_ok=True)
    
    def save_platform_data(platform_name: str, data: set) -> None:
        """Save data for a single platform"""
        file_path = os.path.join(visited_record_dir, f"{platform_name}.pkl")
        with open(file_path, "wb") as f:
            pickle.dump(data, f)
        wis_logger.debug(f"Saved {len(data)} items for platform '{platform_name}' to {file_path}")
    
    # Use thread pool to save data concurrently
    with ThreadPoolExecutor(max_workers=len(existings)) as executor:
        futures = []
        for platform_name, data in existings.items():
            if isinstance(data, set):
                future = executor.submit(save_platform_data, platform_name, data)
                futures.append(future)
            else:
                wis_logger.warning(f"Skipping platform '{platform_name}': data is not a set")
        
        # Wait for all tasks to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                wis_logger.error(f" ✗ Error saving platform data: {e}")

def scrap_article(article: CrawlResult, 
                  extractor: ExtractionStrategy = None, 
                  chunking: ChunkingStrategy = None) -> Tuple[CrawlResult, bool, List[Dict]]:
    
    article_updated = False
    url = article.url
    html = article.html
    cleaned_html = article.cleaned_html
    markdown = article.markdown
    link_dict = article.link_dict
    metadata = article.metadata
  
    if not extractor or isinstance(extractor, NoExtractionStrategy):
        return article, article_updated, []

    t1 = time.perf_counter()
    if not isinstance(extractor, LLMExtractionStrategy):
        # Choose content based on input_format
        content_format = extractor.input_format
        if content_format in ["fit_html", "cleaned_html"]:
            content = cleaned_html
        else:
            content = html
        
        if not content:
            wis_logger.info(f"{url} has no required content to extract, skip")
            return article, article_updated, []

        chunking = chunking or IdentityChunking()
        sections = chunking.chunk(content)
        extracted_content = extractor.run(url, sections)

        # Log extraction completion
        wis_logger.debug(f"[EXTRACT] ✓ {url:.30}... | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
        return article, article_updated, extracted_content
        
    # if use LLMExtractionStrategy, then we need to generate markdown
    if not markdown:
        if not html and not cleaned_html:
            wis_logger.info(f"{url} has no markdown,cleaned_html or html, skip")
            return article, article_updated, []
        
        domain = get_base_domain(url)
        markdown_generator = markdown_generation_hub.get(domain, DefaultMarkdownGenerator)()
        error_msg, title, author, publish, markdown, link_dict = markdown_generator.generate_markdown(
            raw_html=html,
            cleaned_html=cleaned_html,
            base_url=url,
            metadata=metadata,
        )
        if error_msg:
            wis_logger.error(f"[HTML TO MARKDOWN] ✗ {url}\n{error_msg}")
            return article, article_updated, []
        
        wis_logger.debug(f"[HTML TO MARKDOWN] ✓ {url:.30}... | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
        if not article.title:
            article.title = title
        if not article.author:
            article.author = author
        if not article.publish_date:
            article.publish_date = publish
        article.link_dict = link_dict
        article.markdown = markdown
        article_updated = True

    t1 = time.perf_counter()
    if not chunking:
        chunking = MaxLengthChunking()
    sections = chunking.chunk(article.markdown)
    extracted_content = extractor.run(sections=sections,
                                      url=url,
                                      title=article.title,
                                      author=article.author,
                                      publish_date=article.publish_date,
                                      mode='both' if article.link_dict else 'only_info',
                                      link_dict=article.link_dict)
    wis_logger.debug(f"[EXTRACT] ✓ {url:.30}... | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
    return article, article_updated, extracted_content

async def main_process(focus: dict, sources: list, crawlers: dict = {}, db_manager=None):
    # 0. prepare the work
    focus_id = focus["id"]
    wis_logger.info(f'new task initializing, focus_id: {focus_id}')
    focuspoint = focus["focuspoint"].strip()
    restrictions = focus["restrictions"].strip() if focus["restrictions"] else ''
    explanation = focus["explanation"].strip() if focus["explanation"] else ''
    search = focus['search']
    if search:
        # TODO: use a llm to generate the query
        query = [focuspoint]
    else:
        query = []

    wis_logger.debug(f'focus_id: {focus_id}, focus_point: {focuspoint}, search mode: {search} with keywords: {query}')

    existings = get_existings_for_focus(focus_id)
    
    to_crawl_urls = set()
    extractor = LLMExtractionStrategy(
        focuspoint=focuspoint,
        restrictions=restrictions,
        explanation=explanation,
        verbose=os.getenv("VERBOSE", False),
        logger=wis_logger
    )

    # 1. get the posts list from the sources (to parse more related urls)
    tasks = set()
    def wrap_task(coro, meta):
        async def wrapper():
            result = await coro
            return meta, result
        return asyncio.create_task(wrapper())

    for source in sources:
        if source['type'] == 'rss':
            if not source.get('url'):
                wis_logger.warning(f"unvalid rss source {source['id']}: has no url, skip")
                continue
            tasks.add(wrap_task(fetch_rss(source['url'], existings['web']), ('rss', source['url'])))

        elif source['type'] == KUAISHOU_PLATFORM_NAME:
            creators = source.get('creators', '') or ''
            if not creators:
                creator_ids = []
            elif ',' in creators:
                creator_ids = [_id.strip() for _id in creators.split(',')]
            elif '，' in creators:
                creator_ids = [_id.strip() for _id in creators.split('，')]
            else:
                creator_ids = [creators]
            
            if not search and not creator_ids:
                continue

            if not crawlers[KUAISHOU_PLATFORM_NAME]:
                wis_logger.info(f"got {KUAISHOU_PLATFORM_NAME} source, but no valid crawler, skip")
                continue

            kwags = {"keywords": query, "existings": existings[KUAISHOU_PLATFORM_NAME], "creator_ids": creator_ids}
            tasks.add(wrap_task(crawlers[KUAISHOU_PLATFORM_NAME].posts_list(**kwags), (KUAISHOU_PLATFORM_NAME, KUAISHOU_PLATFORM_NAME)))
                
        elif source['type'] == WEIBO_PLATFORM_NAME:
            creators = source.get('creators', '') or ''
            if not creators:
                creator_ids = []
            elif ',' in creators:
                creator_ids = [_id.strip() for _id in creators.split(',')]
            elif '，' in creators:
                creator_ids = [_id.strip() for _id in creators.split('，')]
            else:
                creator_ids = [creators]

            if not search and not creator_ids:
                continue

            if not crawlers[WEIBO_PLATFORM_NAME]:
                wis_logger.info(f"got {WEIBO_PLATFORM_NAME} source, but no valid crawler, skip")
                continue

            kwags = {"keywords": query, "existings": existings[WEIBO_PLATFORM_NAME], "creator_ids": creator_ids}
            tasks.add(wrap_task(crawlers[WEIBO_PLATFORM_NAME].posts_list(**kwags), (WEIBO_PLATFORM_NAME, WEIBO_PLATFORM_NAME)))

        elif source['type'] == 'web':
            if not source.get('url'):
                wis_logger.warning(f"unvalid web source {source['id']}: has no url, skip")
                continue
            to_crawl_urls.add(source['url'])
        else:
            wis_logger.warning(f"unvalid source {source['id']}: has no type, skip")
            continue
    
    to_scrap_articles = []
    posts = []
    t1 = time.perf_counter()
    # 使用 as_completed 并发执行所有任务
    for coro in asyncio.as_completed(tasks):
        (task_type, source_name), result = await coro
        _from = f'from {task_type} source: {source_name}'
        if task_type == 'rss':
            results, markdown, link_dict = result
            if results:
                wis_logger.debug(f'{_from} get {len(results)} articles, add to to_scrap_articles')
                to_scrap_articles.extend(results)
                for result in results:
                    await db_manager.cache_url(result)
            if markdown:
                wis_logger.debug(f'{_from} get {len(link_dict)} posts, add to posts list')
                posts.append((markdown, link_dict, 'web'))
        else:
            markdown, link_dict = result
            wis_logger.debug(f'{_from} get {len(link_dict)} posts, add to posts list')
            posts.append((markdown, link_dict, source_name))

    wis_logger.debug(f" ✓ scource parsing finished, time cost: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
    
    # 2. fetching mediacrawler posts and analyzing search engine results
    chunking = MaxLengthChunking()
    def wrap_post_task(post):
        def wrapper():
            markdown, link_dict, source_name = post
            sections = chunking.chunk(markdown)
            result = extractor.run(sections=sections, mode='only_link', link_dict=link_dict)
            related_urls = set()
            for more in result:
                related_urls.update(more['links'])
            all_urls = set(link_dict.values())
            return source_name, related_urls, all_urls - related_urls
        return wrapper
        
    t1 = time.perf_counter()
    if posts:
        tasks = set()
        with ThreadPoolExecutor(max_workers=min(int(os.getenv("CONCURRENT_NUMBER", 12)), len(posts))) as executor:
            futures = [executor.submit(wrap_post_task(post)) for post in posts]
            for future in as_completed(futures):
                try:
                    source_name, related_urls, un_related_urls = future.result()
                    if source_name == 'web':
                        to_crawl_urls.update(related_urls - existings['web'])
                        existings['web'].update(un_related_urls)
                    elif source_name == WEIBO_PLATFORM_NAME:
                        existings[WEIBO_PLATFORM_NAME].update(un_related_urls)
                        for note in un_related_urls:
                            if f"https://m.weibo.cn/detail/{note}" in existings['web']:
                                continue
                            tasks.add(asyncio.create_task(crawlers[WEIBO_PLATFORM_NAME].post_as_article(note)))
                    elif source_name == KUAISHOU_PLATFORM_NAME:
                        existings[KUAISHOU_PLATFORM_NAME].update(un_related_urls)
                        for video in un_related_urls:
                            if f"https://www.kuaishou.com/short-video/{video}" in existings['web']:
                                continue
                            tasks.add(asyncio.create_task(crawlers[KUAISHOU_PLATFORM_NAME].video_as_article(video)))
                except Exception as e:
                    wis_logger.error(f"Error Extracting Post List: {e}")
                    continue

        save_existings_for_focus(focus_id, existings)

        for coro in asyncio.as_completed(tasks):
            article = await coro
            if article:
                to_scrap_articles.append(article)
    
    if search:
        search_results = await search_with_jina(query[0], existings['web'])
        if search_results:
            to_crawl_urls.update(search_results - existings['web'])

    wis_logger.debug(f"[SOURCING] ✓ finished, time cost: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")

    # 3. tik-tok style processing: 
    # use multiple threads to scrape the articles -- get more related urls add to to_crawl_urls...
    # use asyncio loop to crawl the urls -- get articles -- add to to_scrap_articles...
    _epoch = 0
    while to_scrap_articles or to_crawl_urls:
        _epoch += 1
        if _epoch > MAX_EPOCH:
            wis_logger.info(f"reach Max Epoch: {MAX_EPOCH}, we have to quit. Still have {len(to_scrap_articles)} articles to extract.")
            break
        wis_logger.info(f"Epoch {_epoch} starting, we have {len(to_scrap_articles)} articles to extract.")
        if to_scrap_articles:
            batch_urls = {article.url for article in to_scrap_articles}
            t1 = time.perf_counter()
            with ThreadPoolExecutor(max_workers=min(int(os.getenv("CONCURRENT_NUMBER", 12)), len(to_scrap_articles))) as executor:
                futures = [executor.submit(scrap_article, article, extractor, chunking) for article in to_scrap_articles]
                processed_urls = set()  # 收集成功处理的 URL
                for future in as_completed(futures):
                    try:
                        article, article_updated, results = future.result()
                        processed_urls.add(article.url)  # 记录成功处理的 URL
                        if article_updated:
                            await db_manager.cache_url(article)
                        for result in results:
                            to_crawl_urls.update(result['links'] - existings['web'] - batch_urls)
                            for info in result['infos']:
                                await db_manager.add_info(focuspoint_id=focus_id, **info)
                        existings['web'].add(article.url)
                        if article.redirected_url:
                            existings['web'].add(article.redirected_url)
                    except Exception as e:
                        wis_logger.error(f" ✗ Error processing article: {e}")
                        continue

            save_existings_for_focus(focus_id, existings)
            # 只保留未成功处理的 articles，失败的会在下次循环重试
            to_scrap_articles = [article for article in to_scrap_articles 
                                if article.url not in processed_urls]
            wis_logger.debug(f"[BATCH SCRAPING] ✓ finished, time cost: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")

        if not to_crawl_urls:
            wis_logger.debug(f"no more urls to crawl, finished")
            continue
        wis_logger.info(f"Epoch {_epoch} web fetching stage starting, we have {len(to_crawl_urls)} urls to crawl")
        # for each loop we use a new context for better memory usage and avoid potiential problems
        async with AsyncWebCrawler(crawler_config_map=crawler_config_map, db_manager=db_manager) as crawler:
            async for result in await crawler.arun_many(list(to_crawl_urls)):
                if result and result.success:
                    to_scrap_articles.append(result)
        to_crawl_urls.clear()

    extractor.show_usage()
