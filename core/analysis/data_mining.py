"""
Data mining module for WiseFlow.
This module provides functions for extracting insights from collected information
using various data mining techniques.
"""
import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set, Union
import re
from collections import Counter, defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from loguru import logger
from ..utils.general_utils import get_logger
from ..utils.pb_api import PbTalker
from ..llms.openai_wrapper import openai_llm as llm

project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)
data_mining_logger = get_logger('data_mining', project_dir)
pb = PbTalker(data_mining_logger)

model = os.environ.get("PRIMARY_MODEL", "")
if not model:
    raise ValueError("PRIMARY_MODEL not set, please set it in environment variables or edit core/.env")

# Prompts for entity extraction
ENTITY_EXTRACTION_PROMPT = """You are an expert in entity extraction. Your task is to identify and extract named entities from the provided text.
Please identify the following types of entities:
- People (individuals, groups of people)
- Organizations (companies, institutions, agencies)
- Locations (countries, cities, geographical areas)
- Products (goods, services, brands)
- Technologies (technical terms, methodologies, frameworks)
- Events (conferences, meetings, incidents)
- Dates and Times
Text to analyze:
{text}
For each entity you identify, provide:
1. The entity name exactly as it appears in the text
2. The entity type (from the categories above)
3. A brief description or context (optional)
Format your response as a JSON array of objects with the following structure:
[
  {
    "name": "entity name",
    "type": "entity type",
    "description": "brief description or context"
  },
  ...
]
"""

# Prompts for topic extraction
TOPIC_EXTRACTION_PROMPT = """You are an expert in topic modeling and extraction. Your task is to identify the main topics discussed in the provided text.
Text to analyze:
{text}
Please identify 3-7 main topics in this text. For each topic:
1. Provide a concise label (1-3 words)
2. List key terms associated with this topic
3. Provide a brief description of what this topic encompasses
Format your response as a JSON array of objects with the following structure:
[
  {
    "label": "topic label",
    "key_terms": ["term1", "term2", "term3", ...],
    "description": "brief description of the topic"
  },
  ...
]
"""

# Prompts for sentiment analysis
SENTIMENT_ANALYSIS_PROMPT = """You are an expert in sentiment analysis. Your task is to analyze the sentiment expressed in the provided text.
Text to analyze:
{text}
Please analyze the overall sentiment of this text, as well as any specific sentiments expressed about key entities or topics.
Format your response as a JSON object with the following structure:
{
  "overall_sentiment": {
    "polarity": "positive/negative/neutral/mixed",
    "strength": "value from 0.0 to 1.0",
    "explanation": "brief explanation of your assessment"
  },
  "entity_sentiments": [
    {
      "entity": "entity name",
      "polarity": "positive/negative/neutral/mixed",
      "strength": "value from 0.0 to 1.0",
      "explanation": "brief explanation"
    },
    ...
  ]
}
"""

# Prompts for relationship extraction
RELATIONSHIP_EXTRACTION_PROMPT = """You are an expert in relationship extraction. Your task is to identify relationships between entities in the provided text.
Text to analyze:
{text}
Please identify relationships between entities in this text. For each relationship:
1. Identify the source entity
2. Identify the target entity
3. Describe the relationship between them
4. Provide the specific text that indicates this relationship (if possible)
Format your response as a JSON array of objects with the following structure:
[
  {
    "source": "source entity name",
    "source_type": "person/organization/location/etc.",
    "target": "target entity name",
    "target_type": "person/organization/location/etc.",
    "relationship": "description of relationship",
    "evidence": "text indicating this relationship"
  },
  ...
]
"""

# Prompts for temporal pattern analysis
TEMPORAL_PATTERN_PROMPT = """You are an expert in temporal pattern analysis. Your task is to identify patterns, trends, or changes over time in the provided information.
The information spans from {start_date} to {end_date}.
Information items:
{items}
Please analyze this information and identify:
1. Temporal patterns or trends
2. Changes in frequency or intensity over time
3. Periodic events or cycles
4. Notable shifts or turning points
Format your response as a JSON object with the following structure:
{
  "patterns": [
    {
      "pattern_type": "trend/cycle/shift/etc.",
      "description": "description of the pattern",
      "time_period": "relevant time period",
      "significance": "explanation of why this pattern is significant"
    },
    ...
  ],
  "summary": "brief summary of the overall temporal patterns"
}
"""

async def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extract named entities from text.
    
    Args:
        text: The text to analyze
        
    Returns:
        List of dictionaries containing entity information
    """
    data_mining_logger.debug("Extracting entities from text")
    
    # Create the prompt
    prompt = ENTITY_EXTRACTION_PROMPT.format(text=text)
    
    # Generate the analysis
    result = await llm([
        {'role': 'system', 'content': 'You are an expert in entity extraction.'},
        {'role': 'user', 'content': prompt}
    ], model=model, temperature=0.1)
    
    # Parse the JSON response
    try:
        # Find JSON array in the response
        json_match = re.search(r'\[\s*\{.*\}\s*\]', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            entities = json.loads(json_str)
            data_mining_logger.debug(f"Extracted {len(entities)} entities")
            return entities
        else:
            data_mining_logger.warning("No valid JSON found in entity extraction response")
            return []
    except Exception as e:
        data_mining_logger.error(f"Error parsing entity extraction response: {e}")
        return []

async def extract_topics(text: str) -> List[Dict[str, Any]]:
    """
    Extract topics from text.
    
    Args:
        text: The text to analyze
        
    Returns:
        List of dictionaries containing topic information
    """
    data_mining_logger.debug("Extracting topics from text")
    
    # Create the prompt
    prompt = TOPIC_EXTRACTION_PROMPT.format(text=text)
    
    # Generate the analysis
    result = await llm([
        {'role': 'system', 'content': 'You are an expert in topic modeling and extraction.'},
        {'role': 'user', 'content': prompt}
    ], model=model, temperature=0.2)
    
    # Parse the JSON response
    try:
        # Find JSON array in the response
        json_match = re.search(r'\[\s*\{.*\}\s*\]', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            topics = json.loads(json_str)
            data_mining_logger.debug(f"Extracted {len(topics)} topics")
            return topics
        else:
            data_mining_logger.warning("No valid JSON found in topic extraction response")
            return []
    except Exception as e:
        data_mining_logger.error(f"Error parsing topic extraction response: {e}")
        return []

async def extract_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment in text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary containing sentiment analysis results
    """
    data_mining_logger.debug("Analyzing sentiment in text")
    
    # Create the prompt
    prompt = SENTIMENT_ANALYSIS_PROMPT.format(text=text)
    
    # Generate the analysis
    result = await llm([
        {'role': 'system', 'content': 'You are an expert in sentiment analysis.'},
        {'role': 'user', 'content': prompt}
    ], model=model, temperature=0.1)
    
    # Parse the JSON response
    try:
        # Find JSON object in the response
        json_match = re.search(r'\{\s*"overall_sentiment".*\}', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            sentiment = json.loads(json_str)
            data_mining_logger.debug("Sentiment analysis completed successfully")
            return sentiment
        else:
            data_mining_logger.warning("No valid JSON found in sentiment analysis response")
            return {"overall_sentiment": {"polarity": "neutral", "strength": 0.0, "explanation": "Failed to parse response"}}
    except Exception as e:
        data_mining_logger.error(f"Error parsing sentiment analysis response: {e}")
        return {"overall_sentiment": {"polarity": "neutral", "strength": 0.0, "explanation": f"Error: {str(e)}"}}

async def extract_relationships(text: str) -> List[Dict[str, Any]]:
    """
    Extract relationships between entities in text.
    
    Args:
        text: The text to analyze
        
    Returns:
        List of dictionaries containing relationship information
    """
    data_mining_logger.debug("Extracting relationships from text")
    
    # Create the prompt
    prompt = RELATIONSHIP_EXTRACTION_PROMPT.format(text=text)
    
    # Generate the analysis
    result = await llm([
        {'role': 'system', 'content': 'You are an expert in relationship extraction.'},
        {'role': 'user', 'content': prompt}
    ], model=model, temperature=0.2)
    
    # Parse the JSON response
    try:
        # Find JSON array in the response
        json_match = re.search(r'\[\s*\{.*\}\s*\]', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            relationships = json.loads(json_str)
            data_mining_logger.debug(f"Extracted {len(relationships)} relationships")
            return relationships
        else:
            data_mining_logger.warning("No valid JSON found in relationship extraction response")
            return []
    except Exception as e:
        data_mining_logger.error(f"Error parsing relationship extraction response: {e}")
        return []

async def analyze_temporal_patterns(items: List[Dict[str, Any]], start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Analyze temporal patterns in a collection of information items.
    
    Args:
        items: List of information items with timestamps
        start_date: Start date of the analysis period
        end_date: End date of the analysis period
        
    Returns:
        Dictionary containing temporal pattern analysis results
    """
    data_mining_logger.debug(f"Analyzing temporal patterns from {start_date} to {end_date}")
    
    # Format the items for the prompt
    formatted_items = []
    for i, item in enumerate(items, 1):
        content = item.get('content', '')
        timestamp = item.get('created', '')
        url = item.get('url', '')
        formatted_items.append(f"Item {i} ({timestamp}):\nContent: {content}\nSource: {url}\n")
    
    items_text = "\n".join(formatted_items)
    
    # Create the prompt
    prompt = TEMPORAL_PATTERN_PROMPT.format(
        start_date=start_date,
        end_date=end_date,
        items=items_text
    )
    
    # Generate the analysis
    result = await llm([
        {'role': 'system', 'content': 'You are an expert in temporal pattern analysis.'},
        {'role': 'user', 'content': prompt}
    ], model=model, temperature=0.2)
    
    # Parse the JSON response
    try:
        # Find JSON object in the response
        json_match = re.search(r'\{\s*"patterns".*\}', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            patterns = json.loads(json_str)
            data_mining_logger.debug("Temporal pattern analysis completed successfully")
            return patterns
        else:
            data_mining_logger.warning("No valid JSON found in temporal pattern analysis response")
            return {"patterns": [], "summary": "Failed to parse response"}
    except Exception as e:
        data_mining_logger.error(f"Error parsing temporal pattern analysis response: {e}")
        return {"patterns": [], "summary": f"Error: {str(e)}"}

def generate_knowledge_graph(relationships: List[Dict[str, Any]], output_path: Optional[str] = None) -> nx.DiGraph:
    """
    Generate a knowledge graph from relationship data.
    
    Args:
        relationships: List of relationship dictionaries
        output_path: Optional path to save the graph visualization
        
    Returns:
        NetworkX DiGraph object representing the knowledge graph
    """
    data_mining_logger.debug("Generating knowledge graph")
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes and edges
    for rel in relationships:
        source = rel.get('source', '')
        target = rel.get('target', '')
        relationship = rel.get('relationship', '')
        source_type = rel.get('source_type', '')
        target_type = rel.get('target_type', '')
        
        if not source or not target:
            continue
        
        # Add nodes with attributes
        if not G.has_node(source):
            G.add_node(source, type=source_type)
        
        if not G.has_node(target):
            G.add_node(target, type=target_type)
        
        # Add edge with attributes
        G.add_edge(source, target, relationship=relationship)
    
    data_mining_logger.debug(f"Knowledge graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Visualize and save the graph if output_path is provided
    if output_path and G.number_of_nodes() > 0:
        try:
            plt.figure(figsize=(12, 8))
            
            # Position nodes using spring layout
            pos = nx.spring_layout(G)
            
            # Draw nodes
            node_types = {node: data.get('type', 'unknown') for node, data in G.nodes(data=True)}
            unique_types = set(node_types.values())
            color_map = {t: plt.cm.tab10(i/10) for i, t in enumerate(unique_types)}
            
            for node_type in unique_types:
                nodes = [node for node, t in node_types.items() if t == node_type]
                nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=[color_map[node_type]], label=node_type)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7)
            
            # Draw labels
            nx.draw_networkx_labels(G, pos, font_size=8)
            
            # Draw edge labels
            edge_labels = {(u, v): d.get('relationship', '') for u, v, d in G.edges(data=True)}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
            
            plt.title("Knowledge Graph")
            plt.legend()
            plt.axis('off')
            
            # Save the figure
            plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
            plt.close()
            
            data_mining_logger.debug(f"Knowledge graph visualization saved to {output_path}")
        except Exception as e:
            data_mining_logger.error(f"Error visualizing knowledge graph: {e}")
    
    return G

async def analyze_info_items(info_items: List[Dict[str, Any]], focus_id: str) -> Dict[str, Any]:
    """
    Perform comprehensive analysis on a collection of information items.
    
    Args:
        info_items: List of information items to analyze
        focus_id: ID of the focus point
        
    Returns:
        Dictionary containing analysis results
    """
    data_mining_logger.info(f"Performing comprehensive analysis for focus ID: {focus_id}")
    
    if not info_items:
        data_mining_logger.warning(f"No information items found for focus ID {focus_id}")
        return {"error": "No information items found"}
    
    # Combine all content for entity and topic extraction
    combined_text = "\n\n".join([item.get('content', '') for item in info_items])
    
    # Extract entities, topics, and relationships in parallel
    entities_task = asyncio.create_task(extract_entities(combined_text))
    topics_task = asyncio.create_task(extract_topics(combined_text))
    relationships_task = asyncio.create_task(extract_relationships(combined_text))
    
    # Get start and end dates for temporal analysis
    timestamps = [item.get('created', '') for item in info_items if item.get('created')]
    start_date = min(timestamps) if timestamps else datetime.now().isoformat()
    end_date = max(timestamps) if timestamps else datetime.now().isoformat()
    
    # Analyze temporal patterns
    temporal_patterns_task = asyncio.create_task(analyze_temporal_patterns(info_items, start_date, end_date))
    
    # Wait for all tasks to complete
    entities = await entities_task
    topics = await topics_task
    relationships = await relationships_task
    temporal_patterns = await temporal_patterns_task
    
    # Generate knowledge graph
    graph_output_path = os.path.join(project_dir, f"knowledge_graph_{focus_id}.png")
    knowledge_graph = generate_knowledge_graph(relationships, graph_output_path)
    
    # Create the result
    result = {
        "focus_id": focus_id,
        "item_count": len(info_items),
        "entities": entities,
        "topics": topics,
        "relationships": relationships,
        "temporal_patterns": temporal_patterns,
        "knowledge_graph_path": graph_output_path if os.path.exists(graph_output_path) else None,
        "generated_at": datetime.now().isoformat()
    }
    
    # Save the analysis to the database
    try:
        analysis_record = {
            "focus_id": focus_id,
            "entities": json.dumps(entities),
            "topics": json.dumps(topics),
            "relationships": json.dumps(relationships),
            "temporal_patterns": json.dumps(temporal_patterns),
            "knowledge_graph_path": graph_output_path if os.path.exists(graph_output_path) else None,
            "item_count": len(info_items)
        }
        pb.add(collection_name='data_mining_analysis', body=analysis_record)
        data_mining_logger.info(f"Analysis for focus ID {focus_id} saved to database")
    except Exception as e:
        data_mining_logger.error(f"Error saving analysis to database: {e}")
        # Save to a local file as backup
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        with open(os.path.join(project_dir, f'{timestamp}_analysis_{focus_id}.json'), 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
    
    return result

async def get_analysis_for_focus(focus_id: str, max_age_hours: int = 24) -> Dict[str, Any]:
    """
    Get the most recent data mining analysis for a focus point, generating a new one if needed.
    
    Args:
        focus_id: The ID of the focus point
        max_age_hours: Maximum age of analysis in hours before regenerating
        
    Returns:
        Dictionary containing the analysis results
    """
    data_mining_logger.info(f"Getting data mining analysis for focus ID: {focus_id}")
    
    # Calculate the cutoff time
    cutoff_time = (datetime.now() - timedelta(hours=max_age_hours)).isoformat()
    
    # Try to get recent analysis from the database
    filter_query = f"focus_id='{focus_id}' && created>='{cutoff_time}'"
    recent_analysis = pb.read(collection_name='data_mining_analysis', filter=filter_query, sort="-created")
    
    if recent_analysis:
        data_mining_logger.info(f"Found recent data mining analysis for focus ID {focus_id}")
        analysis = recent_analysis[0]
        
        # Convert JSON strings back to objects
        for field in ['entities', 'topics', 'relationships', 'temporal_patterns']:
            if field in analysis and isinstance(analysis[field], str):
                try:
                    analysis[field] = json.loads(analysis[field])
                except:
                    analysis[field] = []
        
        return analysis
    
    # No recent analysis found, generate a new one
    data_mining_logger.info(f"No recent analysis found for focus ID {focus_id}, generating new one")
    
    # Get information items for this focus point
    info_items = pb.read(collection_name='infos', filter=f"tag='{focus_id}'")
    
    if not info_items:
        data_mining_logger.warning(f"No information items found for focus ID {focus_id}")
        return {"error": f"No information items found for focus ID {focus_id}"}
    
    # Perform analysis
    return await analyze_info_items(info_items, focus_id)