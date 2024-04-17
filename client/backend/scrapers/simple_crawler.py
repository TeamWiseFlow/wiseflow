from gne import GeneralNewsExtractor
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from general_utils import extract_and_convert_dates
import chardet
from get_logger import get_logger
import os

extractor = GeneralNewsExtractor()
header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/604.1 Edg/112.0.100.0'}

project_dir = os.environ.get("PROJECT_DIR", "")
os.makedirs(project_dir, exist_ok=True)
logger = get_logger(name='simple_crawler', file=os.path.join(project_dir, f'simple_crawler.log'))


def simple_crawler(url: str | Path) -> (int, dict):
    """
    返回文章信息dict和flag，负数为报错，0为没有结果，11为成功
    """
    try:
        with httpx.Client() as client:
            response = client.get(url, headers=header, timeout=30)
            rawdata = response.content
            encoding = chardet.detect(rawdata)['encoding']
            text = rawdata.decode(encoding)
        result = extractor.extract(text)
    except Exception as e:
        logger.warning(f"cannot get content from {url}\n{e}")
        return -7, {}

    if not result:
        logger.error(f"gne cannot extract {url}")
        return 0, {}

    if len(result['title']) < 4 or len(result['content']) < 24:
        logger.info(f"{result} not valid")
        return 0, {}

    if result['title'].startswith('服务器错误') or result['title'].startswith('您访问的页面') or result['title'].startswith('403')\
            or result['content'].startswith('This website uses cookies') or result['title'].startswith('出错了'):
        logger.warning(f"can not get {url} from the Internet")
        return -7, {}

    date_str = extract_and_convert_dates(result['publish_time'])
    if date_str:
        result['publish_time'] = date_str
    else:
        result['publish_time'] = datetime.strftime(datetime.today(), "%Y%m%d")

    soup = BeautifulSoup(text, "html.parser")
    try:
        meta_description = soup.find("meta", {"name": "description"})
        if meta_description:
            result['abstract'] = meta_description["content"].strip()
        else:
            result['abstract'] = ''
    except Exception:
        result['abstract'] = ''

    result['url'] = str(url)
    return 11, result
