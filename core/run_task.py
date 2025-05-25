# -*- coding: utf-8 -*-
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# import logging
# logging.getLogger("httpx").setLevel(logging.WARNING)

import asyncio
from general_process import main_process, wiseflow_logger, pb
from core.async_database import init_database, cleanup_database

counter = 0

async def schedule_task():
    global counter
    
    # 预初始化数据库
    try:
        await init_database()
    except Exception as e:
        wiseflow_logger.error(f"Failed to initialize database: {e}")
        return
    
    try:
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
            wiseflow_logger.info('task execute loop finished, work after 3600 seconds')
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        wiseflow_logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        wiseflow_logger.error(f"Unexpected error in main loop: {e}")
    finally:
        # 清理数据库资源
        await cleanup_database()

asyncio.run(schedule_task())