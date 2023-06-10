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
        setAnswer(data.utterance.summary);
        setParticipantList(data.utterance.participants)
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
              <svg aria-hidden="true" class="w-5 h-5 text-blue-600 dark:text-blue-500" focusable="false" data-prefix="fas" data-icon="paper-plane" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M511.6 36.86l-64 415.1c-1.5 9.734-7.375 18.22-15.97 23.05c-4.844 2.719-10.27 4.097-15.68 4.097c-4.188 0-8.319-.8154-12.29-2.472l-122.6-51.1l-50.86 76.29C226.3 508.5 219.8 512 212.8 512C201.3 512 192 502.7 192 491.2v-96.18c0-7.115 2.372-14.03 6.742-19.64L416 96l-293.7 264.3L19.69 317.5C8.438 312.8 .8125 302.2 .0625 289.1s5.469-23.72 16.06-29.77l448-255.1c10.69-6.109 23.88-5.547 34 1.406S513.5 24.72 511.6 36.86z"></path></svg>
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
