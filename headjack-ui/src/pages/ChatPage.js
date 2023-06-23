import React, { useState, useCallback, useEffect } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { TypeAnimation } from "react-type-animation";
import { Player } from "@lottiefiles/react-lottie-player";
import animatedYellowRobot from "../lottie/yellowRobot.json";
import animatedPurpleRobot from "../lottie/purpleRobot.json";
import Plot from "react-plotly.js";

const MessageContent = ({ message }) => {
  const [showQuery, setShowQuery] = useState(false);
  const [showSql, setShowSql] = useState([]);

  if (
    message.source === "metric_calculate_agent" &&
    message.marker.startsWith("Obs") &&
    message.metadata.results.length > 0
  ) {
    const { results, submitted_query } = message.metadata;
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
    const { metadatas, documents } = message.metadata;

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
              <th className="py-2 px-4 border border-gray-300">Description</th>
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
    const plotData = message.metadata;
    return <Plot data={plotData.data} layout={plotData.layout} />;
  }
};

const Pill = ({ children }) => (
  <span className="bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2">
    {children}
  </span>
);

const Message = ({ message }) => {
  const segments = message.utterance.split(/(\(agent\).*?\(\/agent\))/g);

  return (
    <div className="flex flex-wrap">
      {segments.map((segment, index) =>
        segment.startsWith("(agent)") && segment.endsWith("(/agent)") ? (
          <Pill key={index}>
            {segment.replace(/\(agent\)/g, "").replace(/\(\/agent\)/g, "")}
          </Pill>
        ) : (
          <TypeAnimation
            key={index}
            sequence={[segment]}
            speed={90}
            cursor={false}
            repeat={0}
          />
        )
      )}
    </div>
  );
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
      let reply_finished = message.utterance==null
      if (!reply_finished){addToMessageHistory(message)}
      setSendDisabled(!reply_finished);
      setIsLoading(!reply_finished);
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
      case "Closing":
        return null;
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
    <div className="flex flex-col h-screen w-full">
      <div className="flex items-center justify-center bg-gray-200 h-24">
        <h2 className="text-2xl font-bold">HeadJack Chat</h2>
        <Player
          autoplay
          loop
          src={isLoading ? animatedPurpleRobot : animatedYellowRobot}
          speed={isLoading ? 2 : 1}
          style={{ height: "50px", width: "50px" }}
        />
      </div>
      <div className="flex flex-col flex-grow bg-gray-100 w-full overflow-y-auto">
        <div className="py-6 px-4 sm:px-6 lg:py-12 lg:px-8 h-full flex flex-col w-full">
          <div className="flex-grow overflow-y-auto">
            {messageHistory.map((message, index) => {
              if (message.metadata != null) {
                return (
                  <div
                    key={index}
                    className={`flex ${
                      message.isUser ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`${
                        message.isUser ? "bg-blue-300" : "bg-white"
                      } shadow-lg rounded-lg p-4 max-w-4xl mb-4`}
                      style={{
                        textAlign: message.isUser ? "right" : "left",
                      }}
                    >
                      <p className="text-gray-000 dark:text-gray-000">
                        <Message message={message}/>
                      </p>
                      <MessageContent message={message} />
                    </div>
                  </div>
                );
              } else {
                return (
                  <div
                    key={index}
                    className={`flex ${
                      message.isUser ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`${
                        message.isUser ? "bg-blue-300" : "bg-white"
                      } shadow-lg rounded-lg p-4 max-w-4xl mb-4`}
                     style={{
                        textAlign: message.isUser ? "right" : "left",
                      }}
                    >
                      <p className="font-medium mb-2">
                        {message.isUser ? "You" : "HeadJack"}
                      </p>
                      <p className="text-gray-900 dark:text-gray-900">
                        
                        <Message message={message}/>
                      </p>
              
                    </div>
                  </div>
                );
              }
            })}
          </div>
          <form onSubmit={handleSubmit} className="mt-6 flex">
            <input
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              className="flex-grow outline-none px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-700 dark:text-white"
              placeholder="Type a message..."
            />
            <button
              type="submit"
              disabled={sendDisabled}
              className={`ml-4 px-4 py-2 rounded-md bg-blue-500 text-white font-medium
                ${sendDisabled ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              Send
            </button>
          </form>
        </div>
      </div>
      <div className="flex items-center justify-center bg-gray-200 h-16">
        <span className="text-sm">Chat connection is &nbsp;</span>{renderWSBadge(connectionStatus)}
      </div>
    </div>
  );
};

export default ChatPage;
