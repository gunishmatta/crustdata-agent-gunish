import React, { useState } from "react";
import axios from "axios";
import "./Chat.css"; // Custom CSS file for styling

const Chat = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [source, setSource] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!query.trim()) {
      alert("Please enter a question before sending.");
      return;
    }

    setIsLoading(true);
    setResponse("");
    setSource("");
    try {
      const result = await axios.post("http://localhost:8000/agent/", { query });
      setResponse(result.data.response || "No response available.");
      setSource(result.data.source || "Unknown source");
    } catch (error) {
      setResponse("An error occurred while processing your request.");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>Crustdata Agent</h1>
      </header>
      <main className="chat-main">
        <textarea
          rows="5"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about Crustdata's API..."
          className="chat-textarea"
        />
        <button onClick={handleSend} className="chat-button" disabled={isLoading}>
          {isLoading ? "Sending..." : "Send"}
        </button>
        {response && (
          <div className="chat-response">
            <h2>Response</h2>
            <p className="chat-response-text">{response}</p>
            <p className="chat-response-source">Source: {source}</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default Chat;
