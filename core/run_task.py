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
import signal
import sys
from general_process import main_process
from async_logger import wis_logger
from async_database import AsyncDatabaseManager
from custom_processes import crawler_config_map

loop_counter = 0
shutdown_event = asyncio.Event()

def signal_handler(sig, frame):
    """处理 SIGINT 信号 (Ctrl+C)"""
    wis_logger.debug(f"Received signal {sig}, initiating graceful shutdown...")
    shutdown_event.set()

async def cleanup_resources(crawlers, db_manager):
    """清理所有资源"""
    wis_logger.debug("Starting resource cleanup...")
    
    try:
        # 清理 web 爬虫（浏览器资源）
        if "web" in crawlers:
            wis_logger.debug("Closing web crawler...")
            await crawlers["web"].close()
            
        # 清理数据库
        wis_logger.debug("Cleaning up database...")
        await db_manager.cleanup()
        wis_logger.debug("Resource cleanup completed successfully")
        
    except Exception as e:
        wis_logger.warning(f"Error during resource cleanup: {e}")

async def schedule_task():
    # 设置信号处理器
    if sys.platform != 'win32':
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    # initialize if any error, will raise exception
    db_manager = AsyncDatabaseManager()
    await db_manager.initialize()
    crawlers = {}
    
    try:
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
        wis_logger.info("All crawlers initialized successfully, starting main loop...")
        
        while not shutdown_event.is_set():
            try:
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
                
                if jobs:
                    await asyncio.gather(*jobs)
                
                wis_logger.info('task execute loop finished, work after 3600 seconds')
                
                # 使用 wait_for 来允许中断 sleep
                try:
                    await asyncio.wait_for(shutdown_event.wait(), timeout=3600)
                    break  # 如果 shutdown_event 被设置，退出循环
                except asyncio.TimeoutError:
                    continue  # 超时后继续下一个循环
                    
            except asyncio.CancelledError:
                wis_logger.debug("Task cancelled, shutting down...")
                break
            except KeyboardInterrupt:
                wis_logger.debug("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                wis_logger.warning(f"Unexpected error in main loop: {e}")
                # 不退出循环，继续处理
                
    except Exception as e:
        wis_logger.warning(f"Critical error during initialization: {e}")
    finally:
        await cleanup_resources(crawlers, db_manager)

if __name__ == "__main__":
    try:
        asyncio.run(schedule_task())
    except KeyboardInterrupt:
        wis_logger.debug("Program interrupted by user")
    except Exception as e:
        wis_logger.warning(f"Program failed with error: {e}")
    finally:
        wis_logger.debug("Program shutdown complete")
