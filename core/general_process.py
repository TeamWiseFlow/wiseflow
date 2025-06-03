# -*- coding: utf-8 -*-
from async_database import db_manager, init_database, cleanup_database
from async_logger import wis_logger, base_directory
from typing import List, Dict, Tuple
from tools.general_utils import extract_and_convert_dates, is_chinese, isURL
from wis.utils import get_base_domain
import time, pickle
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
    WeixinArticleMarkdownGenerator,
    markdown_generation_hub,
    DefaultMarkdownGenerator,
    ExtractionStrategy,
    NoExtractionStrategy,
    LLMExtractionStrategy,
    JsonCssExtractionStrategy,
    JsonXPathExtractionStrategy,
    JsonLxmlExtractionStrategy,
    RegexExtractionStrategy,
    ChunkingStrategy,
    RegexChunking,
    IdentityChunking,
    MaxLengthChunking,
    CrawlResult,
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

def get_existings_for_focus(focus_id: str) -> dict:
    visited_record_dir = os.path.join(base_directory, ".wis", "visited_record", focus_id)
    if not os.path.exists(visited_record_dir):
        os.makedirs(visited_record_dir, exist_ok=True)
        return {"web": set(), KUAISHOU_PLATFORM_NAME: set(), WEIBO_PLATFORM_NAME: set()}
    
    existings = {}
    for name in ["web", KUAISHOU_PLATFORM_NAME, WEIBO_PLATFORM_NAME]:
        file_path = os.path.join(visited_record_dir, f"{name}.pkl")
        if not os.path.exists(file_path):
            continue
        with open(file_path, "rb") as f:
            existings[name] = pickle.load(f)

    return existings


def scrap_article(article: CrawlResult, extractor: ExtractionStrategy = None, chunking: ChunkingStrategy = None) -> Tuple[bool, List[Dict]]:
    article_updated = False
    url = article.url
    html = article.html
    cleaned_html = article.cleaned_html
    markdown = article.markdown
    link_dict = article.link_dict
    metadata = article.metadata
  
    if not extractor or isinstance(extractor, NoExtractionStrategy):
        return article_updated, []

    t1 = time.perf_counter()
    if not isinstance(extractor, LLMExtractionStrategy):
        # Choose content based on input_format
        content_format = extractor.input_format
        if content_format in ["fit_html", "cleaned_html"]:
            content = cleaned_html
        else:
            content = html

        chunking = chunking or IdentityChunking()
        sections = chunking.chunk(content)
        extracted_content = extractor.run(url, sections)

        # Log extraction completion
        wis_logger.debug(f"[EXTRACT] {url:.30}... | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
        return article_updated, extracted_content
        
    # if use LLMExtractionStrategy, then we need to generate markdown
    if not markdown:
        domain = get_base_domain(url)
        markdown_generator = markdown_generation_hub.get(domain, DefaultMarkdownGenerator)()
        error_msg, title, author, publish, markdown, link_dict = markdown_generator.generate_markdown(
            raw_html=html,
            cleaned_html=cleaned_html,
            base_url=url,
            metadata=metadata,
        )
        if error_msg:
            wis_logger.error(f"[HTML TO MARKDOWN] FAILED {url}\n{error_msg}")
            return article_updated, []
        
        wis_logger.debug(f"[HTML TO MARKDOWN] {url:.30}... | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
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
    wis_logger.debug(f"[EXTRACT] {url:.30}... | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
    return article_updated, extracted_content


async def main_process(focus: dict, sources: list):
    # 0. prepare the work
    wis_logger.debug('new task initializing...')
    focus_id = focus["id"]
    focuspoint = focus["focuspoint"].strip()
    restrictions = focus["restrictions"].strip() if focus["restrictions"] else ''

    # TODO: use a llm to generate the query
    query = focus['keywords']
    search = focus['search_engine']
    if search:
        query = [query.strip()] if query else [focuspoint]
    else:
        query = []

    wis_logger.debug(f'focus_id: {focus_id}, focus_point: {focuspoint}, restrictions: {restrictions}, search mode: {search} with keywords: {query}')

    if not db_manager.ready:
        await init_database()

    existings = get_existings_for_focus(focus_id)

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
                wis_logger.warning(f"unvalid kuaishou source {source['id']}: has no keywords and no creators, skip")
                continue

            ks_crawler = KuaiShouCrawler()
            try:
                await ks_crawler.async_initialize()
                kwags = {"keywords": query, "existings": existings[KUAISHOU_PLATFORM_NAME], "creator_ids": creator_ids}
                tasks.add(wrap_task(ks_crawler.posts_list(**kwags), (KUAISHOU_PLATFORM_NAME, KUAISHOU_PLATFORM_NAME)))
            except Exception as e:
                wis_logger.error(f"initialize kuaishou crawler failed: {e}, will abort all the sources for kuaishou platform")
                
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
                wis_logger.warning(f"unvalid weibo source {source['id']}: has no keywords and no creators, skip")

            wb_crawler = WeiboCrawler()
            try:
                await wb_crawler.async_initialize()
                kwags = {"keywords": query, "existings": existings[WEIBO_PLATFORM_NAME], "creator_ids": creator_ids}
                tasks.add(wrap_task(wb_crawler.posts_list(**kwags), (WEIBO_PLATFORM_NAME, WEIBO_PLATFORM_NAME)))
            except Exception as e:
                wis_logger.error(f"initialize weibo crawler failed: {e}, will abort all the sources for weibo platform")

        elif source['type'] == 'web':
            if not source.get('url'):
                wis_logger.warning(f"unvalid web source {source['id']}: has no url, skip")
                continue
            if source['url'] not in existings['web'] and isURL(source['url']):
                to_crawl_urls.add(source['url'])
        else:
            wis_logger.warning(f"unvalid source {source['id']}: has no type, skip")
            continue

    if search:
        tasks.add(wrap_task(search_with_jina(query[0]), ('search', 'Jina Search Engine')))
    
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
                    await db_manager.cache_url(result)
            if markdown:
                wis_logger.debug(f'get {len(link_dict)} articles, add to posts list')
                posts.append((markdown, link_dict, 'web'))

        elif task_type == 'search':
            markdown, link_dict = result
            wis_logger.debug(f'get {len(link_dict)} items, add to posts list')
            posts.append((markdown, link_dict, 'web'))

        else:
            markdown, link_dict = result
            wis_logger.debug(f'get {len(link_dict)} items, add to posts list')
            posts.append((markdown, link_dict, source_name))

    # save the existings
    # 这里先验证下，是否 existings 符合预期被更新了
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
    with ThreadPoolExecutor(max_workers=min(int(os.getenv("CONCURRENT_NUMBER", 12)), len(posts))) as executor:
        futures = [executor.submit(wrap_post_task(post)) for post in posts]
        for future in as_completed(futures):
            source_name, result = future.result()
            if source_name == 'web':
                for more in result:
                    to_crawl_urls.update(more['links'])
            elif source_name == WEIBO_PLATFORM_NAME:
                for more in result:
                    for note in more['links']:
                        tasks.add(asyncio.create_task(wb_crawler.post_as_article(note, db_manager)))
            elif source_name == KUAISHOU_PLATFORM_NAME:
                for more in result:
                    for video in more['links']:
                        tasks.add(asyncio.create_task(ks_crawler.video_as_article(video, db_manager)))

    for coro in asyncio.as_completed(tasks):
        article = await coro
        if article:
            to_scrap_articles.append(article)

    wis_logger.debug(f"Posts from sources fetching finished, time cost: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")

    # 3. tik-tok style processing: 
    # use multiple threads to scrape the articles -- get more related urls add to to_crawl_urls...
    # use asyncio loop to crawl the urls -- get articles -- add to to_scrap_articles...
    loop_counter = 0
    while to_scrap_articles:
        loop_counter += 1
        wis_logger.debug(f"loop {loop_counter} starting...")
        t1 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=min(int(os.getenv("CONCURRENT_NUMBER", 12)), len(to_scrap_articles))) as executor:
            futures = [executor.submit(scrap_article, article, extractor, chunking) for article in to_scrap_articles]
            for future in as_completed(futures):
                article_updated, results = future.result()
                if article_updated:
                    await db_manager.cache_url(article)
                for result in results:
                    print(result['infos'])
                    to_crawl_urls.update(result['links'])
        wis_logger.debug(f"loop {loop_counter} scraping stage finished, time cost: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")

        if not to_crawl_urls:
            wis_logger.debug(f"loop {loop_counter} no more urls to crawl, finished")
            continue
            
        t1 = time.perf_counter()
        # for each loop we use a new context for better memory usage and avoid potiential problems
        async with AsyncWebCrawler(config=default_browser_config, verbose=os.getenv("VERBOSE", "False")) as crawler:
            async for result in await crawler.arun_many(to_crawl_urls, crawler_config):
                if result.success:
                    to_scrap_articles.append(result)
                else:
                    wis_logger.warning(f'{result.url} failed to crawl')
        wis_logger.debug(f"loop {loop_counter} crawling stage finished, time cost: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")


if __name__ == "__main__":
    import asyncio
    async def main():
        await init_database()
        focus_points_data = await db_manager.get_activated_focus_points_with_sources()
        tasks = set()
        for focus in focus_points_data:
            if not focus.get('sources'):
                continue
            tasks.add(asyncio.create_task(main_process(focus['focus_point'], focus['sources'])))
        await asyncio.gather(*tasks)
        await cleanup_database()
    asyncio.run(main())



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