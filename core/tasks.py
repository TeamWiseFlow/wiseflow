"""
通过编辑这个脚本，可以自定义需要的后台任务
"""
import schedule
import time
from topnews import pipeline
from loguru import logger
from utils.pb_api import PbTalker
import os
from utils.general_utils import get_logger_level
from datetime import datetime, timedelta
import pytz
import requests


project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)
logger_file = os.path.join(project_dir, 'tasks.log')
dsw_log = get_logger_level()
logger.add(
    logger_file,
    level=dsw_log,
    backtrace=True,
    diagnose=True,
    rotation="50 MB"
)

pb = PbTalker(logger)
utc_now = datetime.now(pytz.utc)
# 减去一天得到前一天的UTC时间
utc_yesterday = utc_now - timedelta(days=1)
utc_last = utc_yesterday.strftime("%Y-%m-%d %H:%M:%S")


def task():
    """
    global counter
    sites = pb.read('sites', filter='activated=True')
    urls = []
    for site in sites:
        if not site['per_hours'] or not site['url']:
            continue
        if counter % site['per_hours'] == 0:
            urls.append(site['url'])
    logger.info(f'\033[0;32m task execute loop {counter}\033[0m')
    logger.info(urls)
    if urls:
        sp(sites=urls)
    else:
        if counter % 24 == 0:
            sp()
        else:
            print('\033[0;33mno work for this loop\033[0m')
    counter += 1
    """
    global utc_last
    logger.debug(f'last_collect_time: {utc_last}')
    datas = pb.read(collection_name='insights', filter=f'updated>="{utc_last}"', fields=['id', 'content', 'tag', 'articles'])
    logger.debug(f"got {len(datas)} items")
    utc_last = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    logger.debug(f'now_utc_time: {utc_last}')

    tags = pb.read(collection_name='tags', filter=f'activated=True')
    tags_dict = {item["id"]: item["name"] for item in tags if item["name"]}
    top_news = {}
    for id, name in tags_dict.items():
        logger.debug(f'tag: {name}')
        data = [item for item in datas if item['tag'] == id]
        topnew = pipeline(data, logger)
        if not topnew:
            logger.debug(f'no top news for {name}')
            continue

        top_news[id] = {}
        for content, articles in topnew.items():
            content_urls = [pb.read('articles', filter=f'id="{a}"', fields=['url'])[0]['url'] for a in articles]
            # 去除重叠内容
            # 如果发现重叠内容，哪个标签长就把对应的从哪个标签删除
            to_skip = False
            for k, v in top_news.items():
                to_del_key = None
                for c, u in v.items():
                    if not set(content_urls).isdisjoint(set(u)):
                        if len(topnew) > len(v):
                            to_skip = True
                        else:
                            to_del_key = c
                        break
                if to_del_key:
                    del top_news[k][to_del_key]
                if to_skip:
                    break
            if not to_skip:
                top_news[id][content] = content_urls

        if not top_news[id]:
            del top_news[id]

    if not top_news:
        logger.info("no top news today")
        return

    # 序列化为字符串
    top_news_text = {"#党建引领基层治理": [],
                     "#数字社区": [],
                     "#优秀活动案例": []}

    for id, v in top_news.items():
        # top_news[id] = {content: '\n\n'.join(urls) for content, urls in v.items()}
        top_news[id] = {content: urls[0] for content, urls in v.items()}
        if id == 's3kqj9ek8nvtthr':
            top_news_text["#数字社区"].append("\n".join(f"{content}\n{urls}" for content, urls in top_news[id].items()))
        elif id == 'qpcgotbqyz3a617':
            top_news_text["#优秀活动案例"].append("\n".join(f"{content}\n{urls}" for content, urls in top_news[id].items()))
        else:
            top_news_text["#党建引领基层治理"].append("\n".join(f"{content}\n{urls}" for content, urls in top_news[id].items()))

    top_news_text = {k: "\n".join(v) for k, v in top_news_text.items()}
    top_news_text = "\n\n".join(f"{k}\n{v}" for k, v in top_news_text.items())
    logger.info(top_news_text)

    data = {
        "wxid": "R:10860349446619856",
        "content": top_news_text
    }
    try:
        response = requests.post("http://localhost:8088/api/sendtxtmsg", json=data)
        if response.status_code == 200:
            logger.info("send message to wechat success")
            time.sleep(1)
            data = {
                "wxid": "R:10860349446619856",
                "content": "[太阳] 今日份的临小助内参来啦！",
                "atlist": ["@all"]
            }
            try:
                response = requests.post("http://localhost:8088/api/sendtxtmsg", json=data)
                if response.status_code == 200:
                    logger.info("send notify to wechat success")
            except Exception as e:
                logger.error(f"send notify to wechat failed: {e}")
    except Exception as e:
        logger.error(f"send message to wechat failed: {e}")


schedule.every().day.at("07:38").do(task)

task()
while True:
    schedule.run_pending()
    time.sleep(60)
