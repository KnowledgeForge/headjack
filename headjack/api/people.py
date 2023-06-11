import logging

from fastapi import APIRouter

from headjack.agents.people_search import people_search_agent
from headjack.models.utterance import User, Utterance
from headjack.utils.consistency import Consistency

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/people", tags=["people"])


@router.post("/{query}")
async def find_people(query: str, consistency: Consistency = Consistency.OFF) -> Utterance:
    result = await people_search_agent(User(utterance=query), *Consistency.map(consistency))  # type: ignore
    return result
