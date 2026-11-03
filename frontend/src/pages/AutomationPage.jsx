import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import {
  Zap, Play, Plus, CheckCircle, Clock,
  ArrowRight, Shield, Bell, AlertTriangle
} from 'lucide-react';

export const AutomationPage = () => {
  const { user, primaryRole } = useAuth();
  const { addToast } = useNotification();

  const [rules, setRules] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [rulesRes, logsRes] = await Promise.all([
        api.get('/automation/rules'),
        api.get('/automation/logs')
      ]);
      setRules(rulesRes.data);
      setLogs(logsRes.data);
    } catch (e) {
      console.error(e);
      addToast('Failed to load automation engine state', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTestRule = async (ruleId) => {
    try {
      const res = await api.post(`/automation/rules/${ruleId}/test`);
      addToast(res.data.message, 'success');
      fetchData();
    } catch (err) {
      addToast('Rule evaluation test failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">ITSM Workflow Automation Engine</h1>
          <p className="text-xs text-slate-400 mt-0.5">Declarative business process rules: TRIGGER → CONDITIONS → ACTIONS pipeline</p>
        </div>

        <div className="px-3 py-1.5 rounded-lg bg-brand-950 border border-brand-500/30 text-brand-300 font-mono text-xs font-semibold flex items-center space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-brand-400 animate-pulse"></span>
          <span>Celery & Redis Background Worker Active</span>
        </div>
      </div>

      {/* Rules Pipeline Cards */}
      <div className="space-y-4">
        <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Configured Declarative Rules</h2>
        <div className="grid grid-cols-1 gap-4">
          {rules.map((rule) => {
            let conditions = {};
            let actions = [];
            try {
              conditions = JSON.parse(rule.conditions_json || '{}');
              actions = JSON.parse(rule.actions_json || '[]');
            } catch (e) {}

            return (
              <div
                key={rule.id}
                className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4 text-xs"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-100 text-sm">{rule.name}</span>
                      <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">
                        ACTIVE
                      </span>
                    </div>
                    <p className="text-slate-400 text-xs mt-1">{rule.description}</p>
                  </div>

                  <button
                    onClick={() => handleTestRule(rule.id)}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold border border-slate-700 shrink-0 transition-colors"
                  >
                    <Play className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Test Trigger</span>
                  </button>
                </div>

                {/* Pipeline visualizer: TRIGGER -> CONDITIONS -> ACTIONS */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 font-mono text-[11px]">
                  {/* Trigger */}
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-1 rounded-lg bg-brand-950 text-brand-300 border border-brand-500/40 font-bold">
                      TRIGGER: {rule.trigger_event}
                    </span>
                  </div>

                  <ArrowRight className="w-4 h-4 text-slate-600 hidden md:block shrink-0" />

                  {/* Conditions */}
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-1 rounded-lg bg-amber-950 text-amber-300 border border-amber-500/40">
                      CONDITIONS: {Object.keys(conditions).length === 0 ? 'ALL' : JSON.stringify(conditions)}
                    </span>
                  </div>

                  <ArrowRight className="w-4 h-4 text-slate-600 hidden md:block shrink-0" />

                  {/* Actions */}
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-1 rounded-lg bg-purple-950 text-purple-300 border border-purple-500/40 font-bold">
                      ACTIONS: {actions.length} Executable Dispatches
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-slate-500 text-[11px] pt-1">
                  <span>Execution count: <strong className="text-slate-300">{rule.execution_count} times</strong></span>
                  <span>Registered: {new Date(rule.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Execution Logs Inspector */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-xl space-y-2">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Engine Execution Audit Logs</h2>
          <span className="text-[11px] text-slate-500 font-mono">Last 50 executions</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4">Event</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Execution Diagnostics</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/30">
                  <td className="py-2.5 px-4 font-mono text-slate-400 whitespace-nowrap text-[11px]">
                    {new Date(log.created_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                  <td className="py-2.5 px-4 font-mono font-bold text-brand-300 whitespace-nowrap">{log.trigger_event}</td>
                  <td className="py-2.5 px-4 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      log.status === 'SUCCESS' ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {log.status}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 font-mono text-[11px] text-slate-300 max-w-xl truncate">
                    {log.execution_details}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
