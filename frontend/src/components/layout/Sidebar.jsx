import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  Ticket,
  AlertTriangle,
  Server,
  GitPullRequest,
  ShieldAlert,
  BookOpen,
  Activity,
  Zap,
  FileText,
  Sliders
} from 'lucide-react';

export const Sidebar = () => {
  const { primaryRole } = useAuth();
  const role = primaryRole.toLowerCase();

  const navItems = [
    { label: 'Executive Dashboard', path: '/', icon: LayoutDashboard, roles: ['all'] },
    { label: 'Service Desk', path: '/tickets', icon: Ticket, roles: ['all'] },
    { label: 'Incident Operations', path: '/incidents', icon: AlertTriangle, roles: ['system administrator', 'it operations manager', 'it support technician', 'security analyst', 'auditor'] },
    { label: 'IT Assets & CMDB', path: '/assets', icon: Server, roles: ['all'] },
    { label: 'Change Management', path: '/changes', icon: GitPullRequest, roles: ['system administrator', 'it operations manager', 'it support technician', 'auditor'] },
    { label: 'Cybersecurity Ops', path: '/security', icon: ShieldAlert, roles: ['system administrator', 'it operations manager', 'security analyst', 'auditor'] },
    { label: 'Knowledge Base', path: '/knowledge', icon: BookOpen, roles: ['all'] },
    { label: 'Infrastructure Monitor', path: '/monitoring', icon: Activity, roles: ['system administrator', 'it operations manager', 'it support technician', 'security analyst'] },
    { label: 'Workflow Automation', path: '/automation', icon: Zap, roles: ['system administrator', 'it operations manager', 'auditor'] },
    { label: 'Audit & Compliance', path: '/audit', icon: FileText, roles: ['system administrator', 'auditor'] },
    { label: 'Integrations & Config', path: '/integrations', icon: Sliders, roles: ['system administrator', 'it operations manager'] },
  ];

  const filteredItems = navItems.filter((item) => {
    if (item.roles.includes('all')) return true;
    if (role.includes('admin')) return true;
    return item.roles.some((r) => role.includes(r.toLowerCase()));
  });

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/50 flex flex-col justify-between shrink-0 h-[calc(100vh-4rem)]">
      <div className="py-4 px-3 space-y-1">
        <div className="px-3 mb-2 text-[11px] font-bold text-slate-400 tracking-wider uppercase">
          Operations Modules
        </div>
        {filteredItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-brand-600/20 text-brand-300 border border-brand-500/30 glow-brand'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      <div className="p-3 border-t border-slate-800/60 bg-slate-950/40">
        <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400">
          <div className="flex items-center justify-between font-semibold text-slate-300 mb-1">
            <span>SLA Health</span>
            <span className="text-emerald-400 font-bold">98.4%</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-emerald-500 h-full rounded-full" style={{ width: '98.4%' }}></div>
          </div>
          <div className="text-[10px] text-slate-400 mt-1">Enterprise Standard Target: 95%</div>
        </div>
      </div>
    </aside>
  );
};
