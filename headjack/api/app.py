"""
Headjack web server
"""
import logging
from typing import Any, Dict
from uuid import UUID, uuid4
import uvicorn
import jwt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from headjack.config import get_chroma_client

import os

from headjack.models.session import Session

_logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.environ.get('HEADJACK_SECRET', "headjack_secret")
PORT = os.environ.get('HEADJACK_PORT', "8679")

# locate templates
templates = Jinja2Templates(directory="web")


@app.get("/")
def get_home():
    return templates.TemplateResponse("chat-demo.html", {"PORT": PORT})


@app.get("/session")
def new_session():
    access_token = jwt.encode({"session_id": str(uuid4())}, SECRET_KEY, algorithm="HS256")
    return {"access_token": access_token}


def decode_token(access_token: str) -> Dict[str, Any]:
    return jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])


def get_agent_session(access_token: str):
    payload = decode_token(access_token)
    session_id = payload["session_id"]
    session_uuid = UUID(session_id)
    if session := Session.sessions.get(session_uuid):
        return session
    from headjack.agents.standard import StandardAgent
    from headjack.models.tool import ToolSchema, Tool

    knowledge_search_schema = ToolSchema(
        **{
            "name": "Knowledge Search",
            "description": "Tool used to search for general knowledge."
            "Multiple queries can be provided for relevant results for each.",
            "parameters": [
                {
                    "name": "query",
                    "description": "Distinct queries",
                    "type": "string",
                    "max_length": 3,
                },
            ],
        }
    )
    knowledge_search = Tool(knowledge_search_schema)
    tools = [knowledge_search]
    agent = StandardAgent(
        model_identifier="chatgpt",
        tools=tools,
        decoder="argmax(openai_chunksize=4)",
    )
    session = Session(agent, session_id=session_uuid)
    return session

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, access_token: str, websocket: WebSocket):
        payload = decode_token(access_token)
        session_id = payload["session_id"]
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, access_token: str):
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
        session_id = payload["session_id"]
        del self.active_connections[session_id]


manager = ConnectionManager()


@app.websocket("/chat/{access_token}")
async def websocket_endpoint(websocket: WebSocket, access_token: str):
    await manager.connect(access_token, websocket)
    session = get_agent_session(access_token)

    while True:
        try:
            data = await websocket.receive_json()
            message = data["message"]
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

            
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
