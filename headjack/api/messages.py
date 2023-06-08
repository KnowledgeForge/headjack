import logging

from fastapi import APIRouter

from headjack.agents.messages_search import messages_search_agent
from headjack.models.utterance import User, Utterance
from headjack.utils.consistency import Consistency

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/{query}")
async def find_conversations(query: str, consistency: Consistency = Consistency.OFF) -> Utterance:
    result = await messages_search_agent(User(utterance=query), *Consistency.map(consistency))  # type: ignore
    return result
