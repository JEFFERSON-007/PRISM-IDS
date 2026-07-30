import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Clock, Code, Cpu, Database, Network, ShieldAlert } from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { alertsApi } from '../services/api/apiClient';
import { Alert } from '../types/types';

export const AlertDetailsPage: React.FC = () => {
  const { alertId } = useParams<{ alertId: string }>();
  const navigate = useNavigate();
  const [alert, setAlert] = useState<Alert | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAlert = async () => {
      if (!alertId) return;
      try {
        const data = await alertsApi.getAlertById(alertId);
        setAlert(data);
      } catch (err) {
        console.error('Error fetching alert details:', err);
        // Fallback demo object
        setAlert({
          id: '1',
          alert_id: alertId || 'ALT-2026-0001',
          timestamp: new Date().toISOString(),
          first_seen: new Date().toISOString(),
          last_seen: new Date().toISOString(),
          detection_id: 'DET-001',
          flow_id: 'FLOW-100',
          src_ip: '192.168.1.50',
          dst_ip: '10.0.0.1',
          src_port: 44321,
          dst_port: 80,
          protocol: 'TCP',
          risk_score: 92.5,
          severity: 'CRITICAL',
          detection_method: 'HYBRID',
          confidence: 0.95,
          status: 'OPEN',
          occurrence_count: 14,
          matched_rules: [
            { rule_id: 'SIG-001', name: 'Port Scanning Pattern', severity: 'HIGH' },
            { rule_id: 'SIG-002', name: 'TCP SYN Flood Anomaly', severity: 'CRITICAL' },
          ],
          ml_prediction: {
            is_malicious: true,
            probability: 0.96,
            model_name: 'RandomForest_v1.joblib',
            confidence: 0.95,
          },
          evidence_summary: {
            packet_count: 1450,
            byte_count: 980400,
            syn_count: 1420,
            ack_count: 12,
            flow_duration_sec: 14.5,
          },
        });
      } finally {
        setLoading(false);
      }
    };

    loadAlert();
  }, [alertId]);

  if (loading || !alert) {
    return <div className="p-8 text-center text-slate-400">Loading alert telemetry...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <button
        onClick={() => navigate('/alerts')}
        className="flex items-center space-x-2 text-slate-400 hover:text-slate-100 transition-colors text-xs font-semibold uppercase tracking-wider"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Live Alerts</span>
      </button>

      {/* Alert Header Banner */}
      <div className="glass-panel p-6 rounded-xl border border-slate-800 flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <h2 className="text-2xl font-bold font-mono text-slate-100">{alert.alert_id}</h2>
            <StatusBadge type="severity" value={alert.severity} />
            <StatusBadge type="status" value={alert.status} />
          </div>
          <p className="text-xs text-slate-400">
            Detected via <span className="text-blue-400 font-semibold">{alert.detection_method}</span> engine | Detection ID: {alert.detection_id}
          </p>
        </div>

        {/* Risk Score Meter */}
        <div className="text-right">
          <p className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">Normalized Risk Score</p>
          <div className="text-4xl font-extrabold text-red-500">{alert.risk_score} <span className="text-xs text-slate-500 font-normal">/ 100</span></div>
          <p className="text-[10px] text-slate-400">Confidence: {(alert.confidence * 100).toFixed(0)}%</p>
        </div>
      </div>

      {/* 5-Tuple Network Flow Card */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800">
        <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Network className="w-4 h-4 text-blue-400" /> Network Flow 5-Tuple Specification
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 bg-slate-900/60 p-4 rounded-lg border border-slate-800/80 font-mono text-xs">
          <div>
            <span className="text-slate-500 block text-[10px] uppercase">Source IP</span>
            <span className="text-slate-200 font-bold">{alert.src_ip}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px] uppercase">Source Port</span>
            <span className="text-slate-200">{alert.src_port}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px] uppercase">Destination IP</span>
            <span className="text-slate-200 font-bold">{alert.dst_ip}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px] uppercase">Destination Port</span>
            <span className="text-slate-200">{alert.dst_port}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px] uppercase">Protocol</span>
            <span className="text-blue-400 font-bold">{alert.protocol}</span>
          </div>
        </div>
      </div>

      {/* Detection Evidence & Rules Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Matched Signature Rules */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" /> Triggered Signature Rules
          </h3>
          <div className="space-y-3">
            {alert.matched_rules?.map((rule, idx) => (
              <div key={idx} className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 flex items-center justify-between">
                <div>
                  <p className="font-mono text-xs text-slate-200 font-semibold">{rule.rule_id}: {rule.name}</p>
                  <p className="text-[10px] text-slate-400">Rule Severity: {rule.severity}</p>
                </div>
                <StatusBadge type="severity" value={rule.severity} />
              </div>
            )) || <p className="text-xs text-slate-500">No signature rules triggered.</p>}
          </div>
        </div>

        {/* Machine Learning Model Output */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-emerald-400" /> ML Classifier Inference
          </h3>
          {alert.ml_prediction ? (
            <div className="p-4 bg-slate-900/60 rounded-lg border border-slate-800 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Classification:</span>
                <span className="font-bold text-red-400">{alert.ml_prediction.is_malicious ? 'MALICIOUS THREAT' : 'BENIGN'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Malicious Probability:</span>
                <span className="font-mono text-slate-200">{(alert.ml_prediction.probability * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Model Artifact:</span>
                <span className="font-mono text-blue-400">{alert.ml_prediction.model_name}</span>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500">ML model standby / not invoked.</p>
          )}
        </div>
      </div>

      {/* Raw Evidence Summary JSON */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800">
        <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Code className="w-4 h-4 text-slate-400" /> Raw Flow Telemetry & Feature Evidence
        </h3>
        <pre className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-xs font-mono text-slate-300 overflow-x-auto">
          {JSON.stringify(alert.evidence_summary || alert, null, 2)}
        </pre>
      </div>
    </div>
  );
};
