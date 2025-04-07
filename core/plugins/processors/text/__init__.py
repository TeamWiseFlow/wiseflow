"""
Text processor for Wiseflow.

This module provides a processor for text data.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import json
import asyncio
import re
from datetime import datetime

from core.plugins.processors import ProcessorBase, ProcessedData
from core.connectors import DataItem
from core.llms.litellm_wrapper import litellm_llm

logger = logging.getLogger(__name__)

class TextProcessor(ProcessorBase):
    """Processor for text data."""
    
    name: str = "text_processor"
    description: str = "Processor for text data"
    processor_type: str = "text"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the text processor."""
        super().__init__(config)
        
    def process(self, data_item: DataItem, params: Optional[Dict[str, Any]] = None) -> ProcessedData:
        """Process a text data item."""
        params = params or {}
        
        # Extract focus point information
        focus_point = params.get("focus_point", "")
        explanation = params.get("explanation", "")
        prompts = params.get("prompts", [])
        
        if not focus_point:
            logger.warning("No focus point provided for text processing")
            return ProcessedData(
                original_item=data_item,
                processed_content=[],
                metadata={"error": "No focus point provided"}
            )
        
        if not data_item.content:
            logger.warning(f"No content in data item {data_item.source_id}")
            return ProcessedData(
                original_item=data_item,
                processed_content=[],
                metadata={"error": "No content in data item"}
            )
        
        # Process the text using LLM
        try:
            # Run the processing in an event loop
            loop = asyncio.get_event_loop()
            processed_content = loop.run_until_complete(
                self._process_with_llm(
                    data_item.content, 
                    focus_point, 
                    explanation, 
                    prompts,
                    data_item.metadata.get("author", ""),
                    data_item.metadata.get("publish_date", "")
                )
            )
            
            return ProcessedData(
                original_item=data_item,
                processed_content=processed_content,
                metadata={
                    "focus_point": focus_point,
                    "explanation": explanation,
                    "source_type": data_item.content_type,
                    "processing_time": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error processing text data: {e}")
            return ProcessedData(
                original_item=data_item,
                processed_content=[],
                metadata={"error": str(e)}
            )
    
    async def _process_with_llm(self, content: str, focus_point: str, explanation: str, prompts: List[str], author: str, publish_date: str) -> List[Dict[str, Any]]:
        """Process text content with LLM."""
        if not prompts or len(prompts) < 3:
            logger.warning("Insufficient prompts provided")
            return []
        
        system_prompt, user_prompt, model = prompts
        
        # Prepare the content
        # Split content into chunks if it's too long
        max_chunk_size = 8000  # Adjust based on model's context window
        chunks = self._split_content(content, max_chunk_size)
        
        results = []
        for chunk in chunks:
            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{chunk}\n\n{user_prompt}"}
                ]
                
                response = litellm_llm(messages, model)
                
                # Parse the response
                parsed_results = self._parse_llm_response(response, author, publish_date)
                results.extend(parsed_results)
                
            except Exception as e:
                logger.error(f"Error processing chunk with LLM: {e}")
        
        return results
    
    def _split_content(self, content: str, max_size: int) -> List[str]:
        """Split content into chunks of maximum size."""
        if len(content) <= max_size:
            return [content]
        
        # Split by paragraphs
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= max_size:
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += paragraph
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If a single paragraph is too long, split it further
                if len(paragraph) > max_size:
                    # Split by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                    current_chunk = ""
                    
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 <= max_size:
                            if current_chunk:
                                current_chunk += " "
                            current_chunk += sentence
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            
                            # If a single sentence is too long, just truncate it
                            if len(sentence) > max_size:
                                for i in range(0, len(sentence), max_size):
                                    chunks.append(sentence[i:i+max_size])
                            else:
                                current_chunk = sentence
                else:
                    current_chunk = paragraph
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _parse_llm_response(self, response: str, author: str, publish_date: str) -> List[Dict[str, Any]]:
        """Parse the LLM response into structured data."""
        try:
            # Try to parse as JSON
            if response.startswith("```json") and response.endswith("```"):
                json_str = response[7:-3].strip()
                data = json.loads(json_str)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data]
            
            # Try to extract JSON from the response
            json_pattern = r'```json\s*([\s\S]*?)\s*```'
            matches = re.findall(json_pattern, response)
            if matches:
                for match in matches:
                    try:
                        data = json.loads(match)
                        if isinstance(data, list):
                            return data
                        elif isinstance(data, dict):
                            return [data]
                    except:
                        pass
            
            # If we can't parse as JSON, create a simple structure
            return [{
                "content": response,
                "author": author,
                "publish_date": publish_date,
                "type": "text"
            }]
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return [{
                "content": response,
                "author": author,
                "publish_date": publish_date,
                "type": "text",
                "parsing_error": str(e)
            }]
