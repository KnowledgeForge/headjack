import React, { useState, useCallback, useEffect } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

const ChatPage = () => {
  const [socketUrl] = useState('ws://localhost:8679/chat/');
  const [messageHistory, setMessageHistory] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [sendDisabled, setSendDisabled] = useState(false);

  const { sendMessage, lastMessage, readyState } = useWebSocket(socketUrl);

  const addToMessageHistory = (message) => {
    setMessageHistory((prev) => [...prev, message]);
  };

  useEffect(() => {
    if (lastMessage !== null) {
      const message = JSON.parse(lastMessage.data);
      addToMessageHistory(message);
      setSendDisabled(false);
    }
  }, [lastMessage]);

  const handleSubmit = useCallback(
    (e) => {
      e.preventDefault();
      const message = { utterance: inputValue.trim(), isUser: true };
      if (message.utterance !== '') {
        sendMessage(JSON.stringify(message));
        addToMessageHistory(message);
        setInputValue('');
        setSendDisabled(true);
      }
    },
    [inputValue, sendMessage]
  );

  const handleInputChange = useCallback((e) => {
    setInputValue(e.target.value);
  }, []);

  const connectionStatus = {
    [ReadyState.CONNECTING]: 'Connecting',
    [ReadyState.OPEN]: 'Open',
    [ReadyState.CLOSING]: 'Closing',
    [ReadyState.CLOSED]: 'Closed',
    [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
  }[readyState];

  return (
    <div className="h-screen flex flex-col">
      <div className="flex-grow p-4 overflow-y-auto">
        <ul className="space-y-4">
          {messageHistory.map((message, idx) => (
            <li
              key={idx}
              className={`flex ${
                message.isUser ? 'justify-end' : ''
              } items-end`}
            >
              <div
                className={`${
                  message.isUser ? 'ml-4' : 'mr-4'
                } max-w-xs bg-gray-200 rounded-lg p-2`}
              >
                <p className="text-gray-800">{JSON.stringify(message.utterance)}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
      <form onSubmit={handleSubmit} className="p-4 bg-gray-300">
        <div className="flex items-center">
          <input
            type="text"
            name="message"
            value={inputValue}
            onChange={handleInputChange}
            className="flex-grow border rounded px-2 py-1 mr-2"
            disabled={readyState !== ReadyState.OPEN || sendDisabled}
          />
          <button
            type="submit"
            className={`${
              readyState === ReadyState.OPEN
                ? 'bg-blue-500 hover:bg-blue-700 text-white'
                : 'bg-red-500 text-white'
            } font-bold py-2 px-4 rounded`}
            disabled={readyState !== ReadyState.OPEN || sendDisabled}
          >
            Send
          </button>
        </div>
        <span className="text-gray-700 mt-2">
          {`The WebSocket is currently ${connectionStatus}`}
        </span>
      </form>
    </div>
  );
};

const App = () => {
  return (
    <div className="w-screen h-screen flex justify-center items-center">
      <ChatPage />
    </div>
  );
};

export default App;