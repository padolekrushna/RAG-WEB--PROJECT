
import React, { useState, useRef, useEffect } from 'react';
import SearchResults from './SearchResults';

const ChatInterface = ({ messages, onQuery, loading, disabled }) => {
  const [query, setQuery] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !disabled && !loading) {
      onQuery(query.trim());
      setQuery('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="no-messages">
            <div className="welcome-message">
              <h3>Welcome to AI Document Q&A</h3>
              <p>Upload and process your documents, then start asking questions!</p>
              <div className="sample-questions">
                <p><strong>Try asking questions like:</strong></p>
                <ul>
                  <li>"What are the main topics covered in the documents?"</li>
                  <li>"Summarize the key findings"</li>
                  <li>"What does it say about [specific topic]?"</li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                <div className="message-header">
                  <span className="message-sender">
                    {message.role === 'user' ? '👤 You' : '🤖 AI Assistant'}
                  </span>
                  <span className="message-time">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="message-text">
                  {message.content}
                </div>
                {message.sources && message.sources.length > 0 && (
                  <SearchResults sources={message.sources} confidence={message.confidence} />
                )}
              </div>
            </div>
          ))
        )}
        
        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="message-header">
                <span className="message-sender">🤖 AI Assistant</span>
              </div>
              <div className="typing-indicator">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span>Thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="query-form">
        <div className="input-container">
          <textarea
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={disabled ? "Please process documents first..." : "Ask a question about your documents..."}
            disabled={disabled || loading}
            rows="1"
            className="query-input"
          />
          <button 
            type="submit" 
            disabled={disabled || loading || !query.trim()}
            className="send-button"
          >
            {loading ? '⏳' : '📤'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;