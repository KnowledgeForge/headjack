import { useState } from "react";

export default function MessagesPage() {
  const [question, setQuestion] = useState("");
  const handleSubmit = (e) => {
    e.preventDefault();
    fetch("http://localhost:8679/messages/", {method: "POST"})
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
      })
      .catch((err) => {
        console.log(err.message);
      });
  }
  return (
    <div className="container mx-auto mt-12">
      <div className="grid grid-cols-1 gap-6 mb-6 lg:grid-cols-3">
        <div className="w-full px-4 py-5 bg-white rounded-lg shadow">
          <div className="text-sm font-medium text-gray-500 truncate">
            Message Threads
          </div>
          <div className="mt-1 text-3xl font-semibold text-gray-900">
            485,252
          </div>
        </div>
      </div>
      <form onSubmit={handleSubmit}>
      <div className="mb-3 pt-0 pl-5 pr-20">
            <input
              type="text"
              required
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What are people saying about our latest earnings report?"
              className="px-3 py-3 placeholder-slate-300 text-slate-600 relative bg-white bg-white rounded text-sm border-0 shadow outline-none focus:outline-none focus:ring w-full"
            />
          </div>
          <button>Ask</button>
          </form>
    </div>
  );
}
