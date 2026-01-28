# -*- coding: utf-8 -*-
import asyncio, schedule, threading, time
from core.warm_up import prepare_to_work
from core.wis import SqliteCache, MAIN_CACHE_FILE
from datetime import datetime, timezone
from core.async_logger import wis_logger
from core.wis.ws_connect import notify_user, notify_user_sync, ask_user
from core.async_database import AsyncDatabaseManager
import copy, random
from core.wis.config import load_runtime_overrides, config
import time, sys


# 时间段定义：从配置的起始时间开始，每 6 小时一个时间段
def _parse_start_time(start_str: str) -> tuple[int, int]:
    try:
        hh, mm = start_str.split(":", 1)
        hour, minute = int(hh), int(mm)
        if 0 <= hour < 24 and 0 <= minute < 60:
            return hour, minute
        raise ValueError("out of range")
    except Exception:
        wis_logger.warning("TIME_SLOTS_START 配置无效，使用默认 00:00")
        return 0, 0


def generate_time_slots() -> dict:
    start_str = config.get('TIME_SLOTS_START', '00:00')
    hour, minute = _parse_start_time(start_str)
    names = ['first', 'second', 'third', 'fourth']
    slots = {}
    for i, name in enumerate(names):
        h = (hour + 6 * i) % 24
        slots[name] = f"{h:02d}:{minute:02d}"
    return slots


TIME_SLOTS = generate_time_slots()

def calculate_limit_hours(updated_str: str) -> int:
    """
    计算 limit_hours: task 的 updated 时间距当前时间的小时数+6
    
    Args:
        updated_str: ISO 8601 格式的时间字符串，如 "2025-09-30T10:30:45.123Z"
    
    Returns:
        limit_hours: 时间差的小时数 + 6
    """
    try:
        # 解析 ISO 8601 格式的时间字符串
        updated_time = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
        current_time = datetime.now(timezone.utc)
        
        # 计算时间差
        time_diff = current_time - updated_time
        hours_diff = int(time_diff.total_seconds() / 3600)
        
        if hours_diff < 18:
            return 24
        return hours_diff + 6
    except Exception as e:
        wis_logger.warning(f"计算 limit_hours 失败: {e}, 使用默认值 24")
        return 24  # 默认值

async def execute_time_slot_tasks(time_slot: str):
    """执行指定时间段的任务，每次都重新初始化所有资源"""
    db_manager = cache_manager = None
    crawlers = {}
    try:
        # 1. 初始化资源
        db_manager = AsyncDatabaseManager(logger=wis_logger)
        await db_manager.initialize()
        
        # 2. 获取任务并分析所需平台
        all_tasks = await db_manager.list_tasks(only_activated=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        if all_tasks:
            all_tasks = [task for task in all_tasks if task['time_slots'] and time_slot in task['time_slots']]
        if not all_tasks:
            wis_logger.info(f"{time_slot} 时段没有可执行的任务")
            await notify_user(7, [date_str, time_slot])
            return
        
        # 打印任务id，方便排查问题，后面跟踪不到了
        task_ids = ', #'.join((str(task['id']) + ' ' + (task['title'] or "") for task in all_tasks))
        msg = f"{date_str} {time_slot} 工作时段开始了"
        wis_logger.info(f"{msg}: #{task_ids}")

        # 3. 分析所需的平台
        required_platforms = set()
        to_do_tasks = []
        task_job_count = {}
        for task in all_tasks:
            task_id = task['id']
            focuses = task['focuses']
            if not focuses:
                wis_logger.info(f"任务 {task['id']} 未设定关注点，跳过")
                continue
            
            sources = task['sources']
            search = task['search']

            # 状态检查
            status = task['status']
            errors = task['errors']
            if status == 2:
                wis_logger.info(f"任务 {task['id']} 存在待用户解决的错误：{" | ".join(errors)}, 跳过")
                await notify_user(80, [str(task['id']), " | ".join(errors)])
                continue
            
            if not sources and not search:
                await notify_user(6, [str(task['id'])])
                continue
            
            required_platforms.update(search)
                
            # 从源列表中提取平台类型
            for source in sources:
                if source.get('type'):
                    required_platforms.add(source['type'])
                
            if 'bing' in search or 'github' in search:
                # bing 和 github 需要 web 支持
                required_platforms.add('web')

            task_job_count[task_id] = {'count': len(focuses), 'status': 0, 'msg': set(), 'apply_count': 0, 'total_processed': 0, 
                                        'crawl_failed': 0, 'info_added': 0, 'start_time': time.perf_counter()}
                
            # 计算当前任务的 limit_hours
            limit_hours = calculate_limit_hours(task.get('updated', ''))
                
            for focus in focuses:
                # 对 sources 和 search 做深度 copy 并打乱顺序，避免并发瞬间访问同一网站
                sources_copy = copy.deepcopy(sources) if sources else []
                search_copy = copy.deepcopy(search) if search else []
                random.shuffle(sources_copy)
                random.shuffle(search_copy)
                to_do_tasks.append((task_id, focus, sources_copy, search_copy, limit_hours))
        
        if not to_do_tasks:
            await notify_user(7, [date_str, time_slot])
            return
        
        # 4. work prepare, user account check/initialize crawlers/execute pre-login
        crawlers = {platform: None for platform in required_platforms}
        cache_manager = SqliteCache(db_path=MAIN_CACHE_FILE, default_namespace='articles')
        await cache_manager.open()

        load_runtime_overrides()
        
        try:
            await prepare_to_work(db_manager, cache_manager, crawlers)
        except RuntimeError as e:
            exp = str(e)
            # 13\70\197\198
            if exp in ['70', '13']:
                await notify_user(int(exp))
            elif exp == '197':
                await notify_user(92, [date_str, time_slot, task_ids])
            elif exp == '198':
                await notify_user(93, [date_str, time_slot])
            else:
                wis_logger.warning(f"unknown error during {date_str} {time_slot} prepare to work: {e}")
            return
            
        except Exception as e:
            wis_logger.warning(f"check on {date_str} {time_slot} startup failed by the cause: {e}")
            await ask_user(199, [str(e)])
        
        await notify_user(2, [task_ids])
        await notify_user(25)

        from core.general_process import main_process

        # 任务包装器，确保无论何时都能获得task_id
        def create_task_wrapper(task_id, focus, sources, search, limit_hours, crawlers, db_manager, cache_manager):
            async def wrapper():
                status, msg, apply_count, recorder = await main_process(focus, sources, search, limit_hours, crawlers, db_manager, cache_manager)
                return task_id, status, msg, apply_count, recorder
            return asyncio.create_task(wrapper())
        
        jobs = [create_task_wrapper(task_id, focus, sources, search, limit_hours, crawlers, db_manager, cache_manager) 
                for task_id, focus, sources, search, limit_hours in to_do_tasks]
        
        # 5. 流式执行任务
        wis_logger.info(f"{date_str} {time_slot} 时间段拆解出 {len(jobs)} 个有效关注点，开始流式执行...")
        
        # 用于跟踪已完成的任务数量
        completed_count = 0
        total_tasks = len(jobs)
        
        try:
            async def process_completed_tasks():
                nonlocal completed_count
                for coro in asyncio.as_completed(jobs):
                    try:
                        result = await coro
                        await process_single_result(result, task_job_count, db_manager)
                    except asyncio.TimeoutError:
                        # 重新抛出 TimeoutError，让外层处理（包括账户错误导致的终止）
                        raise
                    except Exception as e:
                        # 任何已知错误都应该在 main_process 中被捕获，并根据情况反应在 statue 和 warning_msg 中，这里捕获的都应该是程序错误
                        wis_logger.error(f"single task process error during {date_str} {time_slot} work: {e}")
                        # await notify_user(5, [])
                    
                    completed_count += 1
                    if completed_count >= total_tasks:
                        break
            # 设置总体超时时间
            await asyncio.wait_for(
                process_completed_tasks(),
                timeout=5*3600+50*60  # 5小时50分钟超时
            )
            
        except asyncio.TimeoutError as e:
            error_msg = str(e)
            if "Critical account error" in error_msg or "Client version too low" in error_msg:
                wis_logger.warning(f"⚠ {date_str} {time_slot} 时段任务因账户错误终止执行，取消所有未完成的任务: {error_msg}")
            else:
                wis_logger.warning(f"⚠ {date_str} {time_slot} 时段任务执行超时, 取消所有未完成的任务")
                await notify_user(26, [date_str, time_slot])
            # 分离已完成和未完成的任务
            pending_tasks = []
            for task in jobs:
                if not task.done():
                    task.cancel()
                    pending_tasks.append(task)
            
            # 只等待被取消的未完成任务完成
            if pending_tasks:
                await asyncio.gather(*pending_tasks, return_exceptions=True)
        
        wis_logger.info(f"{date_str} {time_slot} 时段工作已结束，共处理 {completed_count}/{total_tasks} 个任务")
        await notify_user(3, [time_slot, str(completed_count), str(total_tasks)])
        # next_job = schedule.next_run()
        # if next_job: 
        #     await notify_user(4, [next_job.strftime('%Y-%m-%d %H:%M:%S')])

    except Exception as e:
        wis_logger.error(f"✗ {time_slot} 时段工作执行失败: {e}")
        await ask_user(199, [str(e)])
    
    finally:
        # 7. 清理资源
        await graceful_shutdown(crawlers, db_manager, cache_manager)

async def process_single_result(result, task_job_count, db_manager):
    """处理单个任务的结果"""
    task_id, status, msg, apply_count, recorder = result
    
    # 检查严重的账户错误，需要立即终止所有任务
    if status in [97, 98, 99]:
        await notify_user(status, [str(task_id)])
        raise asyncio.TimeoutError(f"Critical account error detected (status: {status})")
    elif status == 91:
        await notify_user(91, [])
        raise asyncio.TimeoutError(f"Client version too low, need update (status: {status})")
    elif status == 88:
        await notify_user(status, [str(task_id)])
        msg.add("network_issue")
        
    if status != 2:
        status = 1 if msg else 0

    task_job_count[task_id]['status'] = max(task_job_count[task_id]['status'], status)
    task_job_count[task_id]['msg'].update(msg)
    task_job_count[task_id]['apply_count'] += apply_count
    task_job_count[task_id]['total_processed'] += recorder.total_processed
    task_job_count[task_id]['crawl_failed'] += recorder.crawl_failed
    task_job_count[task_id]['info_added'] += recorder.info_added

    task_job_count[task_id]['count'] -= 1
    if task_job_count[task_id]['count'] == 0:
        error_msg = task_job_count[task_id]['msg']
        if task_job_count[task_id]['total_processed'] == 0:
            error_msg.add("no_processed_urls")
            task_job_count[task_id]['status'] = max(task_job_count[task_id]['status'], 1)
        cost_time = time.perf_counter() - task_job_count[task_id]['start_time']
        # 将耗时 cost_time 换算成分钟，保留1位小数
        cost_time_min = round(cost_time / 60, 1)
        wis_logger.info(f"✓ # {task_id} 任务执行完成, status: {task_job_count[task_id]['status']}, msg: {' | '.join(error_msg)}")
        wis_logger.info(f"total_processed_urls: {task_job_count[task_id]['total_processed']}, crawl_failed: {task_job_count[task_id]['crawl_failed']}, "
                        f"info_added: {task_job_count[task_id]['info_added']}(extract stat not included), "
                        f"apply_count: {task_job_count[task_id]['apply_count']}, cost_time: {cost_time_min} 分钟")
        await notify_user(1, [str(task_id), str(cost_time_min), str(task_job_count[task_id]['total_processed']), 
                             str(task_job_count[task_id]['crawl_failed']), str(task_job_count[task_id]['info_added']), 
                             str(task_job_count[task_id]['apply_count'])])
        # 如果存在警告信息，则通知用户
        if error_msg:
            await notify_user(0, list(error_msg))

        task_id = await db_manager.update_task(task_id, status=task_job_count[task_id]['status'], errors=error_msg, 
                                               updated=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
        if task_id is None:
            wis_logger.warning(f"✗ 任务状态更新失败: {task_id}")
            await notify_user(11, [str(task_id)])

def run_time_slot_task_in_thread(time_slot: str):
    def run_task():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(execute_time_slot_tasks(time_slot))
        except Exception as e:
            wis_logger.error(f"子线程执行失败: {e}")
        finally:
            loop.close()
    
    thread = threading.Thread(target=run_task, name=f"TimeSlot-{time_slot}")
    thread.daemon = True
    thread.start()

async def graceful_shutdown(crawlers, db_manager, cache_manager):
    """优雅关闭：清理资源"""
    # 先等 1s，让残存任务完成
    await asyncio.sleep(1)
    try:
        # 清理爬虫
        if "web" in crawlers and crawlers["web"]:
            if hasattr(crawlers["web"], "close"):
                try:
                    await asyncio.wait_for(crawlers["web"].close(), timeout=8.0)
                    wis_logger.debug("✓ Browser 资源已清理")
                except Exception as e:
                    wis_logger.warning(f"✗ Browser 资源清理失败: {e}")
        
        # 清理缓存和数据库
        if cache_manager:
            try:
                await cache_manager.close()
                wis_logger.debug("✓ 缓存管理器已清理")
            except Exception as e:
                wis_logger.warning(f"✗ 缓存清理失败: {e}")
        
        if db_manager:
            try:
                await db_manager.cleanup()
                wis_logger.debug("✓ 数据库管理器已清理")
            except Exception as e:
                wis_logger.warning(f"✗ 数据库清理失败: {e}")
        
        # 确保所有 pending 任务被驱动完成，避免在 run() 退出后遗留到已关闭的事件循环
        pending = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        if pending:
            for t in pending:
                t.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
    
    except Exception as e:
        wis_logger.warning(f"资源清理过程出错: {e}")

def setup_schedule():
    """设置定时任务"""
    wis_logger.debug("设置定时调度...")
    schedule.clear()
    current_slots = generate_time_slots()
    for time_slot, time_str in current_slots.items():
        schedule.every().day.at(time_str).do(run_time_slot_task_in_thread, time_slot)
    wis_logger.info("设置定时调度完成")

async def check_on_startup():
    # 在程序启动时，先进行，目的是先确认用户状态、引导用户完成相关社交平台和预登录网站的登录
    # 因为任务执行可能放到晚上或者凌晨，用户不一定在电脑旁，所以有必要趁用户刚打开程序时都先检查一下
    db_manager = cache_manager = None
    crawlers = {}
    try:
        # 1. 初始化资源
        db_manager = AsyncDatabaseManager(logger=wis_logger)
        await db_manager.initialize()
        
        # 2. 分析所需的平台
        required_platforms = set(config.get('ALL_PLATFORMS', []))
        if 'rss' in required_platforms:
            required_platforms.add('web')
            required_platforms.remove('rss')

        # 3. work prepare, user account check/initialize crawlers/execute pre-login
        crawlers = {platform: None for platform in required_platforms}
        await prepare_to_work(db_manager, cache_manager, crawlers)

        # 4. just a remainder
        all_tasks = await db_manager.list_tasks(only_activated=True)
        if not all_tasks:
            _ = await ask_user(101, [], timeout=5)

    except RuntimeError as e:
        exp = str(e)
        if exp == '197':
            # 未成功启动任何获取器，无法执行任何任务，请仔细核查相关配置
            await ask_user(100, timeout=5)
            return
        
        if exp == '70':
            # 未正确安装 google chrome，nodriver 连不上
            await ask_user(196, timeout=5)
        if exp in ['13', '198']:
            # 无法连接 wiseflow 服务器，或者是遭遇断网
            await ask_user(198, timeout=5)
        sys.exit(0)
        
    except Exception as e:
        wis_logger.error(f"check on startup failed by the cause: {e}")
        await ask_user(199, [str(e)])

    finally:
        await graceful_shutdown(crawlers, db_manager, cache_manager)

def schedule_task():
    setup_schedule()
    try:
        next_job = schedule.next_run()
        if next_job: 
            notify_user_sync(4, [next_job.strftime('%Y-%m-%d %H:%M:%S')])
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        schedule.clear()
        wis_logger.info("调度器已关闭")
    except Exception as e:
        wis_logger.error(f"调度器异常: {e}")
        schedule.clear()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python run_task.py <time_slot>")
        sys.exit(1)
    
    try:
        asyncio.run(execute_time_slot_tasks(sys.argv[1]))
    except KeyboardInterrupt:
        pass
    