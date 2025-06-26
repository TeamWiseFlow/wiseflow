import base64
import re
import time
from urllib.parse import parse_qs, urlencode, urlparse
from lxml import html

from ..utils import (
    eval_xpath,
    extract_text,
    eval_xpath_list,
    eval_xpath_getindex,
    gen_useragent,
)

base_url = 'https://www.bing.com/search'
"""Bing (Web) search URL"""


def _page_offset(pageno):
    return (int(pageno) - 1) * 10 + 1


def set_bing_cookies(cookies_dict, engine_language="en", engine_region="en-US"):
    # Simplified: logger removed, defaults provided
    cookies_dict['_EDGE_CD'] = f'm={engine_region}&u={engine_language}'
    cookies_dict['_EDGE_S'] = f'mkt={engine_region}&ui={engine_language}'
    # print(f"Debug: Bing cookies set: {cookies_dict}") # Optional: for debugging


async def request(query: str, page_number: int = 1, **kwargs) -> dict:
    """构建 Bing 搜索请求"""
    # Simplified: traits.get_region and traits.get_language removed.
    # Using provided params or defaults for language and region.
    engine_language = kwargs.get('language', 'zh-CN')
    engine_region = kwargs.get('region', 'zh-CN')

    # Build cookies
    cookies = {}
    set_bing_cookies(cookies, engine_language, engine_region)

    query_params = {
        'q': query,
        # if arg 'pq' is missed, sometimes on page 4 we get results from page 1,
        # don't ask why it is only sometimes / its M$ and they have never been
        # deterministic ;)
        'pq': query,
    }

    # To get correct page, arg first and this arg FORM is needed, the value PERE
    # is on page 2, on page 3 its PERE1 and on page 4 its PERE2 .. and so forth.
    # The 'first' arg should never send on page 1.

    if page_number > 1:
        query_params['first'] = _page_offset(page_number)  # see also arg FORM
    if page_number == 2:
        query_params['FORM'] = 'PERE'
    elif page_number > 2:
        query_params['FORM'] = 'PERE%s' % (page_number - 2)

    url = f'{base_url}?{urlencode(query_params)}'

    time_range = kwargs.get('time_range')
    if time_range:
        unix_day = int(time.time() / 86400)
        time_ranges = {'day': '1', 'week': '2', 'month': '3', 'year': f'5_{unix_day-365}_{unix_day}'}
        if time_range in time_ranges:
            url += f'&filters=ex1:"ez{time_ranges[time_range]}"'

    return {
        'url': url,
        'method': 'GET',
        'cookies': cookies,
        'headers': {
            'User-Agent': gen_useragent()
        }
    }


async def parse_response(response_text: str, **kwargs) -> list[dict]:
    """解析 Bing 搜索响应"""
    results = []
    result_len = 0
    page_number = kwargs.get('page_number', 1)

    dom = html.fromstring(response_text)

    # parse results again if nothing is found yet

    for result in eval_xpath_list(dom, '//ol[@id="b_results"]/li[contains(@class, "b_algo")]'):

        link = eval_xpath_getindex(result, './/h2/a', 0, None)
        if link is None:
            continue
        url = link.attrib.get('href')
        title = extract_text(link)

        content = eval_xpath(result, './/p')
        for p in content:
            # Make sure that the element is free of:
            #  <span class="algoSlug_icon" # data-priority="2">Web</span>
            for e in p.xpath('.//span[@class="algoSlug_icon"]'):
                e.getparent().remove(e)
        content = extract_text(content)

        # get the real URL
        if url.startswith('https://www.bing.com/ck/a?'):
            # get the first value of u parameter
            url_query = urlparse(url).query
            parsed_url_query = parse_qs(url_query)
            param_u = parsed_url_query["u"][0]
            # remove "a1" in front
            encoded_url = param_u[2:]
            # add padding
            encoded_url = encoded_url + '=' * (-len(encoded_url) % 4)
            # decode base64 encoded URL
            url = base64.urlsafe_b64decode(encoded_url).decode()

        # append result
        results.append({'url': url, 'title': title, 'content': content})

    # get number_of_results
    if results:
        result_len_container = "".join(eval_xpath(dom, '//span[@class="sb_count"]//text()'))
        if "-" in result_len_container:
            start_str, result_len_container = re.split(r'-\d+', result_len_container)
            start = int(start_str)
        else:
            start = 1

        result_len_container = re.sub('[^0-9]', '', result_len_container)
        if len(result_len_container) > 0:
            result_len = int(result_len_container)

        expected_start = _page_offset(page_number)

        if expected_start != start:
            if expected_start > result_len:
                # Avoid reading more results than available.
                # For example, if there is 100 results from some search and we try to get results from 120 to 130,
                # Bing will send back the results from 0 to 10 and no error.
                # If we compare results count with the first parameter of the request we can avoid this "invalid"
                # results.
                return []

            # Sometimes Bing will send back the first result page instead of the requested page as a rate limiting
            # measure.
            msg = f"Expected results to start at {expected_start}, but got results starting at {start}"
            raise ValueError(msg)

    return results
