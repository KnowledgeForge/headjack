import React, { useState } from "react";

export default function DataTable({ metadatas, documents }) {
  console.log("Metadatas", metadatas);
  console.log("Documents", documents);
  const [showSql, setShowSql] = useState([]);
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
                <a
                  href={`${process.env.REACT_APP_DJ_URL}/nodes/${metadata.name}`}
                  target="_blank"
                >
                  {metadata.name}
                </a>
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
}
