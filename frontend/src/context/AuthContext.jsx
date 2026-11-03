import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';

const AuthContext = createContext();

export const DEMO_USERS = [
  { label: 'System Admin', username: 'admin', password: 'Admin123!', role: 'System Administrator', color: 'bg-purple-600' },
  { label: 'IT Manager', username: 'sarah.manager', password: 'Manager123!', role: 'IT Operations Manager', color: 'bg-blue-600' },
  { label: 'Support Tech', username: 'alex.tech', password: 'Tech123!', role: 'IT Support Technician', color: 'bg-emerald-600' },
  { label: 'Employee', username: 'john.employee', password: 'User123!', role: 'Employee', color: 'bg-amber-600' },
  { label: 'Security Analyst', username: 'elena.sec', password: 'Security123!', role: 'Security Analyst', color: 'bg-red-600' },
  { label: 'Auditor', username: 'marcus.audit', password: 'Auditor123!', role: 'Auditor', color: 'bg-indigo-600' },
];

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(false);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      const res = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      const { access_token, refresh_token, user: userData } = res.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || 'Authentication failed' };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        await api.post('/auth/logout', { refresh_token: refreshToken });
      } catch (e) {
        // ignore
      }
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const switchRole = async (username, password) => {
    return await login(username, password);
  };

  const primaryRole = user?.roles?.[0]?.name || 'Employee';

  return (
    <AuthContext.Provider value={{
      user,
      primaryRole,
      isAuthenticated: !!user,
      loading,
      login,
      logout,
      switchRole,
      DEMO_USERS
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
