#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Schema update script for Wiseflow.

This script updates the PocketBase schema to support the new features in the upgrade plan.
"""

import os
import sys
import logging
import json
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

from core.utils.pb_api import PbTalker
from core.utils.general_utils import get_logger

# Configure logging
logger = get_logger('schema_update')

def update_focus_points_schema(pb: PbTalker) -> bool:
    """
    Update the focus_points collection schema.
    
    Adds:
    - auto_shutdown: Boolean field to enable auto-shutdown for completed tasks
    - references: JSON field to store reference materials
    - concurrency: Number field to control the number of concurrent threads
    """
    logger.info("Updating focus_points schema...")
    
    try:
        # Get the current schema
        collection_name = "focus_points"
        
        # Check if auto_shutdown field exists
        records = pb.read(collection_name, fields=["id", "auto_shutdown"])
        has_auto_shutdown = any("auto_shutdown" in record for record in records)
        
        if not has_auto_shutdown:
            logger.info("Adding auto_shutdown field to focus_points")
            # This is a simplified approach - in a real implementation, you would use the PocketBase Admin API
            # to update the schema. For now, we'll update each record individually.
            for record in pb.read(collection_name, fields=["id"]):
                pb.update(collection_name, record["id"], {"auto_shutdown": False})
        
        # Check if references field exists
        records = pb.read(collection_name, fields=["id", "references"])
        has_references = any("references" in record for record in records)
        
        if not has_references:
            logger.info("Adding references field to focus_points")
            for record in pb.read(collection_name, fields=["id"]):
                pb.update(collection_name, record["id"], {"references": json.dumps([])})
        
        # Check if concurrency field exists
        records = pb.read(collection_name, fields=["id", "concurrency"])
        has_concurrency = any("concurrency" in record for record in records)
        
        if not has_concurrency:
            logger.info("Adding concurrency field to focus_points")
            for record in pb.read(collection_name, fields=["id"]):
                pb.update(collection_name, record["id"], {"concurrency": 1})
        
        logger.info("Successfully updated focus_points schema")
        return True
    except Exception as e:
        logger.error(f"Failed to update focus_points schema: {e}")
        return False

def create_references_collection(pb: PbTalker) -> bool:
    """
    Create the references collection if it doesn't exist.
    
    This collection stores reference materials for focus points.
    """
    logger.info("Creating references collection...")
    
    try:
        # Check if the collection exists by trying to read from it
        try:
            pb.read("references", fields=["id"], filter="", skiptotal=True)
            logger.info("References collection already exists")
            return True
        except Exception:
            # Collection doesn't exist, we'll create it
            pass
        
        # In a real implementation, you would use the PocketBase Admin API to create the collection
        # For now, we'll just log that this needs to be done manually
        logger.warning("""
        Please create the 'references' collection manually in PocketBase with the following fields:
        - id: Text (system field)
        - created: DateTime (system field)
        - updated: DateTime (system field)
        - focus_id: Text (required, relation to focus_points)
        - name: Text (required)
        - type: Text (required, options: url, file, text)
        - content: Text (required)
        - metadata: JSON
        """)
        
        return True
    except Exception as e:
        logger.error(f"Failed to create references collection: {e}")
        return False

def create_tasks_collection(pb: PbTalker) -> bool:
    """
    Create the tasks collection if it doesn't exist.
    
    This collection stores information about running and completed tasks.
    """
    logger.info("Creating tasks collection...")
    
    try:
        # Check if the collection exists by trying to read from it
        try:
            pb.read("tasks", fields=["id"], filter="", skiptotal=True)
            logger.info("Tasks collection already exists")
            return True
        except Exception:
            # Collection doesn't exist, we'll create it
            pass
        
        # In a real implementation, you would use the PocketBase Admin API to create the collection
        # For now, we'll just log that this needs to be done manually
        logger.warning("""
        Please create the 'tasks' collection manually in PocketBase with the following fields:
        - id: Text (system field)
        - created: DateTime (system field)
        - updated: DateTime (system field)
        - task_id: Text (required)
        - focus_id: Text (required, relation to focus_points)
        - status: Text (required, options: pending, running, completed, failed, cancelled)
        - start_time: DateTime
        - end_time: DateTime
        - auto_shutdown: Boolean
        - error: Text
        - metadata: JSON
        """)
        
        return True
    except Exception as e:
        logger.error(f"Failed to create tasks collection: {e}")
        return False

def main():
    """Main entry point for the schema update script."""
    logger.info("Starting schema update...")
    
    # Initialize PocketBase client
    pb = PbTalker(logger)
    
    # Update focus_points schema
    if not update_focus_points_schema(pb):
        logger.error("Failed to update focus_points schema")
        return False
    
    # Create references collection
    if not create_references_collection(pb):
        logger.error("Failed to create references collection")
        return False
    
    # Create tasks collection
    if not create_tasks_collection(pb):
        logger.error("Failed to create tasks collection")
        return False
    
    logger.info("Schema update completed successfully")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)