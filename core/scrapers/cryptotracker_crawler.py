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


async def cryptotracker_crawler(url: str, logger) -> (int, dict):
    if not url.startswith("https://cryptotracker.com"):
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

        tr_list = soup.tbody.find_all('tr')
        r_list = []
        for tr in tr_list:
        #判断tr包含子节点td,且td具有class="name"
            if tr.find_all("td", class_="pe-2"):
                r_list.append({
                    "url": tr.a.get('href'),
                    "author":tr.find(class_='pe-2').text,
                    "title": tr.a.text,
                    #获取当前时间
                    "publish_time": datetime.now().strftime("%Y%m%d"),
                    "content": BeautifulSoup(tr.find(class_='mb-0').get('title'), "lxml").body.text,
                })

        return 111, r_list
