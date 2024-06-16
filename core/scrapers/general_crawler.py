# -*- coding: utf-8 -*-
# when you use this general crawler, remember followings
# When you receive flag -7, it means that the problem occurs in the HTML fetch process.
# When you receive flag 0, it means that the problem occurred during the content parsing process.

from gne import GeneralNewsExtractor
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
from llms.openai_wrapper import openai_llm
# from llms.siliconflow_wrapper import sfa_llm
from bs4.element import Comment
import chardet
from utils.general_utils import extract_and_convert_dates
import asyncio
import json_repair
import os


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


async def general_crawler(url: str, logger) -> (int, dict):
    """
    Return article information dict and flag, negative number is error, 0 is no result, 11 is success

    main work flow:
    first get the content with httpx
    then try to use gne to extract the information
    when fail, try to use a llm to analysis the html
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
        soup = BeautifulSoup(text, "html.parser")

    try:
        result = extractor.extract(text)
    except Exception as e:
        logger.info(f"gne extract error: {e}")
        result = None

    if result['title'].startswith('服务器错误') or result['title'].startswith('您访问的页面') or result[
        'title'].startswith('403') \
            or result['content'].startswith('This website uses cookies') or result['title'].startswith('出错了'):
        logger.warning(f"can not get {url} from the Internet")
        return -7, {}

    if len(result['title']) < 4 or len(result['content']) < 24:
        logger.info(f"gne extract not good: {result}")
        result = None

    if result:
        info = result
        abstract = ''
    else:
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
            logger.debug("failed to parse from llm output")
            return 0, {}

        if 'title' not in decoded_object or 'content' not in decoded_object:
            logger.debug("llm parsed result not good")
            return 0, {}

        info = {'title': decoded_object['title'], 'content': decoded_object['content']}
        abstract = decoded_object.get('abstract', '')
        info['publish_time'] = decoded_object.get('publish_date', '')

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

    date_str = extract_and_convert_dates(info['publish_time'])
    if date_str:
        info['publish_time'] = date_str
    else:
        info['publish_time'] = datetime.strftime(datetime.today(), "%Y%m%d")

    from_site = urlparse(url).netloc
    from_site = from_site.replace('www.', '')
    from_site = from_site.split('.')[0]
    info['content'] = f"[from {from_site}] {info['content']}"

    try:
        meta_description = soup.find("meta", {"name": "description"})
        if meta_description:
            info['abstract'] = f"[from {from_site}] {meta_description['content'].strip()}"
        else:
            if abstract:
                info['abstract'] = f"[from {from_site}] {abstract.strip()}"
            else:
                info['abstract'] = ''
    except Exception:
        if abstract:
            info['abstract'] = f"[from {from_site}] {abstract.strip()}"
        else:
            info['abstract'] = ''

    info['url'] = url
    return 11, info
