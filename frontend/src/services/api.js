
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





