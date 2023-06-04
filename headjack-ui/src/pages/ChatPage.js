import React, { useState, useCallback } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [accessToken, setAccessToken] = useState('');
  const [isChatting, setIsChatting] = useState(false);

  const handleMessage = useCallback(
    (message) => {
      setMessages((prevMessages) => [...prevMessages, message]);
    },
    [setMessages]
  );

  const { sendMessage, lastMessage, readyState, getWebSocket } = useWebSocket(`ws://localhost:8679/chat/${accessToken}`, {
    onOpen: () => console.log('WebSocket connected'),
    onClose: () => console.log(`WebSocket disconnected: ${accessToken}`),
    onError: (event) => console.error('WebSocket error:', event),
    shouldReconnect: (closeEvent) => true,
  });

  if (lastMessage) {
    handleMessage(JSON.parse(lastMessage.data));
  }

  const sendMessageHandler = useCallback(
    (e) => {
      e.preventDefault();
      if (inputMessage.trim() !== '') {
        console.log(inputMessage)
        sendMessage(JSON.stringify({ utterance: inputMessage }));
        setInputMessage('');
      }
    },
    [inputMessage, sendMessage]
  );

  const startChatHandler = useCallback(
    () => {
      fetch('http://localhost:8679/chat/session')
        .then((response) => response.json())
        .then((data) => {
          setAccessToken(data.access_token);
          setIsChatting(true);
        })
        .catch((err) => {
          console.log(err.message);
        });
    },
    [setAccessToken, setIsChatting]
  );

  const restartChatHandler = useCallback(
    () => {
      fetch('http://localhost:8679/chat/session')
        .then((response) => response.json())
        .then((data) => {
            console.log("TOKEN")
            console.log(data)
          setAccessToken(data.access_token);
          setIsChatting(true);
          getWebSocket().close();
        })
        .catch((err) => {
          console.log(err.message);
        });
    },
    [setAccessToken, setIsChatting, getWebSocket]
  );

  const connectionStatus = {
    [ReadyState.CONNECTING]: 'Connecting',
    [ReadyState.OPEN]: 'Open',
    [ReadyState.CLOSING]: 'Closing',
    [ReadyState.CLOSED]: 'Closed',
    [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
  }[readyState];

  return (
    <div className="container mx-auto mt-12">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">Chat</h2>
        {isChatting ? (
          <>

            <div className="h-64 mb-4 overflow-y-auto">
              {messages.map((message, index) => (
                <div key={index} className={`mb-4 ${message.from_user ? 'text-right' : 'text-left'}`}>
                  <span className={`inline-block rounded-lg px-4 py-2 ${message.from_user ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'}`}>
                    {message.content}
                  </span>
                </div>
              ))}
            </div>
            <form onSubmit={sendMessageHandler}>
              <div className="flex space-x-4">
              <button onClick={restartChatHandler} className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded mr-2">
                Clear
              </button>
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Type your message"
                  className="flex-grow px-3 py-3 bg-white rounded text-sm border border-gray-300 focus:outline-none focus:ring focus:border-blue-300"
                />
                <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                  Send
                </button>
              </div>
              <div className="flex mb-4">
              <span>The WebSocket is currently {connectionStatus}</span>
            </div>
            </form>
            {lastMessage ? <span>Last message: {lastMessage.data}</span> : null}
          </>
        ) : (
          <button onClick={startChatHandler} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Start Chat
          </button>
        )}
      </div>
    </div>
  );
}
