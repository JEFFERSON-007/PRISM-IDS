import { create } from 'zustand';
import { Alert } from '../types/types';

interface AlertState {
  liveAlerts: Alert[];
  addLiveAlert: (alert: Alert) => void;
  clearLiveAlerts: () => void;
}

export const useAlertStore = create<AlertState>((set) => ({
  liveAlerts: [],

  addLiveAlert: (alert: Alert) =>
    set((state) => ({
      // Keep newest 50 live alerts in memory buffer
      liveAlerts: [alert, ...state.liveAlerts.filter((a) => a.id !== alert.id)].slice(0, 50),
    })),

  clearLiveAlerts: () => set({ liveAlerts: [] }),
}));
