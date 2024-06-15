from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Literal, Optional
from fastapi.middleware.cors import CORSMiddleware
from insights import pipeline


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
    version="0.1.1",
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
    msg = "Hello, this is Wise Union Backend, version 0.1.1"
    return {"msg": msg}


@app.post("/feed")
async def call_to_feed(background_tasks: BackgroundTasks, request: Request):
    background_tasks.add_task(pipeline, _input=request.model_dump())
    return {"msg": "received well"}
