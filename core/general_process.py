# -*- coding: utf-8 -*-
from utils.pb_api import PbTalker
from utils.general_utils import get_logger
from agents.get_info import GeneralInfoExtractor
from bs4 import BeautifulSoup
import os
import json
import asyncio
from scrapers import *
from urllib.parse import urlparse
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext, PlaywrightPreNavigationContext
from datetime import datetime, timedelta


project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)

os.environ['CRAWLEE_STORAGE_DIR'] = os.path.join(project_dir, 'crawlee_storage')
screenshot_dir = os.path.join(project_dir, 'crawlee_storage', 'screenshots')
wiseflow_logger = get_logger('general_process', project_dir)
pb = PbTalker(wiseflow_logger)
gie = GeneralInfoExtractor(pb, wiseflow_logger)
one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
existing_urls = {url['url'] for url in pb.read(collection_name='infos', fields=['url'], filter=f"created>='{one_month_ago}'")}


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


crawler = PlaywrightCrawler(
    # Limit the crawl to max requests. Remove or increase it for crawling all links.
    # max_requests_per_crawl=1,
    max_request_retries=1,
    request_handler_timeout=timedelta(minutes=5),
)

@crawler.pre_navigation_hook
async def log_navigation_url(context: PlaywrightPreNavigationContext) -> None:
    context.log.info(f'Navigating to {context.request.url} ...')

@crawler.router.default_handler
async def request_handler(context: PlaywrightCrawlingContext) -> None:
    await context.page.wait_for_load_state('networkidle')
    await context.page.wait_for_timeout(2000)
    # Handle dialogs (alerts, confirms, prompts)
    async def handle_dialog(dialog):
        context.log.info(f'Closing dialog: {dialog.message}')
        await dialog.accept()
    context.page.on('dialog', handle_dialog)

    context.log.info('successfully finish fetching')
    wiseflow_logger.info(context.request.url)
    
    html = await context.page.inner_html('head')
    soup = BeautifulSoup(html, 'html.parser')
    web_title = soup.find('title')
    if web_title:
        web_title = web_title.get_text().strip()
    else:
        web_title = ''

    parsed_url = urlparse(context.request.url)
    domain = parsed_url.netloc
    base_tag = soup.find('base', href=True)
    if base_tag and base_tag.get('href'):
        base_url = base_tag['href']
    else:
        # 如果没有 base 标签，使用当前页面的 URL 路径作为 base url
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        if not base_url.endswith('/'):
            # 如果路径不以 / 结尾，则去掉最后一个路径段
            base_url = base_url.rsplit('/', 1)[0] + '/'

    html = await context.page.inner_html('body')
    if domain in custom_scrapers:
        action_dict, link_dict, text = custom_scrapers[domain](html, base_url)
    else:
        action_dict, link_dict, text = general_scraper(html, base_url)

    is_list, results = await gie(link_dict, text, base_url)

    if is_list and results:
        new_urls = [url for url in results if url != base_url and 
                   url != context.request.url and 
                   url not in existing_urls]
        if new_urls:
            await context.add_requests(new_urls)
            existing_urls.update(new_urls)
        return

    if results:
        await save_to_pb(context.request.url, web_title, results)

    # todo: use llm to determine next action
    """
    screenshot_file_name = f"{hashlib.sha256(context.request.url.encode()).hexdigest()}.png"
    await context.page.screenshot(path=os.path.join(screenshot_dir, screenshot_file_name), full_page=True)
    wiseflow_logger.debug(f'screenshot saved to {screenshot_file_name}')
    """

if __name__ == '__main__':
    sites = pb.read('sites', filter='activated=True')
    wiseflow_logger.info('execute all sites one time')
    async def run_all_sites():
        await crawler.run([site['url'].rstrip('/') for site in sites])

    asyncio.run(run_all_sites())
