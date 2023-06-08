import logging
from typing import List

from fastapi import APIRouter

from headjack.agents.plot_data import PlotDataColumn, plot_data
from headjack.models.utterance import Observation, User, Utterance
from headjack.utils.consistency import Consistency

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plot", tags=["plot"])


@router.post("/{query}")
async def plot(query: str, columns: List[PlotDataColumn], consistency: Consistency = Consistency.OFF) -> Utterance:
    utterance = User(utterance=query, parent_=Observation(utterance={"results": {"columns": columns}}))
    return await plot_data(utterance, *(consistency.map(consistency)))
