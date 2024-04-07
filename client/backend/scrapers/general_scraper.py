from pathlib import Path
from urllib.parse import urlparse
import re
from .simple_crawler import simple_crawler
import json
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from llms.dashscope_wrapper import dashscope_llm
from datetime import datetime, date
from requests.compat import urljoin


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
    # 发现llm出来的结果有时会在键值或者内容的引号外面出现\n \t安全起见全部去除，反正后续分析时llm也不看内容的换行这些
    dict_str = out.strip("```").strip("python").strip("json").strip()
    dict_str = dict_str.replace("\n", "").replace("\t", "")
    # 先正则解析出{}中的内容
    dict_str = re.findall(r'{(.*?)}', dict_str)
    # dict_str = dict_str[0].replace("'", '"') #会误伤
    # json loads 要求双引号, 且需要把\n等转译
    dct = json.loads('{' + dict_str[0] + '}')
    date_str = re.findall(r"\d{4}-\d{2}-\d{2}", dct['publish_time'])
    if date_str:
        dct['publish_time'] = date_str[0].replace("-", "")
    else:
        date_str = re.findall(r"\d{4}\d{2}\d{2}", dct['publish_time'])
        if date_str:
            dct['publish_time'] = date_str[0]
        else:
            dct['publish_time'] = datetime.strftime(datetime.today(), "%Y%m%d")
    return dct


sys_info = """给你一段从网页html文件中提取的所有文本，请尝试输出其标题、摘要、内容和发布日期。
发布日期的格式为：XXXX-XX-XX，如果找不到则为空。内容不要包含标题、作者和发布日期。
输出格式为Python字典，key分别为：title、abstract、content和publish_time。
如果你识别出给定文本大部分既不是中文也不是英文，那么请输出：无法解析。
"""


def llm_crawler(url: str | Path, logger=None) -> (int, dict):
    """
    返回文章信息dict和flag，负数为报错，0为没有结果，11为成功
    参考：https://mp.weixin.qq.com/s/4J-kofsfFDiV1FxGlTJLfA
    测试URL：
    url = "https://so.html5.qq.com/page/real/search_news?docid=70000021_40665eb6afe80152"
    url = "https://mp.weixin.qq.com/s?src=11&timestamp=1709999167&ver=5128&signature=e0Tssc4COc*p-RkKaPwUMrGePUxko8N621VxARnI8uKDg*l5C7Z8gBC6RDUAnyGqvmzJ5WEzvaO-T7GvMRw9LwNaJS3Hh2tyaITdmsaVtY9JsSmsidX6u4SqxirGsRdo&new=1"
    """
    # 发送 HTTP 请求获取网页内容
    try:
        response = requests.get(url, timeout=60)
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
    # todo llm_crawler和simple_crawler这里都需要加个判断，对于乱码和总字符量很少的网页需要排除掉
    # 使用 BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(response.text, "html.parser")
    html_text = text_from_soup(soup)
    html_lines = html_text.split('\n')
    html_lines = [line.strip() for line in html_lines if line.strip()]
    html_text = "\n".join(html_lines)
    if not html_text or html_text.startswith('服务器错误') or html_text.startswith('您访问的页面') or html_text.startswith('403'):
        if logger:
            logger.warning(f"can not get {url} from the Internet")
        else:
            print(f"can not get {url} from the Internet")
        return -7, {}

    messages = [
        {"role": "system", "content": sys_info},
        {"role": "user", "content": html_text}
    ]
    llm_output = dashscope_llm(messages, "qwen1.5-72b-chat", logger=logger)
    try:
        info = parse_html_content(llm_output)
    except Exception as e:
        msg = f"can not parse {llm_output}"
        if logger:
            logger.warning(msg)
        else:
            print(msg)
        return 0, {}

    info["url"] = str(url)
    if not info["title"] or not info["content"]:
        return 0, {}

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


def general_scraper(site: str, expiration: date, existing: list[str], logger=None) -> list[dict]:
    try:
        response = requests.get(site, header, timeout=60)
    except:
        if logger:
            logger.error(f"cannot connect {site}")
        else:
            print(f"cannot connect {site}")
        return []

    if response.status_code != 200:
        if logger:
            logger.error(f"cannot connect {site}")
        else:
            print(f"cannot connect {site}")
        return []

    page_source = response.text
    soup = BeautifulSoup(page_source, "html.parser")
    # 解析出全部超链接网址
    parsed_url = urlparse(site)
    base_url = parsed_url.scheme + '://' + parsed_url.netloc
    urls = [urljoin(base_url, link["href"]) for link in soup.find_all("a", href=True)]
    if not urls:
        if logger:
            logger.warning(f"can not find any link from {site}, maybe it's an article site...")
        if site in existing:
            if logger:
                logger.warning(f"{site} has been crawled before, skip it")
            else:
                print(f"{site} has been crawled before, skip it")
            return []
        flag, result = simple_crawler(site, logger=logger)
        if flag != 11:
            flag, result = llm_crawler(site, logger=logger)
            if flag != 11:
                return []
        publish_date = datetime.strptime(result['publish_time'], '%Y%m%d')
        if publish_date.date() < expiration:
            if logger:
                logger.warning(f"{site} is too old, skip it")
            else:
                print(f"{site} is too old, skip it")
            return []
        else:
            return [result]
    # 再逐步解析文章，依然是先使用simple_crawler, 不行再用llm_crawler
    articles = []
    for url in urls:
        if url in existing:
            if logger:
                logger.warning(f"{url} has been crawled before, skip it")
            else:
                print(f"{url} has been crawled before, skip it")
            continue
        existing.append(url)
        flag, result = simple_crawler(url, logger=logger)
        if flag != 11:
            flag, result = llm_crawler(url, logger=logger)
            if flag != 11:
                continue
        publish_date = datetime.strptime(result['publish_time'], '%Y%m%d')
        if publish_date.date() < expiration:
            if logger:
                logger.warning(f"{url} is too old, skip it")
            else:
                print(f"{url} is too old, skip it")
        else:
            articles.append(result)

    return articles
