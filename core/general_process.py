# -*- coding: utf-8 -*-
from utils.pb_api import PbTalker
from utils.general_utils import get_logger, extract_and_convert_dates, is_chinese
from agents.get_info import *
import json
from scrapers import *
from utils.zhipu_search import run_v4_async
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, CacheMode
from datetime import datetime
import feedparser


project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)

wiseflow_logger = get_logger('wiseflow', project_dir)
pb = PbTalker(wiseflow_logger)

model = os.environ.get("PRIMARY_MODEL", "")
if not model:
    raise ValueError("PRIMARY_MODEL not set, please set it in environment variables or edit core/.env")
secondary_model = os.environ.get("SECONDARY_MODEL", model)

async def info_process(url: str, 
                       url_title: str, 
                       author: str, 
                       publish_date: str, 
                       contents: list[str], 
                       link_dict: dict, 
                       focus_id: str,
                       get_info_prompts: list[str]):

    infos = await get_info(contents, link_dict, get_info_prompts, author, publish_date, _logger=wiseflow_logger)
    if infos:
        wiseflow_logger.debug(f'get {len(infos)} infos, will save to pb')

    for info in infos:
        info['url'] = url
        info['url_title'] = url_title
        info['tag'] = focus_id
        _ = pb.add(collection_name='infos', body=info)
        if not _:
            wiseflow_logger.error('add info failed, writing to cache_file')
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            with open(os.path.join(project_dir, f'{timestamp}_cache_infos.json'), 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=4)


async def main_process(focus: dict, sites: list):
    wiseflow_logger.debug('new task initializing...')
    focus_id = focus["id"]
    focus_point = focus["focuspoint"].strip()
    explanation = focus["explanation"].strip()
    wiseflow_logger.debug(f'focus_id: {focus_id}, focus_point: {focus_point}, explanation: {explanation}, search_engine: {focus["search_engine"]}')
    existing_urls = {url['url'] for url in pb.read(collection_name='infos', fields=['url'], filter=f"tag='{focus_id}'")}
    focus_statement = f"//{focus_point}//"
    if explanation:
        if is_chinese(explanation):
            focus_statement = f"{focus_statement}\n解释：{explanation}"
        else:
            focus_statement = f"{focus_statement}\nExplanation: {explanation}"

    date_stamp = datetime.now().strftime('%Y-%m-%d')
    if is_chinese(focus_statement):
        get_link_sys_prompt = get_link_system.replace('{focus_statement}', focus_statement)
        get_link_sys_prompt = f"今天的日期是{date_stamp}，{get_link_sys_prompt}"
        get_link_suffix_prompt = get_link_suffix
        get_info_sys_prompt = get_info_system.replace('{focus_statement}', focus_statement)
        get_info_sys_prompt = f"今天的日期是{date_stamp}，{get_info_sys_prompt}"
        get_info_suffix_prompt = get_info_suffix
    else:
        get_link_sys_prompt = get_link_system_en.replace('{focus_statement}', focus_statement)
        get_link_sys_prompt = f"today is {date_stamp}, {get_link_sys_prompt}"
        get_link_suffix_prompt = get_link_suffix_en
        get_info_sys_prompt = get_info_system_en.replace('{focus_statement}', focus_statement)
        get_info_sys_prompt = f"today is {date_stamp}, {get_info_sys_prompt}"
        get_info_suffix_prompt = get_info_suffix_en
    
    get_link_prompts = [get_link_sys_prompt, get_link_suffix_prompt, secondary_model]
    get_info_prompts = [get_info_sys_prompt, get_info_suffix_prompt, model]

    working_list = set()
    if focus.get('search_engine', False):
        query = focus_point if not explanation else f"{focus_point}({explanation})"
        search_intent, search_content = await run_v4_async(query, _logger=wiseflow_logger)
        _intent = search_intent['search_intent'][0]['intent']
        _keywords = search_intent['search_intent'][0]['keywords']
        wiseflow_logger.info(f'query: {query}\nsearch intent: {_intent}\nkeywords: {_keywords}')
        search_results = search_content['search_result']
        for result in search_results:
            if 'content' not in result or 'link' not in result:
                continue
            url = result['link']
            if url in existing_urls:
                continue
            if '（发布时间' not in result['title']:
                wiseflow_logger.debug(f'can not find publish time in the search result {url}, adding to working list')
                working_list.add(url)
                continue
            title, publish_date = result['title'].split('（发布时间')
            title = title.strip() + '(from search engine)'
            publish_date = publish_date.strip('）')
            # 严格匹配YYYY-MM-DD格式
            date_match = re.search(r'\d{4}-\d{2}-\d{2}', publish_date)
            if date_match:
                publish_date = date_match.group()
                publish_date = extract_and_convert_dates(publish_date)
            else:
                wiseflow_logger.warning(f'can not find publish time in the search result {url}, adding to working list')
                working_list.add(url)
                continue
            author = result.get('media', '')
            if not author:
                author = urlparse(url).netloc
            texts = [result['content']]
            await info_process(url, title, author, publish_date, texts, {}, focus_id, get_info_prompts)

    recognized_img_cache = {}
    for site in sites:
        if site.get('type', 'web') == 'rss':
            try:
                feed = feedparser.parse(site['url'])
            except Exception as e:
                wiseflow_logger.warning(f"{site['url']} RSS feed is not valid: {e}")
                continue
            rss_urls = {entry.link for entry in feed.entries if entry.link}
            wiseflow_logger.debug(f'get {len(rss_urls)} urls from rss source {site["url"]}')
            working_list.update(rss_urls - existing_urls)
        else:
            working_list.add(site['url'])
    
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
        if domain in custom_fetching_configs:
            wiseflow_logger.debug(f'{url} will using custom crawl4ai run config')
            run_config = custom_fetching_configs[domain]
        else:
            run_config = crawler_config
            
        run_config.cache_mode = CacheMode.WRITE_ONLY if url in sites else CacheMode.ENABLED
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            try:
                result = await crawler.arun(url=url, config=run_config)
            except Exception as e:
                wiseflow_logger.error(e)
                continue
        if not result.success:
            wiseflow_logger.warning(f'{url} failed to crawl, destination web cannot reach, skip')
            continue
        metadata_dict = result.metadata if result.metadata else {}

        if domain in custom_scrapers:
            result = custom_scrapers[domain](result)
            raw_markdown = result.content
            used_img = result.images
            title = result.title
            if title == 'maybe a new_type_article':
                wiseflow_logger.warning(f'we found a new type here,{url}')
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
            wiseflow_logger.warning(f'{url} no content, skip')
            continue

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
            author, publish_date = await get_author_and_publish_date(raw_markdown, model, _logger=wiseflow_logger)

        if not author or author.lower() == 'na':
            author = parsed_url.netloc
        
        if publish_date:
            publish_date = extract_and_convert_dates(publish_date)
        else:
            publish_date = date_stamp
        
        await info_process(url, title, author, publish_date, contents, link_dict, focus_id, get_info_prompts)
