"""
Headjack web server
"""
import argparse
import logging
from enum import Enum

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from headjack.api import (
    chat,
    dispatch,
    messages,
    metric_calculate,
    metric_search,
    people,
    plot,
    summary,
)
from headjack.config import get_settings
from headjack.utils import fetch

_logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(chat.router)
app.include_router(summary.router)
app.include_router(metric_search.router)
app.include_router(metric_calculate.router)
app.include_router(messages.router)
app.include_router(dispatch.router)
app.include_router(people.router)
app.include_router(plot.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class COLLECTION_TYPE(str, Enum):
    knowledge = "knowledge"
    metrics = "metrics"
    messages = "messages"
    people = "people"


@app.get("/count")
async def get_number_of_documents(collection: COLLECTION_TYPE) -> JSONResponse:
    settings = get_settings()
    count = await fetch(f"{settings.search_service}/count?collection={collection}", "GET", return_json=True)
    return count


def cli():
    settings = get_settings()
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Host", default=settings.host)
    parser.add_argument("--port", help="Port", default=settings.port, type=int)
    parser.add_argument("--log-level", help="Log Level", default=None, type=int)
    parser.add_argument("--log-config", help="Log config file", default=None, type=str)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level, log_config=args.log_config)
