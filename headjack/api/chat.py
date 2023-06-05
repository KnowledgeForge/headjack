import logging
from typing import Dict

import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from headjack.agents.chat_agent import chat_agent
from headjack.api.helpers import decode_token, get_access_token
from headjack.config import get_headjack_secret
from headjack.models.utterance import User, Utterance

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    parent=None
    while True:
        data = await websocket.receive_json()
        print("data:", data)
        #data should be {utterance: messages}
        user = User.parse_obj(data)
        user.parent_=parent
        print(user)
        _logger.info(f"User chat message: `{user}`")
        print("awaiting response")
        response = await chat_agent(user)
        print("response", response)
        parent=response[0]
        await websocket.send_text(json.dumps(response[0].dict()))
        # await manager.send_utterance(access_token, response[0])
        print("sending response")

