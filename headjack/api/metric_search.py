import logging

from fastapi import APIRouter

from headjack.agents.metric_search import metric_search_agent
from headjack.models.utterance import User, Utterance
from headjack.utils.consistency import Consistency

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metric_search", tags=["metric_search"])


@router.post("/{query}")
async def search_for_metrics(query: str, consistency: Consistency = Consistency.OFF) -> Utterance:
    response = await metric_search_agent(User(utterance=query), *(consistency.map(consistency)))
    response.log()
    return response
