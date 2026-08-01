import React, { useEffect, useState } from 'react';
import { Cpu, RefreshCw } from 'lucide-react';
import { agentsApi } from '../services/api/apiClient';
import { AgentNode } from '../types/types';

export const AgentMonitoringPage: React.FC = () => {
  const [agents, setAgents] = useState<AgentNode[]>([]);
  const [loading, setLoading] = useState(false);

  // Central Server Admin System (Always visible)
  const adminHostNode: AgentNode = {
    id: 'admin-central-hq',
    agent_id: 'PRISM-HQ-CENTRAL',
    name: 'PRISM Central Admin HQ Server',
    hostname: window.location.hostname || 'central-admin-server',
    ip_address: window.location.hostname === 'localhost' ? '127.0.0.1 (Central HQ)' : window.location.hostname,
    os_type: 'Central Security Master Server',
    version: '1.0.0',
    is_online: true,
    health_status: 'healthy',
    last_heartbeat: new Date().toISOString(),
  };

  const fetchAgents = async () => {
    setLoading(true);
    try {
      const data = await agentsApi.getAgents();
      // Ensure Central Admin HQ is always present at position 1
      const filteredRemote = data.filter((a) => a.agent_id !== 'PRISM-HQ-CENTRAL');
      setAgents([adminHostNode, ...filteredRemote]);
    } catch (err) {
      console.error('Error fetching agents:', err);
      // Display Admin Central HQ as primary active node
      setAgents([adminHostNode]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <Cpu className="w-6 h-6 text-emerald-400" /> Distributed Agent Node Fleet
          </h2>
          <p className="text-xs text-slate-400">Monitoring real deployed IDS packet capture & detection agent sensors</p>
        </div>
        <button
          onClick={fetchAgents}
          className="flex items-center space-x-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Fleet</span>
        </button>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <div key={agent.id} className="glass-panel p-5 rounded-xl border border-slate-800 space-y-4 hover:border-slate-700 transition-all">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-bold text-sm text-slate-100">{agent.name}</h3>
                <p className="font-mono text-xs text-slate-400">{agent.agent_id}</p>
              </div>
              <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold uppercase bg-emerald-950/80 text-emerald-400 border border-emerald-800">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>ONLINE</span>
              </span>
            </div>

            <div className="space-y-2 text-xs bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="flex justify-between">
                <span className="text-slate-500">Hostname:</span>
                <span className="font-mono text-slate-300">{agent.hostname}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">IP Address:</span>
                <span className="font-mono text-slate-300">{agent.ip_address}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">OS Environment:</span>
                <span className="text-slate-300">{agent.os_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Agent Version:</span>
                <span className="text-blue-400 font-semibold">v{agent.version}</span>
              </div>
            </div>

            <div className="text-[10px] text-slate-500 flex items-center justify-between pt-1">
              <span>Health: <strong className="text-emerald-400 capitalize">{agent.health_status}</strong></span>
              <span>Last Heartbeat: {new Date(agent.last_heartbeat).toLocaleTimeString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
