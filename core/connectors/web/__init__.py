"""
Web connector for Wiseflow.

This module provides a connector for web sources using crawl4ai.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import uuid
from datetime import datetime
import os

from core.plugins.connectors import ConnectorBase, DataItem
from core.crawl4ai.async_webcrawler import AsyncWebCrawler
from core.crawl4ai.content_scraping_strategy import ContentScrapingStrategy
from core.crawl4ai.async_configs import AsyncConfigs

logger = logging.getLogger(__name__)

class WebConnector(ConnectorBase):
    """Connector for web sources."""
    
    name: str = "web_connector"
    description: str = "Connector for web sources using crawl4ai"
    source_type: str = "web"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the web connector."""
        super().__init__(config)
        self.crawler: Optional[AsyncWebCrawler] = None
        
    def initialize(self) -> bool:
        """Initialize the connector."""
        try:
            # Create the crawler
            configs = AsyncConfigs()
            
            # Apply custom configurations if provided
            if self.config.get("max_depth"):
                configs.max_depth = self.config["max_depth"]
            if self.config.get("max_pages"):
                configs.max_pages = self.config["max_pages"]
            if self.config.get("timeout"):
                configs.timeout = self.config["timeout"]
            if self.config.get("user_agent"):
                configs.user_agent = self.config["user_agent"]
            
            # Create the crawler
            self.crawler = AsyncWebCrawler(configs)
            logger.info(f"Initialized web connector with config: {configs}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize web connector: {e}")
            return False
    
    def collect(self, params: Optional[Dict[str, Any]] = None) -> List[DataItem]:
        """Collect data from web sources."""
        params = params or {}
        urls = params.get("urls", [])
        if not urls:
            if self.config.get("urls"):
                urls = self.config["urls"]
            else:
                logger.error("No URLs provided for web connector")
                return []
        
        if not self.crawler:
            if not self.initialize():
                return []
        
        results = []
        for url in urls:
            try:
                # Crawl the URL
                logger.info(f"Crawling URL: {url}")
                crawl_result = self.crawler.crawl(url)
                
                # Process the crawl result
                for page_url, page_data in crawl_result.items():
                    content = page_data.get("content", "")
                    metadata = {
                        "title": page_data.get("title", ""),
                        "links": page_data.get("links", []),
                        "crawl_time": datetime.now().isoformat()
                    }
                    
                    # Create a data item
                    item = DataItem(
                        source_id=f"web_{uuid.uuid4().hex[:8]}",
                        content=content,
                        metadata=metadata,
                        url=page_url,
                        content_type="text/html",
                        language=page_data.get("language")
                    )
                    results.append(item)
            except Exception as e:
                logger.error(f"Error crawling URL {url}: {e}")
        
        logger.info(f"Collected {len(results)} items from web sources")
        return results
