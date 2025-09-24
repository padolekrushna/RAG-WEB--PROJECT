// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import DocumentUpload from './components/DocumentUpload';
import ChatInterface from './components/ChatInterface';
import FileManager from './components/FileManager';
import SearchResults from './components/SearchResults';
import { apiService } from './services/api';
import './styles/main.css';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [processedFiles, setProcessedFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isProcessed, setIsProcessed] = useState(false);
  const [systemStats, setSystemStats] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Load API key from localStorage
  useEffect(() => {
    const savedApiKey = localStorage.getItem('gemini_api_key');
    if (savedApiKey) {
      setApiKey(savedApiKey);
    }
  }, []);

  // Save API key to localStorage
  useEffect(() => {
    if (apiKey) {
      localStorage.setItem('gemini_api_key', apiKey);
    }
  }, [apiKey]);

  // Load system stats
  useEffect(() => {
    loadSystemStats();
  }, [isProcessed]);

  const loadSystemStats = async () => {
    try {
      const stats = await apiService.getSystemStats();
      setSystemStats(stats);
    } catch (error) {
      console.error('Failed to load system stats:', error);
    }
  };

  const handleFileUpload = async (files) => {
    try {
      setLoading(true);
      const uploadResults = await apiService.uploadDocuments(files);
      setUploadedFiles(prev => [...prev, ...uploadResults]);
      setError('');
    } catch (error) {
      setError(`Upload failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleProcessDocuments = async () => {
    if (!apiKey.trim()) {
      setError('Please provide your Google Gemini API key');
      return;
    }

    if (uploadedFiles.length === 0) {
      setError('Please upload documents first');
      return;
    }

    try {
      setIsProcessing(true);
      setError('');

      const fileIds = uploadedFiles.map(file => file.id);
      const result = await apiService.processDocuments(fileIds, apiKey);
      
      setProcessedFiles(result.processed_files);
      setIsProcessed(true);
      setError('');
    } catch (error) {
      setError(`Processing failed: ${error.message}`);
      setIsProcessed(false);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleQuery = async (query) => {
    if (!isProcessed) {
      setError('Please process documents first');
      return;
    }

    try {
      setLoading(true);
      
      // Add user message
      const userMessage = { role: 'user', content: query, timestamp: new Date().toISOString() };
      setMessages(prev => [...prev, userMessage]);

      const response = await apiService.queryDocuments(query);
      
      // Add assistant message
      const assistantMessage = { 
        role: 'assistant', 
        content: response.response,
        sources: response.sources,
        confidence: response.confidence,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      setError('');
    } catch (error) {
      setError(`Query failed: ${error.message}`);
      const errorMessage = { 
        role: 'assistant', 
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const handleClearDocuments = async () => {
    try {
      await apiService.clearDocuments();
      setUploadedFiles([]);
      setProcessedFiles([]);
      setIsProcessed(false);
      setMessages([]);
      setSystemStats(null);
      setError('');
    } catch (error) {
      setError(`Clear failed: ${error.message}`);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="main-header">
        <div className="header-content">
          <h1>AI Document Q&A System</h1>
          <p>Upload documents and ask questions using advanced RAG with FAISS and Gemini AI</p>
        </div>
      </header>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          {error}
          <button className="error-close" onClick={() => setError('')}>×</button>
        </div>
      )}

      <div className="app-container">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="sidebar-section">
            <h3>⚙️ Configuration</h3>
            <div className="api-key-section">
              <label htmlFor="api-key">🔑 Google Gemini API Key</label>
              <input
                id="api-key"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your API key"
                className="api-key-input"
              />
            </div>
          </div>

          <div className="sidebar-section">
            <h3>📄 Document Management</h3>
            <DocumentUpload onUpload={handleFileUpload} loading={loading} />
            
            {uploadedFiles.length > 0 && (
              <div className="uploaded-files">
                <h4>Uploaded Files ({uploadedFiles.length})</h4>
                <FileManager files={uploadedFiles} />
              </div>
            )}

            <button
              className="process-btn"
              onClick={handleProcessDocuments}
              disabled={isProcessing || uploadedFiles.length === 0 || !apiKey}
            >
              {isProcessing ? '🔄 Processing...' : '🚀 Process Documents'}
            </button>
          </div>

          <div className="sidebar-section">
            <h3>📊 System Status</h3>
            <div className={`status-indicator ${isProcessed ? 'ready' : 'not-ready'}`}>
              <span className="status-icon">{isProcessed ? '✅' : '⏳'}</span>
              <span className="status-text">
                {isProcessed ? 'System Ready' : 'System Not Ready'}
              </span>
            </div>

            {systemStats && (
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">📄 Document Chunks</span>
                  <span className="stat-value">{systemStats.total_chunks}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">💬 Chat Messages</span>
                  <span className="stat-value">{messages.length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">🧠 Memory Usage</span>
                  <span className="stat-value">{systemStats.memory_usage}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">📏 Vector Dim</span>
                  <span className="stat-value">{systemStats.embedding_dimension}</span>
                </div>
              </div>
            )}

            <div className="action-buttons">
              <button
                className="clear-btn"
                onClick={handleClearChat}
                disabled={messages.length === 0}
              >
                🗑️ Clear Chat
              </button>
              <button
                className="clear-btn danger"
                onClick={handleClearDocuments}
                disabled={uploadedFiles.length === 0}
              >
                🗑️ Clear All
              </button>
            </div>
          </div>

          <div className="sidebar-section">
            <h3>ℹ️ How to Use</h3>
            <ol className="instructions">
              <li><strong>Add API Key:</strong> Enter your Google Gemini API key</li>
              <li><strong>Upload Documents:</strong> Add PDF, TXT, or DOCX files</li>
              <li><strong>Process:</strong> Click 'Process Documents' button</li>
              <li><strong>Chat:</strong> Ask questions about your documents</li>
            </ol>
          </div>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          <div className="chat-section">
            <h2>💬 Chat with Your Documents</h2>
            <ChatInterface
              messages={messages}
              onQuery={handleQuery}
              loading={loading}
              disabled={!isProcessed}
            />
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
