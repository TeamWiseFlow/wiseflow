import httpx
import feedparser
from async_logger import wis_logger
from wis import CrawlResult
from typing import List, Tuple


async def fetch_rss(url, existings: set=set()) -> Tuple[List[CrawlResult], str, dict]:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
        content = response.content  # bytes
        parsed = feedparser.parse(content)
    except Exception as e:
        wis_logger.error(f"Error fetching RSS from {url}: {e}")
        return []
    
    if parsed.get("bozo", False):
        wis_logger.error(f"Error parsing RSS from {url}: {parsed.get('bozo_exception', '')}")
        return []
    
    results = []
    markdown = ''
    link_dict = {}
    for entry in parsed.entries:
        html_parts = []
        description = ''
        article_url = entry.get('link', url)
        if article_url in existings:
            continue
        # 1. 如果 entry 有 content 字段，遍历每个 content_item
        if 'content' in entry:
            for content_item in entry.content:
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
        publish_date = entry.get('published', '')
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
