# -*- coding: utf-8 -*-
# general_process.py
from pathlib import Path
from dotenv import load_dotenv

# 加載環境變數
env_path = Path(__file__).parent / 'windows.env'
if env_path.exists():
    load_dotenv(env_path)

import os
from utils.pb_api import PbTalker
from utils.general_utils import get_logger, extract_and_convert_dates, is_chinese
from agents.get_info import *
import json
import asyncio
from scrapers import *
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, CacheMode
from datetime import datetime, timedelta
import logging

logging.getLogger("httpx").setLevel(logging.WARNING)

project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)

wiseflow_logger = get_logger('general_process', project_dir)
pb = PbTalker(wiseflow_logger)
one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
existing_urls = {url['url'] for url in pb.read(collection_name='infos', fields=['url'], filter=f"created>='{one_month_ago}'")}

crawler = AsyncWebCrawler(verbose=False)
model = os.environ.get("PRIMARY_MODEL", "")
if not model:
    raise ValueError("PRIMARY_MODEL not set, please set it in environment variables or edit core/.env")
secondary_model = os.environ.get("SECONDARY_MODEL", model)

async def save_to_pb(url: str, url_title: str, infos: list):
    # saving to pb process
    for info in infos:
        info['url'] = url
        info['url_title'] = url_title
        _ = pb.add(collection_name='infos', body=info)
        if not _:
            wiseflow_logger.error('add info failed, writing to cache_file')
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            with open(os.path.join(project_dir, f'{timestamp}_cache_infos.json'), 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=4)


async def main_process(_sites: set | list):
    # collect tags user set in pb database and determin the system prompt language based on tags
    focus_data = pb.read(collection_name='focus_points', filter=f'activated=True')
    if not focus_data:
        wiseflow_logger.info('no activated tag found, will ask user to create one')
        focus = input('It seems you have not set any focus point, WiseFlow need the specific focus point to guide the following info extract job.'
                    'so please input one now. describe what info you care about shortly: ')
        explanation = input('Please provide more explanation for the focus point (if not necessary, pls just press enter: ')
        focus_data.append({"focuspoint": focus, "explanation": explanation,
                            "id": pb.add('focus_points', {"focuspoint": focus, "explanation": explanation})})


    focus_dict = {item["focuspoint"]: item["id"] for item in focus_data}
    focus_statement = ''
    for item in focus_data:
        tag = item["focuspoint"]
        expl = item["explanation"]
        focus_statement = f"{focus_statement}//{tag}//\n"
        if expl:
            if is_chinese(expl):
                focus_statement = f"{focus_statement}解释：{expl}\n"
            else:
                focus_statement = f"{focus_statement}Explanation: {expl}\n"

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

    recognized_img_cache = {}
    working_list = set()
    working_list.update(_sites)
    await crawler.start()
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
            
        run_config.cache_mode = CacheMode.WRITE_ONLY if url in _sites else CacheMode.ENABLED
        result = await crawler.arun(url=url, config=run_config)
        if not result.success:
            wiseflow_logger.warning(f'{url} failed to crawl, destination web cannot reach, skip')
            continue
        metadata_dict = result.metadata if result.metadata else {}

        if domain in custom_scrapers:
            result = custom_scrapers[domain](result)
            raw_markdown = result.content
            used_img = result.images
            title = result.title
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
            wiseflow_logger.warning(f'{url} no content, something during fetching failed, skip')
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
            prompts = [get_link_sys_prompt, get_link_suffix_prompt, secondary_model]
            links_texts = []
            for _parts in links_parts:
                links_texts.extend(_parts.split('\n\n'))
            more_url = await get_more_related_urls(links_texts, link_dict, prompts, _logger=wiseflow_logger)
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

        prompts = [get_info_sys_prompt, get_info_suffix_prompt, model]
        infos = await get_info(contents, link_dict, prompts, focus_dict, author, publish_date, _logger=wiseflow_logger)
        if infos:
            wiseflow_logger.debug(f'get {len(infos)} infos, will save to pb')
            await save_to_pb(url, title, infos)
    await crawler.close()

if __name__ == '__main__':

    sites = pb.read('sites', filter='activated=True')
    wiseflow_logger.info('execute all sites one time')
    asyncio.run(main_process([site['url'] for site in sites]))
