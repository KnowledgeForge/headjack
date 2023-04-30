import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()
PORT = 8679
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
        <div id="messages" class="bg-white rounded-lg shadow-lg p-4 mb-4" style="height: 500px; overflow-y: scroll;"></div>
        <form id="form" class="flex items-center">
            <input id="input" class="flex-grow border border-gray-400 px-4 py-2 rounded-lg mr-2 focus:outline-none focus:border-blue-500" autocomplete="off" autofocus/>
            <button id="submit" class="bg-blue-500 text-white font-semibold px-4 py-2 rounded-lg">
                <span id="submit-text">Send</span>
                <div id="submit-loading" class="bg-blue-500 w-8 h-8 ml-2 rounded-full flex justify-center items-center hidden">
                    <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                </div>
            </button>
        </form>
    </div>
    <script>
        const messages = document.getElementById('messages');
        const form = document.getElementById('form');
        const input = document.getElementById('input');
        const submitButton = document.getElementById('submit');
        const submitText = document.getElementById('submit-text');
        const submitLoading = document.getElementById('submit-loading');

        const ws = new WebSocket('ws://localhost:{PORT}/ws');

        ws.onmessage = (event) => {{
            const item = document.createElement('div');
            item.textContent = event.data;
            messages.appendChild(item);
            messages.scrollTo(0, messages.scrollHeight);
            input.disabled = false;
            submitButton.disabled = false;
            submitButton.classList.remove('opacity-50');
            submitText.classList.remove('hidden');
            submitLoading.classList.add('hidden');
        }};

        form.onsubmit = async (event) => {{
            event.preventDefault();
            input.disabled = true;
            submitButton.disabled = true;
            submitButton.classList.add('opacity-50');
            submitText.classList.add('hidden');
            submitLoading.classList.remove('hidden');
            ws.send(input.value);
            input.value = '';
        }};
    </script>
</body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(content=html_template)


from headjack.agents.standard import StandardAgent
from headjack.models.session import Session
from headjack.tools.knowledge_search import KnowledgeSearchTool

tools = [KnowledgeSearchTool()]
# agent = StandardAgent(
#     model_identifier="chatgpt",
#     tools=tools,
#     decoder="argmax(openai_chunksize=4)",
# )
agent = StandardAgent(
    model_identifier="openai/text-ada-001",
    tools=tools,
    decoder="argmax",
)
session = Session(agent)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(data)
        async for response in session(str(data)):
            await websocket.send_text(str(response))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8679)
