import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await axios.post(`${API_URL}/api/auth/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
};

// Documents API
export const documentsAPI = {
  upload: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  list: async () => {
    const response = await api.get('/api/documents/list');
    return response.data;
  },
  
  delete: async (filename: string) => {
    const response = await api.delete(`/api/documents/${filename}`);
    return response.data;
  },
  
  stats: async () => {
    const response = await api.get('/api/documents/stats');
    return response.data;
  },
};

// Chat API
export const chatAPI = {
  query: async (question: string, chatHistory: any[] = [], includeSources: boolean = true) => {
    const response = await api.post('/api/chat/query', {
      question,
      chat_history: chatHistory,
      include_sources: includeSources,
    });
    return response.data;
  },
  
  classifyIntent: async (question: string) => {
    const response = await api.post(`/api/chat/classify-intent?question=${encodeURIComponent(question)}`);
    return response.data;
  },
  
  getSuggestions: async (question: string) => {
    const response = await api.post(`/api/chat/suggest?question=${encodeURIComponent(question)}`);
    return response.data;
  },
  
  health: async () => {
    const response = await api.get('/api/chat/health');
    return response.data;
  },
};

// System API
export const systemAPI = {
  health: async () => {
    const response = await axios.get(`${API_URL}/api/health`);
    return response.data;
  },
  
  info: async () => {
    const response = await axios.get(`${API_URL}/api/info`);
    return response.data;
  },
};

export default api;
