"""
Data mining and insights extraction module for Wiseflow.

This module provides advanced data mining capabilities to extract insights,
patterns, and relationships from collected information.
"""

import os
import re
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import uuid
from collections import Counter, defaultdict

# Import necessary modules
from ..llms.openai_wrapper import openai_llm as llm
from ..utils.general_utils import get_logger, normalize_url
from ..analysis import Entity, Relationship, KnowledgeGraph
from ..utils.pb_api import PbTalker

# Setup logging
project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)
insights_logger = get_logger('insights', project_dir)
pb = PbTalker(insights_logger)

model = os.environ.get("PRIMARY_MODEL", "")
if not model:
    raise ValueError("PRIMARY_MODEL not set, please set it in environment variables or edit core/.env")

# ... keep existing InsightExtractor class and other functions ...

# Prompts for insights generation
TREND_ANALYSIS_PROMPT = """You are an expert data analyst specializing in trend identification and pattern recognition. 
Your task is to analyze a collection of information items related to a specific focus point and identify meaningful trends, 
patterns, or insights that might not be immediately obvious from individual items.
Focus point: {focus_point}
Focus explanation: {explanation}
Here are the information items collected over the past {time_period}:
{info_items}
Please analyze this information and provide the following:
1. Key trends or patterns you've identified
2. Emerging topics or themes
3. Notable changes or shifts over time
4. Potential implications or opportunities
5. Gaps in the information that might be worth exploring
Your analysis should be data-driven, insightful, and focused on extracting value that goes beyond what's explicitly stated in the individual items.
"""

ENTITY_RELATIONSHIP_PROMPT = """You are an expert in entity recognition and relationship mapping. 
Your task is to analyze a collection of information items related to a specific focus point and identify key entities 
(people, organizations, products, technologies, etc.) and the relationships between them.
Focus point: {focus_point}
Focus explanation: {explanation}
Here are the information items:
{info_items}
Please analyze this information and provide the following:
1. Key entities mentioned across multiple information items
2. Relationships between these entities
3. Influence networks or hierarchies
4. Potential collaborations or conflicts
5. Central entities that appear to be most connected or influential
Your analysis should focus on extracting the network of relationships that exists beneath the surface of these individual information items.
"""

INSIGHT_SUMMARY_PROMPT = """You are an expert intelligence analyst specializing in synthesizing information and extracting strategic insights.
Your task is to review the trend analysis and entity relationship analysis for a collection of information related to a specific focus point,
and provide a concise, high-value summary of the most important insights.
Focus point: {focus_point}
Focus explanation: {explanation}
Trend Analysis:
{trend_analysis}
Entity Relationship Analysis:
{entity_analysis}
Please provide a concise summary of the most valuable insights from this analysis. Focus on information that would be most actionable
or strategically valuable. Highlight any unexpected findings or connections that might not be obvious from casual reading of the individual items.
Your summary should be clear, concise, and focused on delivering maximum value to someone interested in this topic.
"""

async def generate_trend_analysis(focus_point: str, explanation: str, info_items: List[Dict[str, Any]], time_period: str = "week") -> str:
    """
    Generate a trend analysis for a collection of information items.
    
    Args:
        focus_point: The focus point being analyzed
        explanation: Additional explanation or context for the focus point
        info_items: List of information items to analyze
        time_period: Time period covered by the analysis (e.g., "day", "week", "month")
        
    Returns:
        String containing the trend analysis
    """
    insights_logger.debug(f"Generating trend analysis for focus point: {focus_point}")
    
    # Format the info items for the prompt
    formatted_items = []
    for i, item in enumerate(info_items, 1):
        content = item.get('content', '')
        url = item.get('url', '')
        formatted_items.append(f"Item {i}:\nContent: {content}\nSource: {url}\n")
    
    items_text = "\n".join(formatted_items)
    
    # Create the prompt
    prompt = TREND_ANALYSIS_PROMPT.format(
        focus_point=focus_point,
        explanation=explanation,
        time_period=time_period,
        info_items=items_text
    )
    
    # Generate the analysis
    result = await llm([
        {'role': 'system', 'content': 'You are an expert data analyst specializing in trend identification.'},
        {'role': 'user', 'content': prompt}
    ], model=model, temperature=0.2)
    
    insights_logger.debug("Trend analysis generated successfully")
    return result

async def generate_entity_analysis(focus_point: str, explanation: str, info_items: List[Dict[str, Any]]) -> str:
    """
    Generate an entity relationship analysis for a collection of information items.
    
    Args:
        focus_point: The focus point being analyzed
        explanation: Additional explanation or context for the focus point
        info_items: List of information items to analyze
        
    Returns:
        String containing the entity relationship analysis
    """
    insights_logger.debug(f"Generating entity relationship analysis for focus point: {focus_point}")
    
    # Format the info items for the prompt
    formatted_items = []
    for i, item in enumerate(info_items, 1):
        content = item.get('content', '')
        url = item.get('url', '')
        formatted_items.append(f"Item {i}:\nContent: {content}\nSource: {url}\n")
    
    items_text = "\n".join(formatted_items)
    
    # Create the prompt
    prompt = ENTITY_RELATIONSHIP_PROMPT.format(
        focus_point=focus_point,
        explanation=explanation,
        info_items=items_text
    )
    
    # Generate the analysis
    result = await llm([
        {'role': 'system', 'content': 'You are an expert in entity recognition and relationship mapping.'},
        {'role': 'user', 'content': prompt}
    ], model=model, temperature=0.2)
    
    insights_logger.debug("Entity relationship analysis generated successfully")
    return result

async def generate_insight_summary(focus_point: str, explanation: str, trend_analysis: str, entity_analysis: str) -> str:
    """
    Generate a concise summary of insights based on trend and entity analyses.
    
    Args:
        focus_point: The focus point being analyzed
        explanation: Additional explanation or context for the focus point
        trend_analysis: The trend analysis text
        entity_analysis: The entity relationship analysis text
        
    Returns:
        String containing the insight summary
    """
    insights_logger.debug(f"Generating insight summary for focus point: {focus_point}")
    
    # Create the prompt
    prompt = INSIGHT_SUMMARY_PROMPT.format(
        focus_point=focus_point,
        explanation=explanation,
        trend_analysis=trend_analysis,
        entity_analysis=entity_analysis
    )
    
    # Generate the summary
    result = await llm([
        {'role': 'system', 'content': 'You are an expert intelligence analyst specializing in synthesizing information.'},
        {'role': 'user', 'content': prompt}
    ], model=model, temperature=0.3)
    
    insights_logger.debug("Insight summary generated successfully")
    return result

async def generate_insights_for_focus(focus_id: str, time_period_days: int = 7, force: bool = False) -> Dict[str, Any]:
    """
    Generate comprehensive insights for a specific focus point.
    
    Args:
        focus_id: The ID of the focus point
        time_period_days: Number of days to look back for information items
        force: Force regeneration of insights even if recent insights exist
        
    Returns:
        Dictionary containing the generated insights
    """
    insights_logger.info(f"Generating insights for focus ID: {focus_id}")
    
    # Check for recent insights if not forcing regeneration
    if not force:
        cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()
        filter_query = f"focus_id='{focus_id}' && created>='{cutoff_time}'"
        recent_insights = pb.read(collection_name='insights', filter=filter_query, sort="-created")
        
        if recent_insights:
            insights_logger.info(f"Found recent insights for focus ID {focus_id}")
            return recent_insights[0]
    
    # Get the focus point details
    focus = pb.read_one(collection_name='focus_point', id=focus_id)
    if not focus:
        insights_logger.error(f"Focus point with ID {focus_id} not found")
        return {"error": f"Focus point with ID {focus_id} not found"}
    
    focus_point = focus.get("focuspoint", "").strip()
    explanation = focus.get("explanation", "").strip()
    
    # Calculate the time period
    cutoff_date = (datetime.now() - timedelta(days=time_period_days)).strftime('%Y-%m-%d')
    
    # Get information items for this focus point from the specified time period
    filter_query = f"tag='{focus_id}' && created>='{cutoff_date}'"
    info_items = pb.read(collection_name='infos', filter=filter_query)
    
    if not info_items:
        insights_logger.warning(f"No information items found for focus ID {focus_id} in the last {time_period_days} days")
        return {
            "focus_id": focus_id,
            "focus_point": focus_point,
            "error": f"No information items found in the last {time_period_days} days"
        }
    
    insights_logger.info(f"Found {len(info_items)} information items for analysis")
    
    # Generate the analyses in parallel
    trend_analysis_task = asyncio.create_task(
        generate_trend_analysis(focus_point, explanation, info_items, f"{time_period_days} days")
    )
    entity_analysis_task = asyncio.create_task(
        generate_entity_analysis(focus_point, explanation, info_items)
    )
    
    trend_analysis = await trend_analysis_task
    entity_analysis = await entity_analysis_task
    
    # Generate the summary based on both analyses
    insight_summary = await generate_insight_summary(focus_point, explanation, trend_analysis, entity_analysis)
    
    # Create the result
    result = {
        "focus_id": focus_id,
        "focus_point": focus_point,
        "time_period": f"{time_period_days} days",
        "item_count": len(info_items),
        "trend_analysis": trend_analysis,
        "entity_analysis": entity_analysis,
        "insight_summary": insight_summary,
        "generated_at": datetime.now().isoformat()
    }
    
    # Save the insights to the database
    try:
        insight_record = {
            "focus_id": focus_id,
            "trend_analysis": trend_analysis,
            "entity_analysis": entity_analysis,
            "insight_summary": insight_summary,
            "item_count": len(info_items),
            "time_period": f"{time_period_days} days"
        }
        pb.add(collection_name='insights', body=insight_record)
        insights_logger.info(f"Insights for focus ID {focus_id} saved to database")
    except Exception as e:
        insights_logger.error(f"Error saving insights to database: {e}")
        # Save to a local file as backup
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        with open(os.path.join(project_dir, f'{timestamp}_insights_{focus_id}.json'), 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
    
    return result

async def generate_insights_for_all_active_focuses(time_period_days: int = 7) -> List[Dict[str, Any]]:
    """
    Generate insights for all active focus points.
    
    Args:
        time_period_days: Number of days to look back for information items
        
    Returns:
        List of dictionaries containing the generated insights for each focus point
    """
    insights_logger.info("Generating insights for all active focus points")
    
    # Get all active focus points
    active_focuses = pb.read(collection_name='focus_point', filter="activated=true")
    
    if not active_focuses:
        insights_logger.warning("No active focus points found")
        return []
    
    insights_logger.info(f"Found {len(active_focuses)} active focus points")
    
    # Generate insights for each focus point
    results = []
    for focus in active_focuses:
        try:
            result = await generate_insights_for_focus(focus["id"], time_period_days)
            results.append(result)
        except Exception as e:
            insights_logger.error(f"Error generating insights for focus ID {focus['id']}: {e}")
            results.append({
                "focus_id": focus["id"],
                "focus_point": focus.get("focuspoint", ""),
                "error": str(e)
            })
    
    return results

async def get_insights_for_focus(focus_id: str, max_age_hours: int = 24) -> Dict[str, Any]:
    """
    Get the most recent insights for a focus point, generating new ones if needed.
    
    Args:
        focus_id: The ID of the focus point
        max_age_hours: Maximum age of insights in hours before regenerating
        
    Returns:
        Dictionary containing the insights
    """
    insights_logger.info(f"Getting insights for focus ID: {focus_id}")
    
    # Calculate the cutoff time
    cutoff_time = (datetime.now() - timedelta(hours=max_age_hours)).isoformat()
    
    # Try to get recent insights from the database
    filter_query = f"focus_id='{focus_id}' && created>='{cutoff_time}'"
    recent_insights = pb.read(collection_name='insights', filter=filter_query, sort="-created")
    
    if recent_insights:
        insights_logger.info(f"Found recent insights for focus ID {focus_id}")
        return recent_insights[0]
    
    # No recent insights found, generate new ones
    insights_logger.info(f"No recent insights found for focus ID {focus_id}, generating new ones")
    return await generate_insights_for_focus(focus_id)

# Utility functions for data mining

def extract_time_series(items: List[Dict[str, Any]], time_field: str = "created", 
                       value_field: str = "value") -> Dict[str, List[float]]:
    """
    Extract time series data from a collection of items.
    
    Args:
        items: List of data items
        time_field: Field containing timestamp
        value_field: Field containing numeric value
        
    Returns:
        Dictionary with time series data
    """
    time_series = defaultdict(list)
    
    for item in items:
        timestamp = item.get(time_field)
        value = item.get(value_field)
        
        if timestamp and value is not None:
            try:
                # Convert timestamp to date string
                if isinstance(timestamp, str):
                    date_str = timestamp.split('T')[0]
                elif isinstance(timestamp, datetime):
                    date_str = timestamp.strftime('%Y-%m-%d')
                else:
                    continue
                
                # Convert value to float
                float_value = float(value)
                time_series[date_str].append(float_value)
            except (ValueError, TypeError):
                continue
    
    # Calculate average for each day
    result = {}
    for date_str, values in time_series.items():
        result[date_str] = sum(values) / len(values) if values else 0
    
    return result

def calculate_correlation(series1: Dict[str, float], series2: Dict[str, float]) -> float:
    """
    Calculate correlation coefficient between two time series.
    
    Args:
        series1: First time series dictionary
        series2: Second time series dictionary
        
    Returns:
        Correlation coefficient (-1 to 1)
    """
    # Find common dates
    common_dates = set(series1.keys()) & set(series2.keys())
    if not common_dates or len(common_dates) < 2:
        return 0
    
    # Extract values for common dates
    values1 = [series1[date] for date in common_dates]
    values2 = [series2[date] for date in common_dates]
    
    # Calculate means
    mean1 = sum(values1) / len(values1)
    mean2 = sum(values2) / len(values2)
    
    # Calculate correlation coefficient
    numerator = sum((values1[i] - mean1) * (values2[i] - mean2) for i in range(len(values1)))
    denominator1 = sum((values1[i] - mean1) ** 2 for i in range(len(values1)))
    denominator2 = sum((values2[i] - mean2) ** 2 for i in range(len(values2)))
    
    if denominator1 == 0 or denominator2 == 0:
        return 0
    
    return numerator / ((denominator1 ** 0.5) * (denominator2 ** 0.5))