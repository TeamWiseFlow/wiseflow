# -*- coding: utf-8 -*-
from async_logger import wis_logger, base_directory
from typing import Dict, Tuple
import time, pickle
import asyncio
from custom_processes import *
from tools.github_search import search_with_github
from tools.rss_parsor import fetch_rss
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from wis import (
    LLMExtractionStrategy,
    KUAISHOU_PLATFORM_NAME,
    WEIBO_PLATFORM_NAME,
    MaxLengthChunking,
    DefaultMarkdownGenerator,
    WeixinArticleMarkdownGenerator,
    ExtractionStrategy,
    NoExtractionStrategy,
    LLMExtractionStrategy,
    ChunkingStrategy,
    IdentityChunking,
    MaxLengthChunking,
    CrawlResult,
    search_with_engine
)
from wis.config import MAX_URLS_PER_TASK, EXCLUDE_EXTERNAL_LINKS
from tools.general_utils import Recorder


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
        # wis_logger.debug(f"Saved {len(data)} items for platform '{platform_name}' to {file_path}")
    
    # Use thread pool to save data concurrently
    with ThreadPoolExecutor(max_workers=len(existings)) as executor:
        futures = []
        for platform_name, data in existings.items():
            if isinstance(data, set):
                future = executor.submit(save_platform_data, platform_name, data)
                futures.append(future)
            else:
                wis_logger.warning(f"Skipping platform '{platform_name}' for focus {focus_id}: data is not a set")
        
        # Wait for all tasks to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                wis_logger.error(f" ✗ Error saving platform data for focus {focus_id}: {e}")

def scrap_article(article: CrawlResult, 
                  extractor: ExtractionStrategy = None, 
                  chunking: ChunkingStrategy = None) -> Tuple[CrawlResult, bool, Dict]:
    
    article_updated = False
    url = article.url
    html = article.html
    cleaned_html = article.cleaned_html
    markdown = article.markdown
    link_dict = article.link_dict
    metadata = article.metadata
  
    if not extractor or isinstance(extractor, NoExtractionStrategy):
        return article, article_updated, {'infos': [], 'links': set()}

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
            return article, article_updated, {'infos': [], 'links': set()}

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
            return article, article_updated, {'infos': [], 'links': set()}
        
        if "mp.weixin.qq.com" in url:
            markdown_generator = WeixinArticleMarkdownGenerator()
        else:
            markdown_generator = DefaultMarkdownGenerator()
        error_msg, title, author, publish, markdown, link_dict = markdown_generator.generate_markdown(
            raw_html=html,
            cleaned_html=cleaned_html,
            base_url=url,
            metadata=metadata,
        )
        if error_msg:
            wis_logger.error(f"[HTML TO MARKDOWN] ✗ {url}\n{error_msg}")
            return article, article_updated, {'infos': [], 'links': set()}
        
        wis_logger.debug(f"[HTML TO MARKDOWN] ✓ {url:.30}... | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
        if not article.title or "mp.weixin.qq.com" in url:
            article.title = title
        if not article.author or "mp.weixin.qq.com" in url:
            article.author = author
        if not article.publish_date or "mp.weixin.qq.com" in url:
            article.publish_date = publish
        article.link_dict = link_dict
        article.markdown = markdown
        article_updated = True

    t1 = time.perf_counter()
    if not chunking:
        chunking = MaxLengthChunking()
    sections = chunking.chunk(article.markdown)
    mode = 'both' if article.link_dict else 'only_info'
    if EXCLUDE_EXTERNAL_LINKS and "mp.weixin.qq.com" in url:
        # for weixin article, artilces from different creators share same domain but should be excluded here (even fetching will cause risk control)
        mode = 'only_info'
    extracted_content = extractor.run(sections=sections,
                                      url=url,
                                      title=article.title,
                                      author=article.author,
                                      publish_date=article.publish_date,
                                      mode=mode,
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
    role = focus["role"].strip() if focus["role"] else ''
    purpose = focus["purpose"].strip() if focus["purpose"] else ''
    search = focus['search']
    wis_logger.debug(f'focus_id: {focus_id}, focus_point: {focuspoint}, search with: {search}')

    existings = get_existings_for_focus(focus_id)
    recorder = Recorder(focus_id=focuspoint, max_urls_per_task=MAX_URLS_PER_TASK)

    custom_table = focus.get('custom_table').strip() if focus.get('custom_table') else None
    if custom_table:
        schema = await db_manager.get_custom_table_schema(custom_table)
        if not schema:
            wis_logger.warning(f"focus {focus_id} 's custom table {custom_table}, can not get schema, skip")
            return
    else:
        schema = None

    extractor = LLMExtractionStrategy(
        focuspoint=focuspoint,
        restrictions=restrictions,
        explanation=explanation,
        role=role,
        purpose=purpose,
        schema=schema,
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

    for search_source in search:
        if search_source == 'wb':
            sources.append({'type': WEIBO_PLATFORM_NAME, 'query': {focuspoint}})
        elif search_source == 'ks':
            sources.append({'type': KUAISHOU_PLATFORM_NAME, 'query': {focuspoint}})
        elif search_source == 'github':
            tasks.add(wrap_task(search_with_github(focuspoint, existings['web']), ('posts', 'github')))
        elif search_source in ['bing', 'arxiv'] and crawlers.get('web'):
            tasks.add(wrap_task(search_with_engine(search_source, focuspoint, crawlers['web'], existings['web']),
                                ('article_or_posts', search_source)))
        else:
            wis_logger.warning(f"focus {focus_id} has unvalid search source {search_source}, skip")

    for source in sources:
        if source['type'] == 'rss':
            if not source.get('url'):
                wis_logger.warning(f"focus {focus_id} has unvalid rss source {source['id']}: has no url, skip")
                continue
            tasks.add(wrap_task(fetch_rss(source['url'], existings['web']), ('article_or_posts', 'rss')))
            recorder.rss_source += 1
        
        elif source['type'] == 'web':
            if not source.get('url'):
                wis_logger.warning(f"focus {focus_id} has unvalid web source {source['id']}: has no url, skip")
                continue
            # source website always be added to url_queue
            recorder.add_url(source['url'], 'web')
            recorder.web_source += 1

        elif source['type'] in [KUAISHOU_PLATFORM_NAME, WEIBO_PLATFORM_NAME]:
            if not crawlers.get(source['type']):
                wis_logger.info(f"focus {focus_id} got {source['type']} source, but no valid crawler, skip")
                continue

            query = source.get('query', set())
            task_type = 'posts'
            creators = source.get('creators', '') or ''
            creators = creators.strip()
            if not creators:
                creator_ids = []
            elif creators == '?' or creators == '？':
                creator_ids = ["homefeed"]
                query.add(focuspoint)
                task_type = 'creator'
            elif ',' in creators:
                creator_ids = [_id.strip() for _id in creators.split(',')]
            elif '，' in creators:
                creator_ids = [_id.strip() for _id in creators.split('，')]
            else:
                creator_ids = [creators]
            
            if not query and not creator_ids:
                continue

            kwags = {"keywords": query, "existings": existings[source['type']], "creator_ids": creator_ids}
            tasks.add(wrap_task(crawlers[source['type']].posts_list(**kwags), (task_type, source['type'])))
        
        else:
            wis_logger.warning(f"focus {focus_id} has unvalid source{source['id']}: {source['type']}, skip")
            continue
    
    posts = []
    t1 = time.perf_counter()
    for coro in asyncio.as_completed(tasks):
        (task_type, source_name), result = await coro
        if task_type == 'article_or_posts':
            results, markdown, link_dict = result
            if results:
                recorder.article_queue.extend(results)
                recorder.processed_urls.update({result.url for result in results})
                if source_name not in recorder.item_source:
                    recorder.item_source[source_name] = 0
                recorder.item_source[source_name] += len(results)
                for result in results:
                    await db_manager.cache_url(result)
        else:
            markdown, link_dict = result
        
        if markdown and link_dict:
            wis_logger.debug(f'from {source_name} get {len(link_dict)} posts for focus {focus_id}, need to be extracted further...')
            posts.append((markdown, link_dict, source_name, task_type))
            if source_name not in recorder.mc_count:
                recorder.mc_count[source_name] = 0
            recorder.mc_count[source_name] += len(link_dict)
    
    # 2. fetching mediacrawler posts and analyzing search engine results
    chunking = MaxLengthChunking()
    def wrap_post_task(post):
        def wrapper():
            markdown, link_dict, source_name, task_type = post
            sections = chunking.chunk(markdown)
            result = extractor.run(sections=sections, mode='only_link', link_dict=link_dict)
            all_urls = set(link_dict.values())
            return source_name, result['links'], all_urls - result['links'], task_type
        return wrapper

    if posts:
        tasks = set()
        with ThreadPoolExecutor(max_workers=min(int(os.getenv("CONCURRENT_NUMBER", 12)), len(posts))) as executor:
            futures = [executor.submit(wrap_post_task(post)) for post in posts]
            for future in as_completed(futures):
                try:
                    source_name, related_urls, un_related_urls, task_type = future.result()
                    # for weibo platform
                    if source_name == WEIBO_PLATFORM_NAME:
                        existings[source_name].update(un_related_urls)
                        for note in related_urls:
                            if task_type == 'creator':
                                note_cache = await db_manager.get_wb_cache(note_id=note)
                                if note_cache and note_cache[0]['user_id'] and note_cache[0]['profile_url']:
                                    _url = note_cache[0]['profile_url']
                                    if _url in existings['web'] or _url in recorder.processed_urls:
                                        continue
                                    tasks.add(asyncio.create_task(crawlers[WEIBO_PLATFORM_NAME].as_creator(note_cache[0]['user_id'], note_cache[0]['profile_url'])))
                                else:
                                    wis_logger.warning(f"can not get valid note info for note_id:{note}, so can not crawl creator info")
                                    continue
                            else:
                                _url = f"https://m.weibo.cn/detail/{note}"
                                if _url in existings['web'] or _url in recorder.processed_urls:
                                    continue
                                tasks.add(asyncio.create_task(crawlers[WEIBO_PLATFORM_NAME].as_article(note)))
                            recorder.processed_urls.add(_url)
                            if 'wb' not in recorder.item_source:
                                recorder.item_source['wb'] = 0
                            recorder.item_source['wb'] += 1
                            await asyncio.sleep(1)
                    # for kuaishou platform
                    elif source_name == KUAISHOU_PLATFORM_NAME:
                        existings[KUAISHOU_PLATFORM_NAME].update(un_related_urls)
                        for video in related_urls:
                            if task_type == 'creator':
                                video_cache = await crawlers[KUAISHOU_PLATFORM_NAME].get_specified_video(video)
                                if video_cache and video_cache['user_id']:
                                    _url = f"https://www.kuaishou.com/profile/{video_cache['user_id']}"
                                    if _url in existings['web'] or _url in recorder.processed_urls:
                                        continue
                                    tasks.add(asyncio.create_task(crawlers[KUAISHOU_PLATFORM_NAME].as_creator(video_cache['user_id'])))
                                else:
                                    wis_logger.warning(f"can not get valid video info for video_id:{video}, so can not crawl creator info")
                                    continue
                            else:
                                _url = f"https://www.kuaishou.com/short-video/{video}"
                                if _url in existings['web'] or _url in recorder.processed_urls:
                                    continue
                                tasks.add(asyncio.create_task(crawlers[KUAISHOU_PLATFORM_NAME].as_article(video)))
                            recorder.processed_urls.add(_url)
                            if 'ks' not in recorder.item_source:
                                recorder.item_source['ks'] = 0
                            recorder.item_source['ks'] += 1
                            # it seems that kuaishou can afford more requests per second...
                            # await asyncio.sleep(1)
                    else:
                        recorder.add_url(related_urls - existings['web'], source_name)
                        existings['web'].update(un_related_urls)
                except Exception as e:
                    wis_logger.error(f"Error Extracting Post List: {e}")
                    continue

        save_existings_for_focus(focus_id, existings)

        for coro in asyncio.as_completed(tasks):
            article = await coro
            if article:
                recorder.article_queue.append(article)
            else:
                recorder.crawl_failed += 1
                recorder.total_processed += 1

    wis_logger.debug(f"[SOURCE FINDING] ✓ finished for focus {focus_id}, time cost: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
    wis_logger.info(f"\n{recorder.source_summary()}\n")
    
    # 3. tik-tok style processing: 
    # use multiple threads to scrape the articles -- get more related urls add to to_crawl_urls...
    # use asyncio loop to crawl the urls -- get articles -- add to to_scrap_articles..
    while not recorder.finished():
        if recorder.article_queue:
            t1 = time.perf_counter()
            with ThreadPoolExecutor(max_workers=min(int(os.getenv("CONCURRENT_NUMBER", 12)), len(recorder.article_queue))) as executor:
                futures = [executor.submit(scrap_article, article, extractor, chunking) for article in recorder.article_queue]
                # processed_urls = set()  # 收集成功处理的 URL
                for future in as_completed(futures):
                    recorder.total_processed += 1
                    try:
                        article, article_updated, result = future.result()
                        # processed_urls.add(article.url)  # 记录成功处理的 URL
                        if article_updated:
                            await db_manager.cache_url(article)
                        recorder.add_url(result['links'] - existings['web'], 'article')
                        for info in result['infos']:
                            if custom_table:
                                await db_manager.add_custom_info(custom_table=custom_table, focuspoint_id=focus_id, source=article.url, info=info)
                            else:
                                await db_manager.add_info(focuspoint_id=focus_id, **info)
                            recorder.info_added += 1
                        existings['web'].add(article.url)
                        if article.redirected_url:
                            existings['web'].add(article.redirected_url)
                        recorder.successed += 1
                    except Exception as e:
                        wis_logger.error(f"[EXTRACT] ✗ failed to process article: {e}")
                        recorder.scrap_failed += 1
                        continue

            save_existings_for_focus(focus_id, existings)
            # 只保留未成功处理的 articles，失败的会在下次循环重试
            recorder.article_queue = []
            wis_logger.debug(f"[BATCH SCRAPING] ✓ finished for focus {focus_id}, time cost: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")

        if recorder.url_queue:
            wis_logger.debug(f"focus {focus_id} still have {len(recorder.url_queue)} urls to crawl")
            if crawlers.get('web'):
                async for result in await crawlers['web'].arun_many(list(recorder.url_queue)):
                    if result and result.success:
                        recorder.article_queue.append(result)
                    else:
                        recorder.crawl_failed += 1
                        recorder.total_processed += 1
            else:
                wis_logger.debug("'cause web crawler is not initialized, so we have to skip the batch scraping...")

            recorder.processed_urls.update(recorder.url_queue)
            recorder.url_queue.clear()

        wis_logger.info(f"\n{recorder.scrap_summary()}\n")
        extractor.show_usage()
        wis_logger.debug("========================================")
