"""
LiteLLM wrapper for Wiseflow.

This module provides a wrapper for the LiteLLM library.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
import json
import asyncio

try:
    import litellm
    from litellm import completion
except ImportError:
    raise ImportError("LiteLLM is not installed. Please install it with 'pip install litellm'.")

logger = logging.getLogger(__name__)

class LiteLLMWrapper:
    """Wrapper for the LiteLLM library."""
    
    def __init__(self, default_model: Optional[str] = None):
        """Initialize the LiteLLM wrapper."""
        self.default_model = default_model or os.environ.get("PRIMARY_MODEL", "")
        if not self.default_model:
            logger.warning("No default model specified for LiteLLM wrapper")
    
    def generate(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate text using LiteLLM."""
        try:
            model = model or self.default_model
            if not model:
                raise ValueError("No model specified for generation")
            
            messages = [
                {"role": "system", "content": "You are an expert information extractor."},
                {"role": "user", "content": prompt}
            ]
            
            response = completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text with LiteLLM: {e}")
            raise

def litellm_llm(messages: List[Dict[str, str]], model: str, temperature: float = 0.7, max_tokens: int = 1000, logger=None) -> str:
    """Generate text using LiteLLM."""
    try:
        response = completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    except Exception as e:
        if logger:
            logger.error(f"Error generating text with LiteLLM: {e}")
        raise

async def litellm_llm_async(messages: List[Dict[str, str]], model: str, temperature: float = 0.7, max_tokens: int = 1000, logger=None) -> str:
    """Generate text using LiteLLM asynchronously."""
    try:
        # Run in a thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        )
        
        return response.choices[0].message.content
    except Exception as e:
        if logger:
            logger.error(f"Error generating text with LiteLLM async: {e}")
        raise