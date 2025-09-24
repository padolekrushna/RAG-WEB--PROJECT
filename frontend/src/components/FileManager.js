
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
