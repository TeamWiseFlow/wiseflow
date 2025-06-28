# the request url generate and result parse solution copied from https://github.com/searxng/searxng
# only fitable for china mainland users

import urllib.parse
from lxml import html
import time
from typing import Tuple
from wis import AsyncWebCrawler
from web_crawler_configs import DEFAULT_CRAWLER_CONFIG


bing_search_url = "https://www.bing.com/search"
default_params = {
    "kl": "zh-CN",
    "p": 1,
    "count": 10,
}

def gen_query_url(query, page=1, **kwargs):
    params = default_params.copy()
    params["q"] = query
    params["first"] = (page - 1) * params["count"] + 1
    url = f"{bing_search_url}?{urllib.parse.urlencode(params)}"
    # 时间范围处理（保持原有功能）
    time_range = kwargs.get('time_range')
    if time_range:
        unix_day = int(time.time() / 86400)
        time_ranges = {'day': '1', 'week': '2', 'month': '3', 'year': f'5_{unix_day-365}_{unix_day}'}
        if time_range in time_ranges:
            url += f'&filters=ex1:"ez{time_ranges[time_range]}"'
    return url

async def search_with_bing(query: str, existings: set=set()) -> Tuple[str, dict]:
    search_url = gen_query_url(query)
    run_config = DEFAULT_CRAWLER_CONFIG.clone()
    run_config.check_robots_txt = False
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(search_url, run_config)
    if not result or not result.success:
        return '', {}
    
    markdown = ''
    link_dict = {}
    tree = html.fromstring(result.html)
    
    # 提取搜索结果 - 使用 bing_test.py 的XPath选择器
    for el in tree.xpath('//li[@class="b_algo"]'):
        title_el = el.xpath('.//h2/a')
        if not title_el:
            continue
            
        title = title_el[0].text_content()
        url = title_el[0].get("href")
        if not title or not url:
            continue
        if url in existings:
            continue

        content_el = el.xpath('.//div[@class="b_caption"]/p')
        content = content_el[0].text_content() if content_el else ""
        
        key = f"[{len(link_dict)+1}]"
        link_dict[key] = url
        markdown += f"* {key}{title}\n"
        if content:
            content = content.replace("\n", " ")
            markdown += f"{content}{key}\n"
        markdown += "\n"
        
    return markdown, link_dict
