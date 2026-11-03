import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { TicketsPage } from './pages/TicketsPage';
import { TicketDetailPage } from './pages/TicketDetailPage';
import { IncidentsPage } from './pages/IncidentsPage';
import { AssetsPage } from './pages/AssetsPage';
import { ChangesPage } from './pages/ChangesPage';
import { SecurityPage } from './pages/SecurityPage';
import { KnowledgePage } from './pages/KnowledgePage';
import { MonitoringPage } from './pages/MonitoringPage';
import { AutomationPage } from './pages/AutomationPage';
import { AuditLogsPage } from './pages/AuditLogsPage';
import { IntegrationsPage } from './pages/IntegrationsPage';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export const App = () => {
  return (
    <AuthProvider>
      <NotificationProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="tickets" element={<TicketsPage />} />
              <Route path="tickets/:ticketId" element={<TicketDetailPage />} />
              <Route path="incidents" element={<IncidentsPage />} />
              <Route path="assets" element={<AssetsPage />} />
              <Route path="changes" element={<ChangesPage />} />
              <Route path="security" element={<SecurityPage />} />
              <Route path="knowledge" element={<KnowledgePage />} />
              <Route path="monitoring" element={<MonitoringPage />} />
              <Route path="automation" element={<AutomationPage />} />
              <Route path="audit" element={<AuditLogsPage />} />
              <Route path="integrations" element={<IntegrationsPage />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </NotificationProvider>
    </AuthProvider>
  );
};

export default App;
