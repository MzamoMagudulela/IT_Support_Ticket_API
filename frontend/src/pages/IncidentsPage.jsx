import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import {
  AlertTriangle, Flame, ShieldAlert, CheckCircle, Plus,
  Search, Link as LinkIcon, BookOpen, Clock, FileText, ChevronRight
} from 'lucide-react';

const SEVERITY_COLORS = {
  SEV1_CRITICAL: 'bg-rose-950/80 text-rose-300 border-rose-500/50',
  SEV2_HIGH: 'bg-amber-950/80 text-amber-300 border-amber-500/50',
  SEV3_MEDIUM: 'bg-sky-950/80 text-sky-300 border-sky-500/50',
  SEV4_LOW: 'bg-slate-800 text-slate-300 border-slate-700',
};

export const IncidentsPage = () => {
  const { user, primaryRole } = useAuth();
  const { addToast } = useNotification();

  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [activeTab, setActiveTab] = useState('incidents'); // 'incidents' | 'problems' | 'known_errors'

  const [problems, setProblems] = useState([]);
  const [knownErrors, setKnownErrors] = useState([]);

  // Create Incident Form
  const [createForm, setCreateForm] = useState({
    title: '',
    description: '',
    affected_service: 'Global VPN Gateway',
    severity: 'SEV3_MEDIUM',
    is_major: false,
  });

  // RCA Form
  const [rcaForm, setRcaForm] = useState({
    root_cause: '',
    resolution_summary: '',
    post_incident_report: '',
    status: 'RESOLVED'
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [incRes, prbRes, keRes] = await Promise.all([
        api.get('/incidents'),
        api.get('/incidents/problems/list'),
        api.get('/incidents/known-errors/list')
      ]);
      setIncidents(incRes.data);
      setProblems(prbRes.data);
      setKnownErrors(keRes.data);
      if (incRes.data.length > 0 && !selectedIncident) {
        setSelectedIncident(incRes.data[0]);
        setRcaForm({
          root_cause: incRes.data[0].root_cause || '',
          resolution_summary: incRes.data[0].resolution_summary || '',
          post_incident_report: incRes.data[0].post_incident_report || '',
          status: incRes.data[0].status || 'RESOLVED'
        });
      }
    } catch (e) {
      console.error(e);
      addToast('Failed to load incident data', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSelectIncident = (inc) => {
    setSelectedIncident(inc);
    setRcaForm({
      root_cause: inc.root_cause || '',
      resolution_summary: inc.resolution_summary || '',
      post_incident_report: inc.post_incident_report || '',
      status: inc.status || 'RESOLVED'
    });
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/incidents', createForm);
      addToast(`Incident ${res.data.incident_number} logged!`, 'success');
      setShowCreateModal(false);
      setCreateForm({
        title: '',
        description: '',
        affected_service: 'Global VPN Gateway',
        severity: 'SEV3_MEDIUM',
        is_major: false
      });
      fetchData();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to report incident', 'error');
    }
  };

  const handleUpdateRCA = async (e) => {
    e.preventDefault();
    if (!selectedIncident) return;
    try {
      await api.patch(`/incidents/${selectedIncident.id}`, rcaForm);
      addToast('Root Cause Analysis and Post-Incident Report saved', 'success');
      fetchData();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to update RCA', 'error');
    }
  };

  const majorIncidents = incidents.filter((i) => i.is_major);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">IT Incident Operations & Problem Management</h1>
          <p className="text-xs text-slate-400 mt-0.5">Major incident command, root cause analysis (RCA), and known error records</p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex rounded-lg bg-slate-900 border border-slate-800 p-1 text-xs font-semibold">
            <button
              onClick={() => setActiveTab('incidents')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeTab === 'incidents' ? 'bg-brand-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Incidents ({incidents.length})
            </button>
            <button
              onClick={() => setActiveTab('problems')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeTab === 'problems' ? 'bg-brand-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Problems ({problems.length})
            </button>
            <button
              onClick={() => setActiveTab('known_errors')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeTab === 'known_errors' ? 'bg-brand-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Known Errors ({knownErrors.length})
            </button>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 font-semibold text-xs text-white shadow-lg shadow-rose-600/25 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Declare Incident</span>
          </button>
        </div>
      </div>

      {/* Major Incident Flash Banner if any active major incidents */}
      {majorIncidents.length > 0 && (
        <div className="p-4 rounded-xl bg-gradient-to-r from-rose-950/90 via-slate-900 to-rose-950/70 border border-rose-500/40 shadow-xl flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-rose-600/30 border border-rose-500/50 text-rose-300">
              <Flame className="w-5 h-5 text-rose-400 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-extrabold text-rose-300 tracking-wide uppercase">ACTIVE MAJOR INCIDENT:</span>
                <span className="font-mono text-xs font-bold text-white">{majorIncidents[0].incident_number}</span>
              </div>
              <div className="text-sm font-bold text-slate-100">{majorIncidents[0].title}</div>
              <div className="text-xs text-slate-400 mt-0.5">
                Service: <strong className="text-slate-200">{majorIncidents[0].affected_service}</strong> • Linked Tickets: {majorIncidents[0].linked_ticket_count}
              </div>
            </div>
          </div>
          <button
            onClick={() => handleSelectIncident(majorIncidents[0])}
            className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-xs font-bold text-white shadow transition-colors"
          >
            Open Commander View
          </button>
        </div>
      )}

      {/* Tab 1: Incidents View */}
      {activeTab === 'incidents' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* List (5 cols) */}
          <div className="lg:col-span-5 space-y-3">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">
              Recorded Incident Stream
            </div>
            <div className="space-y-2.5 max-h-[720px] overflow-y-auto pr-1">
              {incidents.map((inc) => (
                <div
                  key={inc.id}
                  onClick={() => handleSelectIncident(inc)}
                  className={`p-4 rounded-xl border text-xs cursor-pointer transition-all ${
                    selectedIncident?.id === inc.id
                      ? 'bg-slate-900 border-brand-500 shadow-lg glow-brand'
                      : 'bg-slate-900/60 border-slate-800 hover:bg-slate-800/60'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono font-bold text-brand-400">{inc.incident_number}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${SEVERITY_COLORS[inc.severity]}`}>
                      {inc.severity}
                    </span>
                  </div>
                  <div className="font-semibold text-slate-100 line-clamp-1">{inc.title}</div>
                  <div className="text-slate-400 text-[11px] line-clamp-2 mt-1">{inc.description}</div>
                  <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800/80 text-[11px] text-slate-500">
                    <span>Service: <strong className="text-slate-300">{inc.affected_service}</strong></span>
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-bold">
                      {inc.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Incident Detail & RCA (7 cols) */}
          <div className="lg:col-span-7">
            {selectedIncident ? (
              <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
                {/* Header */}
                <div className="flex items-start justify-between pb-4 border-b border-slate-800">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-sm font-bold text-brand-400">{selectedIncident.incident_number}</span>
                      {selectedIncident.is_major && (
                        <span className="px-2 py-0.5 rounded bg-rose-600 text-white font-black text-[10px] uppercase">
                          MAJOR INCIDENT
                        </span>
                      )}
                    </div>
                    <h2 className="text-base font-bold text-white mt-1">{selectedIncident.title}</h2>
                    <div className="text-xs text-slate-400 mt-1">
                      Detected: {new Date(selectedIncident.detected_at).toLocaleString()} • Commander: {selectedIncident.commander_name || 'Sarah Jenkins'}
                    </div>
                  </div>
                  <span className={`px-2.5 py-1 rounded text-xs font-bold border ${SEVERITY_COLORS[selectedIncident.severity]}`}>
                    {selectedIncident.severity}
                  </span>
                </div>

                {/* Description */}
                <div>
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Incident Scope</h3>
                  <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {selectedIncident.description}
                  </div>
                </div>

                {/* Linked Tickets & Child Incidents */}
                <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 text-xs flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <LinkIcon className="w-4 h-4 text-brand-400" />
                    <span className="text-slate-300 font-semibold">Correlated Support Tickets:</span>
                  </div>
                  <span className="px-2.5 py-0.5 rounded bg-brand-950 border border-brand-500/40 text-brand-300 font-bold">
                    {selectedIncident.linked_ticket_count} tickets grouped
                  </span>
                </div>

                {/* Root Cause Analysis (RCA) & Post-Incident Report */}
                <form onSubmit={handleUpdateRCA} className="space-y-4 pt-2 border-t border-slate-800">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                    <FileText className="w-4 h-4 text-brand-400" />
                    <span>Post-Incident Review & Root Cause Analysis (RCA)</span>
                  </h3>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Identified Root Cause</label>
                    <textarea
                      rows={2}
                      placeholder="e.g. BGP route flapping due to tier-1 upstream maintenance..."
                      value={rcaForm.root_cause}
                      onChange={(e) => setRcaForm({ ...rcaForm, root_cause: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Permanent Resolution Summary</label>
                    <textarea
                      rows={2}
                      placeholder="Steps implemented to eliminate recurrence..."
                      value={rcaForm.resolution_summary}
                      onChange={(e) => setRcaForm({ ...rcaForm, resolution_summary: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500"
                    />
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <div className="flex items-center space-x-2 text-xs">
                      <span className="font-semibold text-slate-400">Incident Status:</span>
                      <select
                        value={rcaForm.status}
                        onChange={(e) => setRcaForm({ ...rcaForm, status: e.target.value })}
                        className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-200 font-bold"
                      >
                        <option value="DETECTED">DETECTED</option>
                        <option value="INVESTIGATING">INVESTIGATING</option>
                        <option value="IDENTIFIED">IDENTIFIED</option>
                        <option value="MONITORING">MONITORING</option>
                        <option value="RESOLVED">RESOLVED</option>
                      </select>
                    </div>

                    <button
                      type="submit"
                      className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs shadow-md shadow-brand-500/20"
                    >
                      Save RCA & Closure
                    </button>
                  </div>
                </form>
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500">Select an incident to view operations and RCA</div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Problems View */}
      {activeTab === 'problems' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {problems.map((prb) => (
              <div key={prb.id} className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-lg space-y-2.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-amber-400">{prb.problem_number}</span>
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-bold">{prb.status}</span>
                </div>
                <h3 className="font-bold text-slate-100 text-sm">{prb.title}</h3>
                <p className="text-slate-400">{prb.description}</p>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 space-y-1">
                  <div className="text-[11px] font-bold text-brand-300">Workaround:</div>
                  <div className="text-slate-300 font-mono text-[11px]">{prb.workaround || 'Under investigation'}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Known Errors View */}
      {activeTab === 'known_errors' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {knownErrors.map((ke) => (
              <div key={ke.id} className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-lg space-y-2.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-cyan-400">{ke.error_code}</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold">VERIFIED FIX</span>
                </div>
                <h3 className="font-bold text-slate-100 text-sm">{ke.title}</h3>
                <div className="text-slate-400">{ke.description}</div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] font-bold text-amber-400">Immediate Workaround:</div>
                  <div className="text-slate-300">{ke.workaround}</div>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] font-bold text-emerald-400">Permanent Solution:</div>
                  <div className="text-slate-300">{ke.permanent_solution}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create Incident Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl p-6">
            <h2 className="text-base font-bold text-white mb-4 flex items-center space-x-2">
              <Flame className="w-4 h-4 text-rose-500" />
              <span>Declare Production IT Incident</span>
            </h2>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-300 mb-1">Incident Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Europe VPN Concentrator cluster failover degradation"
                  value={createForm.title}
                  onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Incident Scope & Symptoms</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Describe impact, affected employees, and error codes observed..."
                  value={createForm.description}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Affected IT Service</label>
                  <select
                    value={createForm.affected_service}
                    onChange={(e) => setCreateForm({ ...createForm, affected_service: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  >
                    <option value="Global VPN Gateway">Global VPN Gateway</option>
                    <option value="Okta Identity & SSO">Okta Identity & SSO</option>
                    <option value="SAP S/4HANA ERP">SAP S/4HANA ERP</option>
                    <option value="Exchange Online & Outlook">Exchange Online & Outlook</option>
                    <option value="Core Network Infrastructure">Core Network Infrastructure</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Severity</label>
                  <select
                    value={createForm.severity}
                    onChange={(e) => setCreateForm({ ...createForm, severity: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  >
                    <option value="SEV1_CRITICAL">SEV1 - Critical Outage</option>
                    <option value="SEV2_HIGH">SEV2 - High Impact</option>
                    <option value="SEV3_MEDIUM">SEV3 - Moderate Degrade</option>
                    <option value="SEV4_LOW">SEV4 - Low Disruption</option>
                  </select>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-500/40 flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="major"
                  checked={createForm.is_major}
                  onChange={(e) => setCreateForm({ ...createForm, is_major: e.target.checked })}
                  className="w-4 h-4 rounded text-rose-600 bg-slate-900 border-slate-700 focus:ring-0"
                />
                <label htmlFor="major" className="text-xs font-bold text-rose-300 cursor-pointer">
                  Classify as Major Incident (Notifies IT Manager & Opens Bridge)
                </label>
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold"
                >
                  Declare Incident
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
