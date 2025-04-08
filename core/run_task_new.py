#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced task runner for Wiseflow.

This module provides an enhanced task runner with concurrency and plugin support.
"""

from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

import asyncio
import os
import json
import uuid
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

from core.utils.general_utils import get_logger
from core.utils.pb_api import PbTalker
from core.task import AsyncTaskManager, Task, create_task_id
from core.plugins import PluginManager
from core.plugins.connectors import ConnectorBase, DataItem
from core.plugins.processors import ProcessorBase, ProcessedData

# Configure logging
wiseflow_logger = get_logger('wiseflow')

# Initialize PocketBase client
pb = PbTalker(wiseflow_logger)

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

async def process_data_item(data_item: DataItem, focus: Dict[str, Any]) -> Optional[ProcessedData]:
    """Process a data item using the appropriate processor."""
    # Get the focus point processor
    processor_name = "focus_point_processor"
    processor = plugin_manager.get_plugin(processor_name)
    
    if not processor or not isinstance(processor, ProcessorBase):
        wiseflow_logger.error(f"Processor {processor_name} not found or not a valid processor")
        return None
    
    # Prepare focus points for the processor
    focus_points = [{
        "focuspoint": focus.get("focuspoint", ""),
        "explanation": focus.get("explanation", "")
    }]
    
    # Process the data item
    try:
        processed_data = processor.process(data_item, {
            "focus_points": focus_points
        })
        return processed_data
    except Exception as e:
        wiseflow_logger.error(f"Error processing data item {data_item.source_id}: {e}")
        return None

async def save_processed_data(processed_data: ProcessedData, focus_id: str) -> bool:
    """Save processed data to the database."""
    try:
        # Extract information from processed data
        content = processed_data.processed_content
        if isinstance(content, dict):
            content_str = json.dumps(content)
        else:
            content_str = str(content)
        
        # Create info record
        info = {
            "url": processed_data.original_item.url if processed_data.original_item else "",
            "url_title": processed_data.original_item.metadata.get("title", "") if processed_data.original_item else "",
            "tag": focus_id,
            "content": content_str,
            "metadata": json.dumps(processed_data.metadata)
        }
        
        # Save to database
        info_id = pb.add(collection_name='infos', body=info)
        if not info_id:
            wiseflow_logger.error('Failed to add info to database')
            # Save to cache file
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            cache_dir = os.environ.get("PROJECT_DIR", "")
            if cache_dir:
                cache_file = os.path.join(cache_dir, f'{timestamp}_cache_infos.json')
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(info, f, ensure_ascii=False, indent=4)
            return False
        
        return True
    except Exception as e:
        wiseflow_logger.error(f"Error saving processed data: {e}")
        return False

async def collect_from_connector(connector: ConnectorBase, params: Dict[str, Any]) -> List[DataItem]:
    """Collect data from a connector."""
    try:
        return connector.collect(params)
    except Exception as e:
        wiseflow_logger.error(f"Error collecting data from connector {connector.name}: {e}")
        return []

async def process_focus_point(focus: Dict[str, Any], sites: List[Dict[str, Any]]) -> bool:
    """Process a focus point using the plugin system."""
    focus_id = focus["id"]
    focus_point = focus.get("focuspoint", "").strip()
    explanation = focus.get("explanation", "").strip() if focus.get("explanation") else ""
    
    wiseflow_logger.info(f"Processing focus point: {focus_point}")
    
    # Get existing URLs to avoid duplicates
    existing_urls = {url['url'] for url in pb.read(collection_name='infos', fields=['url'], filter=f"tag='{focus_id}'")}
    
    # Get references for this focus point
    references = []
    if focus.get("references"):
        try:
            references = json.loads(focus["references"])
        except:
            references = []
    
    # Process references
    for reference in references:
        ref_type = reference.get("type")
        ref_content = reference.get("content")
        
        if not ref_type or not ref_content:
            continue
        
        if ref_type == "url" and ref_content not in existing_urls:
            # Add URL to sites for processing
            sites.append({"url": ref_content, "type": "web"})
    
    # Determine concurrency for this focus point
    concurrency = focus.get("concurrency", 1)
    if concurrency < 1:
        concurrency = 1
    
    # Create a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(concurrency)
    
    # Process sites
    tasks = []
    for site in sites:
        site_url = site.get("url")
        site_type = site.get("type", "web")
        
        if not site_url:
            continue
        
        if site_url in existing_urls:
            continue
        
        # Add to existing URLs to prevent duplicates
        existing_urls.add(site_url)
        
        # Determine which connector to use
        connector_name = f"{site_type}_connector"
        connector = plugin_manager.get_plugin(connector_name)
        
        if not connector or not isinstance(connector, ConnectorBase):
            wiseflow_logger.warning(f"Connector {connector_name} not found or not a valid connector")
            continue
        
        # Create a task to process this site
        tasks.append(process_site(site, connector, focus, semaphore))
    
    # Wait for all tasks to complete
    if tasks:
        await asyncio.gather(*tasks)
    
    wiseflow_logger.info(f"Completed processing focus point: {focus_point}")
    return True

async def process_site(site: Dict[str, Any], connector: ConnectorBase, focus: Dict[str, Any], semaphore: asyncio.Semaphore) -> None:
    """Process a site using a connector and processor."""
    async with semaphore:
        site_url = site.get("url")
        wiseflow_logger.info(f"Processing site: {site_url}")
        
        # Collect data from the connector
        data_items = await collect_from_connector(connector, {"urls": [site_url]})
        
        if not data_items:
            wiseflow_logger.warning(f"No data collected from {site_url}")
            return
        
        # Process each data item
        for data_item in data_items:
            processed_data = await process_data_item(data_item, focus)
            
            if processed_data:
                # Save the processed data
                await save_processed_data(processed_data, focus["id"])

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
                wiseflow_logger.info(f"Focus point {focus.get('focuspoint', '')} already has active tasks")
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
            wiseflow_logger.info(f"Submitting task {task_id} for focus point: {focus.get('focuspoint', '')}")
            await task_manager.submit_task(task)
            
            # Save task to database
            task_record = {
                "task_id": task_id,
                "focus_id": focus["id"],
                "status": "pending",
                "auto_shutdown": auto_shutdown,
                "metadata": json.dumps({
                    "focus_point": focus.get("focuspoint", ""),
                    "sites_count": len(sites)
                })
            }
            pb.add(collection_name='tasks', body=task_record)
        
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
