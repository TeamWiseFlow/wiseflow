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

# Setup logging
project_dir = os.environ.get("PROJECT_DIR", "")
logger = get_logger('insights', project_dir)

class InsightExtractor:
    """
    Extracts insights from collected data using various data mining techniques.
    """
    
    def __init__(self, pb_client=None):
        """Initialize the insight extractor with optional PocketBase client."""
        self.pb_client = pb_client
        self.knowledge_graph = KnowledgeGraph()
        self.model = os.environ.get("PRIMARY_MODEL", "")
        if not self.model:
            logger.warning("PRIMARY_MODEL not set, using default model")
            self.model = "gpt-4o"
    
    async def extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from content using LLM.
        
        Args:
            content: The text content to analyze
            
        Returns:
            List of extracted entities with their types and metadata
        """
        prompt = """
        Extract all named entities from the following text. For each entity, identify its type 
        (person, organization, location, product, event, technology, etc.) and any relevant attributes.
        
        Return the results as a JSON array of objects with the following structure:
        [
            {
                "name": "entity name",
                "type": "entity type",
                "attributes": {"key1": "value1", "key2": "value2"}
            }
        ]
        
        Text:
        {content}
        """
        
        try:
            response = await llm.achat(
                messages=[{"role": "user", "content": prompt.format(content=content)}],
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("entities", []) if isinstance(result, dict) and "entities" in result else result
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    async def analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """
        Analyze sentiment of content using LLM.
        
        Args:
            content: The text content to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        prompt = """
        Analyze the sentiment of the following text. Provide:
        1. Overall sentiment (positive, negative, or neutral)
        2. Sentiment score (-1.0 to 1.0, where -1 is very negative, 0 is neutral, and 1 is very positive)
        3. Key emotional tones detected (e.g., excitement, concern, anger, etc.)
        4. Any notable sentiment shifts within the text
        
        Return the results as a JSON object.
        
        Text:
        {content}
        """
        
        try:
            response = await llm.achat(
                messages=[{"role": "user", "content": prompt.format(content=content)}],
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "sentiment": "neutral",
                "score": 0,
                "tones": [],
                "shifts": []
            }
    
    async def extract_topics(self, content: str, num_topics: int = 5) -> List[Dict[str, Any]]:
        """
        Extract main topics from content using LLM.
        
        Args:
            content: The text content to analyze
            num_topics: Number of topics to extract
            
        Returns:
            List of topics with relevance scores
        """
        prompt = """
        Extract the {num_topics} most important topics from the following text. For each topic:
        1. Provide a concise label (1-3 words)
        2. Assign a relevance score (0-100)
        3. Include key terms related to this topic
        
        Return the results as a JSON array of objects.
        
        Text:
        {content}
        """
        
        try:
            response = await llm.achat(
                messages=[{"role": "user", "content": prompt.format(content=content, num_topics=num_topics)}],
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("topics", []) if isinstance(result, dict) and "topics" in result else result
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []
    
    async def identify_trends(self, items: List[Dict[str, Any]], time_field: str = "created") -> Dict[str, Any]:
        """
        Identify trends in a collection of items over time.
        
        Args:
            items: List of data items to analyze
            time_field: Field name containing timestamp
            
        Returns:
            Dictionary with trend analysis results
        """
        if not items:
            return {"trends": [], "time_series": {}}
        
        # Sort items by time
        try:
            sorted_items = sorted(items, key=lambda x: x.get(time_field, ""))
        except Exception:
            logger.error(f"Error sorting items by {time_field}")
            sorted_items = items
        
        # Extract all text content for trend analysis
        all_content = "\n\n".join([
            f"Item {i+1} ({item.get(time_field, 'unknown date')}):\n{item.get('content', '')}"
            for i, item in enumerate(sorted_items[:20])  # Limit to 20 items to avoid token limits
        ])
        
        prompt = """
        Analyze the following collection of items over time and identify emerging trends, patterns, or shifts.
        
        For each trend you identify:
        1. Provide a descriptive name
        2. Indicate whether it's increasing, decreasing, or stable
        3. Provide supporting evidence from the items
        4. Estimate when the trend began (if apparent)
        
        Return the results as a JSON object with an array of trend objects.
        
        Items:
        {content}
        """
        
        try:
            response = await llm.achat(
                messages=[{"role": "user", "content": prompt.format(content=all_content)}],
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error identifying trends: {e}")
            return {"trends": []}
    
    async def extract_relationships(self, entities: List[Dict[str, Any]], content: str) -> List[Dict[str, Any]]:
        """
        Extract relationships between entities using LLM.
        
        Args:
            entities: List of extracted entities
            content: Original content for context
            
        Returns:
            List of relationships between entities
        """
        if not entities or len(entities) < 2:
            return []
        
        entity_names = [e["name"] for e in entities]
        entity_str = ", ".join(entity_names)
        
        prompt = """
        Analyze the relationships between the following entities mentioned in the text:
        {entities}
        
        For each meaningful relationship you can identify, provide:
        1. Source entity
        2. Target entity
        3. Relationship type (e.g., "works for", "owns", "located in", "competes with")
        4. Confidence score (0-100)
        5. Supporting evidence from the text
        
        Return the results as a JSON array of relationship objects.
        
        Text:
        {content}
        """
        
        try:
            response = await llm.achat(
                messages=[{"role": "user", "content": prompt.format(entities=entity_str, content=content)}],
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("relationships", []) if isinstance(result, dict) and "relationships" in result else result
        except Exception as e:
            logger.error(f"Error extracting relationships: {e}")
            return []
    
    async def cluster_related_information(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cluster related information items together.
        
        Args:
            items: List of information items
            
        Returns:
            List of clusters with related items
        """
        if not items or len(items) < 2:
            return [{"cluster_id": "cluster_1", "name": "All Items", "items": items}]
        
        # Prepare a condensed version of items for the LLM
        condensed_items = []
        for i, item in enumerate(items):
            condensed = {
                "id": i,
                "title": item.get("title", ""),
                "summary": item.get("summary", "")[:200] + "..." if item.get("summary", "") else ""
            }
            condensed_items.append(condensed)
        
        prompt = """
        Analyze the following information items and cluster them into related groups.
        For each cluster:
        1. Provide a descriptive name
        2. List the IDs of items that belong to this cluster
        3. Explain the common theme or relationship
        
        Return the results as a JSON array of cluster objects.
        
        Items:
        {items}
        """
        
        try:
            response = await llm.achat(
                messages=[{"role": "user", "content": prompt.format(items=json.dumps(condensed_items, ensure_ascii=False))}],
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            clusters_data = json.loads(response.choices[0].message.content)
            clusters = clusters_data.get("clusters", []) if isinstance(clusters_data, dict) and "clusters" in clusters_data else clusters_data
            
            # Reconstruct clusters with full items
            result_clusters = []
            for cluster in clusters:
                item_ids = cluster.get("item_ids", [])
                cluster_items = [items[item_id] for item_id in item_ids if item_id < len(items)]
                
                result_clusters.append({
                    "cluster_id": f"cluster_{uuid.uuid4().hex[:8]}",
                    "name": cluster.get("name", "Unnamed Cluster"),
                    "theme": cluster.get("theme", ""),
                    "items": cluster_items
                })
            
            return result_clusters
        except Exception as e:
            logger.error(f"Error clustering information: {e}")
            return [{"cluster_id": "cluster_1", "name": "All Items", "items": items}]
    
    async def generate_insights_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive insights report from analyzed data.
        
        Args:
            data: Dictionary containing all analyzed data
            
        Returns:
            Dictionary with insights report
        """
        prompt = """
        Generate a comprehensive insights report based on the following analyzed data.
        Include:
        
        1. Executive Summary (key findings in 2-3 sentences)
        2. Main Insights (3-5 most significant insights)
        3. Emerging Trends (patterns or shifts identified)
        4. Key Entities (most important entities and their relationships)
        5. Sentiment Analysis (overall sentiment and notable patterns)
        6. Recommendations (2-3 actionable recommendations based on the insights)
        
        Return the report as a structured JSON object.
        
        Analyzed Data:
        {data}
        """
        
        try:
            response = await llm.achat(
                messages=[{"role": "user", "content": prompt.format(data=json.dumps(data, ensure_ascii=False))}],
                model=self.model,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error generating insights report: {e}")
            return {
                "executive_summary": "Error generating insights report.",
                "main_insights": [],
                "emerging_trends": [],
                "key_entities": [],
                "sentiment_analysis": {},
                "recommendations": []
            }
    
    async def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single data item to extract all insights.
        
        Args:
            item: Data item to process
            
        Returns:
            Dictionary with all extracted insights
        """
        content = item.get("content", "")
        if not content:
            return {"error": "No content to analyze"}
        
        # Extract entities
        entities = await self.extract_entities(content)
        
        # Analyze sentiment
        sentiment = await self.analyze_sentiment(content)
        
        # Extract topics
        topics = await self.extract_topics(content)
        
        # Extract relationships between entities
        relationships = await self.extract_relationships(entities, content)
        
        # Combine all insights
        insights = {
            "item_id": item.get("id", str(uuid.uuid4())),
            "timestamp": datetime.now().isoformat(),
            "entities": entities,
            "sentiment": sentiment,
            "topics": topics,
            "relationships": relationships
        }
        
        return insights
    
    async def process_collection(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a collection of data items to extract collective insights.
        
        Args:
            items: List of data items to process
            
        Returns:
            Dictionary with collective insights
        """
        if not items:
            return {"error": "No items to analyze"}
        
        # Process individual items
        item_insights = []
        for item in items:
            insights = await self.process_item(item)
            item_insights.append(insights)
        
        # Identify trends
        trends = await self.identify_trends(items)
        
        # Cluster related information
        clusters = await self.cluster_related_information(items)
        
        # Generate comprehensive insights report
        report_data = {
            "item_insights": item_insights,
            "trends": trends,
            "clusters": clusters
        }
        insights_report = await self.generate_insights_report(report_data)
        
        # Combine all collective insights
        collective_insights = {
            "timestamp": datetime.now().isoformat(),
            "item_count": len(items),
            "item_insights": item_insights,
            "trends": trends,
            "clusters": clusters,
            "insights_report": insights_report
        }
        
        return collective_insights
    
    def save_insights(self, insights: Dict[str, Any], filepath: str) -> None:
        """
        Save insights to a file.
        
        Args:
            insights: Insights data to save
            filepath: Path to save the file
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(insights, f, ensure_ascii=False, indent=2)
            logger.info(f"Insights saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving insights: {e}")
    
    async def store_insights_in_db(self, insights: Dict[str, Any], collection: str = "insights") -> Optional[str]:
        """
        Store insights in the database.
        
        Args:
            insights: Insights data to store
            collection: Database collection name
            
        Returns:
            ID of the created record or None if failed
        """
        if not self.pb_client:
            logger.warning("No PocketBase client provided, cannot store insights in database")
            return None
        
        try:
            record = await self.pb_client.create(collection, insights)
            logger.info(f"Insights stored in database with ID: {record.id}")
            return record.id
        except Exception as e:
            logger.error(f"Error storing insights in database: {e}")
            return None


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