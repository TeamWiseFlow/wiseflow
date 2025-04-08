"""
Academic archives connector for Wiseflow.

This module provides a connector for academic repositories like arXiv, PubMed, IEEE, etc.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import uuid
from datetime import datetime
import os
import requests
import time
import xml.etree.ElementTree as ET
import json
import re

from core.connectors import ConnectorBase, DataItem

logger = logging.getLogger(__name__)

class AcademicConnector(ConnectorBase):
    """Connector for academic repositories."""
    
    name: str = "academic_connector"
    description: str = "Connector for academic repositories like arXiv, PubMed, IEEE, etc."
    source_type: str = "academic"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the academic connector."""
        super().__init__(config)
        self.apis = {
            "arxiv": {
                "base_url": "http://export.arxiv.org/api/query",
                "enabled": True
            },
            "pubmed": {
                "base_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
                "api_key": None,
                "enabled": True
            },
            "crossref": {
                "base_url": "https://api.crossref.org/works",
                "enabled": True
            }
        }
        
    def initialize(self) -> bool:
        """Initialize the connector."""
        try:
            # Configure APIs from config
            if self.config:
                for api_name, api_config in self.config.items():
                    if api_name in self.apis and isinstance(api_config, dict):
                        self.apis[api_name].update(api_config)
            
            # Get API keys from environment if not in config
            if not self.apis["pubmed"]["api_key"] and "PUBMED_API_KEY" in os.environ:
                self.apis["pubmed"]["api_key"] = os.environ["PUBMED_API_KEY"]
            
            logger.info("Initialized academic connector")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize academic connector: {e}")
            return False
    
    def collect(self, params: Optional[Dict[str, Any]] = None) -> List[DataItem]:
        """Collect data from academic repositories."""
        params = params or {}
        
        # Get search parameters
        query = params.get("query", "")
        if not query:
            logger.error("No query provided for academic connector")
            return []
        
        # Determine which repositories to search
        repositories = params.get("repositories", ["arxiv", "pubmed", "crossref"])
        max_results = params.get("max_results", 10)
        
        results = []
        
        # Search each enabled repository
        for repo in repositories:
            if repo in self.apis and self.apis[repo]["enabled"]:
                try:
                    logger.info(f"Searching {repo} for: {query}")
                    
                    if repo == "arxiv":
                        repo_results = self._search_arxiv(query, max_results)
                    elif repo == "pubmed":
                        repo_results = self._search_pubmed(query, max_results)
                    elif repo == "crossref":
                        repo_results = self._search_crossref(query, max_results)
                    else:
                        repo_results = []
                    
                    results.extend(repo_results)
                    
                    # Respect rate limits
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error searching {repo}: {e}")
        
        logger.info(f"Collected {len(results)} items from academic repositories")
        return results
    
    def _search_arxiv(self, query: str, max_results: int = 10) -> List[DataItem]:
        """Search arXiv for papers."""
        results = []
        try:
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            response = requests.get(self.apis["arxiv"]["base_url"], params=params)
            
            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.content)
                
                # Define namespace
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                
                # Extract entries
                entries = root.findall(".//atom:entry", ns)
                
                for entry in entries:
                    try:
                        # Extract data
                        title = entry.find("atom:title", ns).text.strip()
                        summary = entry.find("atom:summary", ns).text.strip()
                        published = entry.find("atom:published", ns).text
                        
                        # Extract authors
                        authors = []
                        for author in entry.findall(".//atom:author/atom:name", ns):
                            authors.append(author.text)
                        
                        # Extract link
                        links = entry.findall("atom:link", ns)
                        url = ""
                        pdf_url = ""
                        for link in links:
                            rel = link.get("rel", "")
                            if rel == "alternate":
                                url = link.get("href", "")
                            elif rel == "related" and link.get("title") == "pdf":
                                pdf_url = link.get("href", "")
                        
                        # Extract categories/tags
                        categories = []
                        for category in entry.findall("atom:category", ns):
                            categories.append(category.get("term", ""))
                        
                        # Create content
                        content = f"# {title}\n\n"
                        content += f"**Authors:** {', '.join(authors)}\n\n"
                        content += f"**Published:** {published}\n\n"
                        content += f"**Categories:** {', '.join(categories)}\n\n"
                        content += f"**Summary:**\n{summary}\n\n"
                        if pdf_url:
                            content += f"**PDF:** {pdf_url}\n\n"
                        
                        # Create data item
                        item = DataItem(
                            source_id=f"arxiv_{uuid.uuid4().hex[:8]}",
                            content=content,
                            metadata={
                                "title": title,
                                "authors": authors,
                                "published": published,
                                "categories": categories,
                                "pdf_url": pdf_url,
                                "repository": "arxiv",
                                "type": "paper"
                            },
                            url=url,
                            content_type="text/markdown",
                            timestamp=datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ") if published else None
                        )
                        results.append(item)
                    except Exception as e:
                        logger.error(f"Error processing arXiv entry: {e}")
            else:
                logger.warning(f"Failed to search arXiv: {response.status_code}")
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
        
        return results
    
    def _search_pubmed(self, query: str, max_results: int = 10) -> List[DataItem]:
        """Search PubMed for papers."""
        results = []
        try:
            # First, search for IDs
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance"
            }
            
            if self.apis["pubmed"]["api_key"]:
                search_params["api_key"] = self.apis["pubmed"]["api_key"]
            
            search_url = f"{self.apis['pubmed']['base_url']}/esearch.fcgi"
            search_response = requests.get(search_url, params=search_params)
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                pmids = search_data.get("esearchresult", {}).get("idlist", [])
                
                if not pmids:
                    logger.warning(f"No PubMed results found for query: {query}")
                    return results
                
                # Then, fetch details for each ID
                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(pmids),
                    "retmode": "xml"
                }
                
                if self.apis["pubmed"]["api_key"]:
                    fetch_params["api_key"] = self.apis["pubmed"]["api_key"]
                
                fetch_url = f"{self.apis['pubmed']['base_url']}/efetch.fcgi"
                fetch_response = requests.get(fetch_url, params=fetch_params)
                
                if fetch_response.status_code == 200:
                    # Parse XML response
                    root = ET.fromstring(fetch_response.content)
                    
                    # Extract articles
                    articles = root.findall(".//PubmedArticle")
                    
                    for article in articles:
                        try:
                            # Extract PMID
                            pmid = article.find(".//PMID").text
                            
                            # Extract article data
                            article_data = article.find(".//Article")
                            
                            # Extract title
                            title = article_data.find(".//ArticleTitle").text
                            
                            # Extract abstract
                            abstract_element = article_data.find(".//Abstract/AbstractText")
                            abstract = abstract_element.text if abstract_element is not None else "No abstract available"
                            
                            # Extract journal info
                            journal = article_data.find(".//Journal/Title").text
                            
                            # Extract publication date
                            pub_date = article_data.find(".//PubDate")
                            year = pub_date.find("Year").text if pub_date.find("Year") is not None else ""
                            month = pub_date.find("Month").text if pub_date.find("Month") is not None else ""
                            day = pub_date.find("Day").text if pub_date.find("Day") is not None else ""
                            published = f"{year}-{month}-{day}" if day else f"{year}-{month}" if month else year
                            
                            # Extract authors
                            authors = []
                            author_list = article_data.find(".//AuthorList")
                            if author_list is not None:
                                for author in author_list.findall(".//Author"):
                                    last_name = author.find("LastName")
                                    fore_name = author.find("ForeName")
                                    if last_name is not None and fore_name is not None:
                                        authors.append(f"{fore_name.text} {last_name.text}")
                                    elif last_name is not None:
                                        authors.append(last_name.text)
                            
                            # Create content
                            content = f"# {title}\n\n"
                            content += f"**Authors:** {', '.join(authors)}\n\n"
                            content += f"**Journal:** {journal}\n\n"
                            content += f"**Published:** {published}\n\n"
                            content += f"**PMID:** {pmid}\n\n"
                            content += f"**Abstract:**\n{abstract}\n\n"
                            
                            # Create URL
                            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                            
                            # Create data item
                            item = DataItem(
                                source_id=f"pubmed_{pmid}",
                                content=content,
                                metadata={
                                    "title": title,
                                    "authors": authors,
                                    "journal": journal,
                                    "published": published,
                                    "pmid": pmid,
                                    "repository": "pubmed",
                                    "type": "paper"
                                },
                                url=url,
                                content_type="text/markdown"
                            )
                            results.append(item)
                        except Exception as e:
                            logger.error(f"Error processing PubMed article: {e}")
                else:
                    logger.warning(f"Failed to fetch PubMed details: {fetch_response.status_code}")
            else:
                logger.warning(f"Failed to search PubMed: {search_response.status_code}")
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
        
        return results
    
    def _search_crossref(self, query: str, max_results: int = 10) -> List[DataItem]:
        """Search Crossref for papers."""
        results = []
        try:
            params = {
                "query": query,
                "rows": max_results,
                "sort": "relevance",
                "order": "desc"
            }
            
            headers = {
                "User-Agent": "Wiseflow/1.0 (mailto:info@example.com)"
            }
            
            response = requests.get(self.apis["crossref"]["base_url"], params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("message", {}).get("items", [])
                
                for item in items:
                    try:
                        # Extract data
                        title = item.get("title", [""])[0] if item.get("title") else "No title"
                        
                        # Extract authors
                        authors = []
                        for author in item.get("author", []):
                            given = author.get("given", "")
                            family = author.get("family", "")
                            if given and family:
                                authors.append(f"{given} {family}")
                            elif family:
                                authors.append(family)
                        
                        # Extract publication info
                        journal = item.get("container-title", [""])[0] if item.get("container-title") else ""
                        published = item.get("created", {}).get("date-time", "")
                        doi = item.get("DOI", "")
                        
                        # Extract abstract
                        abstract = item.get("abstract", "No abstract available")
                        
                        # Clean up abstract (remove HTML tags)
                        abstract = re.sub(r'<[^>]+>', '', abstract)
                        
                        # Extract URL
                        url = item.get("URL", f"https://doi.org/{doi}" if doi else "")
                        
                        # Create content
                        content = f"# {title}\n\n"
                        content += f"**Authors:** {', '.join(authors)}\n\n"
                        if journal:
                            content += f"**Journal:** {journal}\n\n"
                        content += f"**Published:** {published}\n\n"
                        if doi:
                            content += f"**DOI:** {doi}\n\n"
                        content += f"**Abstract:**\n{abstract}\n\n"
                        
                        # Create data item
                        item = DataItem(
                            source_id=f"crossref_{uuid.uuid4().hex[:8]}",
                            content=content,
                            metadata={
                                "title": title,
                                "authors": authors,
                                "journal": journal,
                                "published": published,
                                "doi": doi,
                                "repository": "crossref",
                                "type": "paper"
                            },
                            url=url,
                            content_type="text/markdown"
                        )
                        results.append(item)
                    except Exception as e:
                        logger.error(f"Error processing Crossref item: {e}")
            else:
                logger.warning(f"Failed to search Crossref: {response.status_code}")
        except Exception as e:
            logger.error(f"Error searching Crossref: {e}")
        
        return results