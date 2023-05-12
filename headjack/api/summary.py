import logging

from fastapi import APIRouter
from headjack.agents.knowledge_search import knowledge_search_agent
_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["summary"])


@router.post("/{query}")
async def generate_a_summary(query: str)->str:
    return (await knowledge_search_agent(query))[0].variables['ANSWER']
