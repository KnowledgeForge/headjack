import json
import logging

from fastapi import APIRouter, WebSocket

from headjack.agents.chat_agent import chat_agent
from headjack.models.utterance import User

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    parent = None
    while True:
        data = await websocket.receive_json()
        user = User.parse_obj(data)
        user.parent_ = parent
        _logger.info(f"User chat message: `{user}`")
        response = await chat_agent(user)
        parent = response[0]
        await websocket.send_text(json.dumps(response[0].dict()))
