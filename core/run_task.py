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

from custom_processes import crawler_config_map

import asyncio
from general_process import main_process
from async_logger import wis_logger
from async_database import AsyncDatabaseManager

loop_counter = 0

async def graceful_shutdown(crawlers, db_manager):
    """优雅关闭：仅清理资源，不再全量取消其它任务，避免噪音异常"""

    wis_logger.debug("Cleaning up resources...")
    try:
        if crawlers.get("web"):
            wis_logger.debug("Closing web crawler...")
            try:
                await asyncio.wait_for(crawlers["web"].close(), timeout=8.0)
            except asyncio.TimeoutError:
                wis_logger.warning("Closing web crawler timed out after 8s; continue shutting down")
            except Exception as e:
                wis_logger.warning(f"Error closing web crawler: {e}")
            else:
                wis_logger.debug("Web crawler closed")

        wis_logger.debug("Cleaning up database...")
        await db_manager.cleanup()
        wis_logger.debug("Database cleanup completed")
        
    except Exception as e:
        wis_logger.warning(f"Error during resource cleanup: {e}")

async def schedule_task():
    # initialize if any error, will raise exception
    db_manager = AsyncDatabaseManager()
    await db_manager.initialize()
    crawlers = {}
    for platform in ALL_PLATFORMS:
        if platform == "web":
            crawler = AsyncWebCrawler(crawler_config_map=crawler_config_map, db_manager=db_manager)
            try:
                await crawler.start()
                crawlers[platform] = crawler
            except Exception as e:
                wis_logger.warning(f"initialize {platform} crawler failed: {e}, will abort all the sources for {platform}")
        elif platform == KUAISHOU_PLATFORM_NAME:
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
    except asyncio.CancelledError:
        wis_logger.info("Event loop cancelled, shutting down...")
    except KeyboardInterrupt:
        wis_logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        wis_logger.error(f"Unexpected error in main loop: {e}")
    finally:
        # 优雅关闭：先取消所有正在运行的任务，再清理资源
        try:
            await asyncio.wait_for(
                graceful_shutdown(crawlers, db_manager), 
                timeout=15.0
            )
        except asyncio.TimeoutError:
            wis_logger.warning("Graceful shutdown timed out after 15 seconds")
        except Exception as e:
            wis_logger.error(f"Error during graceful shutdown: {e}")

try:
    asyncio.run(schedule_task())
except (KeyboardInterrupt, asyncio.CancelledError):
    pass
