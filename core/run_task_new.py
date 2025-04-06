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
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.general_process import main_process, wiseflow_logger, pb
from core.task import AsyncTaskManager, Task, create_task_id
from core.plugins import PluginManager
from core.plugins.connectors import ConnectorBase
from core.plugins.processors import ProcessorBase

# Configure the maximum number of concurrent tasks
MAX_CONCURRENT_TASKS = int(os.environ.get("MAX_CONCURRENT_TASKS", "4"))

# Initialize the task manager
task_manager = AsyncTaskManager(max_workers=MAX_CONCURRENT_TASKS)

# Initialize the plugin manager
plugin_manager = PluginManager(plugins_dir="core")

async def load_plugins():
    """Load and initialize all plugins."""
    wiseflow_logger.info("Loading plugins...")
    plugins = plugin_manager.load_all_plugins()
    wiseflow_logger.info(f"Loaded {len(plugins)} plugins")
    
    # Initialize plugins with configurations
    configs = {}  # Load configurations from database or config files
    results = plugin_manager.initialize_all_plugins(configs)
    
    for name, success in results.items():
        if success:
            wiseflow_logger.info(f"Initialized plugin: {name}")
        else:
            wiseflow_logger.error(f"Failed to initialize plugin: {name}")
    
    return plugins

async def process_focus_point(focus: Dict[str, Any], sites: List[Dict[str, Any]]) -> Any:
    """Process a focus point using the main_process function."""
    wiseflow_logger.info(f"Processing focus point: {focus['focuspoint']}")
    return await main_process(focus, sites)

async def schedule_task():
    """Schedule and manage data mining tasks."""
    # Load plugins
    await load_plugins()
    
    while True:
        wiseflow_logger.info("Checking for active focus points...")
        
        # Get active focus points
        focus_points = pb.read('focus_points', filter='activated=True')
        sites_record = pb.read('sites')
        
        for focus in focus_points:
            # Check if there's already a task running for this focus point
            existing_tasks = task_manager.get_tasks_by_focus(focus["id"])
            active_tasks = [t for t in existing_tasks if t.status in ["pending", "running"]]
            
            if active_tasks:
                wiseflow_logger.info(f"Focus point {focus['focuspoint']} already has active tasks")
                continue
            
            # Get sites for this focus point
            sites = [_record for _record in sites_record if _record['id'] in focus.get('sites', [])]
            
            # Create a new task
            task_id = create_task_id()
            auto_shutdown = focus.get("auto_shutdown", False)
            
            task = Task(
                task_id=task_id,
                focus_id=focus["id"],
                function=process_focus_point,
                args=(focus, sites),
                auto_shutdown=auto_shutdown
            )
            
            # Submit the task
            wiseflow_logger.info(f"Submitting task {task_id} for focus point: {focus['focuspoint']}")
            await task_manager.submit_task(task)
        
        # Wait before checking again
        wiseflow_logger.info("Waiting for 60 seconds before checking for new tasks...")
        await asyncio.sleep(60)

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
