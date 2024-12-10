# -*- coding: utf-8 -*-
from utils.pb_api import PbTalker
from utils.general_utils import get_logger, extract_and_convert_dates
from agents.get_info import GeneralInfoExtractor
from bs4 import BeautifulSoup
import os
import json
import asyncio
from custom_scraper import custom_scraper_map
from urllib.parse import urlparse, urljoin
import hashlib
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
existing_urls = {url['url'] for url in pb.read(collection_name='infos', fields=['url'])}


async def save_to_pb(url: str, infos: list):
    # saving to pb process
    for info in infos:
        info['url'] = url
        _ = pb.add(collection_name='infos', body=info)
        if not _:
            wiseflow_logger.error('add info failed, writing to cache_file')
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            with open(os.path.join(project_dir, f'{timestamp}_cache_infos.json'), 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=4)


crawler = PlaywrightCrawler(
    # Limit the crawl to max requests. Remove or increase it for crawling all links.
    # max_requests_per_crawl=1,
    max_request_retries=2,
    request_handler_timeout=timedelta(minutes=5),
    headless=False if os.environ.get("VERBOSE", "").lower() in ["true", "1"] else True
)

@crawler.pre_navigation_hook
async def log_navigation_url(context: PlaywrightPreNavigationContext) -> None:
    context.log.info(f'Navigating to {context.request.url} ...')

@crawler.router.default_handler
async def request_handler(context: PlaywrightCrawlingContext) -> None:
    # context.log.info(f'Processing {context.request.url} ...')
    # Handle dialogs (alerts, confirms, prompts)
    async def handle_dialog(dialog):
        context.log.info(f'Closing dialog: {dialog.message}')
        await dialog.accept()

    context.page.on('dialog', handle_dialog)
    await context.page.wait_for_load_state('networkidle')
    html = await context.page.inner_html('body')
    context.log.info('successfully finish fetching')

    parsed_url = urlparse(context.request.url)
    domain = parsed_url.netloc
    if domain in custom_scraper_map:
        context.log.info(f'routed to customer scraper for {domain}')
        try:
            article, more_urls, infos = await custom_scraper_map[domain](html, context.request.url)
            if not article and not infos and not more_urls:
                wiseflow_logger.warning(f'{parsed_url} handled by customer scraper, bot got nothing')
        except Exception as e:
            context.log.error(f'error occurred: {e}')
            wiseflow_logger.warning(f'handle {parsed_url} failed by customer scraper, so no info can be found')
            article, infos, more_urls = {}, [], set()

        link_dict = more_urls if isinstance(more_urls, dict) else {}
        related_urls = more_urls if isinstance(more_urls, set) else set()
        if not infos and not related_urls:
            try:
                text = article.get('content', '')
            except Exception as e:
                wiseflow_logger.warning(f'customer scraper output article is not valid dict: {e}')
                text = ''

            if not text:
                wiseflow_logger.warning(f'no content found in {parsed_url} by customer scraper, cannot use llm GIE, aborting')
                infos, related_urls = [], set()
            else:
                author = article.get('author', '')
                publish_date = article.get('publish_date', '')
                # get infos by llm
                try:
                    infos, related_urls, author, publish_date = await gie(text, link_dict, context.request.url, author, publish_date)
                except Exception as e:
                    wiseflow_logger.error(f'gie error occurred in processing: {e}')
                    infos, related_urls = [], set()
    else:
        # Extract data from the page.
        # future work: try to use a visual-llm do all the job...
        text = await context.page.inner_text('body')
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        base_url = f"{parsed_url.scheme}://{domain}"
        link_dict = {}
        for a in links:
            new_url = a.get('href')
            if new_url.startswith('javascript:') or new_url.startswith('#') or new_url.startswith('mailto:'):
                continue
            if new_url in [context.request.url, base_url]:
                continue
            if new_url in existing_urls:
                continue
            t = a.text.strip()
            if new_url and t:
                link_dict[t] = urljoin(base_url, new_url)
                existing_urls.add(new_url)

        publish_date = soup.find('div', class_='date').get_text(strip=True) if soup.find('div', class_='date') else None
        if publish_date:
            publish_date = extract_and_convert_dates(publish_date)
        author = soup.find('div', class_='author').get_text(strip=True) if soup.find('div', class_='author') else None
        if not author:
            author = soup.find('div', class_='source').get_text(strip=True) if soup.find('div', class_='source') else None
        # get infos by llm
        infos, related_urls, author, publish_date = await gie(text, link_dict, base_url, author, publish_date)

    if infos:
        await save_to_pb(context.request.url, infos)

    if related_urls:
        await context.add_requests(list(related_urls))

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
