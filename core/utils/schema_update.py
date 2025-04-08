"""
Schema update utility for PocketBase database.

This module provides functions to update the PocketBase schema with new collections
and fields for the data mining features.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

from .pb_api import PbTalker

logger = logging.getLogger(__name__)

async def update_schema_for_insights(pb_client: PbTalker) -> bool:
    """
    Update the PocketBase schema to add collections for insights data.
    
    Args:
        pb_client: PocketBase client
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if insights collection exists
        collections = await pb_client.get_collections()
        collection_names = [c.get('name') for c in collections]
        
        # Create insights collection if it doesn't exist
        if 'insights' not in collection_names:
            logger.info("Creating insights collection")
            insights_schema = {
                "name": "insights",
                "type": "base",
                "schema": [
                    {
                        "name": "item_id",
                        "type": "text",
                        "required": True,
                        "options": {
                            "min": 1,
                            "max": 255
                        }
                    },
                    {
                        "name": "timestamp",
                        "type": "text",
                        "required": True
                    },
                    {
                        "name": "entities",
                        "type": "json",
                        "required": False
                    },
                    {
                        "name": "sentiment",
                        "type": "json",
                        "required": False
                    },
                    {
                        "name": "topics",
                        "type": "json",
                        "required": False
                    },
                    {
                        "name": "relationships",
                        "type": "json",
                        "required": False
                    }
                ]
            }
            await pb_client.create_collection(insights_schema)
        
        # Create collective_insights collection if it doesn't exist
        if 'collective_insights' not in collection_names:
            logger.info("Creating collective_insights collection")
            collective_insights_schema = {
                "name": "collective_insights",
                "type": "base",
                "schema": [
                    {
                        "name": "timestamp",
                        "type": "text",
                        "required": True
                    },
                    {
                        "name": "focus_id",
                        "type": "text",
                        "required": True,
                        "options": {
                            "min": 1,
                            "max": 255
                        }
                    },
                    {
                        "name": "focus_point",
                        "type": "text",
                        "required": True
                    },
                    {
                        "name": "item_count",
                        "type": "number",
                        "required": False
                    },
                    {
                        "name": "item_insights",
                        "type": "json",
                        "required": False
                    },
                    {
                        "name": "trends",
                        "type": "json",
                        "required": False
                    },
                    {
                        "name": "clusters",
                        "type": "json",
                        "required": False
                    },
                    {
                        "name": "insights_report",
                        "type": "json",
                        "required": False
                    }
                ]
            }
            await pb_client.create_collection(collective_insights_schema)
        
        # Update infos collection to add insights field if it doesn't exist
        if 'infos' in collection_names:
            logger.info("Updating infos collection to add insights field")
            infos_collection = next((c for c in collections if c.get('name') == 'infos'), None)
            if infos_collection:
                schema_fields = infos_collection.get('schema', [])
                field_names = [f.get('name') for f in schema_fields]
                
                if 'insights' not in field_names:
                    schema_fields.append({
                        "name": "insights",
                        "type": "json",
                        "required": False
                    })
                    
                    # Update the collection with the new schema
                    infos_collection['schema'] = schema_fields
                    await pb_client.update_collection(infos_collection.get('id'), infos_collection)
        
        return True
    except Exception as e:
        logger.error(f"Error updating schema for insights: {e}")
        return False

async def update_schema(pb_client: PbTalker) -> bool:
    """
    Update the PocketBase schema with all required changes.
    
    Args:
        pb_client: PocketBase client
        
    Returns:
        True if all updates were successful, False otherwise
    """
    success = True
    
    # Update schema for insights
    insights_success = await update_schema_for_insights(pb_client)
    if not insights_success:
        logger.error("Failed to update schema for insights")
        success = False
    
    # Add more schema updates here as needed
    
    return success