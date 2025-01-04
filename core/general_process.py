# -*- coding: utf-8 -*-
from utils.pb_api import PbTalker
from utils.general_utils import get_logger, extract_and_convert_dates
from utils.deep_scraper import *
from agents.get_info import *
import os
import json
import asyncio
from custom_fetchings import *
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from datetime import datetime, timedelta


project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)

wiseflow_logger = get_logger('general_process', project_dir)
pb = PbTalker(wiseflow_logger)
gie = GeneralInfoExtractor(pb, wiseflow_logger)
one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
existing_urls = {url['url'] for url in pb.read(collection_name='infos', fields=['url'], filter=f"created>='{one_month_ago}'")}

llm_model = os.environ.get("PRIMARY_MODEL", "")
vl_model = os.environ.get("VL_MODEL", "")
if not vl_model:
    wiseflow_logger.warning("VL_MODEL not set, will skip extracting info from img, some info may be lost!")

img_to_be_recognized_pattern = r'§to_be_recognized_by_visual_llm_(.*?)§'
recognized_img_cache = {}


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

default_crawler_config = CrawlerRunConfig(
    delay_before_return_html=2.0,
    exclude_social_media_links=True,
    magic=True,
    scan_full_page=True,
    remove_overlay_elements=True
    )

async def main_process(sites: set):
    working_list = set()
    working_list.update(sites)
    async with AsyncWebCrawler(headless=True, verbose=True) as crawler:
        while working_list:
            url = working_list.pop()
            existing_urls.add(url)
            has_common_ext = any(url.lower().endswith(ext) for ext in common_file_exts)
            if has_common_ext:
                wiseflow_logger.info(f'{url} is a common file, skip')
                continue

            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            if domain in custom_scrapers:
                wiseflow_logger.debug(f'{url} is a custom scraper, use custom scraper')
                raw_markdown, metadata_dict, media_dict = custom_scrapers[domain](url)
            else:
                run_config = crawl4ai_custom_configs[domain] if domain in crawl4ai_custom_configs else default_crawler_config
                crawl4ai_cache_mode = CacheMode.WRITE_ONLY if url in sites else CacheMode.ENABLED
                result = await crawler.arun(url=url, crawler_config=run_config, cache_mode=crawl4ai_cache_mode)
                raw_markdown = result.markdown_v2.raw_markdown
                metadata_dict = result.metadata
                media_dict = result.media

            web_title = metadata_dict.get('title', '')
            base_url = metadata_dict.get('base_url', '')
            if not base_url:
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                if not base_url.endswith('/'):
                    base_url = base_url.rsplit('/', 1)[0] + '/'
            
            existing_urls.add(base_url)

            author = metadata_dict.get('author', '')
            publish_date = extract_and_convert_dates(metadata_dict.get('publish_date', ''))
            if not author or author.lower() == 'na' or not publish_date or publish_date.lower() == 'na':
                author, publish_date = await get_author_and_publish_date(raw_markdown, llm_model)
                wiseflow_logger.debug(f'get author and publish date by llm: {author}, {publish_date}')

            if not author or author.lower() == 'na':
                author = parsed_url.netloc

            if not publish_date:
                publish_date = datetime.now().strftime('%Y-%m-%d')
            
            img_dict = media_dict.get('images', [])
            if not img_dict or not isinstance(img_dict, list):
                used_img = {}
            else:
                used_img = {d['src']: d['alt'] for d in img_dict}
            
            link_dict, (text, reference_map) = deep_scraper(raw_markdown, base_url, used_img)
            wiseflow_logger.debug(f'deep scraper get {len(link_dict)} links, {len(reference_map)} references for text')

            to_be_replaces = {}
            for u, des in link_dict.items():
                matches = re.findall(img_to_be_recognized_pattern, des)
                if matches:
                    for img_url in matches:
                        if img_url in recognized_img_cache:
                            link_dict[u] = des.replace(f'§to_be_recognized_by_visual_llm_{img_url}§', recognized_img_cache[img_url])
                            continue
                        link_dict[u] = des.replace(f'§to_be_recognized_by_visual_llm_{img_url}§', img_url)
                        if img_url in to_be_replaces:
                            to_be_replaces[img_url].append(u)
                        else:
                            to_be_replaces[img_url] = [u]
            matches = re.findall(img_to_be_recognized_pattern, text)
            if matches:
                for img_url in matches:
                    if f'h{img_url}' in recognized_img_cache:
                        text = text.replace(f'§to_be_recognized_by_visual_llm_{img_url}§', recognized_img_cache[f'h{img_url}'])
                        continue
                    text = text.replace(f'§to_be_recognized_by_visual_llm_{img_url}§', f'h{img_url}')
                    img_url = f'h{img_url}'
                    if img_url in to_be_replaces:
                        to_be_replaces[img_url].append("content")
                    else:
                        to_be_replaces[img_url] = ["content"]
            wiseflow_logger.debug(f'total {len(to_be_replaces)} images to be recognized')
            recognized_result = await extract_info_from_img(list(to_be_replaces.keys()), vl_model)
            recognized_img_cache.update(recognized_result)
            for img_url, content in recognized_result.items():
                for u in to_be_replaces[img_url]:
                    if u == "content":
                        text = text.replace(img_url, content)
                    else:
                        link_dict[u] = link_dict[u].replace(img_url, content)
            
            more_urls, infos = await gie(link_dict, text, reference_map, author, publish_date)
            wiseflow_logger.debug(f'get {len(more_urls)} more urls and {len(infos)} infos')
            if more_urls:
                working_list.update(more_urls - existing_urls)
            if infos:
                await save_to_pb(url, web_title, infos)


if __name__ == '__main__':
    sites = pb.read('sites', filter='activated=True')
    wiseflow_logger.info('execute all sites one time')
    asyncio.run(main_process(set([site['url'] for site in sites])))
