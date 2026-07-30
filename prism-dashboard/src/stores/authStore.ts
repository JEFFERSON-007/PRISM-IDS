import { create } from 'zustand';
import { User } from '../types/types';

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('prism_token'),
  user: null,
  isAuthenticated: !!localStorage.getItem('prism_token'),

  setAuth: (token: string, user: User) => {
    localStorage.setItem('prism_token', token);
    set({ token, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('prism_token');
    set({ token: null, user: null, isAuthenticated: false });
  },
}));
