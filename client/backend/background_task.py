"""
通过编辑这个脚本，可以自定义需要的后台任务
"""
import schedule
import time
from work_process import ServiceProcesser

sp = ServiceProcesser()


def task():
    with open('../sites.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f.readlines() if line.strip()]
    sp(sites=urls)


# 每天凌晨1点运行任务
schedule.every().day.at("01:17").do(task)

while True:
    schedule.run_pending()
    time.sleep(60)
