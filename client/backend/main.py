# 这是后端服务的fastapi框架程序
from fastapi import FastAPI
from pydantic import BaseModel
from __init__ import BackendService
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException


class InvalidInputException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=442, detail=detail)


class TranslateRequest(BaseModel):
    article_ids: list[str]


class ReportRequest(BaseModel):
    insight_id: str
    toc: list[str] = [""]  # 第一个元素为大标题，其余为段落标题。第一个元素必须存在，可以是空字符，llm会自动拟标题。
    comment: str = ""


app = FastAPI(
    title="首席情报官 Backend Server",
    description="From DSW Team.",
    version="0.2",
    openapi_url="/openapi.json"
)

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 如果有多个后端服务，可以在这里定义多个后端服务的实例
bs = BackendService()


@app.get("/")
def read_root():
    msg = "Hello, 欢迎使用首席情报官 Backend."
    return {"msg": msg}


@app.post("/translations")
def translate_all_articles(request: TranslateRequest):
    return bs.translate(request.article_ids)


@app.post("/search_for_insight")
def add_article_from_insight(request: ReportRequest):
    return bs.more_search(request.insight_id)


@app.post("/report")
def report(request: ReportRequest):
    return bs.report(request.insight_id, request.toc, request.comment)
