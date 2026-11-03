import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import {
  ShieldAlert, ShieldCheck, AlertOctagon, Terminal,
  Plus, Eye, FileCode, CheckCircle2, Lock, Clock
} from 'lucide-react';

const SEV_BADGES = {
  CRITICAL: 'bg-rose-950/80 text-rose-300 border-rose-500/50',
  HIGH: 'bg-orange-950/80 text-orange-300 border-orange-500/50',
  MEDIUM: 'bg-amber-950/80 text-amber-300 border-amber-500/50',
  LOW: 'bg-sky-950/80 text-sky-300 border-sky-500/50',
};

export const SecurityPage = () => {
  const { user, primaryRole } = useAuth();
  const { addToast } = useNotification();

  const [dashboard, setDashboard] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [loading, setLoading] = useState(true);

  // New Security Incident Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: '',
    description: '',
    category: 'PHISHING',
    severity: 'MEDIUM'
  });

  // Triage Update Form
  const [triageForm, setTriageForm] = useState({
    status: 'INVESTIGATING',
    containment_actions: '',
    resolution_details: ''
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [dashRes, incRes] = await Promise.all([
        api.get('/security/dashboard'),
        api.get('/security/incidents')
      ]);
      setDashboard(dashRes.data);
      setIncidents(incRes.data);
      if (incRes.data.length > 0 && !selectedIncident) {
        setSelectedIncident(incRes.data[0]);
        setTriageForm({
          status: incRes.data[0].status || 'INVESTIGATING',
          containment_actions: incRes.data[0].containment_actions || '',
          resolution_details: incRes.data[0].resolution_details || ''
        });
      }
    } catch (e) {
      console.error(e);
      addToast('Failed to load cybersecurity data', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSelectIncident = (s) => {
    setSelectedIncident(s);
    setTriageForm({
      status: s.status || 'INVESTIGATING',
      containment_actions: s.containment_actions || '',
      resolution_details: s.resolution_details || ''
    });
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/security/incidents', createForm);
      addToast(`Security Incident ${res.data.incident_number} created!`, 'success');
      setShowCreateModal(false);
      setCreateForm({ title: '', description: '', category: 'PHISHING', severity: 'MEDIUM' });
      fetchData();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to report security incident', 'error');
    }
  };

  const handleTriageSubmit = async (e) => {
    e.preventDefault();
    if (!selectedIncident) return;
    try {
      await api.patch(`/security/incidents/${selectedIncident.id}`, triageForm);
      addToast('Security incident containment record updated!', 'success');
      fetchData();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Triage update failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Cybersecurity Operations Center (SecOps)</h1>
          <p className="text-xs text-slate-400 mt-0.5">Threat hunting, phishing triage, SIEM event intelligence & IOC containment</p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 font-semibold text-xs text-white shadow-lg shadow-rose-600/25 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Report Security Incident</span>
        </button>
      </div>

      {/* Security KPI Stats Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Total Security Incidents</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-black text-white">{dashboard?.total_security_incidents ?? 0}</div>
          <div className="text-[11px] text-slate-400 mt-1">Logged across enterprise boundary</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Critical Threat Alerts</span>
            <AlertOctagon className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-black text-rose-400">{dashboard?.critical_alerts ?? 0}</div>
          <div className="text-[11px] text-slate-400 mt-1">Requiring immediate containment</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Under Investigation</span>
            <Terminal className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400">{dashboard?.under_investigation ?? 0}</div>
          <div className="text-[11px] text-slate-400 mt-1">Active analyst triages</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Contained & Resolved</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400">{dashboard?.resolved_incidents ?? 0}</div>
          <div className="text-[11px] text-slate-400 mt-1">Closed without data exposure</div>
        </div>
      </div>

      {/* Main Grid: Incident List (5 cols) & Investigation/Evidence (7 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Incident List */}
        <div className="lg:col-span-5 space-y-2.5 max-h-[750px] overflow-y-auto pr-1">
          {incidents.map((s) => (
            <div
              key={s.id}
              onClick={() => handleSelectIncident(s)}
              className={`p-4 rounded-xl border text-xs cursor-pointer transition-all ${
                selectedIncident?.id === s.id
                  ? 'bg-slate-900 border-rose-500/80 shadow-lg glow-brand'
                  : 'bg-slate-900/60 border-slate-800 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-mono font-bold text-rose-400">{s.incident_number}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${SEV_BADGES[s.severity]}`}>
                  {s.severity}
                </span>
              </div>
              <div className="font-semibold text-slate-100 line-clamp-1">{s.title}</div>
              <div className="text-slate-400 text-[11px] line-clamp-2 mt-1">{s.description}</div>
              <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800 text-[11px]">
                <span className="text-slate-400">Category: <strong className="text-slate-200">{s.category}</strong></span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-bold">
                  {s.status}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Investigation & IOC Evidence Workspace */}
        <div className="lg:col-span-7">
          {selectedIncident ? (
            <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6 text-xs">
              {/* Incident Header */}
              <div className="flex items-start justify-between pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-sm font-bold text-rose-400">{selectedIncident.incident_number}</span>
                    <span className="text-slate-500">•</span>
                    <span className="text-slate-300 font-semibold">{selectedIncident.category}</span>
                  </div>
                  <h2 className="text-base font-bold text-white mt-1">{selectedIncident.title}</h2>
                  <div className="text-slate-400 mt-1">
                    Reporter: {selectedIncident.reporter_name || 'Corporate Employee'} • Analyst: {selectedIncident.analyst_name || 'Elena Vance'}
                  </div>
                </div>
                <span className={`px-2.5 py-1 rounded text-xs font-bold border ${SEV_BADGES[selectedIncident.severity]}`}>
                  {selectedIncident.severity}
                </span>
              </div>

              {/* Description Scope */}
              <div>
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Threat Synopsis</h3>
                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {selectedIncident.description}
                </div>
              </div>

              {/* IOC & Evidence Artifacts */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                  <FileCode className="w-3.5 h-3.5 text-brand-400" />
                  <span>Indicators of Compromise (IOC) & Forensics Evidence</span>
                </h3>
                {selectedIncident.evidence_items?.length === 0 ? (
                  <p className="text-slate-500 text-[11px] py-1">No forensic evidence files attached.</p>
                ) : (
                  <div className="space-y-2">
                    {selectedIncident.evidence_items?.map((ev) => (
                      <div key={ev.id} className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                        <div className="flex justify-between items-center font-bold text-slate-200">
                          <span>{ev.evidence_type}</span>
                          <span className="text-slate-500 text-[10px]">{new Date(ev.created_at).toLocaleTimeString()}</span>
                        </div>
                        <div className="text-slate-400 text-[11px]">{ev.description}</div>
                        {ev.hash_sha256 && (
                          <div className="text-[10px] text-brand-400 font-mono truncate">
                            SHA-256: {ev.hash_sha256}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Containment & Response Form */}
              <form onSubmit={handleTriageSubmit} className="space-y-4 pt-4 border-t border-slate-800">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                  <Lock className="w-3.5 h-3.5 text-rose-400" />
                  <span>Containment & Remediation Actions</span>
                </h3>

                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Immediate Containment Protocol</label>
                  <textarea
                    rows={2}
                    placeholder="e.g. Purged 14 malicious emails across Exchange mailboxes via Graph API. Blocked sender domain 'corp-exec-urgent.com' at edge gateway..."
                    value={triageForm.containment_actions}
                    onChange={(e) => setTriageForm({ ...triageForm, containment_actions: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Resolution & Hardening Notes</label>
                  <textarea
                    rows={2}
                    placeholder="Permanent mitigation, user credential revocation, or SPF/DKIM policy adjustments..."
                    value={triageForm.resolution_details}
                    onChange={(e) => setTriageForm({ ...triageForm, resolution_details: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100"
                  />
                </div>

                <div className="flex items-center justify-between pt-1">
                  <div className="flex items-center space-x-2 text-xs">
                    <span className="font-semibold text-slate-400">Threat Status:</span>
                    <select
                      value={triageForm.status}
                      onChange={(e) => setTriageForm({ ...triageForm, status: e.target.value })}
                      className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-slate-200 font-bold"
                    >
                      <option value="NEW">NEW</option>
                      <option value="INVESTIGATING">INVESTIGATING</option>
                      <option value="CONTAINED">CONTAINED</option>
                      <option value="RESOLVED">RESOLVED</option>
                      <option value="FALSE_POSITIVE">FALSE POSITIVE</option>
                    </select>
                  </div>

                  <button
                    type="submit"
                    className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold shadow-md shadow-rose-600/20"
                  >
                    Commit SecOps Actions
                  </button>
                </div>
              </form>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500">Select an incident to view SecOps triage</div>
          )}
        </div>
      </div>

      {/* Report Security Incident Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl p-6">
            <h2 className="text-base font-bold text-white mb-4 flex items-center space-x-2">
              <ShieldAlert className="w-5 h-5 text-rose-500" />
              <span>Report Cybersecurity Threat or Incident</span>
            </h2>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-300 mb-1">Threat Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Executive Impersonation Phishing Campaign targeting Finance Dept"
                  value={createForm.title}
                  onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Observed Activity & Details</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Include sender emails, IP addresses, suspicious files, or abnormal login prompts..."
                  value={createForm.description}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Category</label>
                  <select
                    value={createForm.category}
                    onChange={(e) => setCreateForm({ ...createForm, category: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  >
                    <option value="PHISHING">Phishing Attempt</option>
                    <option value="MALWARE">Malware Report</option>
                    <option value="SUSPICIOUS_LOGIN">Suspicious Login</option>
                    <option value="UNAUTHORIZED_ACCESS">Unauthorized Access</option>
                    <option value="DATA_EXPOSURE">Data Exposure</option>
                    <option value="COMPROMISED_ACCOUNT">Compromised Account</option>
                    <option value="NETWORK_INTRUSION">Network Intrusion</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Severity</label>
                  <select
                    value={createForm.severity}
                    onChange={(e) => setCreateForm({ ...createForm, severity: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                </div>
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
                  Report Incident
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
