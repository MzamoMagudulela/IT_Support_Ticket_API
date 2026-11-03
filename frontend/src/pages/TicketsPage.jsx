import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import {
  Ticket, Plus, Search, Filter, AlertCircle, Clock,
  ChevronLeft, ChevronRight, User, Tag, CheckCircle
} from 'lucide-react';

const PRIORITY_BADGES = {
  CRITICAL: 'bg-rose-950/80 text-rose-300 border-rose-500/40',
  HIGH: 'bg-amber-950/80 text-amber-300 border-amber-500/40',
  MEDIUM: 'bg-sky-950/80 text-sky-300 border-sky-500/40',
  LOW: 'bg-slate-800 text-slate-300 border-slate-700',
};

const STATUS_BADGES = {
  NEW: 'bg-purple-950/80 text-purple-300 border-purple-500/30',
  ASSIGNED: 'bg-blue-950/80 text-blue-300 border-blue-500/30',
  IN_PROGRESS: 'bg-amber-950/80 text-amber-300 border-amber-500/30',
  PENDING_USER: 'bg-orange-950/80 text-orange-300 border-orange-500/30',
  RESOLVED: 'bg-emerald-950/80 text-emerald-300 border-emerald-500/30',
  CLOSED: 'bg-slate-800 text-slate-400 border-slate-700',
  CANCELLED: 'bg-slate-900 text-slate-500 border-slate-800',
};

export const TicketsPage = () => {
  const navigate = useNavigate();
  const { user, primaryRole } = useAuth();
  const { addToast } = useNotification();

  const [tickets, setTickets] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  // Create Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    subject: '',
    description: '',
    category: 'Software',
    impact: 'MEDIUM',
    urgency: 'MEDIUM',
  });

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '10',
      });
      if (search) params.append('search', search);
      if (statusFilter) params.append('status', statusFilter);
      if (priorityFilter) params.append('priority', priorityFilter);
      if (categoryFilter) params.append('category', categoryFilter);

      const res = await api.get(`/tickets?${params.toString()}`);
      setTickets(res.data.items);
      setTotal(res.data.total);
      setTotalPages(res.data.total_pages);
    } catch (e) {
      console.error(e);
      addToast('Failed to load tickets', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [page, statusFilter, priorityFilter, categoryFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchTickets();
  };

  // Preview calculated priority inside modal
  const previewPriority = () => {
    const { impact, urgency } = createForm;
    if (impact === 'CRITICAL' || (impact === 'HIGH' && urgency === 'CRITICAL') || (impact === 'CRITICAL' && urgency === 'HIGH')) {
      return 'CRITICAL';
    }
    if ((impact === 'HIGH' && urgency === 'HIGH') || (impact === 'MEDIUM' && urgency === 'CRITICAL') || (impact === 'HIGH' && urgency === 'MEDIUM')) {
      return 'HIGH';
    }
    if (impact === 'LOW' && urgency === 'LOW') {
      return 'LOW';
    }
    return 'MEDIUM';
  };

  const handleCreateTicket = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/tickets', createForm);
      addToast(`Ticket ${res.data.reference_number} created successfully!`, 'success');
      setShowCreateModal(false);
      setCreateForm({ subject: '', description: '', category: 'Software', impact: 'MEDIUM', urgency: 'MEDIUM' });
      fetchTickets();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to submit ticket', 'error');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Enterprise Service Desk</h1>
          <p className="text-xs text-slate-400 mt-0.5">Centralized IT operational request intake, assignment, and SLA tracking</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 font-semibold text-xs text-white shadow-lg shadow-brand-500/25 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>New IT Request</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search tickets by reference, subject, or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700/80 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </form>

        <div className="flex items-center space-x-2 w-full md:w-auto overflow-x-auto">
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="NEW">New</option>
            <option value="ASSIGNED">Assigned</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="PENDING_USER">Pending User</option>
            <option value="RESOLVED">Resolved</option>
            <option value="CLOSED">Closed</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => { setPriorityFilter(e.target.value); setPage(1); }}
            className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none"
          >
            <option value="">All Priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}
            className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none"
          >
            <option value="">All Categories</option>
            <option value="Hardware">Hardware</option>
            <option value="Software">Software</option>
            <option value="Network">Network</option>
            <option value="Security">Security</option>
          </select>
        </div>
      </div>

      {/* Ticket Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Ref #</th>
                <th className="py-3 px-4">Subject & Details</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Requester</th>
                <th className="py-3 px-4">Assigned Tech</th>
                <th className="py-3 px-4">SLA Deadline</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    Loading service records...
                  </td>
                </tr>
              ) : tickets.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    No tickets found matching the specified filters.
                  </td>
                </tr>
              ) : (
                tickets.map((t) => (
                  <tr
                    key={t.id}
                    onClick={() => navigate(`/tickets/${t.id}`)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-3.5 px-4 font-mono font-bold text-brand-400 whitespace-nowrap">
                      {t.reference_number}
                    </td>
                    <td className="py-3.5 px-4 max-w-md">
                      <div className="font-semibold text-slate-100 group-hover:text-brand-300 transition-colors line-clamp-1">
                        {t.subject}
                      </div>
                      <div className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                        {t.description}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[11px]">
                        {t.category}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${PRIORITY_BADGES[t.priority] || PRIORITY_BADGES.LOW}`}>
                        {t.priority}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${STATUS_BADGES[t.status] || STATUS_BADGES.NEW}`}>
                        {t.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 whitespace-nowrap">
                      {t.requester_name || 'Corporate Employee'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 whitespace-nowrap">
                      {t.technician_name ? (
                        <span className="text-slate-200">{t.technician_name}</span>
                      ) : (
                        <span className="text-slate-400 italic">Unassigned</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 whitespace-nowrap text-[11px]">
                      {t.resolution_deadline ? (
                        <span className="flex items-center space-x-1">
                          <Clock className="w-3 h-3 text-slate-500" />
                          <span>{new Date(t.resolution_deadline).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                        </span>
                      ) : (
                        <span>N/A</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-3 bg-slate-900 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>Showing {tickets.length} of {total} tickets</span>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              disabled={page <= 1}
              className="p-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-2 font-mono">Page {page} of {totalPages}</span>
            <button
              onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
              disabled={page >= totalPages}
              className="p-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* New Ticket Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl p-6 relative">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <h2 className="text-base font-bold text-white flex items-center space-x-2">
                <Ticket className="w-4 h-4 text-brand-400" />
                <span>Submit IT Support Request</span>
              </h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateTicket} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-300 mb-1">Subject</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Cannot connect to staging PostgreSQL cluster"
                  value={createForm.subject}
                  onChange={(e) => setCreateForm({ ...createForm, subject: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Detailed Description</label>
                <textarea
                  required
                  rows={4}
                  placeholder="Provide troubleshooting steps taken, exact error logs, or affected endpoints..."
                  value={createForm.description}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Category</label>
                  <select
                    value={createForm.category}
                    onChange={(e) => setCreateForm({ ...createForm, category: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  >
                    <option value="Hardware">Hardware</option>
                    <option value="Software">Software</option>
                    <option value="Network">Network</option>
                    <option value="Security">Security</option>
                    <option value="Access/Identity">Access/Identity</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Impact</label>
                  <select
                    value={createForm.impact}
                    onChange={(e) => setCreateForm({ ...createForm, impact: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  >
                    <option value="LOW">Low (Single user)</option>
                    <option value="MEDIUM">Medium (Dept)</option>
                    <option value="HIGH">High (Division)</option>
                    <option value="CRITICAL">Critical (Company)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Urgency</label>
                  <select
                    value={createForm.urgency}
                    onChange={(e) => setCreateForm({ ...createForm, urgency: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  >
                    <option value="LOW">Low (Routine)</option>
                    <option value="MEDIUM">Medium (Normal)</option>
                    <option value="HIGH">High (Urgent)</option>
                    <option value="CRITICAL">Critical (Immediate)</option>
                  </select>
                </div>
              </div>

              {/* Dynamic Matrix Priority Calculated Preview */}
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="text-[11px] text-slate-400">Calculated ITSM Matrix Priority:</div>
                  <div className="text-[10px] text-slate-400">Based on Impact ({createForm.impact}) & Urgency ({createForm.urgency})</div>
                </div>
                <span className={`px-2.5 py-1 rounded text-xs font-bold border ${PRIORITY_BADGES[previewPriority()]}`}>
                  {previewPriority()}
                </span>
              </div>

              <div className="flex justify-end space-x-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold shadow-lg shadow-brand-500/20"
                >
                  Create Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
