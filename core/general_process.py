# -*- coding: utf-8 -*-
from utils.pb_api import PbTalker
from utils.general_utils import get_logger
from agents.get_info import GeneralInfoExtractor
from bs4 import BeautifulSoup
import os
import json
import asyncio
from custom_process import customer_crawler_map
from urllib.parse import urlparse, urljoin
import hashlib
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext


project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)
os.environ['CRAWLEE_STORAGE_DIR'] = os.path.join(project_dir, 'crawlee_storage')
screenshot_dir = os.path.join(project_dir, 'crawlee_storage', 'screenshots')

wiseflow_logger = get_logger('general_process', f'{project_dir}/general_process.log')
pb = PbTalker(wiseflow_logger)
ie = GeneralInfoExtractor(pb, wiseflow_logger)

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
        with open(os.path.join(project_dir, 'cache_articles.json'), 'a', encoding='utf-8') as f:
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
        _ = pb.add(collection_name='agents', body=info)
        if not _:
            wiseflow_logger.error('add insight failed, writing to cache_file')
            with open(os.path.join(project_dir, 'cache_insights.json'), 'a', encoding='utf-8') as f:
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
            text = a.text.strip()
            if new_url and text:
                absolute_url = urljoin(base_url, new_url)
                link_dict[text] = absolute_url
        wiseflow_logger.debug(f'found {len(link_dict)} more links')

        screenshot_file_name = f"{hashlib.sha256(context.request.url.encode()).hexdigest()}.png"
        await context.page.screenshot(path=os.path.join(screenshot_dir, screenshot_file_name), full_page=True)
        wiseflow_logger.debug(f'screenshot saved to {screenshot_file_name}')

        # get infos by llm
        infos, author, publish_date, related_urls = await ie(text, link_dict, base_url, wiseflow_logger)
        if infos:
            # get author and publish date by llm
            wiseflow_logger.debug(f'LLM result -- author: {author}, publish_date: {publish_date}')
            article = {
                'url': context.request.url,
                'title': await context.page.title(),
                'author': author,
                'publish_date': publish_date,
                'screenshot': os.path.join(screenshot_dir, screenshot_file_name),
                'tags': [info['name'] for info in infos]
            }
            await save_to_pb(article, infos)

        # find any related urls
        related_urls = await get_more_related_urls(html, wiseflow_logger)
        wiseflow_logger.debug(f'got {len(related_urls)} more urls')
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
            wiseflow_logger.debug(f'routed to customer process for {domain}')
            try:
                article, infos, related_urls = await customer_crawler_map[domain](url, wiseflow_logger)
            except Exception as e:
                wiseflow_logger.error(f'error occurred in crawling {url}: {e}')
                continue

            if infos and article:
                wiseflow_logger.debug("receiving new infos from customer crawler, saving to pb")
                article['tags'] = [info['name'] for info in infos]
                await save_to_pb(article, infos)
            if related_urls:
                wiseflow_logger.debug('receiving new related_urls from customer crawler, adding to working_list')
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
