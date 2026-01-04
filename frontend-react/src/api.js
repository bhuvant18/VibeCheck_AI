import axios from 'axios';

// Use relative URL in production (Docker), absolute URL in development
const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:8000' : '';

export const verifyText = async (text, apiKey) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/verify`, {
      text: text,
      api_key: apiKey
    });
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const checkHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    return null;
  }
};
