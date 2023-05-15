"""
Headjack web server
"""
import argparse
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from headjack.api import chat, metric_search, summary, metric_calculate
from headjack.config import get_settings

_logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat.router)
app.include_router(summary.router)
app.include_router(metric_search.router)
app.include_router(metric_calculate.router)

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Host", default="0.0.0.0")
    parser.add_argument("--port", help="Port", default=8679, type=int)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
