

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
