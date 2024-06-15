# -*- coding: utf-8 -*-

import os
from urllib.parse import urlparse
from .simple_crawler import simple_crawler
from .mp_crawler import mp_crawler
import httpx
from bs4 import BeautifulSoup
from bs4.element import Comment
from llms.openai_wrapper import openai_llm
# from llms.siliconflow_wrapper import sfa_llm
from datetime import datetime, date
from requests.compat import urljoin
import chardet
from utils.general_utils import extract_and_convert_dates
import asyncio
import json_repair


model = os.environ.get('HTML_PARSE_MODEL', 'gpt-3.5-turbo')
header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/604.1 Edg/112.0.100.0'}


def tag_visible(element: Comment) -> bool:
    if element.parent.name in ["style", "script", "head", "title", "meta", "[document]"]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_soup(soup: BeautifulSoup) -> str:
    res = []
    texts = soup.find_all(string=True)
    visible_texts = filter(tag_visible, texts)
    for v in visible_texts:
        res.append(v)
    text = "\n".join(res)
    return text.strip()


sys_info = '''Your role is to function as an HTML parser, tasked with analyzing a segment of HTML code. Extract the following metadata from the given HTML snippet: the document's title, summary or abstract, main content, and the publication date. Ensure that your response adheres to the JSON format outlined below, encapsulating the extracted information accurately:

```json
{
  "title": "The Document's Title",
  "abstract": "A concise overview or summary of the content",
  "content": "The primary textual content of the article",
  "publish_date": "The publication date in YYYY-MM-DD format"
}
```

Please structure your output precisely as demonstrated, with each field populated correspondingly to the details found within the HTML code.
'''


async def llm_crawler(url: str, logger) -> (int, dict):
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
        soup = BeautifulSoup(text, "html.parser")
        html_text = text_from_soup(soup)
        html_lines = html_text.split('\n')
        html_lines = [line.strip() for line in html_lines if line.strip()]
        html_text = "\n".join(html_lines)
        if len(html_text) > 29999:
            logger.info(f"{url} content too long for llm parsing")
            return 0, {}

        if not html_text or html_text.startswith('服务器错误') or html_text.startswith(
                '您访问的页面') or html_text.startswith('403') \
                or html_text.startswith('出错了'):
            logger.warning(f"can not get {url} from the Internet")
            return -7, {}

    messages = [
        {"role": "system", "content": sys_info},
        {"role": "user", "content": html_text}
    ]
    llm_output = openai_llm(messages, model=model, logger=logger)
    decoded_object = json_repair.repair_json(llm_output, return_objects=True)
    logger.debug(f"decoded_object: {decoded_object}")
    if not isinstance(decoded_object, dict):
        logger.debug("failed to parse")
        return 0, {}

    for key in ['title', 'abstract', 'content']:
        if key not in decoded_object:
            logger.debug(f"{key} not in decoded_object")
            return 0, {}

    info = {'title': decoded_object['title'], 'abstract': decoded_object['abstract'], 'content': decoded_object['content']}
    date_str = decoded_object.get('publish_date', '')

    if date_str:
        info['publish_time'] = extract_and_convert_dates(date_str)
    else:
        info['publish_time'] = datetime.strftime(datetime.today(), "%Y%m%d")

    info["url"] = url
    # Extract the picture link, it will be empty if it cannot be extracted.
    image_links = []
    images = soup.find_all("img")

    for img in images:
        try:
            image_links.append(img["src"])
        except KeyError:
            continue
    info["images"] = image_links

    # Extract the author information, if it cannot be extracted, it will be empty.
    author_element = soup.find("meta", {"name": "author"})
    if author_element:
        info["author"] = author_element["content"]
    else:
        info["author"] = ""

    from_site = urlparse(url).netloc
    from_site = from_site.replace('www.', '')
    from_site = from_site.split('.')[0]
    info['content'] = f"[from {from_site}] {info['content']}"

    if not info['abstract']:
        meta_description = soup.find("meta", {"name": "description"})
        if meta_description:
            info['abstract'] = f"[from {from_site}] {meta_description['content'].strip()}"
        else:
            info['abstract'] = ''

    return 11, info


async def general_scraper(site: str, expiration: date, existing: list[str], logger) -> list[dict]:
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
        urls = []
        for link in soup.find_all("a", href=True):
            absolute_url = urljoin(base_url, link["href"])
            if urlparse(absolute_url).netloc == parsed_url.netloc:
                urls.append(absolute_url)

    if not urls:
        # maybe it's an article site
        logger.info(f"can not find any link from {site}, maybe it's an article site...")
        if site in existing:
            logger.debug(f"{site} has been crawled before, skip it")
            return []

        if site.startswith('https://mp.weixin.qq.com') or site.startswith('http://mp.weixin.qq.com'):
            flag, result = await mp_crawler(site, logger)
        else:
            flag, result = await simple_crawler(site, logger)

        if flag == -7:
            #  -7 means cannot fetch the html, and other crawlers have no effect.
            return []

        if flag != 11:
            flag, result = await llm_crawler(site, logger)
            if flag != 11:
                return []

        publish_date = datetime.strptime(result['publish_time'], '%Y%m%d')
        if publish_date.date() < expiration:
            logger.debug(f"{site} is too old, skip it")
            return []
        else:
            return [result]
    # Then gradually analyze the article, still use simple_crawler first, no use llm_crawler
    articles = []
    for url in urls:
        if url in existing:
            logger.debug(f"{url} has been crawled before, skip it")
            continue

        existing.append(url)

        if url.startswith('https://mp.weixin.qq.com') or url.startswith('http://mp.weixin.qq.com'):
            flag, result = await mp_crawler(url, logger)
        else:
            flag, result = await simple_crawler(url, logger)

        if flag == -7:
            #  -7 means cannot fetch the html, and other crawlers have no effect.
            continue

        if flag != 11:
            flag, result = await llm_crawler(url, logger)
            if flag != 11:
                continue

        publish_date = datetime.strptime(result['publish_time'], '%Y%m%d')
        if publish_date.date() < expiration:
            logger.debug(f"{url} is too old, skip it")
        else:
            articles.append(result)

    return articles
