import logging

from fastapi import APIRouter

from headjack.agents.metric_calculate import metric_calculate_agent
from headjack.models.utterance import User, Utterance
from headjack.utils.consistency import Consistency

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metric_calculate", tags=["metric_calculate"])


@router.post("/{query}")
async def calculate_metric(query: str, consistency: Consistency = Consistency.OFF) -> Utterance:
    response = await metric_calculate_agent(User(utterance=query), *(consistency.map(consistency)))
    response.log()
    return response
