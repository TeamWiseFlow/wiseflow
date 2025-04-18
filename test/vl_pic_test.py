import asyncio
import time
import sys
import re, os

# 将core目录添加到Python路径
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(core_path)
from dotenv import load_dotenv
env_path = os.path.join(core_path, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

from llms.openai_wrapper import openai_llm as llm


vl_models = ["glm-4v-flash"]
pic_url_test_list = ["https://img1.utuku.imgcdc.com/593x0/mili/20250114/af9e4eb4-ffb6-48f3-93fd-c2df50ab2d31.jpg",
"https://img3.utuku.imgcdc.com/650x0/news/20250114/04988522-ee50-419e-94f9-0f47e995d4ac.png",
"https://img3.utuku.imgcdc.com/300x300/news/20250302/a8782be0-d3f5-4ebb-996c-2f74742d8684.jpg",
"https://www.yicai.com/images/logo.png",
"http://wx.qlogo.cn/mmhead/Q3auHgzwzM4Rq0U14VV5UicYPnWw8I9eZ8g6TJ2ltAROQcBxbsxwVKg/0",
"https://p5.itc.cn/q_70,c_lfill,w_140,h_140,g_face/mpbp/pro/20220718/fdf45c289c514d0fa8363cceaacd9b07.png",
"https://mmbiz.qpic.cn/mmbiz_png/fRg3eJSOt2ur70INyK0A4etnkPmZnicOhKcT07w4keGiahyh7RbMgwATwNTUxjVypeKkd6C9syHmwE1WFIrXedcg/640?wxfrom=12&tp=wxpic&usePicPrefetch=1&wx_fmt=png&amp;from=appmsg",
"https://img.36krcdn.com/hsossms/20241221/v2_40c28bcceafc4905b8612d6dce7a6a2a@000000_oswg116731oswg1280oswg545_img_000?x-oss-process=image/resize,m_mfit,w_600,h_400,limit_0/crop,w_600,h_400,g_center",
"http://mmbiz.qpic.cn/mmbiz_png/K85bvE9rzFOgDvibAsz4S0sZqv4O8spfH2mhvOMWicLDRMib7xiaWTMhGnAmXK7qoxQafrSw4XH0r88XbJ6aVAydqw/300?wx_fmt=png",
"https://bootcdn.xuexi.cn/18600410326/bd19863611993ad460d1c23fa910fc00.png",
"https://bootcdn.xuexi.cn/18600410326/69830c9e173b5374aa9b6de43a912e4d.png",
"https://mmbiz.qpic.cn/sz_mmbiz_jpg/pvJcCtibswvCzE7n9LFakd4GTkhwDjrgx4W9lMvGjXgjr8zukPOPjB8mbTnMrNasicoXTk0X8oicrALjThVowyeHA/640?wx_fmt=jpeg&from=appmsg",
"https://imgs.ali213.net/news/IndexTJ/2021/07/30/2021073015457698.jpg",
"https://q0.itc.cn/c_lfill,w_300,h_200,g_face/images01/20250123/f7d23f1c7a0c4c368ce5ed4108a8c008.jpeg",
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
