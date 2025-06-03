# -*- coding: utf-8 -*-
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# import logging
# logging.getLogger("httpx").setLevel(logging.WARNING)

import asyncio
from general_process import main_process
from core.async_logger import wis_logger
from async_database import init_database, cleanup_database, db_manager

counter = 0

async def schedule_task():
    global counter
    
    # 预初始化数据库
    await init_database()
    
    try:
        while True:
            wis_logger.info(f'task execute loop {counter + 1}')
            tasks = await db_manager.get_activated_focus_points_with_sources()
            jobs = []
            for task in tasks:
                focus = task['focus_point']
                sources = task['sources']
                if not focus['per_hour'] or not focus['focuspoint']:
                    continue
                if counter % focus['per_hour'] != 0:
                    continue
                jobs.append(main_process(focus, sources))

            counter += 1
            await asyncio.gather(*jobs)
            wis_logger.info('task execute loop finished, work after 3600 seconds')
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        wis_logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        wis_logger.error(f"Unexpected error in main loop: {e}")
    finally:
        # 清理数据库资源
        await cleanup_database()

asyncio.run(schedule_task())
