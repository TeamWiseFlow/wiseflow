from datetime import datetime
from lxml import etree
from lxml.etree import XPath

from ..utils import eval_xpath_list, eval_xpath_getindex, eval_xpath

# xpaths
arxiv_namespaces = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}
xpath_entry = XPath('//atom:entry', namespaces=arxiv_namespaces)
xpath_title = XPath('.//atom:title', namespaces=arxiv_namespaces)
xpath_id = XPath('.//atom:id', namespaces=arxiv_namespaces)
xpath_summary = XPath('.//atom:summary', namespaces=arxiv_namespaces)
xpath_author_name = XPath('.//atom:author/atom:name', namespaces=arxiv_namespaces)
xpath_doi = XPath('.//arxiv:doi', namespaces=arxiv_namespaces)
xpath_pdf = XPath('.//atom:link[@title="pdf"]', namespaces=arxiv_namespaces)
xpath_published = XPath('.//atom:published', namespaces=arxiv_namespaces)
xpath_journal = XPath('.//arxiv:journal_ref', namespaces=arxiv_namespaces)
xpath_category = XPath('.//atom:category/@term', namespaces=arxiv_namespaces)
xpath_comment = XPath('./arxiv:comment', namespaces=arxiv_namespaces)


async def request(query: str, page_number: int = 1, **kwargs) -> dict:
    number_of_results = 12
    offset = (page_number - 1) * number_of_results

    base_url = (
        'https://export.arxiv.org/api/query?search_query=all:' + '{query}&start={offset}&max_results={number_of_results}'
    )

    string_args = {'query': query, 'offset': offset, 'number_of_results': number_of_results}

    return {'url': base_url.format(**string_args), 'method': 'GET'}


async def parse_response(response_text: str, **kwargs) -> list[dict]:
    # Let errors (e.g., malformed XML) propagate so that the caller can
    # decide how to deal with them. Centralised error handling is performed
    # in `search_with_engine`.
    results = []
    dom = etree.fromstring(response_text.encode('utf-8'))
    
    for entry in eval_xpath_list(dom, xpath_entry):
        title = eval_xpath_getindex(entry, xpath_title, 0).text

        url = eval_xpath_getindex(entry, xpath_id, 0).text
        abstract = eval_xpath_getindex(entry, xpath_summary, 0).text

        authors = [author.text for author in eval_xpath_list(entry, xpath_author_name)]

        #  doi
        doi_element = eval_xpath_getindex(entry, xpath_doi, 0, default=None)
        doi = None if doi_element is None else doi_element.text

        # pdf
        # pdf_element = eval_xpath_getindex(entry, xpath_pdf, 0, default=None)
        # pdf_url = None if pdf_element is None else pdf_element.attrib.get('href')

        # journal
        journal_element = eval_xpath_getindex(entry, xpath_journal, 0, default=None)
        journal = None if journal_element is None else journal_element.text

        # tags
        tag_elements = eval_xpath(entry, xpath_category)
        tags = [str(tag) for tag in tag_elements]

        # comments
        comments_elements = eval_xpath_getindex(entry, xpath_comment, 0, default=None)
        comments = None if comments_elements is None else comments_elements.text

        # Add error handling for publishedDate to maintain robustness
        published_element = eval_xpath_getindex(entry, xpath_published, 0, default=None)
        publishedDate = None
        if published_element is not None and published_element.text:
            publishedDate = datetime.strptime(published_element.text, '%Y-%m-%dT%H:%M:%SZ')

        res_dict = {
            'url': url,
            'title': title,
            'publishedDate': publishedDate,
            'content': abstract,
            'doi': doi,
            'authors': authors,
            'journal': journal,
            'tags': tags,
            'comments': comments,
            # 'pdf_url': pdf_url,
        }

        results.append(res_dict)

    return results
