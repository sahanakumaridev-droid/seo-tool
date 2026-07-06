import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import LandingPage from './pages/LandingPage'
import SimpleDashboard from './pages/SimpleDashboard'
import DashboardPage from './pages/DashboardPage'
import PremiumDashboard from './pages/PremiumDashboard'
import KeywordsPage from './pages/KeywordsPage'
import CompetitorsPage from './pages/CompetitorsPage'
import ContentPage from './pages/ContentPage'
import ArticlesPage from './pages/ArticlesPage'
import RankingsPage from './pages/RankingsPage'
import ReportsPage from './pages/ReportsPage'
import WordPressPage from './pages/WordPressPage'
import PagePreviewPage from './pages/PagePreviewPage'
import SocialPage from './pages/SocialPage'
import LeadsPage from './pages/LeadsPage'
// Marketplace module
import MarketplacePage from './pages/MarketplacePage'
import MyRequestsPage from './pages/MyRequestsPage'
import ProfessionalsPage from './pages/ProfessionalsPage'
import MessagesPage from './pages/MessagesPage'
import CreditsPage from './pages/CreditsPage'
import AdminPage from './pages/AdminPage'

function useAuth() {
  const [authed, setAuthed] = useState(() => localStorage.getItem('seo_auth') === 'true')
  const login = () => { localStorage.setItem('seo_auth', 'true'); setAuthed(true) }
  const logout = () => { localStorage.removeItem('seo_auth'); setAuthed(false) }
  return { authed, login, logout }
}

function DashboardLayout({ children, onLogout }) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-base)', color: 'var(--text-1)' }}>
      <Sidebar />
      <div className="main-content" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Topbar onLogout={onLogout} />
        <div style={{ flex: 1, padding: 24, overflow: 'auto' }}>
          {children}
        </div>
      </div>
    </div>
  )
}

function RequireAuth({ authed, children }) {
  const location = useLocation()
  if (!authed) return <Navigate to="/" state={{ from: location }} replace />
  return children
}

export default function App() {
  const { authed, login, logout } = useAuth()

  return (
    <Routes>
      {/* Premium Dashboard - Full screen, no sidebar */}
      <Route path="/premium" element={<PremiumDashboard />} />
      
      {/* Landing page is the root — passes login handler so it can show the dialog */}
      <Route path="/" element={
        authed
          ? <Navigate to="/simple" replace />
          : <LandingPage onLogin={login} />
      } />

      {/* Simple Dashboard - No sidebar, just the form */}
      <Route path="/simple" element={
        <RequireAuth authed={authed}>
          <SimpleDashboard />
        </RequireAuth>
      } />

      {/* Protected dashboard routes */}
      <Route path="/dashboard" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><DashboardPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/content" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><ContentPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/articles" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><ArticlesPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/keywords" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><KeywordsPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/rankings" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><RankingsPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/reports" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><ReportsPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/wordpress" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><WordPressPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/competitors" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><CompetitorsPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/page-preview" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><PagePreviewPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/social" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><SocialPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/leads" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><LeadsPage /></DashboardLayout>
        </RequireAuth>
      } />

      {/* ── Marketplace routes ── */}
      <Route path="/marketplace" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><MarketplacePage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/my-requests" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><MyRequestsPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/professionals" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><ProfessionalsPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/messages" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><MessagesPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/credits" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><CreditsPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/admin" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><AdminPage /></DashboardLayout>
        </RequireAuth>
      } />

      {/* Catch-all → landing */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
