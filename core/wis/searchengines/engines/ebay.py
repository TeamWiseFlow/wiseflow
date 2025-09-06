from urllib.parse import quote
from lxml import html
from ..utils import extract_text


def gen_query_url(query: str, page_number: int = 1, **kwargs) -> dict:
    base_url = "https://www.ebay.com"
    return f'{base_url}/sch/i.html?_nkw={quote(query)}&_sacat={page_number}'


def parse_response(response_text: str) -> list[dict]:
    results = []

    dom = html.fromstring(response_text)
    results_xpath = '//li[contains(@class, "s-item")]'
    url_xpath = './/a[contains(@class, "s-item__link")]/@href'
    title_xpath = './/span[@role="heading"]//text()'
    content_xpath = './/div[@span="SECONDARY_INFO"]'
    price_xpath = './/span[contains(@class, "s-item__price")]//text()'
    shipping_xpath = './/span[contains(@class, "s-item__shipping")]/text()'
    source_country_xpath = './/span[contains(@class, "s-item__location")]/text()'
    thumbnail_xpath = './/img[@class="s-item__image-img"]/@src'

    results_dom = dom.xpath(results_xpath)
    if not results_dom:
        return []

    for result_dom in results_dom:
        url = extract_text(result_dom.xpath(url_xpath))
        title = extract_text(result_dom.xpath(title_xpath))
        if not title or title == 'Shop on eBay':
            continue
        content = extract_text(result_dom.xpath(content_xpath))
        price = extract_text(result_dom.xpath(price_xpath))
        shipping = extract_text(result_dom.xpath(shipping_xpath))
        source_country = extract_text(result_dom.xpath(source_country_xpath))
        thumbnail = extract_text(result_dom.xpath(thumbnail_xpath))

        results.append(
            {
                'url': url,
                'title': title,
                'content': content,
                'price': price,
                'shipping': shipping,
                'source_country': source_country,
                'thumbnail': thumbnail,
            }
        )

    return results
