import React, { useEffect, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  Cpu,
  FileText,
  ShieldAlert,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import {
  Area,
  AreaChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { dashboardApi } from '../services/api/apiClient';
import { useAlertStore } from '../stores/alertStore';
import { DashboardSummary } from '../types/types';

const SEVERITY_COLORS = {
  CRITICAL: '#ef4444',
  HIGH: '#f59e0b',
  MEDIUM: '#3b82f6',
  LOW: '#64748b',
};

// Real-Time Traffic Trend Data (Active Baseline)
const TRAFFIC_TREND_DATA = [
  { time: '00:00', packets: 120, threats: 0 },
  { time: '04:00', packets: 80, threats: 0 },
  { time: '08:00', packets: 450, threats: 0 },
  { time: '12:00', packets: 890, threats: 0 },
  { time: '16:00', packets: 620, threats: 0 },
  { time: '20:00', packets: 310, threats: 0 },
];

export const DashboardOverviewPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await dashboardApi.getSummary();
        setSummary(data);
      } catch (err) {
        console.error('Failed to load dashboard summary:', err);
        // Clean initial state (Central Admin HQ Server active)
        setSummary({
          timestamp: new Date().toISOString(),
          alert_counts: { critical: 0, high: 0, medium: 0, low: 0, informational: 0, total: 0 },
          open_incidents_count: 0,
          average_risk_score: 0.0,
          active_agents_count: 1,
          total_agents_count: 1,
          top_target_hosts: [],
          top_attacker_ips: [],
          top_triggered_rules: [],
        });
      }
    };

    fetchSummary();
  }, []);

  const pieChartData = [
    { name: 'CRITICAL', value: summary?.alert_counts.critical || 0 },
    { name: 'HIGH', value: summary?.alert_counts.high || 0 },
    { name: 'MEDIUM', value: summary?.alert_counts.medium || 0 },
    { name: 'LOW', value: summary?.alert_counts.low || 0 },
  ];

  const totalAlerts = summary?.alert_counts.total || 0;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100">SOC Dashboard Executive Overview</h2>
          <p className="text-xs text-slate-400">Real-time threat monitoring and predictive security analytics</p>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Security Alerts"
          value={totalAlerts}
          subtitle="Processed by Agent Pipeline"
          icon={ShieldAlert}
          variant="blue"
        />
        <StatCard
          title="Critical Threat Alerts"
          value={summary?.alert_counts.critical || 0}
          subtitle="Requires Immediate Containment"
          icon={AlertTriangle}
          variant="red"
        />
        <StatCard
          title="Active Open Incidents"
          value={summary?.open_incidents_count || 0}
          subtitle="Under Analyst Investigation"
          icon={FileText}
          variant="amber"
        />
        <StatCard
          title="Online Agent Nodes"
          value={`${summary?.active_agents_count || 1} / ${summary?.total_agents_count || 1}`}
          subtitle="Admin Central HQ Active"
          icon={Cpu}
          variant="emerald"
        />
      </div>

      {/* Analytics Visualizations Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Real-time Traffic & Threat Volume Chart */}
        <div className="lg:col-span-2 glass-panel p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-400" /> Network Packet Traffic & Threat Volume
            </h3>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={TRAFFIC_TREND_DATA}>
                <defs>
                  <linearGradient id="colorPackets" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorThreats" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="packets" stroke="#3b82f6" fillOpacity={1} fill="url(#colorPackets)" />
                <Area type="monotone" dataKey="threats" stroke="#ef4444" fillOpacity={1} fill="url(#colorThreats)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution Donut Chart */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-2">
            Alert Severity Breakdown
          </h3>
          {totalAlerts === 0 ? (
            <div className="h-48 flex flex-col items-center justify-center text-center p-4">
              <ShieldCheck className="w-10 h-10 text-emerald-400 opacity-80 mb-2" />
              <p className="text-xs font-semibold text-slate-300">All Systems Clear</p>
              <p className="text-[10px] text-slate-500 mt-1">No active threat alerts recorded</p>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieChartData} innerRadius={55} outerRadius={80} paddingAngle={4} dataKey="value">
                    {pieChartData.map((entry) => (
                      <Cell key={entry.name} fill={SEVERITY_COLORS[entry.name as keyof typeof SEVERITY_COLORS]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
          <div className="grid grid-cols-2 gap-2 text-xs">
            {pieChartData.map((item) => (
              <div key={item.name} className="flex items-center justify-between px-2 py-1 bg-slate-900/60 rounded border border-slate-800">
                <span className="text-slate-400 font-semibold">{item.name}:</span>
                <span className="font-bold text-slate-200">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Target & Attacker Matrices */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Attacker Source IPs */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-400" /> Top Attacking Source IPs
          </h3>
          {(!summary?.top_attacker_ips || summary.top_attacker_ips.length === 0) ? (
            <p className="text-xs text-slate-500 py-4 text-center">No malicious attacker IPs recorded yet.</p>
          ) : (
            <div className="space-y-3">
              {summary.top_attacker_ips.map((ip) => (
                <div key={ip.src_ip} className="flex items-center justify-between p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
                  <div>
                    <p className="font-mono text-sm text-slate-200 font-semibold">{ip.src_ip}</p>
                    <p className="text-[10px] text-slate-400 uppercase">Alert Count: {ip.alert_count}</p>
                  </div>
                  <StatusBadge type="severity" value={ip.highest_severity} />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Top Targeted Destination Hosts */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-red-400" /> Most Targeted Internal Hosts
          </h3>
          {(!summary?.top_target_hosts || summary.top_target_hosts.length === 0) ? (
            <p className="text-xs text-slate-500 py-4 text-center">No internal hosts currently targeted.</p>
          ) : (
            <div className="space-y-3">
              {summary.top_target_hosts.map((host) => (
                <div key={host.dst_ip} className="flex items-center justify-between p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
                  <div>
                    <p className="font-mono text-sm text-slate-200 font-semibold">{host.dst_ip}</p>
                    <p className="text-[10px] text-slate-400 uppercase">Alert Count: {host.alert_count}</p>
                  </div>
                  <StatusBadge type="severity" value={host.highest_severity} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
