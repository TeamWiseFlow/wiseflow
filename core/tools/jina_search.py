import httpx
import os
import asyncio
from typing import Tuple
from global_config import wis_logger

jina_api_key = os.getenv('JINA_API_KEY', '')

async def search_with_jina(query: str) -> Tuple[str, dict]:
    if not jina_api_key:
        wis_logger.warning("JINA_API_KEY is not set")
        return '', {}

    url = 'https://s.jina.ai/'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {jina_api_key}',
        'Content-Type': 'application/json',
        'X-Respond-With': 'no-content'
    }
    data = {
        'q': query
    }

    max_retries = 2
    base_delay = 10  # initial delay in seconds
    markdown = ''
    link_dict = {}
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=30
                )
                result = response.json()
                # Check if the response is successful
                if response.status_code == 200 and result.get('status') == 20000:
                    for item in result.get('data', []):
                        _url = item.get('url', '')
                        if not _url:
                            continue
                        if _url in link_dict:
                            continue
                        title = item.get('title', '')
                        description = item.get('description', '')
                        key = f"[{len(link_dict)+1}]"
                        markdown += f"* title:{title} {key}\ndescription:{description} {key}\n\n"
                        link_dict[key] = _url
                    return markdown, link_dict
                
                # If not successful and not the last attempt, wait and retry
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)  # exponential backoff
                    wis_logger.warning(f"Jina search attempt {attempt + 1} failed, retrying in {delay} seconds")
                    await asyncio.sleep(delay)
                else:
                    wis_logger.error(f"Jina search failed after {max_retries + 1} attempts")
                    return markdown, link_dict

        except Exception as e:
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                wis_logger.warning(f"Jina search attempt {attempt + 1} failed with error: {str(e)}, retrying in {delay} seconds")
                await asyncio.sleep(delay)
            else:
                wis_logger.error(f"Jina search failed after {max_retries + 1} attempts with error: {str(e)}")
                return markdown, link_dict

    return markdown, link_dict

if __name__ == '__main__':
    test_list = ['大语言模型(LLM)最新技术(包括新模型发布，新技术的提出，新的引用等等)',
             '美国关税 特朗普 政策',
             'Chlorogenic acid']

    async def main():
        from pprint import pprint
        tasks = [search_with_jina(query) for query in test_list]
        results = await asyncio.gather(*tasks)
        for query, content in zip(test_list, results):
            print(query)
            pprint(content)
            print('\n')

    import asyncio
    asyncio.run(main())


"""
def search_with_exa(query: str) -> dict:
    headers = {
        "Authorization": "Bearer 1eb13466-23d0-436a-ad78-c65ef904c3fa",
        "Content-Type": "application/json"}

    url = "https://api.exa.ai/search"
    
    payload = {
        "query": query,
        "category": "news",
        "startPublishedDate": "2025-04-08T16:00:00.000Z",
        "endPublishedDate": "2025-04-16T15:59:59.999Z",
        "contents": {
            "text": True
        }
    }
    
    response = httpx.post(url, json=payload, headers=headers, timeout=30)
    return response.json()
"""