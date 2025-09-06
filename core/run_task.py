# -*- coding: utf-8 -*-
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

from wis import (
    KuaiShouCrawler,
    WeiboCrawler,
    ALL_PLATFORMS,
    KUAISHOU_PLATFORM_NAME,
    WEIBO_PLATFORM_NAME,
    AsyncWebCrawler,
)

import asyncio
from general_process import main_process
from async_logger import wis_logger
from async_database import AsyncDatabaseManager
from custom_processes import crawler_config_map

loop_counter = 0

async def schedule_task():
    # initialize if any error, will raise exception
    db_manager = AsyncDatabaseManager()
    await db_manager.initialize()
    crawlers = {}
    for platform in ALL_PLATFORMS:
        if platform == KUAISHOU_PLATFORM_NAME:
            try:
                ks_crawler = KuaiShouCrawler(db_manager=db_manager)
                await ks_crawler.async_initialize()
                crawlers[KUAISHOU_PLATFORM_NAME] = ks_crawler
            except Exception as e:
                wis_logger.warning(f"initialize kuaishou crawler failed: {e}, will abort all the sources for kuaishou platform")
        elif platform == WEIBO_PLATFORM_NAME:
            try:
                wb_crawler = WeiboCrawler(db_manager=db_manager)
                await wb_crawler.async_initialize()
                crawlers[WEIBO_PLATFORM_NAME] = wb_crawler
            except Exception as e:
                wis_logger.warning(f"initialize weibo crawler failed: {e}, will abort all the sources for weibo platform")
        elif platform == 'web':
            try:
                web_crawler = AsyncWebCrawler(crawler_config_map=crawler_config_map, db_manager=db_manager)
                await web_crawler.start()
                crawlers[platform] = web_crawler
            except Exception as e:
                wis_logger.warning(f"initialize web crawler failed: {e}, will abort all the sources for web platform and search engines")
        else:
            raise ValueError(f"platform {platform} not supported")

    global loop_counter
    try:
        while True:
            wis_logger.info(f'task execute loop {loop_counter + 1}')
            tasks = await db_manager.get_activated_focus_points_with_sources()
            jobs = []
            for task in tasks:
                focus = task['focus_point']
                sources = task['sources']
                if not focus:
                    continue
                if not focus['freq'] or not focus['focuspoint']:
                    continue
                if loop_counter % focus['freq'] != 0:
                    continue
                jobs.append(main_process(focus, sources, crawlers, db_manager))
            loop_counter += 1
            await asyncio.gather(*jobs)
            wis_logger.info('task execute loop finished, work after 3600 seconds')
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        wis_logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        wis_logger.error(f"Unexpected error in main loop: {e}")
    finally:
        # 清理数据库资源
        try:
            if "web" in crawlers:
                await crawlers["web"].close()
            await db_manager.cleanup()
            wis_logger.debug("Database cleanup completed")
        except Exception as e:
            wis_logger.error(f"Database cleanup failed: {e}")

asyncio.run(schedule_task())
