// frontend/src/services/api.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  async uploadDocuments(files) {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return await response.json();
  }

  async processDocuments(fileIds, apiKey) {
    const response = await fetch(`${API_BASE_URL}/documents/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_ids: fileIds,
        api_key: apiKey,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Processing failed');
    }

    return await response.json();
  }

  async queryDocuments(query, k = 5) {
    const response = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        k,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Query failed');
    }

    return await response.json();
  }

  async getSystemStats() {
    const response = await fetch(`${API_BASE_URL}/documents/stats`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get stats');
    }

    return await response.json();
  }

  async clearDocuments() {
    const response = await fetch(`${API_BASE_URL}/documents/clear`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Clear failed');
    }

    return await response.json();
  }

  async getSimilarQuestions(query) {
    const response = await fetch(`${API_BASE_URL}/documents/similar-questions/${encodeURIComponent(query)}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get similar questions');
    }

    return await response.json();
  }
}

export const apiService = new ApiService();

// frontend/src/components/DocumentUpload.js
import React, { useCallback, useState } from 'react';

const DocumentUpload = ({ onUpload, loading }) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    const validFiles = files.filter(file => {
      const validTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      return validTypes.includes(file.type);
    });

    if (validFiles.length > 0) {
      onUpload(validFiles);
    }
  }, [onUpload]);

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      onUpload(files);
    }
  };

  return (
    <div className="document-upload">
      <div 
        className={`upload-dropzone ${dragActive ? 'drag-active' : ''} ${loading ? 'loading' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {loading ? (
          <div className="upload-loading">
            <div className="spinner"></div>
            <p>Uploading files...</p>
          </div>
        ) : (
          <>
            <div className="upload-icon">📄</div>
            <p><strong>Drop files here</strong></p>
            <p>or</p>
            <label htmlFor="file-input" className="file-input-label">
              Choose Files
            </label>
            <input
              id="file-input"
              type="file"
              multiple
              accept=".pdf,.txt,.docx"
              onChange={handleFileInput}
              className="file-input"
            />
            <p className="file-types">Supports: PDF, TXT, DOCX</p>
          </>
        )}
      </div>
    </div>
  );
};

export default DocumentUpload;

// frontend/src/components/ChatInterface.js
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

// frontend/src/components/FileManager.js
import React from 'react';

const FileManager = ({ files }) => {
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (contentType) => {
    if (contentType === 'application/pdf') return '📄';
    if (contentType === 'text/plain') return '📝';
    if (contentType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') return '📘';
    return '📋';
  };

  return (
    <div className="file-manager">
      {files.map((file, index) => (
        <div key={file.id || index} className="file-item">
          <div className="file-info">
            <span className="file-icon">{getFileIcon(file.content_type)}</span>
            <div className="file-details">
              <div className="file-name" title={file.filename}>
                {file.filename}
              </div>
              <div className="file-meta">
                <span className="file-size">{formatFileSize(file.size)}</span>
                <span className="file-type">{file.content_type?.split('/').pop()?.toUpperCase()}</span>
              </div>
            </div>
          </div>
          <div className="file-status">
            ✅
          </div>
        </div>
      ))}
    </div>
  );
};

export default FileManager;

// frontend/src/components/SearchResults.js
import React, { useState } from 'react';

const SearchResults = ({ sources, confidence }) => {
  const [expanded, setExpanded] = useState(false);

  const getConfidenceColor = (confidence) => {
    if (confidence > 0.8) return '#28a745';
    if (confidence > 0.6) return '#ffc107';
    return '#dc3545';
  };

  const getConfidenceText = (confidence) => {
    if (confidence > 0.8) return 'High';
    if (confidence > 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div className="search-results">
      <div className="results-header">
        <div className="confidence-indicator">
          <span className="confidence-label">Confidence:</span>
          <span 
            className="confidence-value" 
            style={{ color: getConfidenceColor(confidence) }}
          >
            {getConfidenceText(confidence)} ({(confidence * 100).toFixed(1)}%)
          </span>
        </div>
        <button 
          className="toggle-sources"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? '🔼 Hide Sources' : '🔽 Show Sources'} ({sources.length})
        </button>
      </div>
      
      {expanded && (
        <div className="sources-list">
          {sources.map((source, index) => (
            <div key={index} className="source-item">
              <div className="source-header">
                <span className="source-number">#{source.chunk_id}</span>
                {source.source_name && (
                  <span className="source-name">{source.source_name}</span>
                )}
                <span className="similarity-score">
                  Score: {(source.similarity_score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="source-preview">
                {source.preview}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchResults;
