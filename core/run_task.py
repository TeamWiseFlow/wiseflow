# -*- coding: utf-8 -*-
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

import asyncio
import os
from general_process import main_process, wiseflow_logger, pb
from task import AsyncTaskManager, Task, create_task_id

# Configure the maximum number of concurrent tasks
MAX_CONCURRENT_TASKS = int(os.environ.get("MAX_CONCURRENT_TASKS", "4"))

# Initialize the task manager
task_manager = AsyncTaskManager(max_workers=MAX_CONCURRENT_TASKS)

async def process_focus_task(focus, sites):
    """Process a focus point task."""
    try:
        await main_process(focus, sites)
        return True
    except Exception as e:
        wiseflow_logger.error(f"Error processing focus point {focus.get('id')}: {e}")
        return False

async def schedule_task():
    """Schedule and manage data mining tasks with improved concurrency."""
    counter = 0
    while True:
        wiseflow_logger.info(f'Task execute loop {counter + 1}')
        tasks = pb.read('focus_points', filter='activated=True')
        sites_record = pb.read('sites')
        
        for task in tasks:
            if not task['per_hour'] or not task['focuspoint']:
                continue
            if counter % task['per_hour'] != 0:
                continue
            
            # Get sites for this focus point
            sites = [_record for _record in sites_record if _record['id'] in task.get('sites', [])]
            
            # Check if there's already a task running for this focus point
            existing_tasks = task_manager.get_tasks_by_focus(task['id'])
            active_tasks = [t for t in existing_tasks if t.status in ["pending", "running"]]
            
            if active_tasks:
                wiseflow_logger.info(f"Focus point {task.get('focuspoint', '')} already has active tasks")
                continue
            
            # Create a new task
            task_id = create_task_id()
            auto_shutdown = task.get("auto_shutdown", False)
            
            focus_task = Task(
                task_id=task_id,
                focus_id=task["id"],
                function=process_focus_task,
                args=(task, sites),
                auto_shutdown=auto_shutdown
            )
            
            # Submit the task
            wiseflow_logger.info(f"Submitting task {task_id} for focus point: {task.get('focuspoint', '')}")
            await task_manager.submit_task(focus_task)
            
            # Save task to database
            task_record = {
                "task_id": task_id,
                "focus_id": task["id"],
                "status": "pending",
                "auto_shutdown": auto_shutdown,
                "metadata": {
                    "focus_point": task.get("focuspoint", ""),
                    "sites_count": len(sites)
                }
            }
            pb.add(collection_name='tasks', body=task_record)

        counter += 1
        wiseflow_logger.info('Task execute loop finished, work after 3600 seconds')
        await asyncio.sleep(3600)

async def main():
    """Main entry point."""
    try:
        wiseflow_logger.info("Starting Wiseflow with concurrent task management...")
        await schedule_task()
    except KeyboardInterrupt:
        wiseflow_logger.info("Shutting down...")
        await task_manager.shutdown()
    except Exception as e:
        wiseflow_logger.error(f"Error in main loop: {e}")
        await task_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())