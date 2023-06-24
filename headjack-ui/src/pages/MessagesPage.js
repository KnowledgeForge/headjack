import { useState } from "react";
import { TypeAnimation } from "react-type-animation";
import { Player } from "@lottiefiles/react-lottie-player";
import animatedYellowRobot from "../lottie/yellowRobot.json";
import animatedPurpleRobot from "../lottie/purpleRobot.json";

export default function MessagesPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [participantList, setParticipantList] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [documentCount, setDocumentCount] = useState("");
  fetch(`${process.env.REACT_APP_HEADJACK_SERVER}/count?collection=messages`)
    .then((response) => response.json())
    .then((data) => {
      setDocumentCount(data.count);
    })
    .catch((err) => {
      console.log(err);
    });
  const handleSubmit = (e) => {
    setIsLoading(true);
    setParticipantList([])
    setAnswer("");
    e.preventDefault();
    fetch(
      `${process.env.REACT_APP_HEADJACK_SERVER}/messages/${encodeURIComponent(
        question
      )}`,
      {
        method: "POST",
      }
    )
      .then((response) => response.json())
      .then((data) => {
        setAnswer(data.utterance);
        setParticipantList(data.metadata.participants)
        setIsLoading(false);
      })
      .catch((err) => {
        console.log(err.message);
        setIsLoading(false);
      });
  };
  return (
    <div className="container content-start mx-auto mt-12">
      <div className="grid grid-cols-1 gap-6 mb-6 lg:grid-cols-3">
        <div className="w-full px-4 py-5 bg-white rounded-lg shadow">
          <div className="text-sm font-medium text-gray-500 truncate">
            Conversations
          </div>
          <div className="mt-1 text-3xl font-semibold text-gray-900">
            {documentCount ? documentCount : "..."}
          </div>
        </div>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="mb-3 pt-0 pr-20">
          <input
            type="text"
            required
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Which company projects are people most excited about?"
            className="px-3 py-3 placeholder-slate-300 text-slate-600 relative bg-white bg-white rounded text-sm border-0 shadow outline-none focus:outline-none focus:ring w-full"
          />
          <div className="pt-5">
            {isLoading ? (
              <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold h-10 w-20 rounded">
                <svg
                  className="animate-spin h-8 w-20 text-white"
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
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              </button>
            ) : (
              <button className="bg-blue-500 hover:bg-blue-700 text-white h-10 w-20 rounded">
                Ask
              </button>
            )}
          </div>
        </div>
      </form>
      {participantList ? (
        <>
        {participantList.map(p => (
          <div id="toast-simple" class="flex items-center w-full max-w-xs p-4 space-x-4 text-gray-500 bg-white divide-x divide-gray-200 rounded-lg shadow dark:text-gray-400 dark:divide-gray-700 space-x dark:bg-gray-800" role="alert">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"></path></svg>
              <div class="pl-4 text-sm font-normal">{p}</div>
          </div>
        ))}
        </>
      ): <></>}
      {answer ? (
        <>
        <div className="w-0">
        <Player
          src={isLoading ? animatedPurpleRobot : animatedYellowRobot}
          style={{ height: "60px", width: "80px" }}
          autoplay
          loop
        />
      </div>
        <blockquote className="p-4 my-4 border-l-4 border-gray-300 bg-gray-50">
          <p className="text-l italic font-medium leading-relaxed text-gray-900">
            <TypeAnimation
              sequence={[answer]}
              speed={90}
              cursor={false}
              repeat={0}
            />
          </p>
        </blockquote>
        </>
      ) : (
        <div className="w-0">
          <Player
            src={isLoading ? animatedPurpleRobot : animatedYellowRobot}
            style={{ height: "60px", width: "80px" }}
            speed={isLoading ? 2 : 1}
            autoplay
            loop
          />
        </div>
      )}
    </div>
  );
}
