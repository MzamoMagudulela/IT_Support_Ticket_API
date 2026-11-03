import React, { useState, useEffect } from 'react';
import { useAuth, DEMO_USERS } from '../../context/AuthContext';
import { Bell, ShieldCheck, ChevronDown, LogOut, User, Activity } from 'lucide-react';
import api from '../../api/axios';

export const Navbar = () => {
  const { user, primaryRole, logout, switchRole } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [showNotifs, setShowNotifs] = useState(false);
  const [showRoleMenu, setShowRoleMenu] = useState(false);

  useEffect(() => {
    if (user) {
      api.get('/notifications').then((res) => {
        setNotifications(res.data || []);
      }).catch(() => {});
    }
  }, [user]);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const handleRoleSelect = async (demoUser) => {
    setShowRoleMenu(false);
    await switchRole(demoUser.username, demoUser.password);
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-6 flex items-center justify-between z-30 sticky top-0">
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-cyan-400 flex items-center justify-center font-bold text-white shadow-lg shadow-brand-500/20">
            IT
          </div>
          <span className="font-bold text-base tracking-wide bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            ENTERPRISE <span className="text-brand-400 font-extrabold">ITSM</span>
          </span>
        </div>
        <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Core IT Services Operational</span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Role Quick Switcher for evaluators */}
        <div className="relative">
          <button
            onClick={() => setShowRoleMenu(!showRoleMenu)}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-xs font-semibold text-slate-200 transition-colors"
            title="Switch demo persona to test RBAC permissions"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-brand-400" />
            <span>Role: <strong className="text-brand-300">{primaryRole}</strong></span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {showRoleMenu && (
            <div className="absolute right-0 mt-2 w-64 rounded-xl bg-slate-900 border border-slate-800 shadow-2xl p-2 z-50">
              <div className="px-2 py-1.5 text-xs font-semibold text-slate-400 border-b border-slate-800 mb-1">
                SWITCH TEST ROLE (RBAC Demo)
              </div>
              {DEMO_USERS.map((du) => (
                <button
                  key={du.username}
                  onClick={() => handleRoleSelect(du)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-xs flex items-center justify-between transition-colors ${
                    user?.username === du.username
                      ? 'bg-brand-950/80 text-brand-300 border border-brand-500/40'
                      : 'hover:bg-slate-800 text-slate-300'
                  }`}
                >
                  <span className="font-medium">{du.label}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded text-white ${du.color}`}>
                    {du.role}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifs(!showNotifs)}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors relative"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-rose-500 text-white text-[10px] flex items-center justify-center font-bold">
                {unreadCount}
              </span>
            )}
          </button>

          {showNotifs && (
            <div className="absolute right-0 mt-2 w-80 rounded-xl bg-slate-900 border border-slate-800 shadow-2xl p-3 z-50">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-2">
                <span className="text-xs font-semibold text-slate-300">System Notifications</span>
                <span className="text-[10px] text-slate-400">{notifications.length} total</span>
              </div>
              <div className="max-h-64 overflow-y-auto space-y-2">
                {notifications.length === 0 ? (
                  <p className="text-xs text-slate-400 py-3 text-center">No alerts at this moment</p>
                ) : (
                  notifications.map((n) => (
                    <div key={n.id} className="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/50 text-xs">
                      <div className="font-semibold text-slate-200">{n.title}</div>
                      <div className="text-slate-400 mt-0.5 text-[11px]">{n.message}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Info & Logout */}
        <div className="flex items-center space-x-3 pl-3 border-l border-slate-800">
          <div className="text-right hidden sm:block">
            <div className="text-xs font-semibold text-slate-200">{user?.full_name || 'User'}</div>
            <div className="text-[11px] text-slate-400">{user?.email}</div>
          </div>
          <button
            onClick={logout}
            className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
