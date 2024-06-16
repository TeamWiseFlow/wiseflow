# -*- coding: utf-8 -*-

from urllib.parse import urlparse
from .general_crawler import general_crawler
from .mp_crawler import mp_crawler
import httpx
from bs4 import BeautifulSoup
import asyncio
from requests.compat import urljoin
from datetime import datetime, date


header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/604.1 Edg/112.0.100.0'}

async def general_scraper(site: str, expiration: date, existing: list[str], logger) -> list[dict]:
    logger.debug(f"start processing {site}")
    async with httpx.AsyncClient() as client:
        for retry in range(2):
            try:
                response = await client.get(site, headers=header, timeout=30)
                response.raise_for_status()
                break
            except Exception as e:
                if retry < 1:
                    logger.info(f"request {site} got error {e}\nwaiting 1min")
                    await asyncio.sleep(60)
                else:
                    logger.warning(f"request {site} got error {e}")
                    return []
        page_source = response.text
        soup = BeautifulSoup(page_source, "html.parser")
        # Parse all URLs
        parsed_url = urlparse(site)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        urls = set()
        for link in soup.find_all("a", href=True):
            absolute_url = urljoin(base_url, link["href"])
            if urlparse(absolute_url).netloc == parsed_url.netloc and absolute_url != site:
                urls.add(absolute_url)

    if not urls:
        # maybe it's an article site
        logger.info(f"can not find any link from {site}, maybe it's an article site...")
        if site in existing:
            logger.debug(f"{site} has been crawled before, skip it")
            return []

        if site.startswith('https://mp.weixin.qq.com') or site.startswith('http://mp.weixin.qq.com'):
            flag, result = await mp_crawler(site, logger)
        else:
            flag, result = await general_crawler(site, logger)

        if flag != 11:
            return []

        publish_date = datetime.strptime(result['publish_time'], '%Y%m%d')
        if publish_date.date() < expiration:
            logger.debug(f"{site} is too old, skip it")
            return []
        else:
            return [result]

    articles = []
    for url in urls:
        logger.debug(f"start scraping {url}")
        if url in existing:
            logger.debug(f"{url} has been crawled before, skip it")
            continue

        existing.append(url)

        if url.startswith('https://mp.weixin.qq.com') or url.startswith('http://mp.weixin.qq.com'):
            flag, result = await mp_crawler(url, logger)
        else:
            flag, result = await general_crawler(url, logger)

        if flag != 11:
            continue

        publish_date = datetime.strptime(result['publish_time'], '%Y%m%d')
        if publish_date.date() < expiration:
            logger.debug(f"{url} is too old, skip it")
        else:
            articles.append(result)

    return articles
