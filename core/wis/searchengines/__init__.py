import asyncio
import httpx
import importlib
from datetime import datetime
from async_logger import wis_logger
from ..basemodels import CrawlResult
from typing import List, Tuple

# The unified search entry for every engine under `engines/`.
# Signature is kept consistent with `search_with_jina`, with an extra
# `engine` argument specifying which engine implementation to use.

async def search_with_engine(engine: str, query: str, existings: set[str] = set(), **kwargs) -> Tuple[List[CrawlResult], str, dict]:
    """Search given *query* with the specified *engine*.

    Parameters
    ----------
    engine : str
        Name of the engine module under ``engines`` folder.
    query : str
        Search query string.
    existings : set[str], optional
        URLs that have already been collected – duplicates will be skipped.

    Returns
    -------
    Tuple[List[CrawlResult], str, dict]
        A tuple of search result dictionaries, the markdown content, and the link dictionary.
    """
    # --- locate engine implementation ------------------------------------------------
    try:
        engine_module = importlib.import_module(f"wis.searchengines.engines.{engine}")
    except ImportError as e:
        wis_logger.error(f"Engine '{engine}' not found: {e}")
        return [], "", {}

    max_retries = 3
    base_delay = 10  # seconds
    search_results = []

    for attempt in range(max_retries):
        try:
            # Build HTTP request from engine implementation
            request_params = await engine_module.request(query, **kwargs)

            if not request_params:
                wis_logger.warning(f"Engine '{engine}' returned invalid request parameters: {request_params}")
                return [], "", {}

            if "url" not in request_params:
                wis_logger.warning(f"Engine '{engine}' returned invalid request parameters: {request_params}")
                return [], "", {}

            method = request_params.get("method", "GET").upper()
            url = request_params["url"]
            headers = request_params.get("headers")
            cookies = request_params.get("cookies")

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.request(method, url, headers=headers, cookies=cookies, timeout=30)

            if response.status_code != 200:
                raise httpx.HTTPStatusError("Unexpected status", request=None, response=response)

            # Parse response
            search_results = await engine_module.parse_response(response.text, **kwargs)

        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                wis_logger.warning(
                    f"{engine} search attempt {attempt + 1} failed with error: {str(e)}, retrying in {delay} seconds"
                )
                await asyncio.sleep(delay)
            else:
                wis_logger.error(
                    f"{engine} search failed after {max_retries} attempts with error: {str(e)}"
                )
                return [], "", {}
    
    articles = []
    markdown = ""
    link_dict = {}
    for result in search_results:
        if engine == "ebay":
            # for ebay engine, we treat the result as post list, need to generate the markdown and link_dict
            url = result.get("url")
            if not url or url in existings:
                continue
            title = result.get("title", "") or ""
            title = title.replace("\n", " ")
            content = result.get("content", "") or ""
            content = content.replace("\n", " ")
            # test code
            if content:
                print(f'ebay do have contente! {content}')
            price = result.get("price", "")
            shipping = result.get("shipping", "")
            source_country = result.get("source_country", "")

            key = f"[{len(link_dict)+1}]"
            link_dict[key] = url
            markdown += f"* {key}{title}\nPrice: {price} Shipping: {shipping}\nSource Country: {source_country} {key}\n\n"

        elif engine == "github":
            # for github engine, we treat the result as post list, need to generate the markdown and link_dict
            # the content in search result is the description of the repo, we need to get the full content from the url
            # but there's a chance the full content crawler will fail, in this case, at least we still can get every infos here and more links...
            url = result.get("url")
            if not url or url in existings:
                continue
            title = result.get("title", "")
            content = result.get("content", "")
            publish_date = result.get("publishedDate")
            if (not title and not content) or (not publish_date):
                continue
            if len(content) > 500:
                content = content[:500] + '...'
            tags = ', '.join(result.get("tags", [])) or ""
            # homepage = result.get("homepage", "") or ""
            license = result.get("license_name", "") or ""
            popularity = result.get("popularity", "") or ""
            maintainer = result.get("maintainer", "") or ""
            # Convert datetime to date string format
            date_str = publish_date.strftime("%Y-%m-%d") if isinstance(publish_date, datetime) else str(publish_date)
            key = f"[{len(link_dict)+1}]"
            link_dict[key] = url
            markdown += f"* {key}{title}\nLicense: {license} Popularity: {popularity}\nTags: {tags}\nMaintainer: {maintainer}\n{content}{key}\n\n"
        
        elif engine == "arxiv":
            # for arxiv engine, we have to treat the result as an article, because the url in the result is just the summary page
            # user should only use wiseflow as an information collector to find the potiencial interesting articles, and then use the url to get the full pdf
            url = result.get("url")
            if not url or url in existings:
                continue
            title = result.get("title", "")
            content = result.get("content", "") or ""
            content = content.replace("\n", " ")
            if not title and not content:
                continue
            authors = ' & '.join(result.get("authors", [])) or ""
            comments = result.get("comments", "") or ""
            journal = result.get("journal", "") or ""
            publish_date = result.get("publishedDate", "").strftime("%Y-%m-%d") or ""
            tags = ', '.join(result.get("tags", [])) or ""
            _markdown = ""
            if journal:
                journal = journal.replace("\n", " ")
                _markdown += f"Journal: {journal}\n"
            if tags:
                _markdown += f"Tags: {tags}\n"
            if comments:
                comments = comments.replace("\n", " ")
                _markdown += f"Comments: {comments}\n"
            _markdown += content
            articles.append(CrawlResult(url=url, 
                                        title=title, 
                                        markdown=_markdown,
                                        author=authors,
                                        publish_date=publish_date))

    return articles, markdown, link_dict
