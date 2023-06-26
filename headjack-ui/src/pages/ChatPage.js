import React, { useState, useCallback, useEffect, useRef, useLayoutEffect} from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { Player } from "@lottiefiles/react-lottie-player";
import animatedYellowRobot from "../lottie/yellowRobot.json";
import animatedPurpleRobot from "../lottie/purpleRobot.json";
import Plot from "react-plotly.js";
import DataTable from "../components/dataTable";
const PeopleTable = ({ metadatas }) => {
  return (
    <table className="w-full border-collapse border border-gray-300 max-h-4xl">
      <thead className="bg-gray-50">
        <tr>
          <th className="py-2 px-4 border border-gray-300">First Name</th>
          <th className="py-2 px-4 border border-gray-300">Last Name</th>
          <th className="py-2 px-4 border border-gray-300">Position</th>
          <th className="py-2 px-4 border border-gray-300">Manager ID</th>
          <th className="py-2 px-4 border border-gray-300">Hire Date</th>
          <th className="py-2 px-4 border border-gray-300">Employee</th>
          <th className="py-2 px-4 border border-gray-300">Description</th>
        </tr>
      </thead>
      <tbody>
        {metadatas.map((metadata, index) => (
          <tr key={index} className="bg-white">
            <td className="py-2 px-4 border border-gray-300">{metadata.first_name}</td>
            <td className="py-2 px-4 border border-gray-300">{metadata.last_name}</td>
            <td className="py-2 px-4 border border-gray-300">{metadata.position}</td>
            <td className="py-2 px-4 border border-gray-300">{metadata.manager_id}</td>
            <td className="py-2 px-4 border border-gray-300">{metadata.hire_date}</td>
            <td className="py-2 px-4 border border-gray-300">{metadata.employee.toString()}</td>
            <td className="py-2 px-4 border border-gray-300">{metadata.description}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
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
    message.metadata.metadatas.length > 0
  ) {
    const { metadatas, documents } = message.metadata;

    const handleShowSql = (index) => {
      setShowSql((prevShowSql) => {
        const newShowSql = [...prevShowSql];
        newShowSql[index] = !newShowSql[index];
        return newShowSql;
      });
    };
    return <DataTable metadatas={metadatas} documents={documents} />;
  }else if (
    message.source === "people_search_agent" &&
    message.marker.startsWith("Ans") &&
    message.metadata.people.length > 0
  ) {
    return <PeopleTable metadatas={message.metadata.people} />;
  } else if (
    message.source === "plot_data" &&
    message.marker.startsWith("Obs")
  ) {
    const plotData = message.metadata;
    return <Plot data={plotData.data} layout={plotData.layout} />;
  }
};

const TypingAnimation = ({ text, delay, onAnimationComplete }) => {
  const [displayText, setDisplayText] = useState('');
  const [complete, setComplete] = useState(false);

  const randomDelay = () => {
    const delays = [delay, delay * 2, delay * 3, delay * 4];
    return delays[Math.floor(Math.random() * delays.length)];
  };

  useEffect(() => {
    if (!complete) {
      let currentIndex = 0;

      const intervalId = setInterval(() => {
        const randomChars = Math.floor(Math.random() * 4) + 1;
        setDisplayText(text.slice(0, currentIndex + randomChars));
        currentIndex += randomChars;

        if (currentIndex >= text.length) {
          clearInterval(intervalId);
          setComplete(true);
          onAnimationComplete();
        }
      }, randomDelay());

      return () => clearInterval(intervalId);
    }else{
      setDisplayText(text)
    }
  }, [text, delay, complete, onAnimationComplete]);

  const trimmedDisplayText = displayText.replace(/"/g, '');

  return <span>{trimmedDisplayText}</span>;
};
const TypeAnimationWithPills = ({ message }) => {
  const [allSegments, _] = useState(message.utterance.split(/(\(agent\).*?\(\/agent\))/g));
  const [currentSegmentIndex, setCurrentSegmentIndex] = useState(0);

  const increment = () => {
    let newIndex = Math.min(currentSegmentIndex + 1, allSegments.length - 1);
    // while (allSegments[newIndex].startsWith("(agent)")) {
    //   newIndex = newIndex + 1;
    // }
    setCurrentSegmentIndex(Math.min(newIndex, allSegments.length - 1));
  };

  return (
    <div className="flex flex-wrap">
      {allSegments.slice(0, currentSegmentIndex + 1).map((segment, index) => {
        return segment.startsWith("(agent)") ? (
          <span
            key={index}
            className="bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 ml-2 mr-2"
            style={{
              whiteSpace: "nowrap",
              fontSize: "14px",
              padding: "4px 8px",
            }}
          >          <TypingAnimation
          key={index}
          text={segment.replace(/\(agent\)/g, "").replace(/\(\/agent\)/g, "")}
          delay={35}
          onAnimationComplete={increment}
        />

          </span>
        ) : (
          <TypingAnimation
            key={index}
            text={segment}
            delay={35}
            onAnimationComplete={increment}
          />
        );
      })}
    </div>
  );
};
const ChatPage = () => {
  const [socketUrl] = useState("ws://localhost:8679/chat/");
  const [messageHistory, setMessageHistory] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [sendDisabled, setSendDisabled] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const chatContainerRef = useRef();
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

  useLayoutEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messageHistory]);

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
  const [toast, setToast] = useState(false);
  const submitFeedback = (message, isUpvote) => {
    setToast(true);
    setTimeout(() => {
      setToast(false);
    }, 3000);
  }
  return (
    <div className="flex flex-col h-screen w-full">
            {toast && 
        <div className="fixed bottom-0 right-0 m-4">
          <div className="bg-blue-500 text-white px-4 py-2 rounded" role="alert">
            <strong>Feedback Submitted!</strong>
          </div>
        </div>  
      }
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
          <div className="flex-grow overflow-y-auto" ref={chatContainerRef}>
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
  } shadow-lg rounded-lg p-4 max-w-4xl max-h-4xl mb-4`}
  style={{
    textAlign: message.isUser ? "right" : "left",
  }}
>
  <p className="text-gray-000 dark:text-gray-000">
    <TypeAnimationWithPills message={message}/>
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

                      <p className="text-gray-900 dark:text-gray-900">
                      {message.isUser ? message.utterance : <>                      
                      <p className="font-medium mb-2">
                        HeadJack
                      </p>
                      <TypeAnimationWithPills message={message}/></>}

                      </p>
                      {!message.isUser && 
              <div className="flex float-right">
                <button className="px-2 py-2 font-large" onClick={() => submitFeedback(message, true)}>👍</button>
                <button className="px-2 py-2 font-large" onClick={() => submitFeedback(message, false)}>👎</button>
              </div>
            }
                    </div>
                  </div>
                );
              }
            })}
          </div>
          <form onSubmit={handleSubmit} className="mt-6 flex">
            <input
              type="text"
              disabled={sendDisabled}
              value={inputValue}
              onChange={handleInputChange}
              className={`flex-grow outline-none px-4 py-2 rounded-md ${sendDisabled ? "bg-neutral-400" : "bg-gray-800"} text-white`}
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
