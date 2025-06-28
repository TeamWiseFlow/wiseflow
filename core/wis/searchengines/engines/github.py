from urllib.parse import urlencode
from dateutil import parser
import json


# search-url
search_url = 'https://api.github.com/search/repositories?sort=stars&order=desc&{query}'
accept_header = 'application/vnd.github.preview.text-match+json'


async def request(query: str, **kwargs) -> dict:
    """构建 GitHub 搜索请求"""
    url = search_url.format(query=urlencode({'q': query}))
    
    return {
        'url': url,
        'method': 'GET',
        'headers': {'Accept': accept_header}
    }


async def parse_response(response_text: str, **kwargs) -> list[dict]:
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
                'publishedDate': parser.parse(item.get("updated_at") or item.get("created_at")),
                'tags': item.get('topics', []),
                'popularity': item.get('stargazers_count'),
                'license_name': lic.get('name'),
                # 'license_url': lic_url,
                # 'homepage': item.get('homepage'),
                # 'source_code_url': item.get('clone_url'),
            }
        )

    return results
