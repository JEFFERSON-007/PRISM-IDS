import React from 'react';
import { BarChart3, Network, ShieldCheck } from 'lucide-react';
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const PROTOCOL_DATA = [
  { protocol: 'TCP', count: 1420, color: '#3b82f6' },
  { protocol: 'UDP', count: 480, color: '#10b981' },
  { protocol: 'ICMP', count: 120, color: '#f59e0b' },
];

const PORT_DATA = [
  { port: 'HTTP (80)', alerts: 140 },
  { port: 'HTTPS (443)', alerts: 88 },
  { port: 'SSH (22)', alerts: 64 },
  { port: 'PostgreSQL (5432)', alerts: 45 },
  { port: 'RDP (3389)', alerts: 32 },
];

export const NetworkAnalyticsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-cyan-400" /> Network Traffic & Protocol Analytics
        </h2>
        <p className="text-xs text-slate-400">Deep packet protocol distribution, targeted port vectors, and traffic volume trends</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Protocol Volume Distribution */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Network className="w-4 h-4 text-blue-400" /> Protocol Distribution Breakdown
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={PROTOCOL_DATA}>
                <XAxis dataKey="protocol" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Bar dataKey="count">
                  {PROTOCOL_DATA.map((entry) => (
                    <Cell key={entry.protocol} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Targeted Services & Ports */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" /> Top Targeted Destination Ports & Services
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={PORT_DATA} layout="vertical">
                <XAxis type="number" stroke="#64748b" fontSize={11} />
                <YAxis dataKey="port" type="category" stroke="#64748b" fontSize={10} width={130} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Bar dataKey="alerts" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
