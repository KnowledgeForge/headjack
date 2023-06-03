import json
import logging
from typing import Dict

import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from headjack.api.helpers import decode_token, get_access_token
from headjack.config import get_headjack_secret
from headjack.agents.chat_agent import chat_agent
from headjack.models.utterance import Utterance

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, access_token: str, websocket: WebSocket):
        payload = decode_token(access_token)
        session_id = payload["session_id"]
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, access_token: str):
        payload = jwt.decode(access_token, get_headjack_secret(), algorithms=["HS256"])
        session_id = payload["session_id"]
        del self.active_connections[session_id]

    async def send_utterance(self, access_token: str, utterance: Utterance):
        payload = decode_token(access_token)
        session_id = payload["session_id"]
        websocket = self.active_connections.get(session_id)
        if websocket:
            await websocket.send_json(
                utterance.dict()
            )


manager = ConnectionManager()


@router.get("/session")
def start_a_new_session():
    return {"access_token": get_access_token()}


@router.websocket("/{access_token}")
async def websocket_endpoint(websocket: WebSocket, access_token: str):
    await manager.connect(access_token, websocket)
    while True:
        try:
            data = await websocket.receive_json()
            user = Utterance.parse_obj(data)
            _logger.info(f"User message: {user}")
            response = await chat_agent(user)
            await manager.send_utterance(access_token, response)
        except WebSocketDisconnect:
            manager.disconnect(access_token)