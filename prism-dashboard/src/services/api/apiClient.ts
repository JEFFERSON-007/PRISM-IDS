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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
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

// Auth APIs
export const authApi = {
  login: async (username: string, password: str) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const res = await apiClient.post('/api/v1/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return res.data;
  },
  getMe: async (): Promise<User> => {
    const res = await apiClient.get('/api/v1/auth/me');
    return res.data;
  },
};

// Alerts APIs
export const alertsApi = {
  getAlerts: async (params?: Record<string, any>): Promise<AlertPaginationResponse> => {
    const res = await apiClient.get('/api/v1/alerts', { params });
    return res.data;
  },
  getAlertById: async (alertId: string): Promise<Alert> => {
    const res = await apiClient.get(`/api/v1/alerts/${alertId}`);
    return res.data;
  },
};

// Incidents APIs
export const incidentsApi = {
  getIncidents: async (params?: Record<string, any>): Promise<IncidentPaginationResponse> => {
    const res = await apiClient.get('/api/v1/incidents', { params });
    return res.data;
  },
  createIncident: async (data: { title: string; description?: string; severity: string }): Promise<Incident> => {
    const res = await apiClient.post('/api/v1/incidents', data);
    return res.data;
  },
  getIncidentById: async (id: string): Promise<Incident> => {
    const res = await apiClient.get(`/api/v1/incidents/${id}`);
    return res.data;
  },
  updateStatus: async (id: string, status: string): Promise<Incident> => {
    const res = await apiClient.put(`/api/v1/incidents/${id}/status`, { status });
    return res.data;
  },
  assignAnalyst: async (id: string, assigned_to_user_id: string): Promise<Incident> => {
    const res = await apiClient.put(`/api/v1/incidents/${id}/assign`, { assigned_to_user_id });
    return res.data;
  },
  addNote: async (id: string, note: string): Promise<Incident> => {
    const res = await apiClient.post(`/api/v1/incidents/${id}/notes`, { note });
    return res.data;
  },
};

// Dashboard APIs
export const dashboardApi = {
  getSummary: async (): Promise<DashboardSummary> => {
    const res = await apiClient.get('/api/v1/dashboard/summary');
    return res.data;
  },
  getNetworkAnalytics: async () => {
    const res = await apiClient.get('/api/v1/dashboard/network');
    return res.data;
  },
  getSystemHealth: async (): Promise<SystemHealth> => {
    const res = await apiClient.get('/api/v1/dashboard/system');
    return res.data;
  },
};

// Agents APIs
export const agentsApi = {
  getAgents: async (): Promise<AgentNode[]> => {
    const res = await apiClient.get('/api/v1/agents');
    return res.data;
  },
};
