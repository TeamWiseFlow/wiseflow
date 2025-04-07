"""
YouTube connector for Wiseflow.

This module provides a connector for YouTube videos and channels.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import uuid
from datetime import datetime
import os
import requests
import time
import json
import re

from core.connectors import ConnectorBase, DataItem

logger = logging.getLogger(__name__)

class YouTubeConnector(ConnectorBase):
    """Connector for YouTube videos and channels."""
    
    name: str = "youtube_connector"
    description: str = "Connector for YouTube videos and channels"
    source_type: str = "youtube"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the YouTube connector."""
        super().__init__(config)
        self.api_key = None
        self.api_base_url = "https://www.googleapis.com/youtube/v3"
        
    def initialize(self) -> bool:
        """Initialize the connector."""
        try:
            # Get API key from config or environment
            self.api_key = self.config.get("api_key") if self.config else None
            if not self.api_key and "YOUTUBE_API_KEY" in os.environ:
                self.api_key = os.environ["YOUTUBE_API_KEY"]
            
            if not self.api_key:
                logger.error("No YouTube API key provided")
                return False
            
            logger.info("Initialized YouTube connector")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize YouTube connector: {e}")
            return False
    
    def collect(self, params: Optional[Dict[str, Any]] = None) -> List[DataItem]:
        """Collect data from YouTube."""
        params = params or {}
        
        if not self.api_key:
            if not self.initialize():
                return []
        
        # Determine what to collect
        collection_type = params.get("type", "search")
        query = params.get("query", "")
        channel_id = params.get("channel_id", "")
        video_id = params.get("video_id", "")
        playlist_id = params.get("playlist_id", "")
        max_results = params.get("max_results", 10)
        include_transcripts = params.get("include_transcripts", True)
        
        results = []
        
        try:
            if collection_type == "search" and query:
                # Search for videos
                search_results = self._search_videos(query, max_results)
                results.extend(search_results)
                
                # Get transcripts if requested
                if include_transcripts:
                    for item in search_results:
                        video_id = item.metadata.get("video_id")
                        if video_id:
                            transcript = self._get_transcript(video_id)
                            if transcript:
                                # Create a new data item for the transcript
                                transcript_item = DataItem(
                                    source_id=f"youtube_transcript_{video_id}",
                                    content=transcript,
                                    metadata={
                                        "video_id": video_id,
                                        "title": item.metadata.get("title", ""),
                                        "channel": item.metadata.get("channel", ""),
                                        "type": "transcript"
                                    },
                                    url=f"https://www.youtube.com/watch?v={video_id}",
                                    content_type="text/plain"
                                )
                                results.append(transcript_item)
            
            elif collection_type == "channel" and channel_id:
                # Get channel details
                channel_details = self._get_channel_details(channel_id)
                if channel_details:
                    results.append(channel_details)
                
                # Get channel videos
                channel_videos = self._get_channel_videos(channel_id, max_results)
                results.extend(channel_videos)
                
                # Get transcripts if requested
                if include_transcripts:
                    for item in channel_videos:
                        video_id = item.metadata.get("video_id")
                        if video_id:
                            transcript = self._get_transcript(video_id)
                            if transcript:
                                # Create a new data item for the transcript
                                transcript_item = DataItem(
                                    source_id=f"youtube_transcript_{video_id}",
                                    content=transcript,
                                    metadata={
                                        "video_id": video_id,
                                        "title": item.metadata.get("title", ""),
                                        "channel": item.metadata.get("channel", ""),
                                        "type": "transcript"
                                    },
                                    url=f"https://www.youtube.com/watch?v={video_id}",
                                    content_type="text/plain"
                                )
                                results.append(transcript_item)
            
            elif collection_type == "video" and video_id:
                # Get video details
                video_details = self._get_video_details(video_id)
                if video_details:
                    results.append(video_details)
                
                # Get transcript if requested
                if include_transcripts:
                    transcript = self._get_transcript(video_id)
                    if transcript:
                        # Create a new data item for the transcript
                        transcript_item = DataItem(
                            source_id=f"youtube_transcript_{video_id}",
                            content=transcript,
                            metadata={
                                "video_id": video_id,
                                "title": video_details.metadata.get("title", "") if video_details else "",
                                "channel": video_details.metadata.get("channel", "") if video_details else "",
                                "type": "transcript"
                            },
                            url=f"https://www.youtube.com/watch?v={video_id}",
                            content_type="text/plain"
                        )
                        results.append(transcript_item)
            
            elif collection_type == "playlist" and playlist_id:
                # Get playlist details
                playlist_details = self._get_playlist_details(playlist_id)
                if playlist_details:
                    results.append(playlist_details)
                
                # Get playlist videos
                playlist_videos = self._get_playlist_videos(playlist_id, max_results)
                results.extend(playlist_videos)
                
                # Get transcripts if requested
                if include_transcripts:
                    for item in playlist_videos:
                        video_id = item.metadata.get("video_id")
                        if video_id:
                            transcript = self._get_transcript(video_id)
                            if transcript:
                                # Create a new data item for the transcript
                                transcript_item = DataItem(
                                    source_id=f"youtube_transcript_{video_id}",
                                    content=transcript,
                                    metadata={
                                        "video_id": video_id,
                                        "title": item.metadata.get("title", ""),
                                        "channel": item.metadata.get("channel", ""),
                                        "type": "transcript"
                                    },
                                    url=f"https://www.youtube.com/watch?v={video_id}",
                                    content_type="text/plain"
                                )
                                results.append(transcript_item)
            
            else:
                logger.warning(f"Invalid collection type or missing parameters: {collection_type}")
        
        except Exception as e:
            logger.error(f"Error collecting data from YouTube: {e}")
        
        logger.info(f"Collected {len(results)} items from YouTube")
        return results
    
    def _search_videos(self, query: str, max_results: int = 10) -> List[DataItem]:
        """Search for videos on YouTube."""
        results = []
        try:
            url = f"{self.api_base_url}/search"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": min(max_results, 50),  # API limit is 50
                "key": self.api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                for item in items:
                    try:
                        # Extract data
                        video_id = item["id"]["videoId"]
                        snippet = item["snippet"]
                        title = snippet["title"]
                        description = snippet["description"]
                        channel_title = snippet["channelTitle"]
                        published_at = snippet["publishedAt"]
                        thumbnail_url = snippet["thumbnails"]["high"]["url"] if "high" in snippet["thumbnails"] else ""
                        
                        # Create content
                        content = f"# {title}\n\n"
                        content += f"**Channel:** {channel_title}\n\n"
                        content += f"**Published:** {published_at}\n\n"
                        content += f"**Description:**\n{description}\n\n"
                        content += f"**Video URL:** https://www.youtube.com/watch?v={video_id}\n\n"
                        if thumbnail_url:
                            content += f"**Thumbnail:** {thumbnail_url}\n\n"
                        
                        # Create data item
                        item = DataItem(
                            source_id=f"youtube_video_{video_id}",
                            content=content,
                            metadata={
                                "video_id": video_id,
                                "title": title,
                                "channel": channel_title,
                                "published_at": published_at,
                                "thumbnail_url": thumbnail_url,
                                "type": "video"
                            },
                            url=f"https://www.youtube.com/watch?v={video_id}",
                            content_type="text/markdown",
                            timestamp=datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ") if published_at else None
                        )
                        results.append(item)
                    except Exception as e:
                        logger.error(f"Error processing YouTube search result: {e}")
            else:
                logger.warning(f"Failed to search YouTube: {response.status_code}")
                if response.status_code == 403:
                    logger.error(f"YouTube API quota exceeded or invalid API key")
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
        
        return results
    
    def _get_video_details(self, video_id: str) -> Optional[DataItem]:
        """Get details for a specific video."""
        try:
            url = f"{self.api_base_url}/videos"
            params = {
                "part": "snippet,contentDetails,statistics",
                "id": video_id,
                "key": self.api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                if not items:
                    logger.warning(f"No video found with ID: {video_id}")
                    return None
                
                item = items[0]
                snippet = item["snippet"]
                content_details = item["contentDetails"]
                statistics = item["statistics"]
                
                # Extract data
                title = snippet["title"]
                description = snippet["description"]
                channel_title = snippet["channelTitle"]
                published_at = snippet["publishedAt"]
                thumbnail_url = snippet["thumbnails"]["high"]["url"] if "high" in snippet["thumbnails"] else ""
                duration = content_details["duration"]
                view_count = statistics.get("viewCount", "0")
                like_count = statistics.get("likeCount", "0")
                comment_count = statistics.get("commentCount", "0")
                
                # Create content
                content = f"# {title}\n\n"
                content += f"**Channel:** {channel_title}\n\n"
                content += f"**Published:** {published_at}\n\n"
                content += f"**Duration:** {duration}\n\n"
                content += f"**Views:** {view_count}\n\n"
                content += f"**Likes:** {like_count}\n\n"
                content += f"**Comments:** {comment_count}\n\n"
                content += f"**Description:**\n{description}\n\n"
                content += f"**Video URL:** https://www.youtube.com/watch?v={video_id}\n\n"
                if thumbnail_url:
                    content += f"**Thumbnail:** {thumbnail_url}\n\n"
                
                # Create data item
                return DataItem(
                    source_id=f"youtube_video_{video_id}",
                    content=content,
                    metadata={
                        "video_id": video_id,
                        "title": title,
                        "channel": channel_title,
                        "published_at": published_at,
                        "duration": duration,
                        "view_count": view_count,
                        "like_count": like_count,
                        "comment_count": comment_count,
                        "thumbnail_url": thumbnail_url,
                        "type": "video"
                    },
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    content_type="text/markdown",
                    timestamp=datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ") if published_at else None
                )
            else:
                logger.warning(f"Failed to get video details: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting video details: {e}")
            return None
    
    def _get_channel_details(self, channel_id: str) -> Optional[DataItem]:
        """Get details for a specific channel."""
        try:
            url = f"{self.api_base_url}/channels"
            params = {
                "part": "snippet,contentDetails,statistics",
                "id": channel_id,
                "key": self.api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                if not items:
                    logger.warning(f"No channel found with ID: {channel_id}")
                    return None
                
                item = items[0]
                snippet = item["snippet"]
                content_details = item["contentDetails"]
                statistics = item["statistics"]
                
                # Extract data
                title = snippet["title"]
                description = snippet["description"]
                published_at = snippet["publishedAt"]
                thumbnail_url = snippet["thumbnails"]["high"]["url"] if "high" in snippet["thumbnails"] else ""
                uploads_playlist_id = content_details["relatedPlaylists"]["uploads"]
                subscriber_count = statistics.get("subscriberCount", "0")
                video_count = statistics.get("videoCount", "0")
                view_count = statistics.get("viewCount", "0")
                
                # Create content
                content = f"# {title} (YouTube Channel)\n\n"
                content += f"**Published:** {published_at}\n\n"
                content += f"**Subscribers:** {subscriber_count}\n\n"
                content += f"**Videos:** {video_count}\n\n"
                content += f"**Views:** {view_count}\n\n"
                content += f"**Description:**\n{description}\n\n"
                content += f"**Channel URL:** https://www.youtube.com/channel/{channel_id}\n\n"
                if thumbnail_url:
                    content += f"**Thumbnail:** {thumbnail_url}\n\n"
                
                # Create data item
                return DataItem(
                    source_id=f"youtube_channel_{channel_id}",
                    content=content,
                    metadata={
                        "channel_id": channel_id,
                        "title": title,
                        "published_at": published_at,
                        "subscriber_count": subscriber_count,
                        "video_count": video_count,
                        "view_count": view_count,
                        "uploads_playlist_id": uploads_playlist_id,
                        "thumbnail_url": thumbnail_url,
                        "type": "channel"
                    },
                    url=f"https://www.youtube.com/channel/{channel_id}",
                    content_type="text/markdown",
                    timestamp=datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ") if published_at else None
                )
            else:
                logger.warning(f"Failed to get channel details: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting channel details: {e}")
            return None
    
    def _get_channel_videos(self, channel_id: str, max_results: int = 10) -> List[DataItem]:
        """Get videos from a specific channel."""
        results = []
        try:
            # First, get the channel's uploads playlist ID
            channel_details = self._get_channel_details(channel_id)
            if not channel_details:
                return []
            
            uploads_playlist_id = channel_details.metadata.get("uploads_playlist_id")
            if not uploads_playlist_id:
                logger.warning(f"No uploads playlist found for channel: {channel_id}")
                return []
            
            # Then, get videos from the uploads playlist
            return self._get_playlist_videos(uploads_playlist_id, max_results)
        except Exception as e:
            logger.error(f"Error getting channel videos: {e}")
            return []
    
    def _get_playlist_details(self, playlist_id: str) -> Optional[DataItem]:
        """Get details for a specific playlist."""
        try:
            url = f"{self.api_base_url}/playlists"
            params = {
                "part": "snippet,contentDetails",
                "id": playlist_id,
                "key": self.api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                if not items:
                    logger.warning(f"No playlist found with ID: {playlist_id}")
                    return None
                
                item = items[0]
                snippet = item["snippet"]
                content_details = item["contentDetails"]
                
                # Extract data
                title = snippet["title"]
                description = snippet["description"]
                channel_title = snippet["channelTitle"]
                published_at = snippet["publishedAt"]
                thumbnail_url = snippet["thumbnails"]["high"]["url"] if "high" in snippet["thumbnails"] else ""
                item_count = content_details["itemCount"]
                
                # Create content
                content = f"# {title} (YouTube Playlist)\n\n"
                content += f"**Channel:** {channel_title}\n\n"
                content += f"**Published:** {published_at}\n\n"
                content += f"**Videos:** {item_count}\n\n"
                content += f"**Description:**\n{description}\n\n"
                content += f"**Playlist URL:** https://www.youtube.com/playlist?list={playlist_id}\n\n"
                if thumbnail_url:
                    content += f"**Thumbnail:** {thumbnail_url}\n\n"
                
                # Create data item
                return DataItem(
                    source_id=f"youtube_playlist_{playlist_id}",
                    content=content,
                    metadata={
                        "playlist_id": playlist_id,
                        "title": title,
                        "channel": channel_title,
                        "published_at": published_at,
                        "item_count": item_count,
                        "thumbnail_url": thumbnail_url,
                        "type": "playlist"
                    },
                    url=f"https://www.youtube.com/playlist?list={playlist_id}",
                    content_type="text/markdown",
                    timestamp=datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ") if published_at else None
                )
            else:
                logger.warning(f"Failed to get playlist details: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting playlist details: {e}")
            return None
    
    def _get_playlist_videos(self, playlist_id: str, max_results: int = 10) -> List[DataItem]:
        """Get videos from a specific playlist."""
        results = []
        try:
            url = f"{self.api_base_url}/playlistItems"
            params = {
                "part": "snippet,contentDetails",
                "playlistId": playlist_id,
                "maxResults": min(max_results, 50),  # API limit is 50
                "key": self.api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                for item in items:
                    try:
                        # Extract data
                        snippet = item["snippet"]
                        content_details = item["contentDetails"]
                        
                        video_id = content_details["videoId"]
                        title = snippet["title"]
                        description = snippet["description"]
                        channel_title = snippet["channelTitle"]
                        published_at = snippet["publishedAt"]
                        position = snippet["position"]
                        thumbnail_url = snippet["thumbnails"]["high"]["url"] if "high" in snippet["thumbnails"] else ""
                        
                        # Create content
                        content = f"# {title}\n\n"
                        content += f"**Channel:** {channel_title}\n\n"
                        content += f"**Published:** {published_at}\n\n"
                        content += f"**Position in Playlist:** {position + 1}\n\n"
                        content += f"**Description:**\n{description}\n\n"
                        content += f"**Video URL:** https://www.youtube.com/watch?v={video_id}\n\n"
                        content += f"**Playlist URL:** https://www.youtube.com/playlist?list={playlist_id}\n\n"
                        if thumbnail_url:
                            content += f"**Thumbnail:** {thumbnail_url}\n\n"
                        
                        # Create data item
                        item = DataItem(
                            source_id=f"youtube_playlist_item_{video_id}",
                            content=content,
                            metadata={
                                "video_id": video_id,
                                "playlist_id": playlist_id,
                                "title": title,
                                "channel": channel_title,
                                "published_at": published_at,
                                "position": position,
                                "thumbnail_url": thumbnail_url,
                                "type": "playlist_item"
                            },
                            url=f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}",
                            content_type="text/markdown",
                            timestamp=datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ") if published_at else None
                        )
                        results.append(item)
                    except Exception as e:
                        logger.error(f"Error processing playlist item: {e}")
            else:
                logger.warning(f"Failed to get playlist videos: {response.status_code}")
        except Exception as e:
            logger.error(f"Error getting playlist videos: {e}")
        
        return results
    
    def _get_transcript(self, video_id: str) -> Optional[str]:
        """Get transcript for a specific video using YouTube's transcript API."""
        try:
            # Note: This is a simplified implementation
            # In a real-world scenario, you would use a library like youtube_transcript_api
            # or implement the full API interaction
            
            # For now, we'll use a simple approach to get the transcript
            # This is not a reliable method and is just for demonstration
            
            # In a real implementation, you would use:
            # from youtube_transcript_api import YouTubeTranscriptApi
            # transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            # transcript = " ".join([item["text"] for item in transcript_list])
            
            # Placeholder implementation
            url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"Getting transcript for video: {video_id}")
            
            # This is a placeholder - in a real implementation, you would extract the actual transcript
            return f"This is a placeholder transcript for video {video_id}. In a real implementation, you would extract the actual transcript from the video."
        except Exception as e:
            logger.error(f"Error getting transcript for video {video_id}: {e}")
            return None