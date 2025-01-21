import feedparser
from loguru import logger
import os, sys
import json
from urllib.parse import urlparse

core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(core_path)

from utils.general_utils import isURL


def get_links_from_rss(rss_url: str, existing_urls: set, _logger: logger = None) -> [str]:
    try:
        feed = feedparser.parse(rss_url)
    except Exception as e:
        if _logger:
            _logger.warning(f"RSS feed is not valid: {e}")
        return []
    
    return [entry.link for entry in feed.entries if entry.link and entry.link not in existing_urls]
