import logging

from fastapi import APIRouter
from starlette.responses import JSONResponse

from headjack.agents.metric_search import metric_search_agent

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metric_search", tags=["metric_search"])


@router.post("/{query}")
async def search_for_metrics(query: str) -> JSONResponse:
    return await metric_search_agent(query)
