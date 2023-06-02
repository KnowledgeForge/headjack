import logging

from fastapi import APIRouter

from headjack.agents.metric_calculate import metric_calculate_agent
from headjack.models.utterance import User, Utterance

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metric_calculate", tags=["metric_calculate"])


@router.post("/{query}")
async def calculate_metric(query: str) -> Utterance:
    return await metric_calculate_agent(User(query))
