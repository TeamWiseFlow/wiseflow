"""
Reference management for Wiseflow.

This module provides functionality for managing reference materials for focus points.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import os
import uuid
import json
import shutil
from datetime import datetime
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class Reference:
    """Represents a reference for a focus point."""
    
    def __init__(
        self,
        reference_id: str,
        focus_id: str,
        reference_type: str,
        path: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """Initialize a reference."""
        self.reference_id = reference_id
        self.focus_id = focus_id
        self.reference_type = reference_type
        self.path = path
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the reference to a dictionary."""
        return {
            "reference_id": self.reference_id,
            "focus_id": self.focus_id,
            "reference_type": self.reference_type,
            "path": self.path,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reference':
        """Create a reference from a dictionary."""
        timestamp = None
        if data.get("timestamp"):
            try:
                timestamp = datetime.fromisoformat(data["timestamp"])
            except (ValueError, TypeError):
                pass
                
        return cls(
            reference_id=data["reference_id"],
            focus_id=data["focus_id"],
            reference_type=data["reference_type"],
            path=data["path"],
            content=data.get("content"),
            metadata=data.get("metadata", {}),
            timestamp=timestamp
        )


class ReferenceManager:
    """Manages reference materials for focus points."""
    
    def __init__(self, storage_path: str = "references"):
        """Initialize the reference manager."""
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.references: Dict[str, Reference] = {}
        self.load_references()
        
    def load_references(self) -> None:
        """Load references from storage."""
        index_path = os.path.join(self.storage_path, "index.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    data = json.load(f)
                    for ref_data in data:
                        ref = Reference.from_dict(ref_data)
                        self.references[ref.reference_id] = ref
                logger.info(f"Loaded {len(self.references)} references from storage")
            except Exception as e:
                logger.error(f"Error loading references: {e}")
        
    def save_references(self) -> None:
        """Save references to storage."""
        index_path = os.path.join(self.storage_path, "index.json")
        try:
            with open(index_path, 'w') as f:
                json.dump([ref.to_dict() for ref in self.references.values()], f, indent=2)
            logger.info(f"Saved {len(self.references)} references to storage")
        except Exception as e:
            logger.error(f"Error saving references: {e}")
    
    def add_file_reference(self, focus_id: str, file_path: str) -> Optional[Reference]:
        """Add a file reference to a focus point."""
        try:
            # Generate a unique reference ID
            reference_id = str(uuid.uuid4())
            
            # Create a copy of the file in the storage directory
            filename = os.path.basename(file_path)
            storage_dir = os.path.join(self.storage_path, focus_id)
            os.makedirs(storage_dir, exist_ok=True)
            
            dest_path = os.path.join(storage_dir, f"{reference_id}_{filename}")
            shutil.copy2(file_path, dest_path)
            
            # Extract content from the file
            content = self._extract_content_from_file(file_path)
            
            # Create the reference
            reference = Reference(
                reference_id=reference_id,
                focus_id=focus_id,
                reference_type="file",
                path=dest_path,
                content=content,
                metadata={
                    "original_path": file_path,
                    "filename": filename
                }
            )
            
            # Add to references
            self.references[reference_id] = reference
            self.save_references()
            
            return reference
        except Exception as e:
            logger.error(f"Error adding file reference: {e}")
            return None
    
    def add_web_reference(self, focus_id: str, url: str) -> Optional[Reference]:
        """Add a web reference to a focus point."""
        try:
            # Generate a unique reference ID
            reference_id = str(uuid.uuid4())
            
            # Create a storage directory
            storage_dir = os.path.join(self.storage_path, focus_id)
            os.makedirs(storage_dir, exist_ok=True)
            
            # Parse the URL to get a filename
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path) or "webpage"
            if not filename.endswith(".html"):
                filename += ".html"
            
            dest_path = os.path.join(storage_dir, f"{reference_id}_{filename}")
            
            # Download the content
            content = self._download_web_content(url)
            
            # Save the content
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create the reference
            reference = Reference(
                reference_id=reference_id,
                focus_id=focus_id,
                reference_type="web",
                path=dest_path,
                content=content,
                metadata={
                    "url": url,
                    "domain": parsed_url.netloc
                }
            )
            
            # Add to references
            self.references[reference_id] = reference
            self.save_references()
            
            return reference
        except Exception as e:
            logger.error(f"Error adding web reference: {e}")
            return None
    
    def add_text_reference(self, focus_id: str, content: str, name: str = "text_reference") -> Optional[Reference]:
        """Add a text reference to a focus point."""
        try:
            # Generate a unique reference ID
            reference_id = str(uuid.uuid4())
            
            # Create a storage directory
            storage_dir = os.path.join(self.storage_path, focus_id)
            os.makedirs(storage_dir, exist_ok=True)
            
            # Create a filename
            filename = f"{name}.txt"
            dest_path = os.path.join(storage_dir, f"{reference_id}_{filename}")
            
            # Save the content
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create the reference
            reference = Reference(
                reference_id=reference_id,
                focus_id=focus_id,
                reference_type="text",
                path=dest_path,
                content=content,
                metadata={
                    "name": name
                }
            )
            
            # Add to references
            self.references[reference_id] = reference
            self.save_references()
            
            return reference
        except Exception as e:
            logger.error(f"Error adding text reference: {e}")
            return None
    
    def get_reference(self, reference_id: str) -> Optional[Reference]:
        """Get a reference by ID."""
        return self.references.get(reference_id)
    
    def get_references_by_focus(self, focus_id: str) -> List[Reference]:
        """Get all references for a focus point."""
        return [ref for ref in self.references.values() if ref.focus_id == focus_id]
    
    def delete_reference(self, reference_id: str) -> bool:
        """Delete a reference."""
        if reference_id in self.references:
            reference = self.references[reference_id]
            
            # Delete the file
            try:
                if os.path.exists(reference.path):
                    os.remove(reference.path)
            except Exception as e:
                logger.error(f"Error deleting reference file: {e}")
            
            # Remove from references
            del self.references[reference_id]
            self.save_references()
            
            return True
        return False
    
    def _extract_content_from_file(self, file_path: str) -> str:
        """Extract content from a file."""
        try:
            # Simple text extraction for now
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error extracting content from file: {e}")
            return ""
    
    def _download_web_content(self, url: str) -> str:
        """Download content from a URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error downloading web content: {e}")
            return ""
