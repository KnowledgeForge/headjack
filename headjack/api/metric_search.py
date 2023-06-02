import logging

from fastapi import APIRouter

from headjack.agents.metric_search import metric_search_agent
from headjack.models.utterance import User, Utterance

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metric_search", tags=["metric_search"])


@router.post("/{query}")
async def search_for_metrics(query: str) -> Utterance:
    return await metric_search_agent(User(query))
