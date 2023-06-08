import logging

from fastapi import APIRouter

from headjack.agents.plot_data import PlotData, plot_data
from headjack.models.utterance import Observation, User, Utterance
from headjack.utils.consistency import Consistency

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plot", tags=["plot"])


@router.post("/{query}")
async def plot(query: str, data: PlotData, consistency: Consistency = Consistency.OFF) -> Utterance:
    utterance = User(utterance=query, parent_=Observation(utterance={"results": data}))
    return await plot_data(utterance, *(consistency.map(consistency)))
