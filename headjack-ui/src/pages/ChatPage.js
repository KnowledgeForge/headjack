import React, { useState, useCallback, useEffect } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { TypeAnimation } from "react-type-animation";
import { Player } from "@lottiefiles/react-lottie-player";
import animatedPurpleRobot from "../lottie/purpleRobot.json";
import Plot from "react-plotly.js";

const MessageContent = ({ message }) => {
  const [showQuery, setShowQuery] = useState(false);
  const [showSql, setShowSql] = useState([]);

  if (
    message.source === "metric_calculate_agent" &&
    message.marker.startsWith("Obs") &&
    message.utterance.results.length > 0
  ) {
    const { results, submitted_query } = message.utterance;
    const columns = results[0].columns;
    const rows = results[0].rows;
    return (
      <div className="max-h-96 overflow-y-auto">
        <div className="flex justify-end mb-2">
          <button
            className="bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded mr-2"
            onClick={() => setShowQuery(!showQuery)}
          >
            {showQuery ? "Hide Query" : "Show Query"}
          </button>
        </div>
        {showQuery && (
          <pre className="bg-gray-100 p-2 mb-2">
            <code>{submitted_query}</code>
          </pre>
        )}
        <table className="w-full border-collapse border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column, index) => (
                <th key={index} className="py-2 px-4 border border-gray-300">
                  {column.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="bg-white">
                {row.map((cell, cellIndex) => (
                  <td
                    key={cellIndex}
                    className="py-2 px-4 border border-gray-300"
                  >
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  } else if (
    message.source === "metric_search_agent" &&
    message.marker.startsWith("Obs") &&
    message.utterance.metadatas.length > 0
  ) {
    const { metadatas, documents } = message.utterance;

    const handleShowSql = (index) => {
      setShowSql((prevShowSql) => {
        const newShowSql = [...prevShowSql];
        newShowSql[index] = !newShowSql[index];
        return newShowSql;
      });
    };

    return (
      <div className="max-h-96 overflow-y-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="py-2 px-4 border border-gray-300">Name</th>
              <th className="py-2 px-4 border border-gray-300">
                Description
              </th>
              <th className="py-2 px-4 border border-gray-300">SQL</th>
            </tr>
          </thead>
          <tbody>
            {metadatas[0].map((metadata, index) => (
              <tr key={index} className="bg-white">
                <td className="py-2 px-4 border border-gray-300">
                  {metadata.name}
                </td>
                <td className="py-2 px-4 border border-gray-300">
                  {documents[0][index]}
                </td>
                <td className="py-2 px-4 border border-gray-300">
                  <div className="flex items-center">
                    <button
                      className="bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded mr-2"
                      onClick={() => handleShowSql(index)}
                    >
                      {showSql[index] ? "Hide SQL" : "Show SQL"}
                    </button>
                    {showSql[index] && (
                      <pre className="bg-gray-100 p-2">
                        <code>{metadata.query}</code>
                      </pre>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  } else if (
    message.source === "plot_data" &&
    message.marker.startsWith("Obs")
  ) {
    const plotData = message.utterance;
    return <Plot data={plotData.data} layout={plotData.layout} />;
  } else {
    return (
      <p>
        <TypeAnimation
          sequence={[JSON.stringify(message.utterance)]}
          speed={90}
          cursor={false}
          repeat={0}
        />
      </p>
    );
  }
};

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
      console.log(messageHistory);
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
          <span className="bg-yellow-100 text-yellow-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-yellow-900 dark:text-yellow-300">
            {connectionStatus}
          </span>
        );
      case "Open":
        return (
          <span className="bg-green-100 text-green-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-green-900 dark:text-green-300">
            {connectionStatus}
          </span>
        );
      case "Closing": return null;
      case "Closed":
        return (
          <span className="bg-red-100 text-red-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-red-900 dark:text-red-300">
            {connectionStatus}
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="container flex flex-col h-screen w-full">
      <div className="flex items-center justify-center bg-gray-300 h-24">
        <h1 className="text-3xl font-bold">HeadJack Chat</h1>
        <Player
          autoplay
          loop
          src={animatedPurpleRobot}
          style={{ height: "80px", width: "80px" }}
        />
      </div>
      <div className="flex flex-col flex-grow bg-gray-100 w-full">
        <div className="py-6 px-4 sm:px-6 lg:py-12 lg:px-8 h-full flex flex-col w-full">
  <div className="flex-grow overflow-y-auto">
    {messageHistory.map((message, index) => (
      <div
        key={index}
        className={`flex ${
          message.isUser ? "justify-end" : "justify-start"
        }`}
      >
        <div
          className={`${
            message.isUser ? "bg-blue-400" : "bg-white"
          } shadow-lg rounded-lg p-4 max-w-4xl mb-4`}
          style={{textAlign: message.isUser ? 'right' : 'left'}}
        >
          <MessageContent message={message} />
        </div>
      </div>
    ))}
  </div>
  <form onSubmit={handleSubmit} className="mt-4">
    <div className="flex">
      <input
        type="text"
        value={inputValue}
        onChange={handleInputChange}
        className="block w-full rounded-md border-gray-300 shadow-sm px-4 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        placeholder="Type your message here..."
        disabled={sendDisabled}
      />
      <button
        type="submit"
        className={`ml-2 px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
          sendDisabled ? "opacity-50 cursor-not-allowed" : ""
        }`}
        disabled={sendDisabled}
      >
        {isLoading ? (
          <svg
            className="animate-spin h-5 w-5 text-white"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm12 0a8 8 0 100-16 8 8 0 000 16z"
            ></path>
          </svg>
        ) : (
          <span>Send</span>
        )}
      </button>
    </div>
  </form>
  <div className="bg-gray-900 text-white py-2 px-4 fixed bottom-0 left-0 w-full">
          {renderWSBadge(connectionStatus)}
          WebSocket Connection Status
        </div>
      </div>
</div>

        </div>

    );
  };
  
  export default ChatPage;