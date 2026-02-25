import httpx
import feedparser
from reference.async_logger import wis_logger
from reference.wis import CrawlResult, SqliteCache
from typing import List, Tuple
from reference.wis.ws_connect import notify_user
from reference.tools.general_utils import normalize_publish_date
import asyncio


async def fetch_rss(url, existings: set=set(), cache_manager: SqliteCache = None) -> Tuple[List[CrawlResult], str, dict]:
    entries = None
    if cache_manager:
        entries = await cache_manager.get(url, namespace='rss')
        if entries == '**empty**':
            return [], '', {}
        
    if not entries:
        max_retries = 3
        base_delay = 10  # seconds
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                content = response.content  # bytes
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    wis_logger.debug(f"fetching RSS from {url} attempt {attempt + 1} failed with error: {str(e)}, retrying in {delay} seconds")
                    await asyncio.sleep(delay)
                else:
                    wis_logger.warning(f"fetching RSS from {url} failed after {max_retries} attempts with error: {str(e)}")
                    await notify_user(15, [url])
                    return [], '', {}
        
        parsed = feedparser.parse(content)
        if parsed.get("bozo", False):
            wis_logger.warning(f"Error parsing RSS from {url}: {parsed.get('bozo_exception', '')}")
            raise RuntimeError(f"RSS from {url}: {parsed.get('bozo_exception', '')}")
        
        entries = parsed.entries
        if cache_manager:
            await cache_manager.set(url, entries, 60*24, namespace='rss')
    
    results = []
    markdown = ''
    link_dict = {}
    for entry in entries:
        html_parts = []
        description = ''
        article_url = entry.get('link', url)
        if article_url in existings:
            continue
        # 1. 如果 entry 有 content 字段，遍历每个 content_item
        if 'content' in entry and entry['content']:
            for content_item in entry['content']:
                t = content_item.get('type', '').lower()
                if t.startswith('text/') or t == 'application/xhtml+xml':
                    # 尝试多种字段名
                    for key in ['value', 'body', 'content']:
                        if key in content_item:
                            html_parts.append(content_item[key])
                            break
        # 2. 如果没有 content 字段，尝试 summary 或 description
        if not html_parts:
            summary = entry.get('summary', '')
            description = entry.get('description', '')
            if len(summary) > len(description):
                description = summary
            if len(description) > 50:
                html_parts.append(description)
                description = ''

        if not html_parts and not description:
            wis_logger.debug(f"No content or summary or description found for {article_url} from rss: {url}")
            continue
        # 4. 拼接所有内容为一个整体 html
        author = entry.get('author', '')
        title = entry.get('title', '')
        publish_date = normalize_publish_date(entry.get('published', '')) or entry.get('published', '')
        if html_parts:
            html = '\n\n'.join(html_parts)
            results.append(CrawlResult(
                url=article_url,
                html=html,
                title=title,
                author=author,
                publish_date=publish_date,
            ))
            # existings.add(article_url)  will add when llm extracting finished
        elif description and article_url != url:
            key = f"[{len(link_dict)+1}]"
            link_dict[key] = article_url
            markdown += f"* {key}{description} (Author: {author} Publish Date: {publish_date}) {key}\n"
            # existings.add(article_url)  will add when llm extracting finished
    return results, markdown, link_dict
