import React from 'react';
import { Severity, AlertStatus, IncidentStatus } from '../../types/types';

interface StatusBadgeProps {
  type: 'severity' | 'status' | 'method';
  value: Severity | AlertStatus | IncidentStatus | string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ type, value }) => {
  const valUpper = String(value).toUpperCase();

  let colorClasses = 'bg-slate-800 text-slate-300 border-slate-700';

  if (type === 'severity') {
    switch (valUpper) {
      case 'CRITICAL':
        colorClasses = 'bg-red-950/80 text-red-400 border-red-800 shadow-[0_0_10px_rgba(239,68,68,0.3)]';
        break;
      case 'HIGH':
        colorClasses = 'bg-amber-950/80 text-amber-400 border-amber-800 shadow-[0_0_10px_rgba(245,158,11,0.25)]';
        break;
      case 'MEDIUM':
        colorClasses = 'bg-blue-950/80 text-blue-400 border-blue-800';
        break;
      case 'LOW':
        colorClasses = 'bg-slate-800/80 text-slate-300 border-slate-700';
        break;
      case 'INFORMATIONAL':
        colorClasses = 'bg-emerald-950/80 text-emerald-400 border-emerald-800';
        break;
    }
  } else if (type === 'status') {
    switch (valUpper) {
      case 'OPEN':
      case 'REOPENED':
        colorClasses = 'bg-red-950/50 text-red-400 border-red-800/60';
        break;
      case 'ACKNOWLEDGED':
        colorClasses = 'bg-amber-950/50 text-amber-400 border-amber-800/60';
        break;
      case 'RESOLVED':
        colorClasses = 'bg-emerald-950/50 text-emerald-400 border-emerald-800/60';
        break;
    }
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border transition-colors ${colorClasses}`}
    >
      {value}
    </span>
  );
};
