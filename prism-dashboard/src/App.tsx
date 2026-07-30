import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { AgentMonitoringPage } from './pages/AgentMonitoringPage';
import { AlertDetailsPage } from './pages/AlertDetailsPage';
import { DashboardOverviewPage } from './pages/DashboardOverviewPage';
import { IncidentsPage } from './pages/IncidentsPage';
import { LiveAlertsPage } from './pages/LiveAlertsPage';
import { LoginPage } from './pages/LoginPage';
import { NetworkAnalyticsPage } from './pages/NetworkAnalyticsPage';
import { SettingsPage } from './pages/SettingsPage';
import { SystemHealthPage } from './pages/SystemHealthPage';
import { useAuthStore } from './stores/authStore';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        {/* Protected Dashboard Layout Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardOverviewPage />} />
          <Route path="alerts" element={<LiveAlertsPage />} />
          <Route path="alerts/:alertId" element={<AlertDetailsPage />} />
          <Route path="incidents" element={<IncidentsPage />} />
          <Route path="analytics" element={<NetworkAnalyticsPage />} />
          <Route path="agents" element={<AgentMonitoringPage />} />
          <Route path="system" element={<SystemHealthPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
