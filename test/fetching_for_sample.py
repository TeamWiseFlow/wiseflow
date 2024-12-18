# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import json
import asyncio
from urllib.parse import urlparse, urljoin
import hashlib
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext, PlaywrightPreNavigationContext
from datetime import timedelta


sites = ["https://cryptopanic.com/news/"]


os.environ['CRAWLEE_STORAGE_DIR'] = 'test/webpage_samples/crawlee_storage'
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
        context.log.info(f'navigeting {context.request.url} ...')

    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        # context.log.info(f'Processing {context.request.url} ...')
        # Handle dialogs (alerts, confirms, prompts)
        await context.page.wait_for_load_state('networkidle')
        await context.page.wait_for_timeout(2000)
        
        async def handle_dialog(dialog):
            context.log.info(f'Closing dialog: {dialog.message}')
            await dialog.accept()
        context.page.on('dialog', handle_dialog)
        
        # 尝试查找并点击 "Accept" 按钮
        button_texts = ['Accept', 'Allow', 'Close']
        button_selectors = ['.close-btn', '.accept-button', '.allow-button']
        
        # 等待弹窗出现并尝试关闭
        for text in button_texts:
            try:
                context.log.info(f'等待按钮: {text} 可见...')
                await context.page.wait_for_selector(f'button:text("{text}")', state='visible', timeout=5000)  # 等待最多5秒
                await context.page.locator(f'button:text("{text}")').click()
                context.log.info(f'点击按钮: {text}')
                await context.page.wait_for_timeout(1000)
            except Exception as e:
                context.log.error(f'未能点击按钮: {text}，错误: {e}')
            
        for selector in button_selectors:
            try:
                context.log.info(f'等待选择器: {selector} 可见...')
                await context.page.wait_for_selector(selector, state='visible', timeout=5000)  # 等待最多5秒
                await context.page.locator(selector).click()
                context.log.info(f'点击选择器: {selector}')
                await context.page.wait_for_timeout(1000)
            except Exception as e:
                context.log.error(f'未能点击选择器: {selector}，错误: {e}')

        folder = os.path.join(save_dir, f"{hashlib.sha256(context.request.url.encode()).hexdigest()[-6:]}")
        os.makedirs(folder, exist_ok=True)
        html = await context.page.inner_html('body')
        context.log.info('successfully finish fetching')
        existing_urls = set()
        parsed_url = urlparse(context.request.url)
        domain = parsed_url.netloc
        text = await context.page.inner_text('body')
        with open(os.path.join(folder, 'text.txt'), 'w') as f:
            f.write(text)

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
        with open(os.path.join(folder, 'link_dict.json'), 'w', encoding='utf-8') as f:
            json.dump(link_dict, f, indent=4, ensure_ascii=False)

        links_number_from_html = len(link_dict)
        print(f"links number from html: {links_number_from_html}")

        screenshot_file = os.path.join(folder, 'screenshot.jpg')
        await context.page.screenshot(path=screenshot_file, full_page=True)

    await crawler.run(sites)

if __name__ == '__main__':
    asyncio.run(main(sites))
