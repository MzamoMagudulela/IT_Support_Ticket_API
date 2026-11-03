import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import { FileText, Shield, Search, Filter, Download, User, Clock, Terminal } from 'lucide-react';

export const AuditLogsPage = () => {
  const { user, primaryRole } = useAuth();
  const { addToast } = useNotification();

  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [entityFilter, setEntityFilter] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [selectedLog, setSelectedLog] = useState(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (entityFilter) params.append('entity_type', entityFilter);
      if (actionFilter) params.append('action', actionFilter);
      const res = await api.get(`/audit?${params.toString()}`);
      setLogs(res.data);
    } catch (e) {
      console.error(e);
      addToast('Failed to load compliance audit logs', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [entityFilter, actionFilter]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Enterprise Compliance & Security Audit Logs</h1>
          <p className="text-xs text-slate-400 mt-0.5">Immutable audit trail of access activities, change records, and administrative mutations</p>
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={entityFilter}
            onChange={(e) => setEntityFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200"
          >
            <option value="">All Entities</option>
            <option value="TICKET">Tickets</option>
            <option value="INCIDENT">Incidents</option>
            <option value="CHANGE">Changes</option>
            <option value="ASSET">Assets</option>
            <option value="USER">Users</option>
            <option value="SECURITY_INCIDENT">Security</option>
          </select>

          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200"
          >
            <option value="">All Actions</option>
            <option value="CREATE">CREATE</option>
            <option value="UPDATE">UPDATE</option>
            <option value="LOGIN_SUCCESS">LOGIN SUCCESS</option>
            <option value="ACCOUNT_LOCKED">ACCOUNT LOCKED</option>
            <option value="APPROVED">APPROVED</option>
            <option value="ESCALATE">ESCALATE</option>
            <option value="REASSIGN">REASSIGN</option>
          </select>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Entity Type & ID</th>
                <th className="py-3 px-4">Client IP</th>
                <th className="py-3 px-4">State Mutation Payload</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    Loading compliance records...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    No audit records found.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr
                    key={log.id}
                    onClick={() => setSelectedLog(log)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap text-[11px]">
                      {new Date(log.created_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span className="font-semibold text-slate-200">{log.username || 'System'}</span>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-slate-800 text-brand-300 border border-slate-700">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap font-mono text-slate-300">
                      {log.entity_type} #{log.entity_id || '-'}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap text-[11px]">
                      {log.ip_address || '127.0.0.1'}
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-400 max-w-sm truncate">
                      {log.new_values || log.old_values || '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Log Detail Inspector Modal */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl p-6 space-y-4 text-xs">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <Terminal className="w-4 h-4 text-brand-400" />
                <span>Audit Record Inspector</span>
              </h3>
              <button onClick={() => setSelectedLog(null)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Actor / Principal:</span>
                <span className="font-semibold text-slate-200">{selectedLog.username}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Action Performed:</span>
                <span className="font-bold text-brand-400">{selectedLog.action}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Target Resource:</span>
                <span className="text-slate-200 font-mono">{selectedLog.entity_type} #{selectedLog.entity_id}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Origin IP & User Agent:</span>
                <span className="text-slate-300 font-mono text-[11px] truncate max-w-xs">{selectedLog.ip_address} • {selectedLog.user_agent}</span>
              </div>
            </div>

            {selectedLog.old_values && (
              <div>
                <div className="font-bold text-slate-400 text-[11px] mb-1">Previous Values:</div>
                <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-amber-300 overflow-x-auto whitespace-pre-wrap">
                  {selectedLog.old_values}
                </pre>
              </div>
            )}

            {selectedLog.new_values && (
              <div>
                <div className="font-bold text-slate-400 text-[11px] mb-1">New Applied Values:</div>
                <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-emerald-300 overflow-x-auto whitespace-pre-wrap">
                  {selectedLog.new_values}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
