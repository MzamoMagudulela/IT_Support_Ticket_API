import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import {
  GitPullRequest, Plus, CheckCircle, XCircle, Clock,
  AlertTriangle, ShieldCheck, FileText, ChevronRight
} from 'lucide-react';

const RISK_BADGES = {
  CRITICAL: 'bg-rose-950/80 text-rose-300 border-rose-500/40',
  HIGH: 'bg-orange-950/80 text-orange-300 border-orange-500/40',
  MEDIUM: 'bg-amber-950/80 text-amber-300 border-amber-500/40',
  LOW: 'bg-sky-950/80 text-sky-300 border-sky-500/40',
};

const STATUS_BADGES = {
  DRAFT: 'bg-slate-800 text-slate-300 border-slate-700',
  SUBMITTED_FOR_APPROVAL: 'bg-amber-950/80 text-amber-300 border-amber-500/40',
  APPROVED: 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40',
  REJECTED: 'bg-rose-950/80 text-rose-300 border-rose-500/40',
  SCHEDULED: 'bg-blue-950/80 text-blue-300 border-blue-500/40',
  COMPLETED: 'bg-purple-950/80 text-purple-300 border-purple-500/40',
  ROLLED_BACK: 'bg-rose-900/60 text-rose-200 border-rose-700',
};

export const ChangesPage = () => {
  const { user, primaryRole } = useAuth();
  const { addToast } = useNotification();

  const [changes, setChanges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedChange, setSelectedChange] = useState(null);

  // Approval Modal
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [approvalDecision, setApprovalDecision] = useState('APPROVED');
  const [approvalNotes, setApprovalNotes] = useState('');

  // Create Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: '',
    description: '',
    change_type: 'NORMAL',
    business_justification: '',
    affected_systems: '',
    risk_level: 'MEDIUM',
    risk_assessment: '',
    implementation_plan: '',
    test_procedure: '',
    rollback_plan: '',
  });

  const isManagerOrAdmin = ['admin', 'system administrator', 'it_manager', 'it operations manager'].some(
    (r) => primaryRole.toLowerCase().includes(r)
  );

  const fetchChanges = async () => {
    setLoading(true);
    try {
      const res = await api.get('/changes');
      setChanges(res.data);
      if (res.data.length > 0 && !selectedChange) {
        setSelectedChange(res.data[0]);
      }
    } catch (e) {
      console.error(e);
      addToast('Failed to load change requests', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChanges();
  }, []);

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/changes', createForm);
      addToast(`Change Request ${res.data.change_number} submitted!`, 'success');
      setShowCreateModal(false);
      setCreateForm({
        title: '',
        description: '',
        change_type: 'NORMAL',
        business_justification: '',
        affected_systems: '',
        risk_level: 'MEDIUM',
        risk_assessment: '',
        implementation_plan: '',
        test_procedure: '',
        rollback_plan: '',
      });
      fetchChanges();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to submit change', 'error');
    }
  };

  const handleApprovalSubmit = async (e) => {
    e.preventDefault();
    if (!selectedChange) return;
    try {
      await api.post(`/changes/${selectedChange.id}/approval`, {
        decision: approvalDecision,
        comments: approvalNotes
      });
      addToast(`Change request ${approvalDecision.toLowerCase()}!`, 'success');
      setShowApprovalModal(false);
      fetchChanges();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Approval decision failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">IT Change Advisory Board (CAB) & Release Management</h1>
          <p className="text-xs text-slate-400 mt-0.5">Formal RFC change requests, risk assessment matrices, and rollback plans</p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 font-semibold text-xs text-white shadow-lg shadow-brand-500/25 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Submit RFC Request</span>
        </button>
      </div>

      {/* Main Grid: List (5 cols) & Detail (7 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Change List */}
        <div className="lg:col-span-5 space-y-2.5 max-h-[780px] overflow-y-auto pr-1">
          {changes.map((c) => (
            <div
              key={c.id}
              onClick={() => setSelectedChange(c)}
              className={`p-4 rounded-xl border text-xs cursor-pointer transition-all ${
                selectedChange?.id === c.id
                  ? 'bg-slate-900 border-brand-500 shadow-lg glow-brand'
                  : 'bg-slate-900/60 border-slate-800 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-mono font-bold text-brand-400">{c.change_number}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${STATUS_BADGES[c.status] || STATUS_BADGES.DRAFT}`}>
                  {c.status.replace(/_/g, ' ')}
                </span>
              </div>
              <div className="font-semibold text-slate-100 line-clamp-1">{c.title}</div>
              <div className="text-slate-400 text-[11px] line-clamp-2 mt-1">{c.business_justification}</div>

              <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800 text-[11px]">
                <span className="text-slate-400">Type: <strong className="text-slate-200">{c.change_type}</strong></span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${RISK_BADGES[c.risk_level]}`}>
                  {c.risk_level} RISK
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Change Detail & CAB Decision */}
        <div className="lg:col-span-7">
          {selectedChange ? (
            <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6 text-xs">
              {/* Header */}
              <div className="flex items-start justify-between pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-sm font-bold text-brand-400">{selectedChange.change_number}</span>
                    <span className="text-slate-500">•</span>
                    <span className="text-slate-400 font-semibold">{selectedChange.change_type} CHANGE</span>
                  </div>
                  <h2 className="text-base font-bold text-white mt-1">{selectedChange.title}</h2>
                  <div className="text-slate-400 mt-1">
                    Requester: {selectedChange.requester_name || 'Support Staff'} • Created: {new Date(selectedChange.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div className="flex flex-col items-end space-y-2">
                  <span className={`px-2.5 py-1 rounded text-xs font-bold border ${STATUS_BADGES[selectedChange.status]}`}>
                    {selectedChange.status.replace(/_/g, ' ')}
                  </span>
                  {isManagerOrAdmin && selectedChange.status === 'SUBMITTED_FOR_APPROVAL' && (
                    <button
                      onClick={() => setShowApprovalModal(true)}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold shadow-md shadow-emerald-500/20"
                    >
                      Review & Decide CAB
                    </button>
                  )}
                </div>
              </div>

              {/* Justification & Scope */}
              <div className="space-y-3">
                <div>
                  <div className="font-bold text-slate-300 uppercase tracking-wider text-[11px] mb-1">Business Justification</div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 leading-relaxed">
                    {selectedChange.business_justification}
                  </div>
                </div>

                <div>
                  <div className="font-bold text-slate-300 uppercase tracking-wider text-[11px] mb-1">Affected Systems & Configuration Items</div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-slate-300">
                    {selectedChange.affected_systems}
                  </div>
                </div>
              </div>

              {/* Implementation, Testing & Rollback Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="font-bold text-brand-300 text-[11px]">Implementation Procedure:</div>
                  <p className="text-slate-300 whitespace-pre-wrap">{selectedChange.implementation_plan}</p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="font-bold text-amber-300 text-[11px]">Verification / Test Procedure:</div>
                  <p className="text-slate-300 whitespace-pre-wrap">{selectedChange.test_procedure}</p>
                </div>
              </div>

              {/* Rollback Plan */}
              <div className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-500/30 space-y-1">
                <div className="font-bold text-rose-300 text-[11px] flex items-center space-x-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                  <span>Contingency & Rollback Plan:</span>
                </div>
                <p className="text-slate-300 whitespace-pre-wrap">{selectedChange.rollback_plan}</p>
              </div>

              {/* Approval Outcome if Decided */}
              {selectedChange.approved_by_name && (
                <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/30 space-y-1">
                  <div className="font-bold text-emerald-300 text-[11px] flex items-center space-x-1.5">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                    <span>CAB Decision Record</span>
                  </div>
                  <div className="text-slate-300 text-[11px]">
                    Decided by <strong>{selectedChange.approved_by_name}</strong> on {selectedChange.approval_decision_at ? new Date(selectedChange.approval_decision_at).toLocaleString() : 'N/A'}.
                  </div>
                  {selectedChange.approval_notes && (
                    <div className="text-slate-400 italic mt-0.5">Notes: {selectedChange.approval_notes}</div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500">Select a change request to view CAB details</div>
          )}
        </div>
      </div>

      {/* CAB Decision Modal */}
      {showApprovalModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md shadow-2xl p-6">
            <h3 className="text-base font-bold text-white mb-2 flex items-center space-x-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span>Change Advisory Board Decision</span>
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Authorize or reject implementation for RFC <strong className="text-brand-300 font-mono">{selectedChange?.change_number}</strong>.
            </p>

            <form onSubmit={handleApprovalSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setApprovalDecision('APPROVED')}
                  className={`p-3 rounded-xl border text-center font-bold transition-all ${
                    approvalDecision === 'APPROVED'
                      ? 'bg-emerald-600 text-white border-emerald-500 shadow-lg shadow-emerald-500/20'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  APPROVE CHANGE
                </button>
                <button
                  type="button"
                  onClick={() => setApprovalDecision('REJECTED')}
                  className={`p-3 rounded-xl border text-center font-bold transition-all ${
                    approvalDecision === 'REJECTED'
                      ? 'bg-rose-600 text-white border-rose-500 shadow-lg shadow-rose-500/20'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  REJECT CHANGE
                </button>
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Approval Condition / Decision Notes</label>
                <textarea
                  rows={3}
                  required
                  placeholder="e.g. Approved following review of secondary HA failover telemetry. Ensure network engineer standby on bridges."
                  value={approvalNotes}
                  onChange={(e) => setApprovalNotes(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowApprovalModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold"
                >
                  Record CAB Decision
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create RFC Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-xl shadow-2xl p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-base font-bold text-white mb-4 flex items-center space-x-2">
              <GitPullRequest className="w-5 h-5 text-brand-400" />
              <span>Submit Request For Change (RFC)</span>
            </h2>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-300 mb-1">Change Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Upgrade Core Firewall Firmware to PAN-OS 11.1.2-h3"
                  value={createForm.title}
                  onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Change Category</label>
                  <select
                    value={createForm.change_type}
                    onChange={(e) => setCreateForm({ ...createForm, change_type: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  >
                    <option value="STANDARD">Standard (Pre-approved)</option>
                    <option value="NORMAL">Normal (CAB Review Required)</option>
                    <option value="EMERGENCY">Emergency (Expedited Outage Fix)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Risk Classification</label>
                  <select
                    value={createForm.risk_level}
                    onChange={(e) => setCreateForm({ ...createForm, risk_level: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Business Justification</label>
                <textarea
                  rows={2}
                  required
                  placeholder="Explain why this change is necessary and the risk of not executing it..."
                  value={createForm.business_justification}
                  onChange={(e) => setCreateForm({ ...createForm, business_justification: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-100"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Affected Systems & Infrastructure</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Perimeter Palo Alto 5220 HA Pair"
                  value={createForm.affected_systems}
                  onChange={(e) => setCreateForm({ ...createForm, affected_systems: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-100 font-mono"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Implementation Step-by-Step Plan</label>
                <textarea
                  rows={2}
                  required
                  placeholder="1. Verify secondary HA sync. 2. Install patch on secondary..."
                  value={createForm.implementation_plan}
                  onChange={(e) => setCreateForm({ ...createForm, implementation_plan: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-100"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Verification / Post-Deployment Test Procedure</label>
                <textarea
                  rows={2}
                  required
                  placeholder="Run synthetic ping probes and TCP health checks against DMZ..."
                  value={createForm.test_procedure}
                  onChange={(e) => setCreateForm({ ...createForm, test_procedure: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-100"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Contingency Rollback Plan</label>
                <textarea
                  rows={2}
                  required
                  placeholder="Reboot to previous partition (PAN-OS 11.0.4) within 5 minutes..."
                  value={createForm.rollback_plan}
                  onChange={(e) => setCreateForm({ ...createForm, rollback_plan: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-100"
                />
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
                  className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold"
                >
                  Submit for CAB Approval
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
