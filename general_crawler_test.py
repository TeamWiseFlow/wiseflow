from core.custom_process import crawler as general_crawler
from pprint import pprint
import asyncio

test_list = ['http://society.people.com.cn/n1/2024/1202/c1008-40373268.html']

async def crawler_test():
    for test in test_list:
        data = await general_crawler.run([test])
        print(type(data))

if __name__ == '__main__':
    asyncio.run(crawler_test())
