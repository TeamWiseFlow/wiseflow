from scrapers.simple_crawler import simple_crawler
from typing import Union
from pathlib import Path
import requests
import re
import json
from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup


# 国内的应用场景，sogou搜索应该不错了，还支持weixin、百科搜索
# 海外的应用场景可以考虑使用duckduckgo或者google_search的sdk
# 尽量还是不要自己host一个搜索引擎吧，虽然有类似https://github.com/StractOrg/stract/tree/main的开源方案，但毕竟这是两套工程
def search_insight(keyword: str, logger, exist_urls: list[Union[str, Path]], knowledge: bool = False) -> (int, list):
    """
    搜索网页
    :param keyword: 要搜索的主题
    :param exist_urls: 已经存在的url列表，即这些网页已经存在，搜索结果中如果出现则跳过
    :param knowledge: 是否搜索知识
    :param logger: 日志
    :return: 返回文章信息列表list[dict]和flag，负数为报错，0为没有结果，11为成功
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44",
    }
    # 如果knowledge参数为真，则意味着搜索概念知识，这时只会搜索sogou百科
    # 默认是搜索新闻资讯，同时搜索sogou网页和资讯
    if knowledge:
        url = f"https://www.sogou.com/sogou?query={keyword}&insite=baike.sogou.com"
    else:
        url = quote(f"https://www.sogou.com/web?query={keyword}", safe='/:?=.')
    relist = []
    try:
        r = requests.get(url, headers=headers)
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        item_list = soup.find_all(class_='struct201102')
        for items in item_list:
            item_prelist = items.find(class_="vr-title")
            # item_title = re.sub(r'(<[^>]+>|\s)', '', str(item_prelist))
            href_s = item_prelist.find(class_="", href=True)
            href = href_s["href"]
            if href[0] == "/":
                href_f = redirect_url("https://www.sogou.com" + href)
            else:
                href_f = href
            if href_f not in exist_urls:
                relist.append(href_f)
    except Exception as e:
        logger.error(f"search {url} error: {e}")

    if not knowledge:
        url = f"https://www.sogou.com/sogou?ie=utf8&p=40230447&interation=1728053249&interV=&pid=sogou-wsse-7050094b04fd9aa3&query={keyword}"
        try:
            r = requests.get(url, headers=headers)
            html = r.text
            soup = BeautifulSoup(html, 'html.parser')
            item_list = soup.find_all(class_="news200616")
            for items in item_list:
                item_prelist = items.find(class_="vr-title")
                # item_title = re.sub(r'(<[^>]+>|\s)', '', str(item_prelist))
                href_s = item_prelist.find(class_="", href=True)
                href = href_s["href"]
                if href[0] == "/":
                    href_f = redirect_url("https://www.sogou.com" + href)
                else:
                    href_f = href
                if href_f not in exist_urls:
                    relist.append(href_f)
        except Exception as e:
            logger.error(f"search {url} error: {e}")

    if not relist:
        return -7, []

    # 这里仅使用simple_crawler, 因为search行为要快
    results = []
    for url in relist:
        if url in exist_urls:
            continue
        exist_urls.append(url)
        flag, value = simple_crawler(url, logger)
        if flag != 11:
            continue
        from_site = urlparse(url).netloc
        if from_site.startswith('www.'):
            from_site = from_site.replace('www.', '')
            from_site = from_site.split('.')[0]
            if value['abstract']:
                value['abstract'] = f"({from_site} 报道){value['abstract']}"
            value['content'] = f"({from_site} 报道){value['content']}"
        value['images'] = json.dumps(value['images'])
        results.append(value)

    if results:
        return 11, results
    return 0, []


def redirect_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    }
    r = requests.get(url, headers=headers, allow_redirects=False)  # 不允许重定向
    if r.status_code == 302:
        real_url = r.headers.get('Location')
    else:
        real_url = re.findall("URL='(.*?)'", r.text)[0]
    return real_url
