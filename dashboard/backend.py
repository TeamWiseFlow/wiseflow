from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Literal, Optional
from fastapi.middleware.cors import CORSMiddleware


# backend的操作也应该是针对 pb 操作的，即添加信源、兴趣点等都应该存入 pb，而不是另起一个进程实例
# 当然也可以放弃 pb，但那是另一个问题，数据和设置的管理应该是一套
# 简单说用户侧（api dashboard等）和 core侧 不应该直接对接，都应该通过底层的data infrastructure 进行

class Request(BaseModel):
    """
    Input model
    input = {'user_id': str, 'type': str, 'content':str， 'addition': Optional[str]}
    Type is one of "text", "publicMsg", "site" and "url"；
    """
    user_id: str
    type: Literal["text", "publicMsg", "file", "image", "video", "location", "chathistory", "site", "attachment", "url"]
    content: str
    addition: Optional[str] = None


app = FastAPI(
    title="WiseFlow Union Backend",
    description="From Wiseflow Team.",
    version="0.3.1",
    openapi_url="/openapi.json"
)

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
def read_root():
    msg = "Hello, this is Wise Union Backend, version 0.3.1"
    return {"msg": msg}


@app.post("/feed")
async def call_to_feed(background_tasks: BackgroundTasks, request: Request):
    background_tasks.add_task(message_manager, _input=request.model_dump())
    return {"msg": "received well"}
