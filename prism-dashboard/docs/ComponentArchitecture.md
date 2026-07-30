# Component Architecture

```
App
 ├── BrowserRouter
 └── Routes
     ├── /login -> LoginPage
     └── / -> ProtectedRoute -> MainLayout
         ├── /dashboard -> DashboardOverviewPage
         ├── /alerts -> LiveAlertsPage
         ├── /alerts/:id -> AlertDetailsPage
         ├── /incidents -> IncidentsPage
         ├── /analytics -> NetworkAnalyticsPage
         ├── /agents -> AgentMonitoringPage
         ├── /system -> SystemHealthPage
         └── /settings -> SettingsPage
```
