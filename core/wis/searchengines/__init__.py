import asyncio
import httpx
import importlib
from core.async_logger import wis_logger
from ..basemodels import CrawlResult
from ..async_webcrawler import AsyncWebCrawler
from ..async_cache import SqliteCache
from typing import List, Tuple
from ..ws_connect import notify_user

# The unified search entry for every engine under `engines/`.
# `engine` argument specifying which engine implementation to use.
# two possible crawl method, up to search platform support what
# prior to use httpx, but bing ebay cannot
# use a web-crawler, you can bennifit the cache feature

async def search_with_engine(engine: str, 
                             query: str, 
                             crawler: AsyncWebCrawler, 
                             existings: set[str] = set(), 
                             cache_manager: SqliteCache = None,
                             **kwargs) -> Tuple[List[CrawlResult], str, dict]:
    """Search given *query* with the specified *engine*.

    Parameters
    ----------
    engine : str
        Name of the engine module under ``engines`` folder.
    query : str
        Search query string.
    crawler : AsyncWebCrawler
        The crawler to use for the search.
    existings : set[str], optional
        URLs that have already been collected – duplicates will be skipped.

    Returns
    -------
    Tuple[List[CrawlResult], str, dict]
        A tuple of search result dictionaries, the markdown content, and the link dictionary.
    """
    # --- locate engine implementation ------------------------------------------------
    search_results = []
    if cache_manager:
        search_results = await cache_manager.get(query, namespace=engine)
        if search_results == '**empty**':
            return [], "", {}
        
    if not search_results:
        try:
            engine_module = importlib.import_module(f"wis.searchengines.engines.{engine}")
        except ImportError as e:
            wis_logger.error(f"Engine '{engine}' not found: {e}")
            return [], "", {}
        
        if engine == "arxiv":
            request_params = engine_module.gen_request_params(query, **kwargs)
            method = request_params.get("method", "GET").upper()
            url = request_params["url"]
            async with httpx.AsyncClient(timeout=120) as client:
                for attempt in range(3):
                    try:
                        response = await client.request(method, url)
                        response.raise_for_status
                        break
                    except Exception as e:
                        if attempt < 2:
                            delay = 1 * (2 ** attempt)
                            wis_logger.debug(
                                f"{engine} search attempt {attempt + 1} failed with error: {str(e)}, retrying in {delay} seconds"
                            )
                            await asyncio.sleep(delay)
                        else:
                            wis_logger.warning(
                                f"{engine} search failed after 3 attempts with error: {str(e)}"
                            )
                            await notify_user(15, ['arxiv'])
                            return [], "", {}
            html = response.text

        elif engine == "bing":
            url = engine_module.gen_query_url(query, **kwargs)
            result = await crawler.arun(url)
            if not result or not result.success:
                wis_logger.warning(f"Search with Engine '{engine}', query '{query}', due to crawler, failed")
                await notify_user(15, ['bing'])
                return [], "", {}
            html = result.html

        search_results = engine_module.parse_response(html)
        wis_logger.debug(f"from {engine} got {len(search_results)} search_results")
        if cache_manager:
            await cache_manager.set(query, search_results, 60*24, namespace=engine)

    articles = []
    markdown = ""
    link_dict = {}
    for result in search_results:
        link_url = result.get("url")
        if not link_url or link_url in existings:
            continue
        if engine == "bing":
            title = result.get("title", "")
            content = result.get("content", "")
            if not title and not content:
                continue
            key = f"[{len(link_dict)+1}]"
            link_dict[key] = link_url
            markdown += f"* {key}{title}\n"
            if content:
                content = content.replace("\n", " ")
                markdown += f"{content}{key}\n"
            markdown += "\n"
        
        elif engine == "arxiv":
            # for arxiv engine, we have to treat the result as an article, because the url in the result is just the summary page
            # user should only use wiseflow as an information collector to find the potiencial interesting articles, and then use the url to get the full pdf
            title = result.get("title", "")
            content = result.get("content", "") or ""
            content = content.replace("\n", " ")
            if not title and not content:
                continue
            authors = ' & '.join(result.get("authors", [])) or ""
            comments = result.get("comments", "") or ""
            journal = result.get("journal", "") or ""
            publish_date = result.get("publishedDate", "") or ""
            publish_date = publish_date.split('T')[0] if publish_date and 'T' in publish_date else publish_date
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
            articles.append(CrawlResult(url=link_url, 
                                        title=title, 
                                        markdown=_markdown,
                                        author=authors,
                                        publish_date=publish_date))

    return articles, markdown, link_dict
