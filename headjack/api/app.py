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

from os import path

basepath = path.dirname(__file__)
template_path = path.abspath(path.join(basepath, "..", "..", "web/chat-demo.html"))
# locate templates
with open(template_path) as f:
    template=f.read()



@app.get("/")
def get_home():
    # import pdb; pdb.set_trace()
    return HTMLResponse(template.replace("PORT", PORT))
# templates.TemplateResponse("chat-demo.html", context={"request":request, "PORT": PORT})


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
    from headjack.models.tool import ToolSchema, Tool, HTTPVerb, Param

    knowledge_search_schema = ToolSchema(
        url="http://0.0.0.0:16410/query",
        verb=HTTPVerb.GET,
        name="Knowledge Search",
        description="Tool used to search for general knowledge. Asking a question will return documents containing relevant information.",
        parameters=[
            {
                "name": "text",
                "description": "A succinct piece of text that asks a targeted question to find relevant knowledge documents.",
                "type": "string",
                "max_value": 50,
            },
            {"name": "collection", "type": "string", "options": ["knowledge"]},
        ],
        results={"type": "string", "max_length": 100},
        code="""
    def process_observation(action_input, observation_input):
        return [i for j in observation_input['documents'] for i in j]
    """,
    )
    knowledge_search = Tool(knowledge_search_schema)

    metric_search_schema = ToolSchema(
        url="http://0.0.0.0:16410/query",
        verb=HTTPVerb.GET,
        name="Metric Search",
        description="Tool used to search for metrics. Asking a question will return documents containing relevant information.",
        parameters=[
            {
                "name": "text",
                "description": "Short sequence of words to find relevant metrics.",
                "type": "string",
                "max_value": 50,
            },
            {"name": "collection", "type": "string", "options": ["metrics"]},
        ],
        results={'name': {"type": "string", "max_length": 100}, 'ref_name': {"type": "string", "max_length": 100}, 'query': {"type": "string", "max_length": 100}},
        code="""
    def process_observation(action_input, observation_input):
        return {'name': observation_input['documents'][0], 'ref_name': [m['name'] for m in observation_input['metadatas'][0]], 'query': [m['query'] for m in observation_input['metadatas'][0]]}
    """,
    )

    metric_search = Tool(metric_search_schema)

    metric_dimension_search_schema = ToolSchema(
        url="http://localhost:8000/metrics/common/dimensions",
        verb=HTTPVerb.GET,
        name="Metric Dimension Search",
        description="Tool used to search for dimensions that can be used with a selected metric.",
        parameters=[
            {
                "name": "metric",
                "description": "Metric to search for compatible dimension columns for.",
                "type": "string",
                "options": {"ref": "Metric Search.results.ref_name"},
            },
        ],
        results={"type": "string", "max_length": 100},
    )

    metric_dimension_search = Tool(metric_dimension_search_schema)

    metric_calculate_schema = ToolSchema(
        url="http://localhost:8000/data",
        verb=HTTPVerb.GET,
        name="Metric Calculate",
        description="Tool used to calculate the value of a metric. Choose a metric and at least some dimension or filter.",
        parameters=[
            {
                "name": "metrics",
                "description": "Metric to search for compatible dimension columns for.",
                "type": "string",
                "options": {"ref": "Metric Dimension Search.parameters[0]"},
            },
            {
                "name": "dimensions",
                "description": "Columns to select to group by.",
                "type": [
                    {
                        "name": "groupby column 1",
                        "type": "string",
                        "required": False,
                        "options": {"ref": "Metric Dimension Search.results"},
                    },
                    {
                        "name": "groupby column 2",
                        "type": "string",
                        "required": False,
                        "options": {"ref": "Metric Dimension Search.results"},
                    },
                    {
                        "name": "groupby column 3",
                        "type": "string",
                        "required": False,
                        "options": {"ref": "Metric Dimension Search.results"},
                    },
                ],
            },
            # {
            #     "name": "filters",
            #     "description": "SQL filter expressions using dimension columns from Metric Dimension Search results",
            #     "type": "string",
            #     "max_length": 3,
            #     "required": False,
            # },
        ],
        feedback_retries = 1,
        result_answer=True,
        results={"type": "string"},
        code="""
    def process_action(action_input):
        params=action_input['parameters']
        if not params[1] and not params[2]:
            raise ValueError("at least one of 'dimension' or 'filters' is required")
        return action_input
        
    def process_observation(action_input, observation_input):
        return str(observation_input['results'])
    """,
    )

    metric_calculate = Tool(metric_calculate_schema)
        
    tools = [knowledge_search, metric_search, metric_calculate]
    agent = StandardAgent(
        model_identifier="chatgpt",
        tools=tools,
        decoder="argmax(openai_chunksize=4, chatty_openai=True)",
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

            
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
