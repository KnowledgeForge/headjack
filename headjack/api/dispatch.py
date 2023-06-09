import logging

from fastapi import APIRouter

from headjack.agents.agent_dispatch import agent_dispatch
from headjack.models.utterance import User, Utterance
from headjack.utils.consistency import Consistency

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dispatch", tags=["dispatch"])


@router.post("/{query}")
async def dispatch_request(query: str, consistency: Consistency = Consistency.OFF) -> Utterance:
    response = await agent_dispatch(User(utterance=query), *(consistency.map(consistency)))
    response.log()
    return response
