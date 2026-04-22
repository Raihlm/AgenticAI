const API_BASE = '/api';

export const api = {
  async chat(message, sessionId = null) {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Failed to send message');
    }

    return response.json();
  },

  async getTools() {
    const response = await fetch(`${API_BASE}/tools`);
    if (!response.ok) {
      throw new Error('Failed to fetch tools');
    }
    return response.json();
  },

  async getModels() {
    const response = await fetch(`${API_BASE}/models`);
    if (!response.ok) {
      throw new Error('Failed to fetch models');
    }
    return response.json();
  },

  async getMemory() {
    const response = await fetch(`${API_BASE}/memory`);
    if (!response.ok) {
      throw new Error('Failed to fetch memory');
    }
    return response.json();
  },

  async clearMemory() {
    const response = await fetch(`${API_BASE}/memory/clear`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to clear memory');
    }
    return response.json();
  },

  async healthCheck() {
    const response = await fetch(`${API_BASE}/`);
    if (!response.ok) {
      throw new Error('API not available');
    }
    return response.json();
  },
};
