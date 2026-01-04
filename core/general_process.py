# -*- coding: utf-8 -*-
from core.async_logger import wis_logger
import asyncio
from core.custom_processes import *
from core.tools.github_search import search_with_github
from core.tools.rss_parsor import fetch_rss
from core.wis import (
    ExtractManager,
    search_with_engine,
    SqliteCache,
)
from core.async_database import AsyncDatabaseManager
from core.wis.config import config
from core.tools.general_utils import Recorder
from core.wis.ws_connect import notify_user
# from tools.existing_manage import get_existings_for_focus, save_existings_for_focus

def wrap_task(coro, meta):
    async def wrapper():
        try:
            result = await coro
            return meta, True, result  # (meta, success, result)
        except Exception as e:
            return meta, False, str(e)      # (meta, success, exception)
    return asyncio.create_task(wrapper())

# 理论上 general_process 要捕获并处理所有错误，因为这一层都是批处理多个信源，不能因为某个信源的错误就放弃其他信源了，除非是来自用户设置层面的错误，并且这个错误预计下一次执行还会发生，此时设置任务执行状态为 2
# 如果存在着与用户设置相关，但是并不妨碍走下去的错误，应该将错误的 task_error_code 放入 warning_msg 中，然后将任务执行状态 设置为 1
async def main_process(focus: dict, 
                       sources: list[dict],
                       search: list[str],
                       limit_hours: int,
                       crawlers: dict = {}, 
                       db_manager: AsyncDatabaseManager = None, 
                       cache_manager: SqliteCache = None) -> tuple[int, set, int, Recorder]:
    
    status = 0
    warning_msg = set()

    # 0. prepare the work
    focuspoint = focus["focuspoint"].strip()
    focus_name = f"#{focus['id']} {focuspoint}"
    limit_hours = 24 if (config['WEB_ARTICLE_TTL'] == 1 or config['SocialMedia_TTL'] == 1) else limit_hours

    wis_logger.info(f'new job initializing: {focus_name}, limit_hours: {limit_hours}')
    
    # existings = get_existings_for_focus(focus_id)
    # 目前已经不需要 existings 的机制了，但这里保留 existing 的实例，避免程序修改太多，另外也是配合 recorder 保证单次运行不会重复处理
    existings = {}
    existings['web'] = set()
    recorder = Recorder(focus_id=focus_name, max_urls_per_task=config['MAX_URLS_PER_TASK'])

    try:
        extractor = ExtractManager(focus, db_manager, cache_manager)
    except Exception as e:
        # 这里都是对应focus 设置不当（extractor 初始化阶段）
        wis_logger.warning(f"ExtractManager Initialize Failed: {e}")
        status = 2
        warning_msg.add(str(e))
        return status, warning_msg, 0, recorder

    # 1. get the posts list from the sources (to parse more related urls)
    tasks = set()
    search_query = focuspoint or focus['restrictions']
    for search_source in search:
        if search_source == 'github':
            tasks.add(wrap_task(search_with_github(search_query, existings['web'], cache_manager), ('posts', 'github')))
        elif search_source in ['bing', 'arxiv']:
            tasks.add(wrap_task(search_with_engine(search_source, search_query, crawlers['web'], existings['web'], cache_manager),
                                ('article_or_posts', search_source)))
        else:
            wis_logger.warning(f"{focus_name} has unvalid search source {search_source}, skip")

    for source in sources:
        source_type = source.get('type')
        source_detail = source.get('detail')
        query = source.get('query', set())
        
        # 处理 detail：可能是列表或字符串（兼容旧数据）
        if isinstance(source_detail, list):
            detail_list = source_detail
        elif isinstance(source_detail, str):
            detail_list = [source_detail] if source_detail else []
        else:
            detail_list = []
        
        if not detail_list and not query:
            # wis_logger.warning(f"{focus_name} has unvalid {source_type}: has no detail or query. It should not happen and wired.")
            continue

        if source_type == 'rss':
            # rss 类型：detail 列表中每个 URL 都是独立的源
            for url in detail_list:
                if url and isinstance(url, str) and url.strip():
                    tasks.add(wrap_task(fetch_rss(url.strip(), existings['web'], cache_manager), ('article_or_posts', 'rss')))
                    recorder.rss_source += 1
        
        elif source_type == 'web':
            if not crawlers.get('web'):
                wis_logger.info(f"{focus_name} got {source_type} source, but no valid crawler, skip")
                warning_msg.add('web_miss')
                continue
            # web 类型：detail 列表中每个 URL 都添加到 url_queue
            for url in detail_list:
                if url and isinstance(url, str) and url.strip():
                    recorder.add_url(url.strip(), 'web')
                    recorder.web_source += 1
        else:
            wis_logger.warning(f"{focus_name} has unvalid source type: {source}, wiseflow opensource edition does not support any social media platform, pls try pro edition.")
            continue
        
    # 2. analyzing search engine results
    second_stage_tasks = set()
    for coro in asyncio.as_completed(tasks):
        # 防御性代码，这里拦截的都应该是对应程序代码级错误，或者是信源的解析方案已经失效（此时也得改代码）
        (task_type, source_name), success, result_or_exception = await coro
        if not success:
            e = result_or_exception
            wis_logger.warning(f"failed to process {source_name} {task_type} with error: {e}")
            await notify_user(89, [f"{source_name} - {task_type}:\n{e}"])
            warning_msg.add(f"{source_name}_may_not_support")
            continue
        
        result = result_or_exception

        if task_type == 'article_or_posts':
            results, markdown, link_dict = result
            if results:
                recorder.article_queue.extend(results)
                recorder.processed_urls.update({result.url for result in results})
                if source_name not in recorder.item_source:
                    recorder.item_source[source_name] = 0
                recorder.item_source[source_name] += len(results)
        else:
            markdown, link_dict = result
        
        if markdown and link_dict:
            wis_logger.debug(f'from {source_name} get {len(link_dict)} posts for {focus_name}, need to be extracted further...')
            second_stage_tasks.add(wrap_task(extractor(markdown=markdown, link_dict=link_dict, mode='only_link'), (source_name, task_type)))
    
    third_stage_tasks = set()
    for coro in asyncio.as_completed(second_stage_tasks):
        (source_name, task_type), success, result_or_exception = await coro
        if not success:
            if result_or_exception in ['99', '97', '98', '88', '91']:
                return int(result_or_exception), warning_msg, extractor.apply_count, recorder
            # 这对应程序异常，理论上不应该出现
            wis_logger.warning(f"failed to process {source_name} {task_type} with error: {result_or_exception}")
            await notify_user(89, [f"{source_name} - {task_type}:\n{result_or_exception}"])
            continue
        
        _, related_urls = result_or_exception
        recorder.add_url(related_urls - existings['web'], source_name)

    # save_existings_for_focus(focus_id, existings)
    for coro in asyncio.as_completed(third_stage_tasks):
        # 防御性代码，理论上这里不应该有任何错误
        try:
            article = await coro
        except Exception as e:
            wis_logger.warning(f"failed to process mc as_article or as_creator with error: {e}")
            await notify_user(89, [f"mc as_article or as_creator:\n{e}"])
            continue

        if article:
            recorder.article_queue.append(article)
        else:
            recorder.crawl_failed += 1
            recorder.total_processed += 1

    wis_logger.info(f"\n{recorder.source_summary()}\n")
    
    # 3. di-da style processing: 
    # use multiple threads to scrape the articles -- get more related urls add to to_crawl_urls...
    # use asyncio loop to crawl the urls -- get articles -- add to to_scrap_articles..
    while not recorder.finished():
        if recorder.article_queue:
            scraper_tasks = [wrap_task(extractor(article=article), article) for article in recorder.article_queue]
            for coro in asyncio.as_completed(scraper_tasks):
                recorder.total_processed += 1
                article, success, result_or_exception = await coro
                if not success:
                    if result_or_exception in ['99', '97', '98', '88', '91']:
                        return int(result_or_exception), warning_msg, extractor.apply_count, recorder
                    article_url = article.url if hasattr(article, 'url') else "unknown"
                    wis_logger.info(f"[EXTRACT] ✗ failed to process article: {article_url}: {result_or_exception}")
                    await notify_user(89, [f"Extractor Error When processing {article_url}: {result_or_exception}"])
                    recorder.scrap_failed += 1
                    continue
                
                info_found, related_links = result_or_exception
                
                recorder.add_url(related_links - existings['web'], 'article')
                recorder.info_added += info_found
                recorder.successed += 1
                # 只有成功时才添加到 existing
                existings['web'].add(article.url)
                if article.redirected_url:
                    existings['web'].add(article.redirected_url)
                wis_logger.debug(f"[EXTRACT] ✓ successfully processed article: {article.url}")

            recorder.article_queue = []

        if recorder.url_queue:
            wis_logger.debug(f"{focus_name} still have {len(recorder.url_queue)} urls to crawl")
            if crawlers.get('web'):
                async for result in await crawlers['web'].arun_many(list(recorder.url_queue)):
                    if result and result.success:
                        recorder.article_queue.append(result)
                    else:
                        recorder.crawl_failed += 1
                        recorder.total_processed += 1
            else:
                wis_logger.warning(f"{focus_name} have {len(recorder.url_queue)} urls skipped because no web crawler")
                warning_msg.add('web_miss')

            recorder.processed_urls.update(recorder.url_queue)
            recorder.url_queue.clear()

        wis_logger.info(f"\n{recorder.scrap_summary()}\n")
        wis_logger.debug("========================================")

    return status, warning_msg, extractor.apply_count, recorder
