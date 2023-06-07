import logging

from fastapi import APIRouter

from headjack.agents.knowledge_search import knowledge_search_agent
from headjack.models.utterance import User, Utterance
from headjack.utils.consistency import Consistency

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["summary"])


@router.post("/{query}")
async def generate_a_summary(query: str, consistency: Consistency = Consistency.OFF) -> Utterance:
    result = await knowledge_search_agent(User(utterance=query), *Consistency.map(consistency))  # type: ignore
    return result
