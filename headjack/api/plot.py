import logging
from typing import List

from fastapi import APIRouter

from headjack.agents.plot_data import PlotDataColumn, plot_data_agent
from headjack.models.utterance import Observation, User, Utterance
from headjack.utils.consistency import Consistency

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plot", tags=["plot"])


@router.post("/{query}")
async def plot(query: str, columns: List[PlotDataColumn], consistency: Consistency = Consistency.OFF) -> Utterance:
    utterance = User(utterance=query, parent=Observation(utterance={"results": {"columns": columns}}))
    response = await plot_data_agent(utterance, *(consistency.map(consistency)))
    response.log()
    return response
