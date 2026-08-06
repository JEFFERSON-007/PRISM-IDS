import { create } from 'zustand';
import { User } from '../types/types';

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
}

const defaultUser: User = {
  id: 'usr-1',
  username: 'admin',
  email: 'admin@prism-ids.local',
  role: 'ADMINISTRATOR',
  is_active: true,
};

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('prism_token') || 'demo-admin-token-12345',
  user: defaultUser,
  isAuthenticated: true,

  setAuth: (token: string, user: User) => {
    localStorage.setItem('prism_token', token);
    set({ token, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('prism_token');
    set({ token: null, user: null, isAuthenticated: false });
  },
}));
