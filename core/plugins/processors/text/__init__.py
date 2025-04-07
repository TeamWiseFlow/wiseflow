"""
Text processors for Wiseflow.

This module provides processors for text data.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import json
import os

from core.plugins.processors import ProcessorBase, ProcessedData
from core.plugins.connectors import DataItem
from core.llms.litellm_wrapper import LiteLLMWrapper

logger = logging.getLogger(__name__)

class FocusPointProcessor(ProcessorBase):
    """Processor that extracts information based on focus points using LLMs."""
    
    name: str = "focus_point_processor"
    description: str = "Extracts information based on focus points using LLMs"
    processor_type: str = "text"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the focus point processor."""
        super().__init__(config)
        self.llm = None
        self.focus_points = self.config.get("focus_points", [])
        
    def initialize(self) -> bool:
        """Initialize the processor."""
        try:
            # Initialize the LLM
            self.llm = LiteLLMWrapper()
            
            # Load focus points if not provided in config
            if not self.focus_points and self.config.get("focus_points_path"):
                path = self.config["focus_points_path"]
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        self.focus_points = json.load(f)
            
            if not self.focus_points:
                logger.warning("No focus points provided for focus point processor")
            
            logger.info(f"Initialized focus point processor with {len(self.focus_points)} focus points")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize focus point processor: {e}")
            return False
    
    def process(self, data_item: DataItem, params: Optional[Dict[str, Any]] = None) -> ProcessedData:
        """Process a data item by extracting information based on focus points."""
        params = params or {}
        
        # Get focus points from params or use the ones from config
        focus_points = params.get("focus_points", self.focus_points)
        if not focus_points:
            logger.warning("No focus points provided for processing")
            return ProcessedData(
                source_id=data_item.source_id,
                processed_content="",
                original_item=data_item,
                metadata={"error": "No focus points provided"}
            )
        
        # Prepare the prompt
        prompt = self._create_prompt(data_item.content, focus_points)
        
        try:
            # Process with LLM
            if not self.llm:
                self.initialize()
            
            response = self.llm.generate(prompt)
            
            # Parse the response
            extracted_info = self._parse_response(response)
            
            return ProcessedData(
                source_id=data_item.source_id,
                processed_content=extracted_info,
                original_item=data_item,
                metadata={
                    "focus_points": focus_points,
                    "url": data_item.url,
                    "title": data_item.metadata.get("title", "")
                }
            )
        except Exception as e:
            logger.error(f"Error processing item {data_item.source_id}: {e}")
            return ProcessedData(
                source_id=data_item.source_id,
                processed_content="",
                original_item=data_item,
                metadata={"error": str(e)}
            )
    
    def _create_prompt(self, content: str, focus_points: List[Dict[str, Any]]) -> str:
        """Create a prompt for the LLM based on the content and focus points."""
        focus_points_str = "\n".join([
            f"{i+1}. {fp.get('focuspoint', '')}: {fp.get('explanation', '')}"
            for i, fp in enumerate(focus_points)
        ])
        
        prompt = f"""
You are an expert information extractor. Your task is to analyze the following content and extract information related to specific focus points.

FOCUS POINTS:
{focus_points_str}

CONTENT:
{content}

For each focus point, extract any relevant information from the content. If there is no relevant information for a focus point, indicate "No relevant information found".

Format your response as a JSON object with the following structure:
{{
  "focus_point_1": {{
    "relevant": true/false,
    "information": "extracted information or summary",
    "confidence": 0-100
  }},
  "focus_point_2": {{
    "relevant": true/false,
    "information": "extracted information or summary",
    "confidence": 0-100
  }},
  ...
}}

Only include the JSON object in your response, nothing else.
"""
        return prompt
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data."""
        try:
            # Try to extract JSON from the response
            response = response.strip()
            
            # Find JSON object in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx+1]
                return json.loads(json_str)
            
            # If no JSON found, return the raw response
            return {"raw_response": response}
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return {"error": str(e), "raw_response": response}
