"""
GitHub connector for Wiseflow.

This module provides a connector for GitHub repositories.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import uuid
from datetime import datetime
import os
import requests
import base64
import time

from core.plugins.connectors import ConnectorBase, DataItem

logger = logging.getLogger(__name__)

class GitHubConnector(ConnectorBase):
    """Connector for GitHub repositories."""
    
    name: str = "github_connector"
    description: str = "Connector for GitHub repositories"
    source_type: str = "github"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the GitHub connector."""
        super().__init__(config)
        self.api_token = None
        self.api_base_url = "https://api.github.com"
        self.headers = {}
        
    def initialize(self) -> bool:
        """Initialize the connector."""
        try:
            # Get API token from config or environment
            self.api_token = self.config.get("api_token")
            if not self.api_token and "GITHUB_TOKEN" in os.environ:
                self.api_token = os.environ["GITHUB_TOKEN"]
            
            if not self.api_token:
                logger.warning("No GitHub API token provided. Rate limits will be restricted.")
                self.headers = {
                    "Accept": "application/vnd.github.v3+json"
                }
            else:
                self.headers = {
                    "Accept": "application/vnd.github.v3+json",
                    "Authorization": f"token {self.api_token}"
                }
            
            logger.info("Initialized GitHub connector")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize GitHub connector: {e}")
            return False
    
    def collect(self, params: Optional[Dict[str, Any]] = None) -> List[DataItem]:
        """Collect data from GitHub repositories."""
        params = params or {}
        
        # Get repositories to collect from
        repos = params.get("repositories", [])
        if not repos:
            if self.config.get("repositories"):
                repos = self.config["repositories"]
            else:
                logger.error("No repositories provided for GitHub connector")
                return []
        
        # Determine what to collect
        collect_readme = params.get("collect_readme", True)
        collect_issues = params.get("collect_issues", False)
        collect_code = params.get("collect_code", False)
        max_issues = params.get("max_issues", 10)
        
        results = []
        
        for repo in repos:
            try:
                # Format: "owner/repo"
                if "/" not in repo:
                    logger.warning(f"Invalid repository format: {repo}. Expected 'owner/repo'")
                    continue
                
                logger.info(f"Collecting data from GitHub repository: {repo}")
                
                # Collect README
                if collect_readme:
                    readme = self._get_readme(repo)
                    if readme:
                        results.append(readme)
                
                # Collect issues
                if collect_issues:
                    issues = self._get_issues(repo, max_issues)
                    results.extend(issues)
                
                # Collect code (basic implementation)
                if collect_code:
                    code_files = self._get_code_files(repo)
                    results.extend(code_files)
                
            except Exception as e:
                logger.error(f"Error collecting data from repository {repo}: {e}")
        
        logger.info(f"Collected {len(results)} items from GitHub")
        return results
    
    def _get_readme(self, repo: str) -> Optional[DataItem]:
        """Get the README file from a repository."""
        try:
            url = f"{self.api_base_url}/repos/{repo}/readme"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                content = base64.b64decode(data["content"]).decode("utf-8")
                
                return DataItem(
                    source_id=f"github_readme_{uuid.uuid4().hex[:8]}",
                    content=content,
                    metadata={
                        "repo": repo,
                        "type": "readme",
                        "path": data.get("path", ""),
                        "sha": data.get("sha", ""),
                        "size": data.get("size", 0),
                        "url": data.get("html_url", "")
                    },
                    url=data.get("html_url", ""),
                    content_type="text/markdown"
                )
            else:
                logger.warning(f"Failed to get README for {repo}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting README for {repo}: {e}")
            return None
    
    def _get_issues(self, repo: str, max_issues: int = 10) -> List[DataItem]:
        """Get issues from a repository."""
        results = []
        try:
            url = f"{self.api_base_url}/repos/{repo}/issues"
            params = {
                "state": "all",
                "per_page": max_issues
            }
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                issues = response.json()
                
                for issue in issues:
                    # Skip pull requests
                    if "pull_request" in issue:
                        continue
                    
                    content = f"# {issue['title']}\n\n{issue['body']}"
                    
                    item = DataItem(
                        source_id=f"github_issue_{issue['number']}_{uuid.uuid4().hex[:8]}",
                        content=content,
                        metadata={
                            "repo": repo,
                            "type": "issue",
                            "number": issue["number"],
                            "state": issue["state"],
                            "created_at": issue["created_at"],
                            "updated_at": issue["updated_at"],
                            "labels": [label["name"] for label in issue.get("labels", [])],
                            "user": issue["user"]["login"] if "user" in issue else "",
                            "comments": issue.get("comments", 0)
                        },
                        url=issue["html_url"],
                        content_type="text/markdown",
                        timestamp=datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ") if "created_at" in issue else None
                    )
                    results.append(item)
            else:
                logger.warning(f"Failed to get issues for {repo}: {response.status_code}")
        except Exception as e:
            logger.error(f"Error getting issues for {repo}: {e}")
        
        return results
    
    def _get_code_files(self, repo: str, path: str = "", max_files: int = 5) -> List[DataItem]:
        """Get code files from a repository."""
        results = []
        try:
            url = f"{self.api_base_url}/repos/{repo}/contents/{path}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                contents = response.json()
                
                # If it's a single file
                if not isinstance(contents, list):
                    if contents.get("type") == "file" and contents.get("size", 0) < 1000000:  # Skip large files
                        try:
                            content = base64.b64decode(contents["content"]).decode("utf-8")
                            
                            item = DataItem(
                                source_id=f"github_code_{uuid.uuid4().hex[:8]}",
                                content=content,
                                metadata={
                                    "repo": repo,
                                    "type": "code",
                                    "path": contents["path"],
                                    "sha": contents["sha"],
                                    "size": contents["size"],
                                    "name": contents["name"]
                                },
                                url=contents["html_url"],
                                content_type=self._get_content_type(contents["name"])
                            )
                            results.append(item)
                        except Exception as e:
                            logger.error(f"Error processing file {contents.get('path')}: {e}")
                    return results
                
                # Process directory contents
                files_processed = 0
                for item in contents:
                    if files_processed >= max_files:
                        break
                    
                    if item["type"] == "file" and item["size"] < 1000000:  # Skip large files
                        # Get file content
                        file_url = f"{self.api_base_url}/repos/{repo}/contents/{item['path']}"
                        file_response = requests.get(file_url, headers=self.headers)
                        
                        if file_response.status_code == 200:
                            file_data = file_response.json()
                            try:
                                content = base64.b64decode(file_data["content"]).decode("utf-8")
                                
                                data_item = DataItem(
                                    source_id=f"github_code_{uuid.uuid4().hex[:8]}",
                                    content=content,
                                    metadata={
                                        "repo": repo,
                                        "type": "code",
                                        "path": item["path"],
                                        "sha": item["sha"],
                                        "size": item["size"],
                                        "name": item["name"]
                                    },
                                    url=item["html_url"],
                                    content_type=self._get_content_type(item["name"])
                                )
                                results.append(data_item)
                                files_processed += 1
                                
                                # Respect rate limits
                                time.sleep(0.5)
                            except Exception as e:
                                logger.error(f"Error processing file {item['path']}: {e}")
            else:
                logger.warning(f"Failed to get contents for {repo}/{path}: {response.status_code}")
        except Exception as e:
            logger.error(f"Error getting code files for {repo}/{path}: {e}")
        
        return results
    
    def _get_content_type(self, filename: str) -> str:
        """Get the content type based on the file extension."""
        ext = os.path.splitext(filename)[1].lower()
        
        content_types = {
            ".py": "text/python",
            ".js": "text/javascript",
            ".ts": "text/typescript",
            ".html": "text/html",
            ".css": "text/css",
            ".json": "application/json",
            ".md": "text/markdown",
            ".txt": "text/plain",
            ".c": "text/c",
            ".cpp": "text/cpp",
            ".h": "text/c-header",
            ".java": "text/java",
            ".go": "text/go",
            ".rs": "text/rust",
            ".rb": "text/ruby",
            ".php": "text/php"
        }
        
        return content_types.get(ext, "text/plain")
