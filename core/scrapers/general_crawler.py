# -*- coding: utf-8 -*-
# when you use this general crawler, remember followings
# When you receive flag -7, it means that the problem occurs in the HTML fetch process.
# When you receive flag 0, it means that the problem occurred during the content parsing process.
# when you receive flag 1, the result would be a tuple, means that the input url is possible a article_list page
# and the set contains the url of the articles.
# when you receive flag 11, you will get the dict contains the title, content, url, date, and the source of the article.

from gne import GeneralNewsExtractor
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
from llms.openai_wrapper import openai_llm
# from llms.siliconflow_wrapper import sfa_llm
from bs4.element import Comment
from utils.general_utils import extract_and_convert_dates
import asyncio
import json_repair
import os
from typing import Union
from requests.compat import urljoin
from scrapers import scraper_map


model = os.environ.get('HTML_PARSE_MODEL', 'gpt-3.5-turbo')
header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/604.1 Edg/112.0.100.0'}
extractor = GeneralNewsExtractor()


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


sys_info = '''Your task is to operate as an HTML content extractor, focusing on parsing a provided HTML segment. Your objective is to retrieve the following details directly from the raw text within the HTML, without summarizing or altering the content:

- The document's title
- The complete main content, as it appears in the HTML, comprising all textual elements considered part of the core article body
- The publication time in its original format found within the HTML

Ensure your response fits the following JSON structure, accurately reflecting the extracted data without modification:

```json
{
  "title": "The Document's Exact Title",
  "content": "All the unaltered primary text content from the article",
  "publish_time": "Original Publication Time as per HTML"
}
```

It is essential that your output adheres strictly to this format, with each field filled based on the untouched information extracted directly from the HTML source.'''


async def general_crawler(url: str, logger) -> tuple[int, Union[set, dict]]:
    """
    Return article information dict and flag, negative number is error, 0 is no result, 1 is for article_list page,
    11 is success

    main work flow:
    (for weixin public account articles, which startswith mp.weixin.qq use mp_crawler)
    first get the content with httpx
    then judge is article list (return all article url and flag 1) or article detail page
    then try to use gne to extract the information
    when fail, try to use a llm to analysis the html
    """

    # 0. if there's a scraper for this domain, use it (such as mp.weixin.qq.com)
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    base_url = f"{parsed_url.scheme}://{domain}"
    if domain in scraper_map:
        return await scraper_map[domain](url, logger)

    # 1. get the content with httpx
    async with httpx.AsyncClient() as client:
        for retry in range(2):
            try:
                response = await client.get(url, headers=header, timeout=30)
                response.raise_for_status()
                break
            except Exception as e:
                if retry < 1:
                    logger.info(f"can not reach\n{e}\nwaiting 1min")
                    await asyncio.sleep(60)
                else:
                    logger.error(e)
                    return -7, {}

    # 2. judge is article list (return all article url and flag 1) or article detail page
        page_source = response.text
        if page_source:
            text = page_source
        else:
            try:
                text = response.content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text = response.content.decode('gbk')
                except Exception as e:
                    logger.error(f"can not decode html {e}")
                    return -7, {}

        soup = BeautifulSoup(text, "html.parser")
        # Note: The scheme used here is very crude,
        # it is recommended to write a separate parser for specific business scenarios
        # Parse all URLs
        if len(url) < 50:
            urls = set()
            for link in soup.find_all("a", href=True):
                absolute_url = urljoin(base_url, link["href"])
                format_url = urlparse(absolute_url)
                # only record same domain links
                if not format_url.netloc or format_url.netloc != domain:
                    continue
                # remove hash fragment
                absolute_url = f"{format_url.scheme}://{format_url.netloc}{format_url.path}{format_url.params}{format_url.query}"
                if absolute_url != url:
                    urls.add(absolute_url)

            if len(urls) > 24:
                logger.info(f"{url} is more like an article list page, find {len(urls)} urls with the same netloc")
                return 1, urls

    # 3. try to use gne to extract the information
    try:
        result = extractor.extract(text)
        if 'meta' in result:
            del result['meta']

        if result['title'].startswith('服务器错误') or result['title'].startswith('您访问的页面') or result[
            'title'].startswith('403') \
                or result['content'].startswith('This website uses cookies') or result['title'].startswith('出错了'):
            logger.warning(f"can not get {url} from the Internet")
            return -7, {}

        if len(result['title']) < 4 or len(result['content']) < 24:
            logger.info(f"gne extract not good: {result}")
            result = None
    except Exception as e:
        logger.info(f"gne extract error: {e}")
        result = None

    # 4. try to use a llm to analysis the html
    if not result:
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
        llm_output = openai_llm(messages, model=model, logger=logger, temperature=0.01)
        result = json_repair.repair_json(llm_output, return_objects=True)
        logger.debug(f"decoded_object: {result}")

        if not isinstance(result, dict):
            logger.debug("failed to parse from llm output")
            return 0, {}

        if 'title' not in result or 'content' not in result:
            logger.debug("llm parsed result not good")
            return 0, {}

        # Extract the picture link, it will be empty if it cannot be extracted.
        image_links = []
        images = soup.find_all("img")
        for img in images:
            try:
                image_links.append(urljoin(base_url, img["src"]))
            except KeyError:
                continue
        result["images"] = image_links

        # Extract the author information, if it cannot be extracted, it will be empty.
        author_element = soup.find("meta", {"name": "author"})
        if author_element:
            result["author"] = author_element["content"]
        else:
            result["author"] = ""

    # 5. post process
    date_str = extract_and_convert_dates(result['publish_time'])
    if date_str:
        result['publish_time'] = date_str
    else:
        result['publish_time'] = datetime.strftime(datetime.today(), "%Y%m%d")

    from_site = domain.replace('www.', '')
    from_site = from_site.split('.')[0]
    result['content'] = f"[from {from_site}] {result['content']}"

    try:
        meta_description = soup.find("meta", {"name": "description"})
        if meta_description:
            result['abstract'] = f"[from {from_site}] {meta_description['content'].strip()}"
        else:
            result['abstract'] = ''
    except Exception:
        result['abstract'] = ''

    result['url'] = url
    return 11,  result
