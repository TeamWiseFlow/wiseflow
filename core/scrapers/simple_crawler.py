# -*- coding: utf-8 -*-

from gne import GeneralNewsExtractor
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from utils.general_utils import extract_and_convert_dates
import chardet
from urllib.parse import urlparse
import asyncio


extractor = GeneralNewsExtractor()
header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/604.1 Edg/112.0.100.0'}


async def simple_crawler(url: str, logger) -> (int, dict):
    """
    Return article information dict and flag, negative number is error, 0 is no result, 11 is success
    """
    async with httpx.AsyncClient() as client:
        for retry in range(2):
            try:
                response = await client.get(url, headers=header, timeout=30)
                response.raise_for_status()
                break
            except Exception as e:
                if retry < 1:
                    logger.info(f"request {url} got error {e}\nwaiting 1min")
                    await asyncio.sleep(60)
                else:
                    logger.warning(f"request {url} got error {e}")
                    return -7, {}

        rawdata = response.content
        encoding = chardet.detect(rawdata)['encoding']
        text = rawdata.decode(encoding, errors='replace')
        result = extractor.extract(text)
        if not result:
            logger.error(f"gne cannot extract {url}")
            return 0, {}

        if len(result['title']) < 4 or len(result['content']) < 24:
            logger.info(f"{result} not valid")
            return 0, {}

        if result['title'].startswith('服务器错误') or result['title'].startswith('您访问的页面') or result[
            'title'].startswith('403') \
                or result['content'].startswith('This website uses cookies') or result['title'].startswith('出错了'):
            logger.warning(f"can not get {url} from the Internet")
            return -7, {}

        date_str = extract_and_convert_dates(result['publish_time'])
        if date_str:
            result['publish_time'] = date_str
        else:
            result['publish_time'] = datetime.strftime(datetime.today(), "%Y%m%d")

        from_site = urlparse(url).netloc
        from_site = from_site.replace('www.', '')
        from_site = from_site.split('.')[0]
        result['content'] = f"[from {from_site}] {result['content']}"

        soup = BeautifulSoup(text, "html.parser")
        try:
            meta_description = soup.find("meta", {"name": "description"})
            if meta_description:
                result['abstract'] = f"[from {from_site}] {meta_description['content'].strip()}"
            else:
                result['abstract'] = ''
        except:
            result['abstract'] = ''

        result['url'] = url

    return 11, result
