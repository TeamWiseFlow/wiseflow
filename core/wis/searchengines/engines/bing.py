from urllib.parse import parse_qs, urlencode, urlparse
from lxml import html
from ..utils import eval_xpath, extract_text, eval_xpath_list, eval_xpath_getindex
import base64


def gen_query_url(query, page_number: int = 1, time_range: str = 'day', **kwargs):
    base_url = "https://www.bing.com/search"
    page = page_number
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

    if page > 1:
        query_params['first'] = (page - 1) * 10 + 1
    if page == 2:
        query_params['FORM'] = 'PERE'
    elif page > 2:
        query_params['FORM'] = 'PERE%s' % (page - 2)

    url = f'{base_url}?{urlencode(query_params)}'
    time_ranges = {'day': '1', 'week': '2', 'month': '3'}
    if time_range in time_ranges:
        url += f'&filters=ex1:"ez{time_ranges[time_range]}"'
    return url

def parse_response(response_text: str) -> list[dict]:

    results = []
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

    return results
