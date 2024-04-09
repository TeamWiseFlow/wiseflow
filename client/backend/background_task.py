"""
通过编辑这个脚本，可以自定义需要的后台任务
"""
import schedule
import time
from work_process import ServiceProcesser
import configparser

config = configparser.ConfigParser()
config.read('../config.ini')

if config.has_section('sites'):
    web_pages = config['sites']
    urls = [value for key, value in web_pages.items()]
else:
    urls = []

sp = ServiceProcesser()


def task():
    sp(sites=urls)


# 每天凌晨1点运行任务
schedule.every().day.at("01:17").do(task)

while True:
    schedule.run_pending()
    time.sleep(60)
