

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
