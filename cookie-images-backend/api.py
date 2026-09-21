from contextlib import asynccontextmanager
from typing import Literal
from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.db import DrawTable, close_db
from app.models.response import DrawResponse
from app.models.draw import DrawDocItem


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_db()
    print('DB CLOSED')


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def pagination(
    pn: int = Query(default=0, ge=0),
    ps: int = Query(default=20, ge=12, le=42),
):
    return {"pn": pn, "ps": ps}


def query_options(
    order: Literal["default", "random", "time_asc"] = Query(default="default"),
    filter_type: list[Literal["pixiv", "nico", "x", "all"]] | None = Query(default='all'),
    filter_user: list[int] | None = Query(default=[-1]),
    keyword: str = Query(default=""),
):
    return {"order": order, "filter_type": filter_type, "filter_user": filter_user, "keyword": keyword}


@app.get("/")
async def root(params: dict = Depends(pagination), options: dict = Depends(query_options)):
    data = DrawTable.search(pn=params["pn"], ps=params["ps"], **options)
    return DrawResponse(pn=params["pn"], ps=params["ps"], code=0, message="OK", data=data)
