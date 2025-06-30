import urllib.parse
import json
from ..utils import html_to_text


send_accept_language_header = True
"""The HTTP ``Accept-Language`` header is needed for wikis where
LanguageConverter_ is enabled."""

list_of_wikipedias = 'https://meta.wikimedia.org/wiki/List_of_Wikipedias'
"""`List of all wikipedias <https://meta.wikimedia.org/wiki/List_of_Wikipedias>`_
"""

wikipedia_article_depth = 'https://meta.wikimedia.org/wiki/Wikipedia_article_depth'
"""The *editing depth* of Wikipedia is one of several possible rough indicators
of the encyclopedia's collaborative quality, showing how frequently its articles
are updated.  The measurement of depth was introduced after some limitations of
the classic measurement of article count were realized.
"""

rest_v1_summary_url = 'https://{wiki_netloc}/api/rest_v1/page/summary/{title}'
"""
`wikipedia rest_v1 summary API`_:
  The summary response includes an extract of the first paragraph of the page in
  plain text and HTML as well as the type of page. This is useful for page
  previews (fka. Hovercards, aka. Popups) on the web and link previews in the
  apps.

HTTP ``Accept-Language`` header (:py:obj:`send_accept_language_header`):
  The desired language variant code for wikis where LanguageConverter_ is
  enabled.

.. _wikipedia rest_v1 summary API:
   https://en.wikipedia.org/api/rest_v1/#/Page%20content/get_page_summary__title_

"""

wiki_lc_locale_variants = {
    "zh": (
        "zh-CN",
        "zh-HK",
        "zh-MO",
        "zh-MY",
        "zh-SG",
        "zh-TW",
    ),
    "zh-classical": ("zh-classical",),
}
"""Mapping rule of the LanguageConverter_ to map a language and its variants to
a Locale (used in the HTTP ``Accept-Language`` header). For example see `LC
Chinese`_.

.. _LC Chinese:
   https://meta.wikimedia.org/wiki/Wikipedias_in_multiple_writing_systems#Chinese
"""

wikipedia_script_variants = {
    "zh": (
        "zh_Hant",
        "zh_Hans",
    )
}

# Simplified: Removed get_wiki_params, traits, and complex locale logic.
# The request function will now take an optional 'lang' parameter (e.g., "en", "de").
# Defaulting to "en.wikipedia.org".
# The send_accept_language_header is kept, assuming the caller might want to set it.

async def request(query: str, **kwargs) -> dict:
    """构建 Wikipedia 搜索请求"""
    if query.islower():
        query = query.title()

    lang = kwargs.get('language', 'en')
    wiki_netloc = f"{lang}.wikipedia.org"

    title = urllib.parse.quote(query)
    url = rest_v1_summary_url.format(wiki_netloc=wiki_netloc, title=title)
    
    headers = {}
    if send_accept_language_header:
        headers['Accept-Language'] = f'{lang}'

    return {
        'url': url,
        'method': 'GET',
        'headers': headers if headers else None
    }

display_type = ["infobox"]

async def parse_response(response_text: str, **kwargs) -> list[dict]:
    results = []
    api_result = json.loads(response_text)

    if api_result.get('type') == 'https://mediawiki.org/wiki/HyperSwitch/errors/bad_request' and \
       api_result.get('detail') == 'title-invalid-characters':
        return []

    title = html_to_text(api_result.get('titles', {}).get('display') or api_result.get('title', ''))
    wikipedia_link = api_result.get('content_urls', {}).get('desktop', {}).get('page', '')

    if not wikipedia_link or not title:
        return []

    # Get description/content
    description = api_result.get('description', '')
    extract = api_result.get('extract', '')
    content = extract if extract else description

    # Check if we should display this result
    if "list" in display_type or api_result.get('type') != 'standard':
        # show item in the result list if 'list' is in the display options or it
        # is a item that can't be displayed in a infobox.
        result = {
            'url': wikipedia_link, 
            'title': title, 
            'content': content
        }
            
        # Add additional metadata if available
        if 'coordinates' in api_result:
            coords = api_result['coordinates']
            result['coordinates'] = f"{coords.get('lat', '')}, {coords.get('lon', '')}"
        
        results.append(result)

    # Also add infobox result if requested
    if "infobox" in display_type and api_result.get('type') == 'standard':
        infobox_result = {
            'infobox': title,
            'id': wikipedia_link,
            'content': content,
            'urls': [{'title': 'Wikipedia', 'url': wikipedia_link}]
        }
            
        results.append(infobox_result)

    return results
