import time

from pydantic import BaseModel, Field


class IpInfoModel(BaseModel):
    """Unified IP model"""
    ip: str = Field(title="ip")
    port: int = Field(title="端口")
    user: str = Field(title="IP代理认证的用户名")
    protocol: str = Field(default="https", title="代理IP的协议")
    password: str = Field(title="IP代理认证用户的密码")
    expired_time_ts: int = Field(title="IP过期时间时间戳，单位秒")

    def format_httpx_proxy(self) -> str:
        """
        Get the httpx proxy string
        Returns:

        """
        httpx_proxy = f"{self.protocol}://{self.user}:{self.password}@{self.ip}:{self.port}"
        return httpx_proxy

    @property
    def is_expired(self) -> bool:
        """
        Check if the IP is expired
        Returns:
            bool: True if the IP is expired, False otherwise
            Note: expired_time_ts=0 means never expire
        """
        if self.expired_time_ts == 0:
            return False  # Never expire
        return self.expired_time_ts < int(time.time())
    

class IpGetError(Exception):
    """ ip get error"""
