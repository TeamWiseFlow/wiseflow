from pathlib import Path
from urllib.parse import urlparse
import re
from .simple_crawler import simple_crawler
import httpx
from bs4 import BeautifulSoup
from bs4.element import Comment
from llms.dashscope_wrapper import dashscope_llm
from datetime import datetime, date
from requests.compat import urljoin
import chardet
from general_utils import extract_and_convert_dates


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


# qwen1.5-72b解析json格式太容易出错，网页上的情况太多，比如经常直接使用英文的"，这样后面json.loads就容易出错……
sys_info = '''你是一个html网页解析器，你将接收一段用户从网页html文件中提取的文本，请解析出其标题、摘要、内容和发布日期，发布日期格式为YYYY-MM-DD。
结果请按照以下格式返回（整体用三引号包裹）：
"""
标题||摘要||内容||发布日期XXXX-XX-XX
"""
'''


def llm_crawler(url: str | Path, logger) -> (int, dict):
    """
    返回文章信息dict和flag，负数为报错，0为没有结果，11为成功
    参考：https://mp.weixin.qq.com/s/4J-kofsfFDiV1FxGlTJLfA
    """
    # 发送 HTTP 请求获取网页内容
    try:
        with httpx.Client() as client:
            response = client.get(url, headers=header, timeout=30)
            rawdata = response.content
            encoding = chardet.detect(rawdata)['encoding']
            text = rawdata.decode(encoding)
    except Exception as e:
        logger.error(e)
        return -7, {}

    # 使用 BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(text, "html.parser")
    html_text = text_from_soup(soup)
    html_lines = html_text.split('\n')
    html_lines = [line.strip() for line in html_lines if line.strip()]
    html_text = "\n".join(html_lines)
    if len(html_text) > 29999:
        logger.warning(f"{url} content too long for llm parsing")
        return 0, {}

    if not html_text or html_text.startswith('服务器错误') or html_text.startswith('您访问的页面') or html_text.startswith('403')\
            or html_text.startswith('出错了'):
        logger.warning(f"can not get {url} from the Internet")
        return -7, {}

    messages = [
        {"role": "system", "content": sys_info},
        {"role": "user", "content": html_text}
    ]
    llm_output = dashscope_llm(messages, "qwen1.5-72b-chat", logger=logger)
    try:
        info = parse_html_content(llm_output)
    except Exception:
        msg = f"can not parse {llm_output}"
        logger.debug(msg)
        return 0, {}

    if len(info['title']) < 4 or len(info['content']) < 24:
        logger.debug(f"{info} not valid")
        return 0, {}

    info["url"] = str(url)
    # 提取图片链接，提取不到就空着
    image_links = []
    images = soup.find_all("img")

    for img in images:
        try:
            # 不是所有网站都是这个结构，比如公众号文章的就不行。
            image_links.append(img["src"])
        except KeyError:
            continue
    info["images"] = image_links

    # 提取作者信息，提取不到就空着
    author_element = soup.find("meta", {"name": "author"})
    if author_element:
        info["author"] = author_element["content"]
    else:
        info["author"] = ""

    if not info['abstract']:
        meta_description = soup.find("meta", {"name": "description"})
        if meta_description:
            info['abstract'] = meta_description["content"]
        else:
            info['abstract'] = ''

    return 11, info


def general_scraper(site: str, expiration: date, existing: list[str], logger) -> list[dict]:
    try:
        with httpx.Client() as client:
            response = client.get(site, headers=header, timeout=30)
    except Exception as e:
        logger.error(e)
        return []

    page_source = response.text
    soup = BeautifulSoup(page_source, "html.parser")
    # 解析出全部超链接网址
    parsed_url = urlparse(site)
    base_url = parsed_url.scheme + '://' + parsed_url.netloc
    urls = [urljoin(base_url, link["href"]) for link in soup.find_all("a", href=True)]
    if not urls:
        logger.warning(f"can not find any link from {site}, maybe it's an article site...")
        if site in existing:
            logger.debug(f"{site} has been crawled before, skip it")
            return []
        flag, result = simple_crawler(site, logger)
        if flag != 11:
            flag, result = llm_crawler(site, logger)
            if flag != 11:
                return []
        publish_date = datetime.strptime(result['publish_time'], '%Y%m%d')
        if publish_date.date() < expiration:
            logger.debug(f"{site} is too old, skip it")
            return []
        else:
            return [result]
    # 再逐步解析文章，依然是先使用simple_crawler, 不行再用llm_crawler
    articles = []
    for url in urls:
        if url in existing:
            logger.debug(f"{url} has been crawled before, skip it")
            continue
        existing.append(url)
        flag, result = simple_crawler(url, logger)
        if flag != 11:
            flag, result = llm_crawler(url, logger)
            if flag != 11:
                continue
        publish_date = datetime.strptime(result['publish_time'], '%Y%m%d')
        if publish_date.date() < expiration:
            logger.debug(f"{url} is too old, skip it")
        else:
            articles.append(result)

    return articles
