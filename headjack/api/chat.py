import json
import logging

from fastapi import APIRouter, WebSocket

from headjack.agents.chat_agent import chat_agent
from headjack.models.utterance import User, Utterance
from headjack.utils.consistency import Consistency

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_consistency: Consistency = Consistency.OFF,
    agent_consistency=Consistency.OFF,
    max_agent_uses: int = 3,
):
    await websocket.accept()
    parent = None
    while True:
        data = await websocket.receive_json()
        user = User.parse_obj(data)
        user.parent = parent
        try:
            response = await chat_agent(user, max_agent_uses, chat_consistency, agent_consistency)
        except Exception as e:
            response = Utterance(utterance=f"The chat agent ran into an unexpected error: {str(e)}")
        parent = response
        parent.log()
        await websocket.send_text(json.dumps(response.dict()))
