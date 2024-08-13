# -*- coding: utf-8 -*-

import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import re
import asyncio
from pyppeteer import launch


header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/604.1 Edg/112.0.100.0"
}


async def coinlive_crawler(url: str, logger) -> (int, dict):
    if not url.startswith("https://www.coinlive.com"):
        logger.warning(
            f"{url} is not a cryptotracker url, you should not use this function"
        )
        return -5, {}

    async with httpx.AsyncClient() as client:

        for retry in range(2):
            try:
                response = await client.get(url, headers=header, timeout=30)
                response.raise_for_status()
                break
            except Exception as e:
                if retry < 1:
                    logger.info(f"{e}\nwaiting 1min")
                    await asyncio.sleep(60)
                else:
                    logger.warning(e)
                    return -7, {}

        soup = BeautifulSoup(response, "lxml")

        # 如果是列表页
        if url.startswith("https://www.coinlive.com/hot-news"):
            news_list = soup.find_all(class_=re.compile("new_item_title"))
            s = set()
            for news in news_list:
                s.add("https://www.coinlive.com" + news.get("href"))
            return 1, s

        # 如果是详情页
        elif url.startswith("https://www.coinlive.com/news-flash"):
            r = {
                "url": url,
                "title": soup.find(class_=re.compile("title___1")).text,
                #获取当前时间
                "publish_time": datetime.now().strftime("%Y%m%d"),
                "content": soup.find(class_=re.compile("share___")).div.text,
            }
            return 11, r
