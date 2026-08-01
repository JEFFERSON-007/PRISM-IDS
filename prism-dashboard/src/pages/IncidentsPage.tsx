import React, { useEffect, useState } from 'react';
import { FileText, Plus, ShieldCheck } from 'lucide-react';
import { toast } from 'sonner';
import { StatusBadge } from '../components/ui/StatusBadge';
import { incidentsApi } from '../services/api/apiClient';
import { Incident } from '../types/types';

export const IncidentsPage: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [newNote, setNewNote] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // New Incident Form
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState('HIGH');

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const res = await incidentsApi.getIncidents();
      setIncidents(res.items);
      if (res.items.length > 0 && !selectedIncident) {
        setSelectedIncident(res.items[0]);
      }
    } catch (err) {
      console.error('Error loading incidents:', err);
      // Clean empty state - show real incidents only
      setIncidents([]);
      setSelectedIncident(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, []);

  const handleCreateIncident = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await incidentsApi.createIncident({ title, description, severity });
      toast.success('Incident created successfully');
      setShowCreateModal(false);
      setTitle('');
      setDescription('');
      fetchIncidents();
    } catch (err) {
      toast.error('Failed to create incident');
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!selectedIncident) return;
    try {
      const updated = await incidentsApi.updateStatus(selectedIncident.incident_id, newStatus);
      setSelectedIncident(updated);
      toast.success(`Status updated to ${newStatus}`);
      fetchIncidents();
    } catch (err) {
      toast.error('Failed to update status');
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIncident || !newNote.trim()) return;
    try {
      const updated = await incidentsApi.addNote(selectedIncident.incident_id, newNote);
      setSelectedIncident(updated);
      setNewNote('');
      toast.success('Note added');
      fetchIncidents();
    } catch (err) {
      toast.error('Failed to add note');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <FileText className="w-6 h-6 text-amber-400" /> Security Incident Response Center
          </h2>
          <p className="text-xs text-slate-400">SOC Analyst incident tracking, triage, and investigation workflows</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-[0_0_12px_rgba(59,130,246,0.3)] transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>New Incident</span>
        </button>
      </div>

      {incidents.length === 0 ? (
        <div className="glass-panel p-12 rounded-xl border border-slate-800 text-center space-y-3">
          <ShieldCheck className="w-12 h-12 text-emerald-400 mx-auto opacity-80" />
          <h3 className="text-base font-bold text-slate-200">No Open Security Incidents</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            All system threat levels are normal. When live threats trigger critical thresholds, incident tickets will populate automatically.
          </p>
        </div>
      ) : (
        /* Incident Split Layout */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Incident List Column */}
          <div className="space-y-3">
            {incidents.map((inc) => (
              <div
                key={inc.id}
                onClick={() => setSelectedIncident(inc)}
                className={`p-4 glass-panel rounded-xl border transition-all cursor-pointer ${
                  selectedIncident?.id === inc.id
                    ? 'border-blue-500 bg-blue-500/10 shadow-[0_0_15px_rgba(59,130,246,0.15)]'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs font-bold text-slate-200">{inc.incident_id}</span>
                  <StatusBadge type="severity" value={inc.severity} />
                </div>
                <h4 className="text-sm font-semibold text-slate-100 mb-1 line-clamp-1">{inc.title}</h4>
                <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2">
                  <StatusBadge type="status" value={inc.status} />
                  <span>{new Date(inc.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Selected Incident Detail View */}
          {selectedIncident && (
            <div className="lg:col-span-2 glass-panel p-6 rounded-xl border border-slate-800 space-y-6">
              <div className="flex items-start justify-between border-b border-slate-800 pb-4">
                <div>
                  <div className="flex items-center space-x-3 mb-1">
                    <h3 className="text-lg font-bold text-slate-100">{selectedIncident.title}</h3>
                    <StatusBadge type="severity" value={selectedIncident.severity} />
                    <StatusBadge type="status" value={selectedIncident.status} />
                  </div>
                  <p className="text-xs text-slate-400">Incident Identifier: {selectedIncident.incident_id}</p>
                </div>

                {/* Status Transition Action Buttons */}
                <div className="flex space-x-2">
                  {selectedIncident.status === 'OPEN' && (
                    <button
                      onClick={() => handleStatusChange('ACKNOWLEDGED')}
                      className="px-3 py-1.5 bg-amber-600/20 hover:bg-amber-600/40 text-amber-300 text-xs font-semibold rounded-lg border border-amber-500/40"
                    >
                      Acknowledge
                    </button>
                  )}
                  {selectedIncident.status !== 'RESOLVED' && (
                    <button
                      onClick={() => handleStatusChange('RESOLVED')}
                      className="px-3 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-300 text-xs font-semibold rounded-lg border border-emerald-500/40"
                    >
                      Resolve Incident
                    </button>
                  )}
                </div>
              </div>

              {/* Description */}
              <div>
                <h4 className="text-xs font-semibold uppercase text-slate-400 mb-1">Description</h4>
                <p className="text-xs text-slate-200 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                  {selectedIncident.description || 'No detailed description provided.'}
                </p>
              </div>

              {/* Analyst Investigation Notes Thread */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold uppercase text-slate-400 flex items-center gap-2">
                  Analyst Investigation Log
                </h4>
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {selectedIncident.notes?.map((note, idx) => (
                    <div key={idx} className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-xs space-y-1">
                      <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                        <span>Author: {note.author}</span>
                        <span>{new Date(note.timestamp).toLocaleString()}</span>
                      </div>
                      <p className="text-slate-200">{note.note}</p>
                    </div>
                  ))}
                </div>

                {/* Add Note Form */}
                <form onSubmit={handleAddNote} className="flex space-x-2 pt-2">
                  <input
                    type="text"
                    placeholder="Type investigation note..."
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    className="flex-1 bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-blue-500"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg"
                  >
                    Add Note
                  </button>
                </form>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modal to Create Incident */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 w-full max-w-md space-y-4">
            <h3 className="text-lg font-bold text-slate-100">Create New Security Incident</h3>
            <form onSubmit={handleCreateIncident} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100"
                  placeholder="e.g. DDoS Attack on Web Gateway"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 h-20"
                  placeholder="Details of investigation..."
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Severity</label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100"
                >
                  <option value="CRITICAL">CRITICAL</option>
                  <option value="HIGH">HIGH</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="LOW">LOW</option>
                </select>
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg"
                >
                  Create Incident
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
