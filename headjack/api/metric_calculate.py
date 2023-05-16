import logging

from fastapi import APIRouter
from starlette.responses import JSONResponse

from headjack.agents.metric_calculate import metric_calculate_agent

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metric_calculate", tags=["metric_calculate"])


@router.post("/{query}")
async def calculate_metric(query: str) -> JSONResponse:
    return await metric_calculate_agent(query)
