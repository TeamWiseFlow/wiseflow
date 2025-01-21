from exa_search import search_with_exa
import time
from pprint import pprint
import requests
import uuid

api_key = ''

def run_v4_sync(query: str):
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

    resp = requests.post(
        url,
        json=data,
        headers={'Authorization': api_key},
        timeout=300
    )
    result = resp.json()
    return result['choices'][0]['message']


test_list = ['广东全省的台风预警——仅限2024年的信息',
             '大模型技术突破与创新——包括新算法与模型，新的研究成果',
             '事件图谱方面的知识',
             '人工智能领军人物介绍',
             '社区治理',
             '新获批的氢能项目——60万吨级别以上',
             '氢能项目招标信息——2024年12月以后',
             '各地住宅网签最新数据——2025年1月6日以后']

for query in test_list:
    print(query)
    print('\n')
    print('test bigmodel...')
    start_time = time.time()
    print(run_v4_sync(query))
    end_time = time.time()
    print(f"bigmodel time: {end_time - start_time}")
    print('\n')
    print('*' * 25)