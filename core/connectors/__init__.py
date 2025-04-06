"""
Data source connectors for Wiseflow.

This module provides base classes for data source connectors.
"""

from typing import Dict, List, Any, Optional, Union
from abc import abstractmethod
import logging
from datetime import datetime

from core.plugins import PluginBase

logger = logging.getLogger(__name__)

class DataItem:
    """Represents a single item of data collected from a source."""
    
    def __init__(
        self,
        source_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        url: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        content_type: str = "text",
        language: Optional[str] = None,
        raw_data: Optional[Any] = None
    ):
        """Initialize a data item."""
        self.source_id = source_id
        self.content = content
        self.metadata = metadata or {}
        self.url = url
        self.timestamp = timestamp or datetime.now()
        self.content_type = content_type
        self.language = language
        self.raw_data = raw_data
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the data item to a dictionary."""
        return {
            "source_id": self.source_id,
            "content": self.content,
            "metadata": self.metadata,
            "url": self.url,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "content_type": self.content_type,
            "language": self.language
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataItem':
        """Create a data item from a dictionary."""
        timestamp = None
        if data.get("timestamp"):
            try:
                timestamp = datetime.fromisoformat(data["timestamp"])
            except (ValueError, TypeError):
                pass
                
        return cls(
            source_id=data["source_id"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            url=data.get("url"),
            timestamp=timestamp,
            content_type=data.get("content_type", "text"),
            language=data.get("language")
        )


class ConnectorBase(PluginBase):
    """Base class for data source connectors."""
    
    name: str = "base_connector"
    description: str = "Base connector class"
    source_type: str = "generic"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the connector with optional configuration."""
        super().__init__(config)
        self.last_run: Optional[datetime] = None
        
    @abstractmethod
    def collect(self, params: Optional[Dict[str, Any]] = None) -> List[DataItem]:
        """Collect data from the source."""
        pass
    
    def initialize(self) -> bool:
        """Initialize the connector. Return True if successful, False otherwise."""
        try:
            # Perform any necessary initialization
            logger.info(f"Initialized connector: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize connector {self.name}: {e}")
            return False
    
    def update_last_run(self) -> None:
        """Update the last run timestamp."""
        self.last_run = datetime.now()
        
    def get_last_run(self) -> Optional[datetime]:
        """Get the last run timestamp."""
        return self.last_run
