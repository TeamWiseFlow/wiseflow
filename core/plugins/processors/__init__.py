"""
Processors for Wiseflow.

This module provides base classes for data processors.
"""

from typing import Dict, List, Any, Optional, Union
from abc import abstractmethod
import logging
from datetime import datetime

from core.plugins import PluginBase
from core.connectors import DataItem

logger = logging.getLogger(__name__)

class ProcessedData:
    """Represents processed data from a processor."""
    
    def __init__(
        self,
        original_item: Optional[DataItem] = None,
        processed_content: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """Initialize processed data."""
        self.original_item = original_item
        self.processed_content = processed_content
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the processed data to a dictionary."""
        return {
            "original_item": self.original_item.to_dict() if self.original_item else None,
            "processed_content": self.processed_content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessedData':
        """Create processed data from a dictionary."""
        timestamp = None
        if data.get("timestamp"):
            try:
                timestamp = datetime.fromisoformat(data["timestamp"])
            except (ValueError, TypeError):
                pass
                
        original_item = None
        if data.get("original_item"):
            try:
                from core.connectors import DataItem
                original_item = DataItem.from_dict(data["original_item"])
            except Exception as e:
                logger.error(f"Error creating DataItem from dictionary: {e}")
        
        return cls(
            original_item=original_item,
            processed_content=data.get("processed_content"),
            metadata=data.get("metadata", {}),
            timestamp=timestamp
        )


class ProcessorBase(PluginBase):
    """Base class for data processors."""
    
    name: str = "base_processor"
    description: str = "Base processor class"
    processor_type: str = "generic"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the processor with optional configuration."""
        super().__init__(config)
        
    @abstractmethod
    def process(self, data_item: DataItem, params: Optional[Dict[str, Any]] = None) -> ProcessedData:
        """Process a data item."""
        pass
    
    def initialize(self) -> bool:
        """Initialize the processor. Return True if successful, False otherwise."""
        try:
            # Perform any necessary initialization
            logger.info(f"Initialized processor: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize processor {self.name}: {e}")
            return False
