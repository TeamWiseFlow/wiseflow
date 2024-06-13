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
    toc: list[str] = [""]  # The first element is a headline, and the rest are paragraph headings. The first element must exist, can be a null character, and llm will automatically make headings.
    comment: str = ""


app = FastAPI(
    title="wiseflow Backend Server",
    description="From WiseFlow Team.",
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

bs = BackendService()


@app.get("/")
def read_root():
    msg = "Hello, This is WiseFlow Backend."
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
