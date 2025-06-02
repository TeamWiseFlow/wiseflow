import httpx
import feedparser
from global_config import wis_logger
from async_database import db_manager
from wis import CrawlResult
from typing import List, Tuple


async def fetch_rss(url) -> Tuple[List[CrawlResult], str, dict]:
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
            wis_logger.debug(f"No content found for {article_url} from rss: {url}, using summary or description")
            for key in ['summary', 'description']:
                if key in entry:
                    description = entry[key]
                    break
        # 3. 如果还是没有内容，跳过
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
            continue
        if description and article_url != url:
            key = f"[{len(link_dict)+1}]"
            link_dict[key] = article_url
            markdown += f"* {description} (Author: {author} Publish Date: {publish_date}) {key}\n"
    # TODO: 需要把 results 写入数据库
    return results, markdown, link_dict