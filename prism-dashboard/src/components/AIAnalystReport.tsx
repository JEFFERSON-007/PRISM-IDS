import React, { useEffect, useState } from 'react';
import { Bot, AlertTriangle, ShieldCheck, Activity, Terminal } from 'lucide-react';
import { LLMAnalysisResponse } from '../types/types';
import { llmApi } from '../services/api/apiClient';

interface AIAnalystReportProps {
  alertId: string;
}

export const AIAnalystReport: React.FC<AIAnalystReportProps> = ({ alertId }) => {
  const [report, setReport] = useState<LLMAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        setLoading(true);
        const data = await llmApi.analyzeAlert(alertId);
        setReport(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch AI analysis:', err);
        setError('AI Security Analyst is currently offline or unavailable.');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [alertId]);

  if (loading) {
    return (
      <div className="glass-panel p-6 rounded-xl border border-blue-500/30 bg-blue-900/10 flex items-center justify-center space-x-3">
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-400"></div>
        <span className="text-blue-400 font-mono text-sm">AI Security Analyst is analyzing telemetry...</span>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="glass-panel p-5 rounded-xl border border-slate-800 bg-slate-900/50">
        <div className="flex items-center space-x-2 text-slate-400">
          <Bot className="w-5 h-5" />
          <span className="text-sm font-semibold">{error || 'No AI analysis available.'}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-xl border border-blue-500/30 bg-gradient-to-br from-slate-900 to-blue-950/20 overflow-hidden">
      {/* Header */}
      <div className="bg-blue-900/30 border-b border-blue-500/20 p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-500/20 rounded-lg">
            <Bot className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="font-bold text-blue-100 font-mono">Autonomous AI Analyst Briefing</h3>
            <p className="text-[10px] text-blue-400 uppercase tracking-widest">Model: {report.generated_by_model}</p>
          </div>
        </div>
        <div className="text-right">
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 bg-blue-500/10 border border-blue-500/30 rounded text-xs text-blue-300">
            <Activity className="w-3 h-3 mr-1" />
            Analyzed {new Date(report.timestamp).toLocaleTimeString()}
          </span>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Executive Summary & Technical */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-blue-300 uppercase tracking-wider flex items-center">
              <Terminal className="w-3 h-3 mr-2" /> Executive Summary
            </h4>
            <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/50 p-4 rounded-lg border border-slate-800/50">
              {report.executive_summary}
            </p>
          </div>
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center">
              <AlertTriangle className="w-3 h-3 mr-2" /> Risk & Impact Assessment
            </h4>
            <div className="bg-slate-950/50 p-4 rounded-lg border border-slate-800/50 space-y-4">
              <div>
                <span className="text-xs text-slate-500 uppercase">Trigger Rationale</span>
                <p className="text-sm text-slate-300 mt-1">{report.trigger_rationale}</p>
              </div>
              <div className="pt-2 border-t border-slate-800">
                <span className="text-xs text-slate-500 uppercase">Likely Impact</span>
                <p className="text-sm text-amber-200/90 mt-1">{report.likely_impact}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Technical Explanation */}
        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Technical Analysis</h4>
          <p className="text-sm text-slate-400 font-mono bg-slate-950 p-3 rounded border border-slate-800">
            {report.technical_explanation}
          </p>
        </div>

        {/* Remediation & MITRE */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Remediation */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center">
              <ShieldCheck className="w-3 h-3 mr-2" /> Recommended Actions
            </h4>
            <div className="space-y-2">
              {report.remediation_actions?.map((action, idx) => (
                <div key={idx} className="bg-emerald-950/20 border border-emerald-900/50 p-3 rounded-lg">
                  <div className="flex justify-between items-start mb-1">
                    <span className="font-semibold text-emerald-300 text-sm">{action.title}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded border ${
                      action.priority <= 1 ? 'bg-red-500/20 border-red-500/50 text-red-300' :
                      action.priority === 2 ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' :
                      'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                    }`}>
                      P{action.priority} — {action.action_type}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">{action.details}</p>
                </div>
              ))}
              {(!report.remediation_actions || report.remediation_actions.length === 0) && (
                <p className="text-sm text-slate-500">No specific remediation actions recommended.</p>
              )}
            </div>
          </div>

          {/* MITRE ATT&CK */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">MITRE ATT&CK Mapping</h4>
            <div className="flex flex-wrap gap-2">
              {report.mitre_attack_mapping?.map((mitre, idx) => (
                <div key={idx} className="bg-indigo-950/30 border border-indigo-500/30 px-3 py-2 rounded-lg flex flex-col">
                  <span className="text-[10px] text-indigo-400 font-mono mb-1">{mitre.technique_id}</span>
                  <span className="text-xs font-semibold text-indigo-200">{mitre.technique_name}</span>
                  <span className="text-[10px] text-slate-500 mt-1 capitalize">{mitre.tactic.toLowerCase()}</span>
                </div>
              ))}
              {(!report.mitre_attack_mapping || report.mitre_attack_mapping.length === 0) && (
                <p className="text-sm text-slate-500">No MITRE ATT&CK techniques mapped.</p>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
