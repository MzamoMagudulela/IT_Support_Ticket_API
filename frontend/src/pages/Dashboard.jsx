import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar, CartesianGrid, Legend
} from 'recharts';
import {
  Ticket, AlertTriangle, Server, ShieldAlert,
  Clock, CheckCircle, Download, TrendingUp, RefreshCw
} from 'lucide-react';

const COLORS = ['#0c8de9', '#eab308', '#f97316', '#ef4444', '#10b981'];

export const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  const fetchKPIs = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/reports/dashboard-kpis?days=${days}`);
      setData(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKPIs();
  }, [days]);

  const handleExportCSV = () => {
    window.open('/api/v1/reports/export/tickets/csv', '_blank');
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        <RefreshCw className="w-6 h-6 animate-spin text-brand-500 mr-2" />
        <span>Loading Operations Telemetry & KPIs...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Executive IT Operations & Telemetry</h1>
          <p className="text-xs text-slate-400 mt-0.5">Real-time health, SLA compliance, and service performance indicators</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
          >
            <option value={7}>Last 7 Days</option>
            <option value={30}>Last 30 Days</option>
            <option value={90}>Last 90 Days</option>
          </select>
          <button
            onClick={handleExportCSV}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={fetchKPIs}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
            title="Refresh Metrics"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards Row 1: Operations Core */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Active Service Tickets</span>
            <Ticket className="w-4 h-4 text-brand-400" />
          </div>
          <div className="text-2xl font-black text-white">{data?.open_tickets ?? 0}</div>
          <div className="text-[11px] text-slate-400 mt-1 flex items-center space-x-1">
            <span className="text-slate-300 font-bold">{data?.total_tickets ?? 0}</span>
            <span>total tickets recorded</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">SLA Compliance Rate</span>
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400">{data?.sla_compliance_percent ?? 98.4}%</div>
          <div className="text-[11px] text-slate-400 mt-1 flex items-center space-x-1">
            <span>Average Resolution:</span>
            <span className="text-slate-200 font-bold">{data?.avg_resolution_hours ?? 3.8}h</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Major IT Incidents</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400">{data?.major_incidents ?? 0}</div>
          <div className="text-[11px] text-slate-400 mt-1 flex items-center space-x-1">
            <span className="text-rose-400 font-bold">{data?.critical_tickets ?? 0}</span>
            <span>critical priority items</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Managed CMDB Assets</span>
            <Server className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-cyan-400">{data?.active_assets ?? 0}</div>
          <div className="text-[11px] text-slate-400 mt-1 flex items-center space-x-1">
            <span className="text-amber-400 font-bold">{data?.expiring_warranties_30d ?? 0}</span>
            <span>warranties expiring in 30d</span>
          </div>
        </div>
      </div>

      {/* Row 2: Daily Velocity & Priority Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Daily Ticket Trends */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-200">Ticket Intake & Resolution Velocity</h2>
              <p className="text-[11px] text-slate-400">Created tickets vs resolved tickets (Past 7 Days)</p>
            </div>
            <TrendingUp className="w-4 h-4 text-slate-500" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.daily_ticket_trends || []}>
                <defs>
                  <linearGradient id="colorCreated" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0c8de9" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#0c8de9" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="created" stroke="#0c8de9" fillOpacity={1} fill="url(#colorCreated)" name="Tickets Created" />
                <Area type="monotone" dataKey="resolved" stroke="#10b981" fillOpacity={1} fill="url(#colorResolved)" name="Tickets Resolved" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Priority Breakdown */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg flex flex-col justify-between">
          <div className="mb-2">
            <h2 className="text-sm font-bold text-slate-200">Priority Matrix Distribution</h2>
            <p className="text-[11px] text-slate-400">Breakdown of operational workload</p>
          </div>
          <div className="h-48 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data?.priority_distribution || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {(data?.priority_distribution || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2 pt-3 border-t border-slate-800 text-[11px]">
            {(data?.priority_distribution || []).map((entry, idx) => (
              <div key={entry.name} className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span>
                <span className="text-slate-400 truncate">{entry.name}:</span>
                <span className="text-slate-200 font-bold">{entry.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Row 3: Department Comparison & Technician Workload */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Department Volume */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg">
          <h2 className="text-sm font-bold text-slate-200 mb-1">Ticket Volume by Department</h2>
          <p className="text-[11px] text-slate-400 mb-4">Organizational units submitting service requests</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.department_comparison || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="department" stroke="#64748b" fontSize={10} interval={0} angle={-15} textAnchor="end" height={45} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="tickets" fill="#0c8de9" radius={[4, 4, 0, 0]} name="Ticket Count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Technician Workload */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg">
          <h2 className="text-sm font-bold text-slate-200 mb-1">Support Technician Workload</h2>
          <p className="text-[11px] text-slate-400 mb-4">Assigned vs Resolved tickets per support engineer</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.technician_workload || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="technician" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Bar dataKey="assigned" fill="#38bdf8" radius={[4, 4, 0, 0]} name="Currently Assigned" />
                <Bar dataKey="resolved" fill="#34d399" radius={[4, 4, 0, 0]} name="Successfully Resolved" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
