import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()
PORT = 8679
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Headjack</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css">
</head>
<body class="bg-gray-200">
    <div class="max-w-xl mx-auto px-4 py-8">
        <h1 class="text-2xl font-bold mb-4">Headjack</h1>
        <div id="messages" class="bg-white rounded-lg shadow-lg p-4 mb-4" style="height: 300px; overflow-y: scroll;"></div>
        <form id="form" class="flex items-center">
            <input id="input" class="flex-grow border border-gray-400 px-4 py-2 rounded-lg mr-2 focus:outline-none focus:border-blue-500" autocomplete="off" autofocus/>
            <button id="submit" class="bg-blue-500 text-white font-semibold px-4 py-2 rounded-lg">Send</button>
        </form>
    </div>
    <script>
        const messages = document.getElementById('messages');
        const form = document.getElementById('form');
        const input = document.getElementById('input');
        const submitButton = document.getElementById('submit');

        const ws = new WebSocket('ws://localhost:{PORT}/ws');

        ws.onmessage = (event) => {{
            const item = document.createElement('div');
            item.textContent = event.data;
            messages.appendChild(item);
            messages.scrollTo(0, messages.scrollHeight);
            input.disabled = false;
            submitButton.classList.remove('animate-ping');
        }};

        form.onsubmit = async (event) => {{
            event.preventDefault();
            input.disabled = true;
            submitButton.classList.add('animate-ping');
            ws.send(input.value);
            input.value = '';
            await new Promise(resolve => setTimeout(resolve, 2000));
        }};
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(content=html_template)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await asyncio.sleep(2)
        await websocket.send_text(f"Echo: {data}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8679)