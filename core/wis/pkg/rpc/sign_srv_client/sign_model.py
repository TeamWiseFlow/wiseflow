# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：  
# 1. 不得用于任何商业用途。  
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。  
# 3. 不得进行大规模爬取或对平台造成运营干扰。  
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。   
# 5. 不得用于任何非法或不当的用途。
#   
# 详细许可条款请参阅项目根目录下的LICENSE文件。  
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。  


# -*- coding: utf-8 -*-
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class XhsSignResult(BaseModel):
    x_s: str = Field(..., title="x_s", description="x_s")
    x_t: str = Field(..., title="x_t", description="x_t")
    x_s_common: str = Field(..., title="x_s_common", description="x_s_common")
    x_b3_traceid: str = Field(..., title="x_t_common", description="x_b3_trace_id")
    x_mns: str = Field(..., title="x_mns", description="x_mns")


class XhsSignRequest(BaseModel):
    uri: str = Field(..., title="uri", description="请求的uri")
    data: Optional[Any] = Field(None, title="data", description="请求body的数据")
    cookies: str = Field("", title="cookies", description="cookies")


class XhsSignResponse(BaseModel):
    biz_code: int = 0
    msg: str = "OK!"
    isok: bool = True
    data: Optional[XhsSignResult] = None


class DouyinSignResult(BaseModel):
    a_bogus: str = Field(..., title="a_bogus", description="a_bogus")


class DouyinSignRequest(BaseModel):
    uri: str = Field(..., title="request_uri", description="请求的uri")
    query_params: str = Field(..., title="query_params", description="请求的query_params(urlencode之后的参数)")
    user_agent: str = Field(..., title="user_agent", description="请求的user_agent")
    cookies: str = Field(..., title="cookies", description="请求的cookies")


class DouyinSignResponse(BaseModel):
    biz_code: int = 0
    msg: str = "OK!"
    isok: bool = True
    data: Optional[DouyinSignResult] = None


class BililiSignResult(BaseModel):
    wts: str = Field(..., title="wts", description="wts")
    w_rid: str = Field(..., title="w_rid", description="w_rid")


class BilibliSignRequest(BaseModel):
    req_data: Dict = Field(..., title="req_data", description="json格式的请求参数")
    cookies: str = Field(..., title="cookis", description="登录成功的cookis")


class BilibliSignResponse(BaseModel):
    biz_code: int = 0
    msg: str = "OK!"
    isok: bool = True
    data: Optional[BililiSignResult] = None


class ZhihuSignResult(BaseModel):
    x_zst_81: str = Field(..., title="x_zst_81", description="x_zst_81")
    x_zse_96: str = Field(..., title="x_zse_96", description="x_zse_96")

class ZhihuSignRequest(BaseModel):
    uri: str = Field(..., title="uri", description="请求的uri")
    cookies: str = Field(..., title="cookies", description="请求的cookies")


class ZhihuSignResponse(BaseModel):
    biz_code: int = 0
    msg: str = "OK!"
    isok: bool = True
    data: Optional[ZhihuSignResult] = None
