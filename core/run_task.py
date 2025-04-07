#!/usr/bin/env python
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
import json
from datetime import datetime

from general_process import main_process, wiseflow_logger, pb
from task import AsyncTaskManager, Task, create_task_id
from analysis import CrossSourceAnalyzer, KnowledgeGraph
from llms.advanced import AdvancedLLMProcessor

# Configure the maximum number of concurrent tasks
MAX_CONCURRENT_TASKS = int(os.environ.get("MAX_CONCURRENT_TASKS", "4"))

# Initialize the task manager
task_manager = AsyncTaskManager(max_workers=MAX_CONCURRENT_TASKS)

# Initialize the cross-source analyzer
cross_source_analyzer = CrossSourceAnalyzer()

# Initialize the advanced LLM processor
advanced_llm_processor = AdvancedLLMProcessor()

async def process_focus_task(focus, sites):
    """Process a focus point task."""
    try:
        await main_process(focus, sites)
        
        # Perform cross-source analysis if enabled
        if focus.get("cross_source_analysis", False):
            await perform_cross_source_analysis(focus)
        
        return True
    except Exception as e:
        wiseflow_logger.error(f"Error processing focus point {focus.get('id')}: {e}")
        return False

async def perform_cross_source_analysis(focus):
    """Perform cross-source analysis for a focus point."""
    try:
        wiseflow_logger.info(f"Performing cross-source analysis for focus point: {focus.get('focuspoint', '')}")
        
        # Get all information collected for this focus point
        infos = pb.read('infos', filter=f'tag="{focus["id"]}"')
        
        if not infos:
            wiseflow_logger.warning(f"No information found for focus point: {focus.get('focuspoint', '')}")
            return
        
        # Analyze the collected information
        knowledge_graph = cross_source_analyzer.analyze(infos)
        
        # Save the knowledge graph
        graph_dir = os.path.join(os.environ.get("PROJECT_DIR", ""), "knowledge_graphs")
        os.makedirs(graph_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        graph_path = os.path.join(graph_dir, f"{focus['id']}_{timestamp}.json")
        
        cross_source_analyzer.save_graph(graph_path)
        
        # Save a reference to the knowledge graph in the database
        graph_record = {
            "focus_id": focus["id"],
            "path": graph_path,
            "timestamp": timestamp,
            "entity_count": len(knowledge_graph.entities),
            "metadata": {
                "focus_point": focus.get("focuspoint", ""),
                "created_at": knowledge_graph.created_at.isoformat()
            }
        }
        
        pb.add(collection_name='knowledge_graphs', body=graph_record)
        
        wiseflow_logger.info(f"Cross-source analysis completed for focus point: {focus.get('focuspoint', '')}")
    except Exception as e:
        wiseflow_logger.error(f"Error performing cross-source analysis: {e}")

async def generate_insights(focus):
    """Generate insights for a focus point using advanced LLM processing."""
    try:
        wiseflow_logger.info(f"Generating insights for focus point: {focus.get('focuspoint', '')}")
        
        # Get all information collected for this focus point
        infos = pb.read('infos', filter=f'tag="{focus["id"]}"')
        
        if not infos:
            wiseflow_logger.warning(f"No information found for focus point: {focus.get('focuspoint', '')}")
            return
        
        # Prepare content for processing
        content = ""
        for info in infos:
            content += f"Source: {info.get('url', 'Unknown')}\n"
            content += f"Title: {info.get('url_title', 'Unknown')}\n"
            content += f"Content: {info.get('content', '')}\n\n"
        
        # Process with advanced LLM
        result = await advanced_llm_processor.multi_step_reasoning(
            content=content,
            focus_point=focus.get("focuspoint", ""),
            explanation=focus.get("explanation", ""),
            content_type="text/plain",
            metadata={
                "focus_id": focus["id"],
                "source_count": len(infos)
            }
        )
        
        # Save the insights
        insights_record = {
            "focus_id": focus["id"],
            "timestamp": datetime.now().isoformat(),
            "insights": result,
            "metadata": {
                "focus_point": focus.get("focuspoint", ""),
                "model": result.get("metadata", {}).get("model", "unknown")
            }
        }
        
        pb.add(collection_name='insights', body=insights_record)
        
        wiseflow_logger.info(f"Insights generated for focus point: {focus.get('focuspoint', '')}")
    except Exception as e:
        wiseflow_logger.error(f"Error generating insights: {e}")

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
            
            # Schedule insight generation if enabled
            if task.get("generate_insights", False):
                insight_task_id = create_task_id()
                insight_task = Task(
                    task_id=insight_task_id,
                    focus_id=task["id"],
                    function=generate_insights,
                    args=(task,),
                    auto_shutdown=auto_shutdown
                )
                
                # Submit the insight task with a delay to ensure data collection is complete
                wiseflow_logger.info(f"Scheduling insight generation for focus point: {task.get('focuspoint', '')}")
                await asyncio.sleep(3600)  # Wait for 1 hour
                await task_manager.submit_task(insight_task)
                
                # Save insight task to database
                insight_task_record = {
                    "task_id": insight_task_id,
                    "focus_id": task["id"],
                    "status": "pending",
                    "auto_shutdown": auto_shutdown,
                    "type": "insight_generation",
                    "metadata": {
                        "focus_point": task.get("focuspoint", ""),
                        "parent_task_id": task_id
                    }
                }
                pb.add(collection_name='tasks', body=insight_task_record)

        counter += 1
        wiseflow_logger.info('Task execute loop finished, work after 3600 seconds')
        await asyncio.sleep(3600)

async def main():
    """Main entry point."""
    try:
        wiseflow_logger.info("Starting Wiseflow with concurrent task management and advanced analysis...")
        await schedule_task()
    except KeyboardInterrupt:
        wiseflow_logger.info("Shutting down...")
        await task_manager.shutdown()
    except Exception as e:
        wiseflow_logger.error(f"Error in main loop: {e}")
        await task_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())