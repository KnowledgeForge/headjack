import logging

from fastapi import APIRouter

from headjack.agents.agent_dispatch import agent_dispatch

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dispatch", tags=["dispatch"])


@router.post("/{query}")
async def dispatch_request(query: str) -> str:
    return (await agent_dispatch(query))
