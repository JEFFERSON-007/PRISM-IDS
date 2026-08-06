import axios from 'axios';
import {
  Alert,
  AlertPaginationResponse,
  AgentNode,
  DashboardSummary,
  Incident,
  IncidentPaginationResponse,
  SystemHealth,
  User,
} from '../../types/types';

const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
  const scheme = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'https' : 'http';
  return `${scheme}://${host}:8000`;
};

export const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to inject JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('prism_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API calls
export const authApi = {
  login: async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await apiClient.post<{ access_token: string; token_type: string }>('/api/v1/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  getCurrentUser: async () => {
    const response = await apiClient.get<User>('/api/v1/auth/me');
    return response.data;
  },
};

// Analytics & Dashboard API calls
export const analyticsApi = {
  getSummary: async () => {
    const response = await apiClient.get<DashboardSummary>('/api/v1/dashboard/summary');
    return response.data;
  },
  getNetworkAnalytics: async (timeRange: string = '24h') => {
    const response = await apiClient.get(`/api/v1/dashboard/network?range=${timeRange}`);
    return response.data;
  },
  getSystemHealth: async () => {
    const response = await apiClient.get<SystemHealth>('/api/v1/dashboard/system');
    return response.data;
  },
};

export const dashboardApi = analyticsApi;

// Alerts API calls
export const alertsApi = {
  getAlerts: async (params?: { page?: number; limit?: number; page_size?: number; severity?: string; status?: string; protocol?: string; search?: string }) => {
    const response = await apiClient.get<AlertPaginationResponse>('/api/v1/alerts', { params });
    return response.data;
  },
  getAlertById: async (id: string) => {
    const response = await apiClient.get<Alert>(`/api/v1/alerts/${id}`);
    return response.data;
  },
  updateAlertStatus: async (id: string, status: string) => {
    const response = await apiClient.patch<Alert>(`/api/v1/alerts/${id}/status`, { status });
    return response.data;
  },
};

// Incidents API calls
export const incidentsApi = {
  getIncidents: async (params?: { page?: number; limit?: number; status?: string; severity?: string }) => {
    const response = await apiClient.get<IncidentPaginationResponse>('/api/v1/incidents', { params });
    return response.data;
  },
  getIncidentById: async (id: string) => {
    const response = await apiClient.get<Incident>(`/api/v1/incidents/${id}`);
    return response.data;
  },
  updateIncidentStatus: async (id: string, status: string) => {
    const response = await apiClient.patch<Incident>(`/api/v1/incidents/${id}`, { status });
    return response.data;
  },
  createIncident: async (data: { title: string; description: string; severity: string }) => {
    const response = await apiClient.post<Incident>('/api/v1/incidents', data);
    return response.data;
  },
  updateStatus: async (id: string, status: string) => {
    const response = await apiClient.patch<Incident>(`/api/v1/incidents/${id}`, { status });
    return response.data;
  },
  addNote: async (id: string, note: string) => {
    const response = await apiClient.post<Incident>(`/api/v1/incidents/${id}/notes`, { note });
    return response.data;
  },
};

// Agents API calls
export const agentsApi = {
  getAgents: async () => {
    const response = await apiClient.get<AgentNode[]>('/api/v1/agents');
    return response.data;
  },
  getAgentById: async (id: string) => {
    const response = await apiClient.get<AgentNode>(`/api/v1/agents/${id}`);
    return response.data;
  },
};
