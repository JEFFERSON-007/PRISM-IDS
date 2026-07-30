import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  Activity,
  BarChart3,
  Cpu,
  FileText,
  LogOut,
  Server,
  Settings,
  ShieldAlert,
  Wifi,
  WifiOff,
} from 'lucide-react';
import { Toaster } from 'sonner';
import { useAuthStore } from '../stores/authStore';
import { useWebSocket } from '../services/websocket/useWebSocket';

export const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const logout = useAuthStore((state) => state.logout);
  const user = useAuthStore((state) => state.user);
  const { isConnected } = useWebSocket();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { label: 'Overview', path: '/dashboard', icon: Activity },
    { label: 'Live Alerts', path: '/alerts', icon: ShieldAlert },
    { label: 'Incidents', path: '/incidents', icon: FileText },
    { label: 'Network Analytics', path: '/analytics', icon: BarChart3 },
    { label: 'Agent Nodes', path: '/agents', icon: Cpu },
    { label: 'System Health', path: '/system', icon: Server },
    { label: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-[#090d16] flex text-slate-100 font-sans">
      <Toaster position="top-right" theme="dark" richColors />

      {/* Sidebar Navigation */}
      <aside className="w-64 bg-[#0f172a]/90 border-r border-slate-800 flex flex-col justify-between p-4 sticky top-0 h-screen z-30">
        <div>
          {/* Brand Logo */}
          <div className="flex items-center space-x-3 px-3 py-4 mb-6 border-b border-slate-800/80">
            <div className="p-2 bg-blue-600/20 border border-blue-500/40 rounded-lg">
              <ShieldAlert className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-wider text-slate-100">PRISM <span className="text-blue-500">IDS</span></h1>
              <p className="text-[10px] text-slate-400 tracking-widest uppercase">Security Operations</p>
            </div>
          </div>

          {/* Nav Links */}
          <nav className="space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-[0_0_12px_rgba(59,130,246,0.15)]'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`
                }
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Footer User Profile & Logout */}
        <div className="border-t border-slate-800 pt-4 px-2">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-200">{user?.username || 'SOC Analyst'}</p>
              <p className="text-[10px] text-slate-400 uppercase">{user?.role || 'Administrator'}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Body */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="h-16 bg-[#0f172a]/60 border-b border-slate-800/80 px-6 flex items-center justify-between sticky top-0 backdrop-blur-md z-20">
          <div className="flex items-center space-x-4">
            <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">
              PRISM Threat Detection Network
            </span>
          </div>

          <div className="flex items-center space-x-4">
            {/* Live WebSocket Status Indicator */}
            <div className="flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold border bg-slate-900/80 border-slate-700">
              {isConnected ? (
                <>
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  <Wifi className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Live WS Stream</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-3.5 h-3.5 text-red-400" />
                  <span className="text-red-400">Disconnected</span>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Dynamic Route Page View */}
        <main className="p-6 flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
