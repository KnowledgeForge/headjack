import logging
from uuid import UUID, uuid4

import jwt
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from headjack_server.agents.standard import StandardAgent
from headjack_server.models.session import Session
from headjack_server.models.utterance import Answer, User
from headjack_server.tools.knowledge_search import KnowledgeSearchTool

_logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "secret"
PORT = 8769
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>HeadJack Chat Client</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css">
    <link rel="icon" href="https://avatars.githubusercontent.com/u/131468933?s=40&v=4">
</head>
<body class="bg-gray-200">
    <div class="max-w-4xl mx-auto px-4 py-8">
        <div class="flex items-center mb-8">
            <img src="https://avatars.githubusercontent.com/u/131468933?s=40&v=4" class="h-8 w-8 mr-2" alt="HeadJack Icon" />
            <h1 class="text-2xl font-bold">HeadJack Chat Client</h1>
        </div>
        <div class="flex justify-between items-center mb-4">
            <button id="new_session" class="bg-blue-500 text-white font-semibold px-4 py-2 rounded-lg">New Session</button>
            <label class="inline-flex items-center mt-3">
                <input type="checkbox" class="form-checkbox h-5 w-5 text-gray-600" id="debug"><span class="ml-2">Debug</span>
            </label>
        </div>
        <div id="messages" class="bg-white rounded-lg shadow-lg p-4 mb-4 disabled" style="height: 500px; overflow-y: scroll;"></div>
        <form id="form" class="flex items-center disabled">
            <input id="input" class="flex-grow border border-gray-400 px-4 py-2 rounded-lg mr-2 focus:outline-none focus:border-blue-500" autocomplete="off" autofocus disabled/>
            <button id="submit" class="bg-blue-500 text-white font-semibold px-4 py-2 rounded-lg disabled">
                <span id="submit-text">Send</span>
                <div id="submit-loading" class="bg-blue-500 w-8 h-8 ml-2 rounded-full flex justify-center items-center hidden">
                    <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                </div>
            </button>
        </form>
    </div>

    <script>
        let ws;
        let access_token;

        const messages = document.getElementById('messages');
        const form = document.getElementById('form');
        const input = document.getElementById('input');
        const submitButton = document.getElementById('submit');
        const submitText = document.getElementById('submit-text');
        const submitLoading = document.getElementById('submit-loading');
        const newSession = document.getElementById('new_session');
        const debug = document.getElementById('debug');

        newSession.addEventListener('click', () => {{
            fetch('/session')
                .then(res => res.json())
                .then(data => {{
                    access_token = data.access_token;
                    messages.classList.remove('disabled');
                    form.classList.remove('disabled');
                    input.disabled = false;
                    submitButton.disabled = false;
                    ws = new WebSocket(`ws://localhost:{PORT}/ws/${{access_token}}`);
                    ws.onmessage = onMessage;
                    newSession.style.display = 'none';
                }})
        }})

        function onMessage(event) {{
            const data = JSON.parse(event.data);

            let item;
            if (data.kind === 'User') {{
                item = document.createElement('div');
                item.classList.add('text-right', 'bg-blue-100');
                item.textContent = data.message;
            }}
            if (data.kind!=="" && (data.kind === 'Answer' || debug.checked)) {{
                item = document.createElement('div');
                item.classList.add('text-left', 'bg-gray-100');
                item.textContent = data.message;
            }}
            const info = document.createElement('div');
            info.classList.add('text-xs', 'italic', 'text-gray-500');
            info.textContent = `${{data.kind}} - ${{data.time}}`;
            item.appendChild(info);
            messages.appendChild(item);
            messages.scrollTo(0, messages.scrollHeight);

            if (data.message !== "") {{
                input.disabled = false;
                submitButton.disabled = false;
                submitButton.classList.remove('opacity-50');
                submitText.classList.remove('hidden');
                submitLoading.classList.add('hidden');
            }}
        }}

        form.onsubmit = async (event) => {{
            event.preventDefault();
            if (!ws) return;
            input.disabled = true;
            submitButton.disabled = true;
            submitButton.classList.add('opacity-50');
            submitText.classList.add('hidden');
            submitLoading.classList.remove('hidden');
            const message = input.value;
            ws.send(JSON.stringify({{kind: "User", message}}));
            let item = document.createElement('div');
            item.classList.add('text-right', 'bg-blue-100');
            item.textContent = message;
            const info = document.createElement('div');
            info.classList.add('text-xs', 'italic', 'text-gray-500');
            info.textContent = `User - ${{new Date().toISOString()}}`;
            item.appendChild(info);
            messages.appendChild(item);
            messages.scrollTo(0, messages.scrollHeight);
            input.value = '';
            input.focus();
        }};
    </script>
</body>
</html>
"""


@app.get("/")
def get():
    return HTMLResponse(html_template)


@app.get("/session")
def new_session():
    access_token = jwt.encode({"session_id": str(uuid4())}, SECRET_KEY, algorithm="HS256")
    return {"access_token": access_token}


def get_agent_session(access_token: str):
    payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
    session_id = payload["session_id"]
    session_uuid = UUID(session_id)
    if session := Session.sessions.get(session_uuid):
        return session
    tools = [KnowledgeSearchTool()]
    agent = StandardAgent(
        model_identifier="chatgpt",
        tools=tools,
        decoder="argmax(openai_chunksize=4)",
    )
    session = Session(agent, session_id=session_uuid)
    return session


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, access_token: str, websocket: WebSocket):
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
        session_id = payload["session_id"]
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, access_token: str):
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
        session_id = payload["session_id"]
        del self.active_connections[session_id]


manager = ConnectionManager()


@app.websocket("/ws/{access_token}")
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
    uvicorn.run(app, host="0.0.0.0", port=PORT)
