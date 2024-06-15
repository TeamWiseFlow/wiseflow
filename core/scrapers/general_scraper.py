# -*- coding: utf-8 -*-

import os
from urllib.parse import urlparse
import re
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


def parse_html_content(out: str) -> dict:
    dct = {'title': '', 'abstract': '', 'content': '', 'publish_time': ''}
    pattern = re.compile(r'\"\"\"(.*?)\"\"\"', re.DOTALL)
    result = pattern.findall(out)
    result = result[0].strip()
    dict_strs = result.split('||')
    if not dict_strs:
        dict_strs = result.split('|||')
        if not dict_strs:
            return dct
    if len(dict_strs) == 3:
        dct['title'] = dict_strs[0].strip()
        dct['content'] = dict_strs[1].strip()
    elif len(dict_strs) == 4:
        dct['title'] = dict_strs[0].strip()
        dct['content'] = dict_strs[2].strip()
        dct['abstract'] = dict_strs[1].strip()
    else:
        return dct
    date_str = extract_and_convert_dates(dict_strs[-1])
    if date_str:
        dct['publish_time'] = date_str
    else:
        dct['publish_time'] = datetime.strftime(datetime.today(), "%Y%m%d")
    return dct


sys_info = '''As an HTML parser, you'll receive a block of HTML code. Your task is to extract its title, summary, content, and publication date, with the date formatted as YYYY-MM-DD. Return the results in the following format (enclosed within triple quotes):
"""
Title||Summary||Content||Release Date YYYY-MM-DD
"""
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
            logger.warning(f"{url} content too long for llm parsing")
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
    try:
        info = parse_html_content(llm_output)
    except:
        msg = f"can not parse {llm_output}"
        logger.debug(msg)
        return 0, {}

    if len(info['title']) < 4 or len(info['content']) < 24:
        logger.debug(f"{info} not valid")
        return 0, {}

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
        urls = [urljoin(base_url, link["href"]) for link in soup.find_all("a", href=True)]

    if not urls:
        # maybe it's an article site
        logger.warning(f"can not find any link from {site}, maybe it's an article site...")
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
