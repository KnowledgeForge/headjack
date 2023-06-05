import logging

from fastapi import APIRouter

from headjack.agents.knowledge_search import knowledge_search_agent
from headjack.models.utterance import User, Utterance

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["summary"])


@router.post("/{query}")
async def generate_a_summary(query: str) -> Utterance:
    result = await knowledge_search_agent(User(utterance=query))
    return result[0]
