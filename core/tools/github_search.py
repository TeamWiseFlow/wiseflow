import asyncio
import httpx
from core.async_logger import wis_logger
from typing import Tuple
from urllib.parse import urlencode
import json
from core.wis import SqliteCache
from core.wis.ws_connect import notify_user


def gen_request(query: str) -> dict:
    """构建 GitHub 搜索请求"""
    # search-url
    search_url = 'https://api.github.com/search/repositories?sort=stars&order=desc&{query}'
    accept_header = 'application/vnd.github.preview.text-match+json'
    url = search_url.format(query=urlencode({'q': query}))
    
    return {
        'url': url,
        'method': 'GET',
        'headers': {'Accept': accept_header}
    }

def parse_response(response_text: str) -> list[dict]:
    """解析 GitHub 搜索响应"""
    
    results = []
    data = json.loads(response_text)

    for item in data.get('items', []):
        content = [item.get(i).strip() for i in ['language', 'description'] if item.get(i)]

        # license can be None
        lic = item.get('license') or {}
        #lic_url = None
        # if lic.get('spdx_id'):
            # lic_url = f"https://spdx.org/licenses/{lic.get('spdx_id')}.html"

        results.append(
            {
                'url': item.get('html_url'),
                'title': item.get('full_name'),
                'content': ' / '.join(content),
                # 'thumbnail': item.get('owner', {}).get('avatar_url'),
                # 'package_name': item.get('name'),
                # 'version': item.get('updated_at'),
                'maintainer': item.get('owner', {}).get('login'),
                'publishedDate': item.get("updated_at") or item.get("created_at"),
                'tags': item.get('topics', []),
                'popularity': item.get('stargazers_count'),
                'license_name': lic.get('name'),
                # 'license_url': lic_url,
                # 'homepage': item.get('homepage'),
                # 'source_code_url': item.get('clone_url'),
            }
        )

    return results

async def search_with_github(query: str, existings: set[str] = set(), cache_manager: SqliteCache = None) -> Tuple[str, dict]:
    raw_result = None
    if cache_manager:
        raw_result = await cache_manager.get(query, namespace='github_search')
        if raw_result == '**empty**':
            return '', {}
        
    if not raw_result:
        request_params = gen_request(query)
        max_retries = 3
        base_delay = 10  # seconds
        for attempt in range(max_retries):
            try:
                method = request_params.get("method", "GET").upper()
                url = request_params["url"]
                headers = request_params.get("headers")

                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.request(method, url, headers=headers, timeout=30)
                response.raise_for_status()
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    wis_logger.debug(f"github search attempt {attempt + 1} failed with error: {str(e)}, retrying in {delay} seconds")
                    await asyncio.sleep(delay)
                else:
                    wis_logger.warning(
                        f"github search failed after {max_retries} attempts with error: {str(e)}"
                    )
                    await notify_user(15, ['github'])
                    return "", {}
        
        # Parse response
        raw_result = parse_response(response.text)

        if cache_manager:
            await cache_manager.set(query, raw_result, 60*24, namespace='github_search')
    
    markdown = ""
    link_dict = {}
    for result in raw_result:
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
        # Extract date part from datetime string (format: 2024-01-01T12:00:00Z -> 2024-01-01)
        date_str = publish_date.split('T')[0] if publish_date and 'T' in publish_date else str(publish_date)
        key = f"[{len(link_dict)+1}]"
        link_dict[key] = url
        markdown += f"* {key}{title}\nLicense: {license}\nPopularity: {popularity}\nTags: {tags}\nMaintainer: {maintainer}\n{content}\nPublished Date: {date_str}\n\n"

    return markdown, link_dict
