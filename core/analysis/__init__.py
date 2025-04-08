"""
Cross-source analysis for Wiseflow.

This module provides functionality for analyzing data across different sources.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import uuid
from datetime import datetime
import os
import json
import re

logger = logging.getLogger(__name__)

class Entity:
    """Represents an entity extracted from data."""
    
    def __init__(
        self,
        entity_id: str,
        name: str,
        entity_type: str,
        sources: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """Initialize an entity."""
        self.entity_id = entity_id
        self.name = name
        self.entity_type = entity_type
        self.sources = sources
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now()
        self.relationships: List[Relationship] = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary."""
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "entity_type": self.entity_type,
            "sources": self.sources,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "relationships": [rel.to_dict() for rel in self.relationships]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create an entity from a dictionary."""
        timestamp = None
        if data.get("timestamp"):
            try:
                timestamp = datetime.fromisoformat(data["timestamp"])
            except (ValueError, TypeError):
                pass
                
        entity = cls(
            entity_id=data["entity_id"],
            name=data["name"],
            entity_type=data["entity_type"],
            sources=data["sources"],
            metadata=data.get("metadata", {}),
            timestamp=timestamp
        )
        
        # Add relationships
        for rel_data in data.get("relationships", []):
            relationship = Relationship.from_dict(rel_data)
            entity.relationships.append(relationship)
        
        return entity


class Relationship:
    """Represents a relationship between entities."""
    
    def __init__(
        self,
        relationship_id: str,
        source_id: str,
        target_id: str,
        relationship_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """Initialize a relationship."""
        self.relationship_id = relationship_id
        self.source_id = source_id
        self.target_id = target_id
        self.relationship_type = relationship_type
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the relationship to a dictionary."""
        return {
            "relationship_id": self.relationship_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create a relationship from a dictionary."""
        timestamp = None
        if data.get("timestamp"):
            try:
                timestamp = datetime.fromisoformat(data["timestamp"])
            except (ValueError, TypeError):
                pass
                
        return cls(
            relationship_id=data["relationship_id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            relationship_type=data["relationship_type"],
            metadata=data.get("metadata", {}),
            timestamp=timestamp
        )


class KnowledgeGraph:
    """Represents a knowledge graph of entities and relationships."""
    
    def __init__(self, name: str, description: str = ""):
        """Initialize a knowledge graph."""
        self.name = name
        self.description = description
        self.entities: Dict[str, Entity] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the graph."""
        self.entities[entity.entity_id] = entity
        self.updated_at = datetime.now()
        
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID."""
        return self.entities.get(entity_id)
    
    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the graph."""
        source_entity = self.get_entity(relationship.source_id)
        target_entity = self.get_entity(relationship.target_id)
        
        if source_entity and target_entity:
            source_entity.relationships.append(relationship)
            self.updated_at = datetime.now()
        else:
            logger.warning(f"Cannot add relationship: source or target entity not found")
    
    def get_relationships(self, entity_id: str) -> List[Relationship]:
        """Get all relationships for an entity."""
        entity = self.get_entity(entity_id)
        if entity:
            return entity.relationships
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the knowledge graph to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "entities": [entity.to_dict() for entity in self.entities.values()],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeGraph':
        """Create a knowledge graph from a dictionary."""
        graph = cls(
            name=data["name"],
            description=data.get("description", "")
        )
        
        # Set timestamps
        if data.get("created_at"):
            try:
                graph.created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                pass
                
        if data.get("updated_at"):
            try:
                graph.updated_at = datetime.fromisoformat(data["updated_at"])
            except (ValueError, TypeError):
                pass
        
        # Add entities
        for entity_data in data.get("entities", []):
            entity = Entity.from_dict(entity_data)
            graph.entities[entity.entity_id] = entity
        
        return graph
    
    def save(self, filepath: str) -> None:
        """Save the knowledge graph to a file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"Knowledge graph saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving knowledge graph: {e}")
    
    @classmethod
    def load(cls, filepath: str) -> Optional['KnowledgeGraph']:
        """Load a knowledge graph from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            graph = cls.from_dict(data)
            logger.info(f"Knowledge graph loaded from {filepath}")
            return graph
        except Exception as e:
            logger.error(f"Error loading knowledge graph: {e}")
            return None


class CrossSourceAnalyzer:
    """Analyzes data across different sources."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the cross-source analyzer."""
        self.config = config or {}
        self.knowledge_graph = KnowledgeGraph(
            name=self.config.get("graph_name", "Wiseflow Knowledge Graph"),
            description=self.config.get("graph_description", "Knowledge graph for cross-source analysis")
        )
        
    def analyze(self, data_items: List[Dict[str, Any]]) -> KnowledgeGraph:
        """Analyze data items and build a knowledge graph."""
        # Extract entities from data items
        entities = self._extract_entities(data_items)
        
        # Add entities to the knowledge graph
        for entity in entities:
            self.knowledge_graph.add_entity(entity)
        
        # Extract relationships between entities
        relationships = self._extract_relationships(entities)
        
        # Add relationships to the knowledge graph
        for relationship in relationships:
            self.knowledge_graph.add_relationship(relationship)
        
        return self.knowledge_graph
    
    def _extract_entities(self, data_items: List[Dict[str, Any]]) -> List[Entity]:
        """Extract entities from data items."""
        entities = []
        
        for item in data_items:
            try:
                # Extract basic metadata
                source_id = item.get("source_id", "")
                content = item.get("content", "")
                metadata = item.get("metadata", {})
                source_type = metadata.get("type", "")
                
                # Extract entities based on source type
                if source_type == "paper":
                    # Extract authors
                    authors = metadata.get("authors", [])
                    for author in authors:
                        entity_id = f"author_{uuid.uuid4().hex[:8]}"
                        entity = Entity(
                            entity_id=entity_id,
                            name=author,
                            entity_type="person",
                            sources=[source_id],
                            metadata={
                                "role": "author",
                                "source_type": source_type
                            }
                        )
                        entities.append(entity)
                    
                    # Extract the paper itself as an entity
                    title = metadata.get("title", "")
                    if title:
                        entity_id = f"paper_{uuid.uuid4().hex[:8]}"
                        entity = Entity(
                            entity_id=entity_id,
                            name=title,
                            entity_type="paper",
                            sources=[source_id],
                            metadata={
                                "journal": metadata.get("journal", ""),
                                "published": metadata.get("published", ""),
                                "doi": metadata.get("doi", ""),
                                "pmid": metadata.get("pmid", ""),
                                "source_type": source_type
                            }
                        )
                        entities.append(entity)
                
                elif source_type == "video":
                    # Extract the video as an entity
                    title = metadata.get("title", "")
                    if title:
                        entity_id = f"video_{uuid.uuid4().hex[:8]}"
                        entity = Entity(
                            entity_id=entity_id,
                            name=title,
                            entity_type="video",
                            sources=[source_id],
                            metadata={
                                "channel": metadata.get("channel", ""),
                                "published_at": metadata.get("published_at", ""),
                                "video_id": metadata.get("video_id", ""),
                                "source_type": source_type
                            }
                        )
                        entities.append(entity)
                    
                    # Extract the channel as an entity
                    channel = metadata.get("channel", "")
                    if channel:
                        entity_id = f"channel_{uuid.uuid4().hex[:8]}"
                        entity = Entity(
                            entity_id=entity_id,
                            name=channel,
                            entity_type="channel",
                            sources=[source_id],
                            metadata={
                                "source_type": source_type
                            }
                        )
                        entities.append(entity)
                
                elif source_type == "code":
                    # Extract the code file as an entity
                    name = metadata.get("name", "")
                    if name:
                        entity_id = f"code_{uuid.uuid4().hex[:8]}"
                        entity = Entity(
                            entity_id=entity_id,
                            name=name,
                            entity_type="code",
                            sources=[source_id],
                            metadata={
                                "repo": metadata.get("repo", ""),
                                "path": metadata.get("path", ""),
                                "sha": metadata.get("sha", ""),
                                "source_type": source_type
                            }
                        )
                        entities.append(entity)
                
                # Extract common entities from content (simplified)
                # In a real implementation, you would use NLP techniques
                # to extract entities from the content
                
                # For demonstration, we'll just extract some basic patterns
                
                # Extract URLs
                url_pattern = r'https?://[^\s)"]+'
                urls = re.findall(url_pattern, content)
                for url in urls:
                    entity_id = f"url_{uuid.uuid4().hex[:8]}"
                    entity = Entity(
                        entity_id=entity_id,
                        name=url,
                        entity_type="url",
                        sources=[source_id],
                        metadata={
                            "source_type": source_type
                        }
                    )
                    entities.append(entity)
                
                # Extract email addresses
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, content)
                for email in emails:
                    entity_id = f"email_{uuid.uuid4().hex[:8]}"
                    entity = Entity(
                        entity_id=entity_id,
                        name=email,
                        entity_type="email",
                        sources=[source_id],
                        metadata={
                            "source_type": source_type
                        }
                    )
                    entities.append(entity)
                
            except Exception as e:
                logger.error(f"Error extracting entities from data item: {e}")
        
        return entities
    
    def _extract_relationships(self, entities: List[Entity]) -> List[Relationship]:
        """Extract relationships between entities."""
        relationships = []
        
        # Create a dictionary of entities by name for quick lookup
        entities_by_name = {}
        for entity in entities:
            if entity.name not in entities_by_name:
                entities_by_name[entity.name] = []
            entities_by_name[entity.name].append(entity)
        
        # Create a dictionary of entities by type for quick lookup
        entities_by_type = {}
        for entity in entities:
            if entity.entity_type not in entities_by_type:
                entities_by_type[entity.entity_type] = []
            entities_by_type[entity.entity_type].append(entity)
        
        # Create relationships based on entity types
        for entity in entities:
            if entity.entity_type == "person" and entity.metadata.get("role") == "author":
                # Find papers by this author
                for paper_entity in entities_by_type.get("paper", []):
                    if any(source in paper_entity.sources for source in entity.sources):
                        relationship_id = f"rel_{uuid.uuid4().hex[:8]}"
                        relationship = Relationship(
                            relationship_id=relationship_id,
                            source_id=entity.entity_id,
                            target_id=paper_entity.entity_id,
                            relationship_type="authored",
                            metadata={
                                "confidence": 1.0
                            }
                        )
                        relationships.append(relationship)
            
            elif entity.entity_type == "video":
                # Find the channel for this video
                channel_name = entity.metadata.get("channel", "")
                if channel_name:
                    for channel_entity in entities_by_type.get("channel", []):
                        if channel_entity.name == channel_name:
                            relationship_id = f"rel_{uuid.uuid4().hex[:8]}"
                            relationship = Relationship(
                                relationship_id=relationship_id,
                                source_id=channel_entity.entity_id,
                                target_id=entity.entity_id,
                                relationship_type="published",
                                metadata={
                                    "confidence": 1.0
                                }
                            )
                            relationships.append(relationship)
            
            elif entity.entity_type == "code":
                # Find the repository for this code file
                repo_name = entity.metadata.get("repo", "")
                if repo_name:
                    for repo_entity in entities:
                        if repo_entity.entity_type == "repository" and repo_entity.name == repo_name:
                            relationship_id = f"rel_{uuid.uuid4().hex[:8]}"
                            relationship = Relationship(
                                relationship_id=relationship_id,
                                source_id=repo_entity.entity_id,
                                target_id=entity.entity_id,
                                relationship_type="contains",
                                metadata={
                                    "confidence": 1.0
                                }
                            )
                            relationships.append(relationship)
        
        return relationships
    
    def save_graph(self, filepath: str) -> None:
        """Save the knowledge graph to a file."""
        self.knowledge_graph.save(filepath)
    
    def load_graph(self, filepath: str) -> None:
        """Load a knowledge graph from a file."""
        graph = KnowledgeGraph.load(filepath)
        if graph:
            self.knowledge_graph = graph