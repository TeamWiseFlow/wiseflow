# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import json
import asyncio
from urllib.parse import urlparse
import hashlib
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext, PlaywrightPreNavigationContext
from datetime import timedelta


sites = ["https://www.gzhu.edu.cn/", "https://www.cnaiplus.com/a/news/?btwaf=75608141"]

os.environ['CRAWLEE_STORAGE_DIR'] = 'webpage_samples/crawlee_storage'
save_dir = 'webpage_samples'

async def main(sites: list):
    crawler = PlaywrightCrawler(
        # Limit the crawl to max requests. Remove or increase it for crawling all links.
        # max_requests_per_crawl=1,
        max_request_retries=1,
        request_handler_timeout=timedelta(minutes=5)
    )

    @crawler.pre_navigation_hook
    async def log_navigation_url(context: PlaywrightPreNavigationContext) -> None:
        context.log.info(f'navigating {context.request.url} ...')

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

        file = os.path.join(save_dir, f"{hashlib.sha256(context.request.url.encode()).hexdigest()[-6:]}.json")

        html = await context.page.inner_html('head')
        soup = BeautifulSoup(html, 'html.parser')
        web_title = soup.find('title')
        if web_title:
            web_title = web_title.get_text().strip()
        else:
            web_title = ''

        base_tag = soup.find('base', href=True)
        if base_tag and base_tag.get('href'):
            base_url = base_tag['href']
        else:
            # if no base tag, use the current url as base url
            parsed_url = urlparse(context.request.url)
            domain = parsed_url.netloc
            base_url = f"{parsed_url.scheme}://{domain}"

        html = await context.page.inner_html('body')
        raw_html = {
            "url": context.request.url,
            "web_title": web_title,
            "base_url": base_url,
            "html": html
        }

        with open(file, 'w', encoding='utf-8') as f:
            json.dump(raw_html, f, indent=4, ensure_ascii=False)

    await crawler.run(sites)

if __name__ == '__main__':
    asyncio.run(main(sites))
