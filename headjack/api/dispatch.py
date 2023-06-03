import logging

from fastapi import APIRouter

from headjack.agents.agent_dispatch import agent_dispatch
from headjack.models.utterance import User, Utterance

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dispatch", tags=["dispatch"])


@router.post("/{query}")
async def dispatch_request(query: str) -> Utterance:
    return await agent_dispatch(User(utterance=query))
