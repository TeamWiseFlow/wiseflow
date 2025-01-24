# -*- coding: utf-8 -*-
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

import asyncio
from general_process import main_process, wiseflow_logger, pb

counter = 0

async def schedule_task():
    global counter
    while True:
        wiseflow_logger.info(f'task execute loop {counter + 1}')
        tasks = pb.read('focus_points', filter='activated=True')
        sites_record = pb.read('sites')
        jobs = []
        for task in tasks:
            if not task['per_hour'] or not task['focuspoint']:
                continue
            if counter % task['per_hour'] != 0:
                continue
            sites = [_record for _record in sites_record if _record['id'] in task['sites']]
            jobs.append(main_process(task, sites))

        counter += 1
        await asyncio.gather(*jobs)
        wiseflow_logger.info(f'task execute loop finished, work after 3600 seconds')
        await asyncio.sleep(3600)

asyncio.run(schedule_task())