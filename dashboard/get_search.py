from .simple_crawler import simple_crawler
from .mp_crawler import mp_crawler
from typing import Union
from pathlib import Path
import requests
import re
from urllib.parse import quote
from bs4 import BeautifulSoup
import time


def search_insight(keyword: str, logger, exist_urls: list[Union[str, Path]], knowledge: bool = False) -> (int, list):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44",
    }
    # If the knowledge parameter is true, it means searching for conceptual knowledge, then only sogou encyclopedia will be searched
    # The default is to search for news information, and search for sogou pages and information at the same time
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

    results = []
    for url in relist:
        if url in exist_urls:
            continue
        exist_urls.append(url)
        if url.startswith('https://mp.weixin.qq.com') or url.startswith('http://mp.weixin.qq.com'):
            flag, article = mp_crawler(url, logger)
            if flag == -7:
                logger.info(f"fetch {url} failed, try to wait 1min and try again")
                time.sleep(60)
                flag, article = mp_crawler(url, logger)
        else:
            flag, article = simple_crawler(url, logger)

        if flag != 11:
            continue

        results.append(article)

    if results:
        return 11, results
    return 0, []


def redirect_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    }
    r = requests.get(url, headers=headers, allow_redirects=False)
    if r.status_code == 302:
        real_url = r.headers.get('Location')
    else:
        real_url = re.findall("URL='(.*?)'", r.text)[0]
    return real_url
