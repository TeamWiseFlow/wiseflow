import asyncio
import time
import sys
import re, os

# 将core目录添加到Python路径
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(core_path)

from llms.openai_wrapper import openai_llm as llm


vl_models = ['deepseek-ai/Janus-Pro-7B']
pic_url_test_list = ["http://wx.qlogo.cn/mmhead/Q3auHgzwzM55VjAUib4ibtDJzRJYl2Cn7gptSxwhmyyvdBwkS9SwUQtQ/0",
"http://mmbiz.qpic.cn/mmbiz_png/Oe1ibnzkdE2PQc84CVcyiaW9Cw7KssCq2dGXrHsRxscWHySXrTkaLBJ5Jw7ztaRE9d3l5yayXfDAYmDXRFuqyLAA/0?wx_fmt=png",
"http://mmbiz.qpic.cn/mmbiz_jpg/DhKPeHFI5HhgEgSGl8CMdNgo3dovxjhnCKLukmF18OtpHDE9IcwlyNT0xTQ28oFrfa4tDW4yQSicOpFY3SNCd5w/0?wx_fmt=jpeg",
"http://mmbiz.qpic.cn/mmbiz_png/CM7KBM0HLAiaj8f0bEAIa9EfPtI8Kd374zjaiaRTiaz8z2CMyJZDtnaAekuK4bEBllicqiclPUh87SeeAcfEvpUWgYA/0?wx_fmt=png",
"http://wx.qlogo.cn/mmhead/Q3auHgzwzM4Rq0U14VV5UicYPnWw8I9eZ8g6TJ2ltAROQcBxbsxwVKg/0",
"http://mmbiz.qpic.cn/sz_mmbiz_png/Bcdib1U6AjwVmSic6l8qbibZfvensdLfcjmNlpz8wjm3cgwJibwXaAgzuGU7vYXDnsJ3fbgOUFHtNQH4iaBGBm43iccg/0?wx_fmt=png",
"https://mmbiz.qpic.cn/mmbiz_png/fRg3eJSOt2ur70INyK0A4etnkPmZnicOhKcT07w4keGiahyh7RbMgwATwNTUxjVypeKkd6C9syHmwE1WFIrXedcg/640?wxfrom=12&tp=wxpic&usePicPrefetch=1&wx_fmt=png&amp;from=appmsg",
"https://img.36krcdn.com/hsossms/20241221/v2_40c28bcceafc4905b8612d6dce7a6a2a@000000_oswg116731oswg1280oswg545_img_000?x-oss-process=image/resize,m_mfit,w_600,h_400,limit_0/crop,w_600,h_400,g_center",
"http://mmbiz.qpic.cn/mmbiz_png/K85bvE9rzFOgDvibAsz4S0sZqv4O8spfH2mhvOMWicLDRMib7xiaWTMhGnAmXK7qoxQafrSw4XH0r88XbJ6aVAydqw/300?wx_fmt=png",
"https://bootcdn.xuexi.cn/18600410326/bd19863611993ad460d1c23fa910fc00.png",
"https://bootcdn.xuexi.cn/18600410326/69830c9e173b5374aa9b6de43a912e4d.png",
"https://bootcdn.xuexi.cn/18600410326/0458c43bba70d60ca77d6f158835dd6c.png",
"https://bootcdn.xuexi.cn/18600410326/1398b93f1f4273536e56e8899ad46d17.png",
"https://bootcdn.xuexi.cn/18600410326/963274d57bd3c27e3c262984887c9e48.png",
]

async def extract_text_from_url(url):
    for model in vl_models:
        print(f"running {model} ...\n")
        start_time = time.time()
        llm_output = await llm([{"role": "user",
                                "content": [{"type": "image_url", "image_url": {"url": url, "detail": "high"}},
                                {"type": "text", "text": "提取图片中的所有文字，如果图片不包含文字或者文字很少或者你判断图片仅是网站logo、商标、图标等，则输出NA。注意请仅输出提取出的文字，不要输出别的任何内容。"}]}],
        model=model)
        print(f"output: \n{llm_output}\n")
        print(f"time spent: {time.time() - start_time}\n")


if __name__ == '__main__':
    for url in pic_url_test_list:
        print(f"testing {url} ...\n")
        asyncio.run(extract_text_from_url(url))
