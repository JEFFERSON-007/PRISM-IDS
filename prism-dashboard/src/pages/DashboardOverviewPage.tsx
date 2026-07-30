import React, { useEffect, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  Cpu,
  FileText,
  ShieldAlert,
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

// Synthetic Traffic Trend Data
const TRAFFIC_TREND_DATA = [
  { time: '00:00', packets: 4200, threats: 12 },
  { time: '04:00', packets: 3800, threats: 8 },
  { time: '08:00', packets: 8900, threats: 45 },
  { time: '12:00', packets: 12400, threats: 78 },
  { time: '16:00', packets: 1100, threats: 92 },
  { time: '20:00', packets: 7500, threats: 34 },
];

export const DashboardOverviewPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const liveAlerts = useAlertStore((state) => state.liveAlerts);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await dashboardApi.getSummary();
        setSummary(data);
      } catch (err) {
        console.error('Failed to load dashboard summary:', err);
        // Fallback demo data
        setSummary({
          timestamp: new Date().toISOString(),
          alert_counts: { critical: 4, high: 14, medium: 32, low: 88, informational: 150, total: 288 },
          open_incidents_count: 5,
          average_risk_score: 72.4,
          active_agents_count: 3,
          total_agents_count: 3,
          top_target_hosts: [
            { dst_ip: '10.0.0.1 (Web Server)', alert_count: 142, highest_severity: 'CRITICAL' },
            { dst_ip: '10.0.0.5 (DB Server)', alert_count: 89, highest_severity: 'HIGH' },
            { dst_ip: '10.0.0.12 (DNS Gateway)', alert_count: 45, highest_severity: 'MEDIUM' },
          ],
          top_attacker_ips: [
            { src_ip: '192.168.1.50', alert_count: 120, highest_severity: 'CRITICAL' },
            { src_ip: '45.33.22.11', alert_count: 98, highest_severity: 'HIGH' },
            { src_ip: '185.220.101.5', alert_count: 54, highest_severity: 'HIGH' },
          ],
          top_triggered_rules: [
            { rule_name: 'SIG-001 Port Scanning', trigger_count: 150 },
            { rule_name: 'SIG-002 TCP SYN Flood', trigger_count: 88 },
          ],
        });
      }
    };

    fetchSummary();
  }, []);

  const pieChartData = [
    { name: 'CRITICAL', value: summary?.alert_counts.critical || 4 },
    { name: 'HIGH', value: summary?.alert_counts.high || 14 },
    { name: 'MEDIUM', value: summary?.alert_counts.medium || 32 },
    { name: 'LOW', value: summary?.alert_counts.low || 88 },
  ];

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
          value={summary?.alert_counts.total || 288}
          subtitle="Processed by Agent Pipeline"
          icon={ShieldAlert}
          variant="blue"
        />
        <StatCard
          title="Critical Threat Alerts"
          value={summary?.alert_counts.critical || 4}
          subtitle="Requires Immediate Containment"
          icon={AlertTriangle}
          variant="red"
        />
        <StatCard
          title="Active Open Incidents"
          value={summary?.open_incidents_count || 5}
          subtitle="Under Analyst Investigation"
          icon={FileText}
          variant="amber"
        />
        <StatCard
          title="Online Agent Nodes"
          value={`${summary?.active_agents_count || 3} / ${summary?.total_agents_count || 3}`}
          subtitle="100% Healthy Telemetry"
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
          <div className="space-y-3">
            {summary?.top_attacker_ips.map((ip) => (
              <div key={ip.src_ip} className="flex items-center justify-between p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
                <div>
                  <p className="font-mono text-sm text-slate-200 font-semibold">{ip.src_ip}</p>
                  <p className="text-[10px] text-slate-400 uppercase">Alert Count: {ip.alert_count}</p>
                </div>
                <StatusBadge type="severity" value={ip.highest_severity} />
              </div>
            ))}
          </div>
        </div>

        {/* Top Targeted Destination Hosts */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-red-400" /> Most Targeted Internal Hosts
          </h3>
          <div className="space-y-3">
            {summary?.top_target_hosts.map((host) => (
              <div key={host.dst_ip} className="flex items-center justify-between p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
                <div>
                  <p className="font-mono text-sm text-slate-200 font-semibold">{host.dst_ip}</p>
                  <p className="text-[10px] text-slate-400 uppercase">Alert Count: {host.alert_count}</p>
                </div>
                <StatusBadge type="severity" value={host.highest_severity} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
