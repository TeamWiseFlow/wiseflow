from gne import GeneralNewsExtractor
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import re


extractor = GeneralNewsExtractor()
header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/604.1 Edg/112.0.100.0'}


def simple_crawler(url: str | Path, logger=None) -> (int, dict):
    """
    返回文章信息dict和flag，负数为报错，0为没有结果，11为成功
    """
    try:
        response = requests.get(url, header, timeout=60)
    except:
        if logger:
            logger.error(f"cannot connect {url}")
        else:
            print(f"cannot connect {url}")
        return -7, {}

    if response.status_code != 200:
        if logger:
            logger.error(f"cannot connect {url}")
        else:
            print(f"cannot connect {url}")
        return -7, {}

    text = response.text
    result = extractor.extract(text)
    if not result or not result['title'] or not result['content']:
        if logger:
            logger.error(f"gne cannot extract {url}")
        else:
            print(f"gne cannot extract {url}")
        return 0, {}

    if result['title'].startswith('服务器错误') or result['title'].startswith('您访问的页面') or result['title'].startswith('403'):
        if logger:
            logger.warning(f"can not get {url} from the Internet")
        else:
            print(f"can not get {url} from the Internet")
        return -7, {}

    date_str = re.findall(r"\d{4}-\d{2}-\d{2}", result['publish_time'])
    if date_str:
        result['publish_time'] = date_str[0]
    else:
        date_str = re.findall(r"\d{4}\d{2}\d{2}", result['publish_time'])
        if date_str:
            result['publish_time'] = date_str[0]
        else:
            result['publish_time'] = datetime.strftime(datetime.today(), "%Y%m%d")

    soup = BeautifulSoup(text, "html.parser")
    try:
        meta_description = soup.find("meta", {"name": "description"})
        if meta_description:
            result['abstract'] = meta_description["content"]
        else:
            result['abstract'] = ''
    except:
        result['abstract'] = ''

    result['url'] = str(url)
    return 11, result
