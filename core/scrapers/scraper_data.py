from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class ScraperResultData:
    """用于存储网页抓取数据的数据类"""
    url: str
    content: Optional[str] = None
    links: Optional[Dict[str, str]] = None
    images: Optional[List[str]] = None
    author: Optional[str] = None
    publish_date: Optional[str] = None
    title: Optional[str] = None
    base: Optional[str] = None

    def __post_init__(self):
        # 验证 url 是否存在且为字符串类型
        if not isinstance(self.url, str) or not self.url.strip():
            raise ValueError("URL 必须是非空字符串")

        # 初始化可选字段
        if self.images is None:
            self.images = []
        
        if self.links is None:
            self.links = {}

        # 确保 publish_date 是字符串格式
        if self.publish_date is not None:
            if isinstance(self.publish_date, datetime):
                self.publish_date = self.publish_date.isoformat()
            elif not isinstance(self.publish_date, str):
                self.publish_date = str(self.publish_date)

        # 确保 images 是列表类型
        if self.images is not None:
            if not isinstance(self.images, list):
                raise ValueError("images 必须是列表类型")
