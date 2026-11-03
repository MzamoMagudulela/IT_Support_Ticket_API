import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import {
  Ticket, ArrowLeft, Clock, User, Shield, AlertTriangle,
  Send, Lock, Paperclip, CheckCircle2, RotateCcw, ArrowUpRight,
  Link as LinkIcon, GitMerge
} from 'lucide-react';

export const TicketDetailPage = () => {
  const { ticketId } = useParams();
  const navigate = useNavigate();
  const { user, primaryRole } = useAuth();
  const { addToast } = useNotification();

  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [commentText, setCommentText] = useState('');
  const [commentType, setCommentType] = useState('PUBLIC');
  const [technicians, setTechnicians] = useState([]);

  // Modals
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedTechId, setSelectedTechId] = useState('');
  const [assignReason, setAssignReason] = useState('');

  const [showStatusModal, setShowStatusModal] = useState(false);
  const [newStatus, setNewStatus] = useState('IN_PROGRESS');
  const [statusComment, setStatusComment] = useState('');
  const [resolutionDetails, setResolutionDetails] = useState('');

  const [showReopenModal, setShowReopenModal] = useState(false);
  const [reopenReason, setReopenReason] = useState('');

  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const [escalateReason, setEscalateReason] = useState('');

  const isPrivileged = ['admin', 'system administrator', 'it_manager', 'it operations manager', 'technician', 'it support technician'].some(
    (r) => primaryRole.toLowerCase().includes(r)
  );

  const fetchTicket = async () => {
    try {
      const res = await api.get(`/tickets/${ticketId}`);
      setTicket(res.data);
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to load ticket', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchTechnicians = async () => {
    try {
      const res = await api.get('/users?role=technician');
      setTechnicians(res.data);
    } catch (e) {}
  };

  useEffect(() => {
    fetchTicket();
    if (isPrivileged) fetchTechnicians();
  }, [ticketId]);

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    try {
      await api.post(`/tickets/${ticketId}/comments`, {
        content: commentText,
        comment_type: commentType
      });
      setCommentText('');
      addToast('Comment added', 'success');
      fetchTicket();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to post comment', 'error');
    }
  };

  const handleAssignSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/tickets/${ticketId}/assign`, {
        technician_id: Number(selectedTechId),
        reason: assignReason || 'Assigned via Service Desk'
      });
      addToast('Technician assigned successfully', 'success');
      setShowAssignModal(false);
      fetchTicket();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Assignment failed', 'error');
    }
  };

  const handleStatusSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/tickets/${ticketId}/status`, {
        new_status: newStatus,
        comment: statusComment,
        resolution_details: resolutionDetails
      });
      addToast(`Status updated to ${newStatus}`, 'success');
      setShowStatusModal(false);
      fetchTicket();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Status update failed', 'error');
    }
  };

  const handleReopenSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/tickets/${ticketId}/reopen`, { reason: reopenReason });
      addToast('Ticket reopened', 'success');
      setShowReopenModal(false);
      fetchTicket();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Reopen failed', 'error');
    }
  };

  const handleEscalateSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/tickets/${ticketId}/escalate`, { reason: escalateReason });
      addToast('Ticket escalated to Level ' + (ticket.escalation_level + 1), 'warning');
      setShowEscalateModal(false);
      fetchTicket();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Escalation failed', 'error');
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post(`/tickets/${ticketId}/attachments`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      addToast('Attachment uploaded successfully', 'success');
      fetchTicket();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Upload failed', 'error');
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400 text-sm">Loading ticket details...</div>;
  }

  if (!ticket) {
    return (
      <div className="p-8 text-center">
        <h2 className="text-base font-bold text-slate-200">Ticket Not Found</h2>
        <button onClick={() => navigate('/tickets')} className="mt-4 px-4 py-2 rounded-lg bg-slate-800 text-xs">
          Return to Service Desk
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Back button & Action buttons */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <button
          onClick={() => navigate('/tickets')}
          className="flex items-center space-x-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Ticket Register</span>
        </button>

        <div className="flex items-center space-x-2 flex-wrap">
          {/* Status Changer */}
          <button
            onClick={() => setShowStatusModal(true)}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700"
          >
            Change Status ({ticket.status})
          </button>

          {/* Assign Tech */}
          {isPrivileged && (
            <button
              onClick={() => setShowAssignModal(true)}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700"
            >
              Assign Technician
            </button>
          )}

          {/* Reopen if Resolved */}
          {['RESOLVED', 'CLOSED'].includes(ticket.status) && (
            <button
              onClick={() => setShowReopenModal(true)}
              className="px-3 py-1.5 rounded-lg bg-amber-950/80 hover:bg-amber-900 border border-amber-600/50 text-amber-300 text-xs font-semibold flex items-center space-x-1"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reopen Ticket</span>
            </button>
          )}

          {/* Escalate */}
          {isPrivileged && (
            <button
              onClick={() => setShowEscalateModal(true)}
              className="px-3 py-1.5 rounded-lg bg-rose-950/80 hover:bg-rose-900 border border-rose-600/50 text-rose-300 text-xs font-semibold flex items-center space-x-1"
            >
              <ArrowUpRight className="w-3.5 h-3.5" />
              <span>Escalate Ticket</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 cols): Details & Comments Timeline */}
        <div className="lg:col-span-2 space-y-6">
          {/* Subject & Description Card */}
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <span className="font-mono text-sm font-bold text-brand-400">{ticket.reference_number}</span>
                  <span className="text-slate-500">•</span>
                  <span className="text-xs text-slate-400">{ticket.category}</span>
                  {ticket.escalation_level > 0 && (
                    <span className="px-2 py-0.5 rounded bg-rose-900/60 border border-rose-500 text-rose-300 text-[10px] font-bold animate-pulse">
                      ESCALATION L{ticket.escalation_level}
                    </span>
                  )}
                </div>
                <h1 className="text-lg font-bold text-white tracking-tight">{ticket.subject}</h1>
              </div>

              <div className="flex flex-col items-end shrink-0">
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-800 border border-slate-700 text-slate-200">
                  {ticket.status}
                </span>
                <span className="text-[11px] text-slate-400 mt-1">Priority: <strong className="text-brand-300">{ticket.priority}</strong></span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-300 text-xs leading-relaxed whitespace-pre-wrap font-sans">
              {ticket.description}
            </div>

            {ticket.resolution_details && (
              <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-xs">
                <div className="font-bold text-emerald-300 flex items-center space-x-1.5 mb-1">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Resolution Summary</span>
                </div>
                <p className="text-slate-300 whitespace-pre-wrap">{ticket.resolution_details}</p>
              </div>
            )}
          </div>

          {/* Activity & Comment Timeline */}
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
            <h2 className="text-sm font-bold text-white tracking-tight flex items-center space-x-2">
              <Clock className="w-4 h-4 text-brand-400" />
              <span>Activity & Discussion Timeline</span>
            </h2>

            {/* Existing Comments */}
            <div className="space-y-4">
              {ticket.comments.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-4">No comments or activity logs yet.</p>
              ) : (
                ticket.comments.map((c) => (
                  <div
                    key={c.id}
                    className={`p-4 rounded-xl border text-xs space-y-1.5 ${
                      c.comment_type === 'INTERNAL_NOTE'
                        ? 'bg-amber-950/20 border-amber-600/40 text-amber-200'
                        : 'bg-slate-950/70 border-slate-800 text-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between font-semibold">
                      <div className="flex items-center space-x-2">
                        <span className="text-slate-200 font-bold">{c.author_name}</span>
                        {c.comment_type === 'INTERNAL_NOTE' && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center space-x-1">
                            <Lock className="w-2.5 h-2.5" />
                            <span>INTERNAL NOTE</span>
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-500">
                        {new Date(c.created_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <p className="leading-relaxed whitespace-pre-wrap text-slate-300 text-xs">{c.content}</p>
                  </div>
                ))
              )}
            </div>

            {/* Post New Comment Box */}
            <form onSubmit={handleAddComment} className="pt-4 border-t border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300">Add Entry</span>
                {isPrivileged && (
                  <div className="flex items-center space-x-3 text-xs">
                    <label className="flex items-center space-x-1.5 cursor-pointer text-slate-300">
                      <input
                        type="radio"
                        name="ctype"
                        value="PUBLIC"
                        checked={commentType === 'PUBLIC'}
                        onChange={() => setCommentType('PUBLIC')}
                      />
                      <span>Public Reply</span>
                    </label>
                    <label className="flex items-center space-x-1.5 cursor-pointer text-amber-400 font-semibold">
                      <input
                        type="radio"
                        name="ctype"
                        value="INTERNAL_NOTE"
                        checked={commentType === 'INTERNAL_NOTE'}
                        onChange={() => setCommentType('INTERNAL_NOTE')}
                      />
                      <span>Internal Tech Note</span>
                    </label>
                  </div>
                )}
              </div>

              <textarea
                rows={3}
                required
                placeholder={commentType === 'INTERNAL_NOTE' ? 'Record internal troubleshooting steps, radius logs, or diagnostic traces...' : 'Write an update to the user...'}
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                className={`w-full border rounded-xl p-3 text-xs placeholder-slate-500 focus:outline-none ${
                  commentType === 'INTERNAL_NOTE'
                    ? 'bg-amber-950/10 border-amber-500/40 text-amber-100 focus:border-amber-400'
                    : 'bg-slate-950 border-slate-700 text-slate-100 focus:border-brand-500'
                }`}
              />

              <div className="flex justify-between items-center">
                <label className="cursor-pointer text-xs font-semibold text-slate-400 hover:text-slate-200 flex items-center space-x-1.5">
                  <Paperclip className="w-3.5 h-3.5" />
                  <span>Attach Evidence / Log File</span>
                  <input type="file" onChange={handleFileUpload} className="hidden" />
                </label>

                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs flex items-center space-x-1.5 shadow-md shadow-brand-500/20"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Post Entry</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Right Column (1 col): Metadata, SLA Tracking, Attachments, History */}
        <div className="space-y-6">
          {/* Metadata Card */}
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4 text-xs">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Ticket Attributes</h3>
            
            <div className="space-y-3">
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Requester:</span>
                <span className="font-semibold text-slate-200">{ticket.requester_name}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Assigned Tech:</span>
                <span className="font-semibold text-brand-300">{ticket.technician_name || 'Unassigned'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Department:</span>
                <span className="font-semibold text-slate-200">{ticket.department_name || 'Engineering'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Related Asset:</span>
                <span className="font-semibold text-slate-200">{ticket.related_asset_tag || 'None'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Impact / Urgency:</span>
                <span className="font-semibold text-slate-200">{ticket.impact} / {ticket.urgency}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Submitted:</span>
                <span className="text-slate-300">{new Date(ticket.created_at).toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* SLA Tracking Countdown */}
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-3 text-xs">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
              <Clock className="w-3.5 h-3.5 text-brand-400" />
              <span>SLA Performance Clocks</span>
            </h3>

            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
              <div className="flex justify-between text-[11px]">
                <span className="text-slate-400">First Response Target:</span>
                <span className="font-bold text-slate-200">
                  {ticket.first_responded_at ? 'Met (Recorded)' : ticket.response_deadline ? new Date(ticket.response_deadline).toLocaleTimeString() : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between text-[11px]">
                <span className="text-slate-400">Resolution Deadline:</span>
                <span className="font-bold text-amber-400">
                  {ticket.resolution_deadline ? new Date(ticket.resolution_deadline).toLocaleString() : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Attachments Card */}
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-3 text-xs">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Attachments ({ticket.attachments.length})</h3>
            </div>
            {ticket.attachments.length === 0 ? (
              <p className="text-[11px] text-slate-500 py-2">No files attached to this ticket.</p>
            ) : (
              <div className="space-y-2">
                {ticket.attachments.map((a) => (
                  <div key={a.id} className="p-2 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between text-[11px]">
                    <div className="truncate max-w-[180px] font-medium text-slate-300">{a.file_name}</div>
                    <span className="text-[10px] text-slate-500">{Math.round(a.file_size_bytes / 1024)} KB</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Assign Modal */}
      {showAssignModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md shadow-2xl p-6">
            <h3 className="text-base font-bold text-white mb-4">Assign Support Technician</h3>
            <form onSubmit={handleAssignSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-300 mb-1">Select Technician</label>
                <select
                  required
                  value={selectedTechId}
                  onChange={(e) => setSelectedTechId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200"
                >
                  <option value="">Choose technician...</option>
                  {technicians.map((tech) => (
                    <option key={tech.id} value={tech.id}>
                      {tech.full_name} ({tech.username})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Reason / Instructions</label>
                <input
                  type="text"
                  placeholder="e.g. Assigned for diagnostic packet capture"
                  value={assignReason}
                  onChange={(e) => setAssignReason(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAssignModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold"
                >
                  Assign Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Status Modal */}
      {showStatusModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md shadow-2xl p-6">
            <h3 className="text-base font-bold text-white mb-4">Update Ticket Status</h3>
            <form onSubmit={handleStatusSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-300 mb-1">New Status</label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200"
                >
                  <option value="NEW">NEW</option>
                  <option value="ASSIGNED">ASSIGNED</option>
                  <option value="IN_PROGRESS">IN PROGRESS</option>
                  <option value="PENDING_USER">PENDING USER (Pauses SLA)</option>
                  <option value="RESOLVED">RESOLVED</option>
                  <option value="CLOSED">CLOSED</option>
                  <option value="CANCELLED">CANCELLED</option>
                </select>
              </div>

              {newStatus === 'RESOLVED' && (
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Resolution Summary Details</label>
                  <textarea
                    rows={3}
                    required
                    placeholder="Describe exact root cause and solution implemented..."
                    value={resolutionDetails}
                    onChange={(e) => setResolutionDetails(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-100"
                  />
                </div>
              )}

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Transition Note</label>
                <input
                  type="text"
                  placeholder="Optional status transition remark"
                  value={statusComment}
                  onChange={(e) => setStatusComment(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-100"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowStatusModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold"
                >
                  Confirm Transition
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Reopen Modal */}
      {showReopenModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md shadow-2xl p-6">
            <h3 className="text-base font-bold text-white mb-3">Reopen Ticket</h3>
            <p className="text-xs text-slate-400 mb-4">Please state why the issue requires reopening and further technician investigation.</p>
            <form onSubmit={handleReopenSubmit} className="space-y-4 text-xs">
              <div>
                <textarea
                  rows={3}
                  required
                  placeholder="Issue reappeared after router reboot..."
                  value={reopenReason}
                  onChange={(e) => setReopenReason(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-100"
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowReopenModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-semibold"
                >
                  Reopen Issue
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Escalate Modal */}
      {showEscalateModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md shadow-2xl p-6">
            <h3 className="text-base font-bold text-white mb-3 text-rose-400">Escalate Service Ticket</h3>
            <p className="text-xs text-slate-400 mb-4">Escalating elevates priority to CRITICAL and notifies leadership.</p>
            <form onSubmit={handleEscalateSubmit} className="space-y-4 text-xs">
              <div>
                <textarea
                  rows={3}
                  required
                  placeholder="Breach of business continuity or blocking customer transactions..."
                  value={escalateReason}
                  onChange={(e) => setEscalateReason(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-100"
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowEscalateModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold"
                >
                  Confirm Escalation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
