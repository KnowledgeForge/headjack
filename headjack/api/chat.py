from fastapi import APIRouter
from typing import Dict
import logging
import jwt
from fastapi import WebSocket, WebSocketDisconnect
from os import path
from fastapi.responses import HTMLResponse

from headjack.api.helpers import get_agent_session, decode_token, get_access_token
from headjack.config import get_settings, get_headjack_secret

_logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/chat',
    tags = ['chat']
)


basepath = path.dirname(__file__)
template_path = path.abspath(path.join(basepath, "..", "..", "web/chat-demo.html"))
# locate templates
with open(template_path) as f:
    template = f.read()

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


manager = ConnectionManager()

@router.get("/session")
def new_session():
    return {"access_token": get_access_token()}

@router.get("/")
def get_home():
    settings = get_settings()
    return HTMLResponse(template.replace("PORT", settings.port))


@router.websocket("/{access_token}")
async def websocket_endpoint(websocket: WebSocket, access_token: str):
    await manager.connect(access_token, websocket)
    session = get_agent_session(access_token)

    while True:
        try:
            data = await websocket.receive_json()
            message = data["message"]
            print(message)
            _logger.info(f"User message: {message}")
            async for response in session(message):
                await websocket.send_json(
                    {
                        "message": str(response.utterance_),
                        "marker": response.marker,
                        "kind": response.__class__.__name__,
                        "time": response.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    },
                )
            await websocket.send_json({"message": "", "marker": "", "kind": "", "time": ""})
        except WebSocketDisconnect:
            manager.disconnect(access_token)

