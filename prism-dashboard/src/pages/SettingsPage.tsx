import React from 'react';
import { Bell, Key, Server, Settings, User } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

export const SettingsPage: React.FC = () => {
  const user = useAuthStore((state) => state.user);

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
          <Settings className="w-6 h-6 text-slate-400" /> SOC Console & Preferences
        </h2>
        <p className="text-xs text-slate-400">Manage user authentication profile, alerts toaster preferences, and environment settings</p>
      </div>

      {/* User Profile Card */}
      <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
        <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <User className="w-4 h-4 text-blue-400" /> Analyst Profile
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-500 mb-1 uppercase text-[10px]">Username</label>
            <input
              type="text"
              readOnly
              value={user?.username || 'admin'}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-slate-200"
            />
          </div>
          <div>
            <label className="block text-slate-500 mb-1 uppercase text-[10px]">Role / Access Level</label>
            <input
              type="text"
              readOnly
              value={user?.role || 'ADMINISTRATOR'}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-blue-400 font-semibold"
            />
          </div>
        </div>
      </div>

      {/* Notification Preferences */}
      <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
        <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Bell className="w-4 h-4 text-amber-400" /> Real-Time Toast Notifications
        </h3>
        <div className="space-y-3 text-xs">
          <label className="flex items-center space-x-3 cursor-pointer">
            <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-900 text-blue-600" />
            <span className="text-slate-200">Toast notification on CRITICAL severity alerts</span>
          </label>
          <label className="flex items-center space-x-3 cursor-pointer">
            <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-900 text-blue-600" />
            <span className="text-slate-200">Toast notification on HIGH severity alerts</span>
          </label>
          <label className="flex items-center space-x-3 cursor-pointer">
            <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-900 text-blue-600" />
            <span className="text-slate-200">Toast notification on Incident updates</span>
          </label>
        </div>
      </div>

      {/* Read-only Server Configuration */}
      <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
        <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Server className="w-4 h-4 text-cyan-400" /> Environment API Endpoint Configuration
        </h3>
        <div className="space-y-3 text-xs">
          <div>
            <label className="block text-slate-500 mb-1 uppercase text-[10px]">Backend REST API Base URL</label>
            <input
              type="text"
              readOnly
              value="http://localhost:8000"
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 font-mono text-slate-300"
            />
          </div>
          <div>
            <label className="block text-slate-500 mb-1 uppercase text-[10px]">WebSocket Stream URL</label>
            <input
              type="text"
              readOnly
              value="ws://localhost:8000/ws/v1/connect"
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 font-mono text-slate-300"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
