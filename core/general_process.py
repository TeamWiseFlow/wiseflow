# -*- coding: utf-8 -*-
from utils.pb_api import PbTalker
from utils.general_utils import get_logger, extract_and_convert_dates
from agents.get_info import GeneralInfoExtractor
from bs4 import BeautifulSoup
import os
import json
import asyncio
from custom_crawlers import customer_crawler_map
from urllib.parse import urlparse, urljoin
import hashlib
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext
from datetime import datetime


project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)

os.environ['CRAWLEE_STORAGE_DIR'] = os.path.join(project_dir, 'crawlee_storage')
screenshot_dir = os.path.join(project_dir, 'crawlee_storage', 'screenshots')
wiseflow_logger = get_logger('general_process', f'{project_dir}/general_process.log')
pb = PbTalker(wiseflow_logger)
gie = GeneralInfoExtractor(pb, wiseflow_logger)

# Global variables
working_list = set()
existing_urls = {url['url'] for url in pb.read(collection_name='articles', fields=['url']) if url['url']}
lock = asyncio.Lock()

async def save_to_pb(article: dict, infos: list):
    # saving to pb process
    screenshot = article.pop('screenshot') if 'screenshot' in article else None
    article_id = pb.add(collection_name='articles', body=article)
    if not article_id:
        wiseflow_logger.error('add article failed, writing to cache_file')
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        with open(os.path.join(project_dir, f'{timestamp}_cache_article.json'), 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=4)
        return
    if screenshot:
        file = open(screenshot, 'rb')
        file_name = os.path.basename(screenshot)
        message = pb.upload('articles', article_id, 'screenshot', file_name, file)
        file.close()
        if not message:
            wiseflow_logger.warning(f'{article_id} upload screenshot failed, file location: {screenshot}')

    for info in infos:
        info['articles'] = [article_id]
        _ = pb.add(collection_name='infos', body=info)
        if not _:
            wiseflow_logger.error('add info failed, writing to cache_file')
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            with open(os.path.join(project_dir, f'{timestamp}_cache_infos.json'), 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=4)


async def pipeline(url: str):
    global working_list, existing_urls
    working_list.add(url)
    crawler = PlaywrightCrawler(
        # Limit the crawl to max requests. Remove or increase it for crawling all links.
        max_requests_per_crawl=100,
    )
    # Define the default request handler, which will be called for every request.
    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        context.log.info(f'Processing {context.request.url} ...')
        # Handle dialogs (alerts, confirms, prompts)
        async def handle_dialog(dialog):
            context.log.info(f'Closing dialog: {dialog.message}')
            await dialog.accept()

        context.page.on('dialog', handle_dialog)

        # Extract data from the page.
        # future work: try to use a visual-llm do all the job...
        text = await context.page.inner_text('body')
        wiseflow_logger.debug(f"got text: {text}")
        html = await context.page.inner_html('body')
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        base_url = context.request.url
        link_dict = {}
        for a in links:
            new_url = a.get('href')
            t = a.text.strip()
            if new_url and t:
                link_dict[t] = urljoin(base_url, new_url)
        wiseflow_logger.debug(f'found {len(link_dict)} more links')

        publish_date = soup.find('div', class_='date').get_text(strip=True) if soup.find('div', class_='date') else None
        if publish_date:
            publish_date = extract_and_convert_dates(publish_date)
        author = soup.find('div', class_='author').get_text(strip=True) if soup.find('div', class_='author') else None
        if not author:
            author = soup.find('div', class_='source').get_text(strip=True) if soup.find('div',
                                                                                         class_='source') else None

        screenshot_file_name = f"{hashlib.sha256(context.request.url.encode()).hexdigest()}.png"
        await context.page.screenshot(path=os.path.join(screenshot_dir, screenshot_file_name), full_page=True)
        wiseflow_logger.debug(f'screenshot saved to {screenshot_file_name}')

        # get infos by llm
        infos, related_urls, author, publish_date = await gie(text, link_dict, base_url, author, publish_date)
        if infos:
            article = {
                'url': context.request.url,
                'title': await context.page.title(),
                'author': author,
                'publish_date': publish_date,
                'screenshot': os.path.join(screenshot_dir, screenshot_file_name),
                'tags': [info['tag'] for info in infos]
            }
            await save_to_pb(article, infos)

        if related_urls:
            async with lock:
                new_urls = related_urls - existing_urls
                working_list.update(new_urls)

        # todo: use llm to determine next action

    while working_list:
        async with lock:
            if not working_list:
                break
            url = working_list.pop()
            existing_urls.add(url)
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain in customer_crawler_map:
            wiseflow_logger.info(f'routed to customer crawler for {domain}')
            try:
                article, more_urls = await customer_crawler_map[domain](url, wiseflow_logger)
            except Exception as e:
                wiseflow_logger.error(f'error occurred in crawling {url}: {e}')
                continue

            if not article and not more_urls:
                wiseflow_logger.info(f'no content found in {url} by customer crawler')
                continue

            text = article.pop('content') if 'content' in article else None
            author = article.get('author', None)
            publish_date = article.get('publish_date', None)
            title = article.get('title', "")
            screenshot = article.get('screenshot', '')

            # get infos by llm
            try:
                infos, related_urls, author, publish_date = await gie(text, more_urls, url, author, publish_date)
            except Exception as e:
                wiseflow_logger.error(f'gie error occurred in processing {article}: {e}')
                continue

            if infos:
                article = {
                    'url': url,
                    'title': title,
                    'author': author,
                    'publish_date': publish_date,
                    'screenshot': screenshot,
                    'tags': [info['tag'] for info in infos]
                }
                await save_to_pb(article, infos)

            if related_urls:
                async with lock:
                    new_urls = related_urls - existing_urls
                    working_list.update(new_urls)
            continue

        try:
            await crawler.run([url])
        except Exception as e:
            wiseflow_logger.error(f'error occurred in crawling {url}: {e}')


if __name__ == '__main__':
    import asyncio

    asyncio.run(pipeline())
