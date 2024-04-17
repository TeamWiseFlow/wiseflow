"""
通过编辑这个脚本，可以自定义需要的后台任务
"""
import schedule
import time
from work_process import ServiceProcesser
from pb_api import pb

sp = ServiceProcesser()
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
    counter += 1
    print(f'\033[0;32mtask execute loop {counter}\033[0m')
    print(urls)
    if urls:
        sp(sites=urls)
    else:
        if counter % 24 == 0:
            sp()


schedule.every().hour.at(":38").do(task)

while True:
    schedule.run_pending()
    time.sleep(60)
