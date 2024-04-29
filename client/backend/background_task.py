"""
通过编辑这个脚本，可以自定义需要的后台任务
"""
import schedule
import time
import os
from work_process import ServiceProcesser
from general_utils import get_logger_level
from loguru import logger
from pb_api import PbTalker

project_dir = os.environ.get("PROJECT_DIR", "")
os.makedirs(project_dir, exist_ok=True)
logger_file = os.path.join(project_dir, 'scanning_task.log')
dsw_log = get_logger_level()

logger.add(
    logger_file,
    level=dsw_log,
    backtrace=True,
    diagnose=True,
    rotation="50 MB"
)
pb = PbTalker(logger)

sp = ServiceProcesser(pb=pb, logger=logger)
counter = 0


# 每小时唤醒一次，如果pb的sites表中有信源，会挑取符合周期的信源执行，没有没有的话，则每24小时执行专有爬虫一次
def task():
    global counter
    sites = pb.read('sites', filter='activated=True')
    urls = []
    for site in sites:
        if not site['per_hours'] or not site['url']:
            continue
        if counter % site['per_hours'] == 0:
            urls.append(site['url'])
    print(f'\033[0;32m task execute loop {counter}\033[0m')
    print(urls)
    if urls:
        sp(sites=urls)
    else:
        if counter % 24 == 0:
            sp()
        else:
            print('\033[0;33mno work for this loop\033[0m')
    counter += 1


schedule.every().hour.at(":38").do(task)

task()
while True:
    schedule.run_pending()
    time.sleep(60)
