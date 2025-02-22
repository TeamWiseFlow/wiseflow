import httpx
import uuid
import os

zhipu_api_key = os.getenv('ZHIPU_API_KEY', '')

async def run_v4_async(query: str, _logger=None):
    if not zhipu_api_key:
        if _logger:
            _logger.warning("ZHIPU_API_KEY is not set")
        else:
            print("ZHIPU_API_KEY is not set")
        return None

    msg = [
        {
            "role": "user", 
            "content": query
        }
    ]
    tool = "web-search-pro"
    url = "https://open.bigmodel.cn/api/paas/v4/tools"
    request_id = str(uuid.uuid4())
    data = {
        "request_id": request_id,
        "tool": tool,
        "stream": False,
        "messages": msg
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            json=data,
            headers={'Authorization': zhipu_api_key},
            timeout=300
        )
        result = resp.json()
        result = result['choices'][0]['message']['tool_calls']
        if len(result) == 0:
            return {'search_intent': [{'intent': 'Unkown Reason Failed', 'keywords': ''}]}, {'search_result': []}
        elif len(result) == 1:
            return result[0], {'search_result': []}
        else:
            return result[0], result[1]

if __name__ == '__main__':
    test_list = [#'广东全省的台风预警——仅限2024年的信息',
             #'大模型技术突破与创新——包括新算法与模型，新的研究成果',
             #'事件图谱方面的知识',
             #'人工智能领军人物介绍',
             #'社区治理',
             #'新获批的氢能项目——60万吨级别以上',
             '新技术(文章主要内容必须是介绍某项智能汽车相关的新技术，且日期在2025年1月之后，并对提及的新技术进行摘要，格式如：新技术名称、新技术简要描述、行业应用情况（如有）)',
             #'各地住宅网签最新数据——2025年1月6日以后'
             ]

    async def main():
        from pprint import pprint
        tasks = [run_v4_async(query) for query in test_list]
        results = await asyncio.gather(*tasks)
        for query, (intent, content) in zip(test_list, results):
            print('test bigmodel...')
            pprint(intent)
            print('\n')
            pprint(content)
            print('\n')

    import asyncio
    asyncio.run(main())
