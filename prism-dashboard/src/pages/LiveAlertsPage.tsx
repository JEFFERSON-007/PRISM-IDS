import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, RefreshCw, Search, ShieldAlert, ShieldCheck } from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { alertsApi } from '../services/api/apiClient';
import { useAlertStore } from '../stores/alertStore';
import { Alert } from '../types/types';

export const LiveAlertsPage: React.FC = () => {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);

  // Filter States
  const [severity, setSeverity] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [protocol, setProtocol] = useState<string>('');
  const [search, setSearch] = useState<string>('');

  const liveAlerts = useAlertStore((state) => state.liveAlerts);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const res = await alertsApi.getAlerts({
        severity: severity || undefined,
        status: statusFilter || undefined,
        protocol: protocol || undefined,
        search: search || undefined,
        page,
        page_size: 15,
      });
      setAlerts(res.items);
      setTotalRecords(res.total_records);
      setTotalPages(res.total_pages);
    } catch (err) {
      console.error('Error fetching alerts:', err);
      // Clean empty state - show real alerts only
      setAlerts([]);
      setTotalRecords(0);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [page, severity, statusFilter, protocol]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-blue-400" /> Real-Time Security Alert Stream
          </h2>
          <p className="text-xs text-slate-400">Live network security event management and threat investigation</p>
        </div>
        <button
          onClick={fetchAlerts}
          className="flex items-center space-x-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="glass-panel p-4 rounded-xl border border-slate-800 flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search IP, Alert ID, Rule..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchAlerts()}
            className="w-full bg-slate-900/80 border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Severity Filter */}
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
          className="bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Severities</option>
          <option value="CRITICAL">CRITICAL</option>
          <option value="HIGH">HIGH</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="LOW">LOW</option>
        </select>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="OPEN">OPEN</option>
          <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
          <option value="RESOLVED">RESOLVED</option>
        </select>

        {/* Protocol Filter */}
        <select
          value={protocol}
          onChange={(e) => setProtocol(e.target.value)}
          className="bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Protocols</option>
          <option value="TCP">TCP</option>
          <option value="UDP">UDP</option>
          <option value="ICMP">ICMP</option>
        </select>
      </div>

      {/* Alerts Table */}
      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden">
        {alerts.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <ShieldCheck className="w-12 h-12 text-emerald-400 mx-auto opacity-80" />
            <h3 className="text-base font-bold text-slate-200">No Threat Alerts Detected</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              All monitored system network interfaces are operating securely. Live network packet capture and hybrid detection engine actively monitoring...
            </p>
          </div>
        ) : (
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-semibold text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3.5">Severity</th>
                <th className="p-3.5">Alert ID</th>
                <th className="p-3.5">Source IP</th>
                <th className="p-3.5">Destination IP</th>
                <th className="p-3.5">Protocol</th>
                <th className="p-3.5">Risk Score</th>
                <th className="p-3.5">Method</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {alerts.map((alert) => (
                <tr key={alert.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3.5">
                    <StatusBadge type="severity" value={alert.severity} />
                  </td>
                  <td className="p-3.5 font-mono font-semibold text-slate-100">{alert.alert_id}</td>
                  <td className="p-3.5 font-mono text-slate-300">{alert.src_ip}:{alert.src_port}</td>
                  <td className="p-3.5 font-mono text-slate-300">{alert.dst_ip}:{alert.dst_port}</td>
                  <td className="p-3.5 font-mono text-slate-400">{alert.protocol}</td>
                  <td className="p-3.5 font-bold">
                    <span
                      className={
                        alert.risk_score >= 80
                          ? 'text-red-400'
                          : alert.risk_score >= 50
                          ? 'text-amber-400'
                          : 'text-blue-400'
                      }
                    >
                      {alert.risk_score}
                    </span>
                  </td>
                  <td className="p-3.5 text-slate-400">{alert.detection_method}</td>
                  <td className="p-3.5">
                    <StatusBadge type="status" value={alert.status} />
                  </td>
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => navigate(`/alerts/${alert.alert_id}`)}
                      className="p-1.5 bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 rounded-lg border border-blue-500/30 transition-colors"
                      title="Investigate Alert"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* Pagination Footer */}
        {alerts.length > 0 && (
          <div className="p-4 bg-slate-900/60 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Showing page {page} of {totalPages} ({totalRecords} records)</span>
            <div className="flex space-x-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700 disabled:opacity-40"
              >
                Previous
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
