import React, { useState, useCallback, useEffect } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { TypeAnimation } from "react-type-animation";
import { Player } from "@lottiefiles/react-lottie-player";
import animatedPurpleRobot from "../lottie/purpleRobot.json";

const ChatPage = () => {
  const [socketUrl] = useState("ws://localhost:8679/chat/");
  const [messageHistory, setMessageHistory] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [sendDisabled, setSendDisabled] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { sendMessage, lastMessage, readyState } = useWebSocket(socketUrl);

  const addToMessageHistory = (message) => {
    setMessageHistory((prev) => [...prev, message]);
  };

  useEffect(() => {
    if (lastMessage !== null) {
      const message = JSON.parse(lastMessage.data);
      addToMessageHistory(message);
      setSendDisabled(false);
      setIsLoading(false);
    }
  }, [lastMessage]);

  const handleSubmit = useCallback(
    (e) => {
      e.preventDefault();
      const message = { utterance: inputValue.trim(), isUser: true };
      if (message.utterance !== "") {
        setIsLoading(true);
        sendMessage(JSON.stringify(message));
        addToMessageHistory(message);
        setInputValue("");
        setSendDisabled(true);
      }
    },
    [inputValue, sendMessage]
  );

  const handleInputChange = useCallback((e) => {
    setInputValue(e.target.value);
  }, []);

  const connectionStatus = {
    [ReadyState.CONNECTING]: "Connecting",
    [ReadyState.OPEN]: "Open",
    [ReadyState.CLOSING]: "Closing",
    [ReadyState.CLOSED]: "Closed",
    [ReadyState.UNINSTANTIATED]: "Uninstantiated",
  }[readyState];

  const renderWSBadge = (connectionStatus) => {
    switch (connectionStatus) {
      case "Connecting":
        return (
          <span class="bg-yellow-100 text-yellow-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-yellow-900 dark:text-yellow-300">
            {connectionStatus}
          </span>
        );
      case "Open":
        return (
          <span class="bg-green-100 text-green-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-green-900 dark:text-green-300">
            {connectionStatus}
          </span>
        );
      case "Closing":
        return (
          <span class="bg-red-100 text-red-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-red-900 dark:text-red-300">
            {connectionStatus}
          </span>
        );
      case "Closed":
        return (
          <span class="bg-red-100 text-red-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-red-900 dark:text-red-300">
            {connectionStatus}
          </span>
        );
      case "Uninstantiated":
        return (
          <span class="bg-gray-100 text-gray-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-gray-700 dark:text-gray-300">
            {connectionStatus}
          </span>
        );
    }
  };

  return (
    <div className="container mx-auto mt-12">
      <div className="bg-white rounded-lg shadow p-6">
        <ul className="space-y-4 ">
          {messageHistory.map((message, idx) => (
            <li
              key={idx}
              className={`flex ${
                message.isUser ? "justify-end ps-16" : "pe-16"
              } items-end`}
            >
              <div
                className={`${
                  message.isUser ? "bg-gray-200" : "bg-blue-400"
                } px-4 py-4 rounded-md overflow-hidden flex items-start`}
              >
                <p className="text-gray-800">
                  {message.isUser ? (
                    message.utterance
                  ) : (
                    <TypeAnimation
                      sequence={[message.utterance]}
                      speed={90}
                      cursor={false}
                      repeat={0}
                    />
                  )}
                </p>
              </div>
            </li>
          ))}
          {isLoading ? (
            <Player
              src={animatedPurpleRobot}
              style={{ height: "60px", width: "80px" }}
              speed={2}
              autoplay
              loop
            />
          ) : (
            <></>
          )}
        </ul>
      </div>
      <form onSubmit={handleSubmit} className="p-3 bg-gray-100 rounded-lg">
        <div className="flex items-center">
          <input
            type="text"
            name="message"
            value={inputValue}
            onChange={handleInputChange}
            autoComplete="off"
            className="flex-grow border rounded px-2 py-1 mr-2"
            disabled={readyState !== ReadyState.OPEN || sendDisabled}
          />
          <button
            type="submit"
            className={`${
              readyState === ReadyState.OPEN
                ? "bg-blue-500 hover:bg-blue-700 text-white"
                : "bg-red-500 text-white"
            } font-bold py-2 px-4 rounded`}
            disabled={readyState !== ReadyState.OPEN || sendDisabled}
          >
            Send
          </button>
        </div>
        <span className="text-gray-700 mt-2">
          {`Websocket Status: `}
          {renderWSBadge(connectionStatus)}
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
