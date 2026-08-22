import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import BlogPage from './pages/BlogPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import OnboardingPage from './pages/OnboardingPage'
import SiteAuditPage from './pages/SiteAuditPage'
import GoogleAdsPage from './pages/GoogleAdsPage'
import IndexingStatusPage from './pages/IndexingStatusPage'
import IntegrationsPage from './pages/IntegrationsPage'
import ComingSoonPage from './pages/ComingSoonPage'
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
import LeadEnginePage from './pages/LeadEnginePage'
import InstantQuotePage from './pages/InstantQuotePage'
import LandingPage from './pages/LandingPage'
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
  const logout = () => {
    localStorage.removeItem('seo_auth')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('mp_token')
    localStorage.removeItem('mp_user')
    setAuthed(false)
  }
  return { authed, login, logout }
}

function DashboardLayout({ children, onLogout }) {
  const [navOpen, setNavOpen] = useState(false)
  const location = useLocation()
  // Close the mobile drawer on route change
  useEffect(() => { setNavOpen(false) }, [location.pathname])
  return (
    <div className="crm-shell" style={{ display: 'flex', minHeight: '100vh', background: '#ffffff', color: '#1d1d1f' }}>
      <Sidebar open={navOpen} />
      {navOpen && <div className="sidebar-backdrop" onClick={() => setNavOpen(false)} />}
      <div className="main-content" style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <Topbar onLogout={onLogout} onMenuClick={() => setNavOpen(v => !v)} />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'auto' }}>
          <div className="dashboard-content-pad" style={{ flex: 1 }}>
            {children}
          </div>
        </div>
      </div>
    </div>
  )
}

function RequireAuth({ authed, children }) {
  const location = useLocation()
  // `authed` is React state and can lag one render behind localStorage right
  // after login()/onLogin() fires a navigate() in the same event handler —
  // localStorage is written synchronously, so fall back to it to avoid
  // bouncing through "/" on that first render.
  const isAuthed = authed || localStorage.getItem('seo_auth') === 'true'
  if (!isAuthed) return <Navigate to="/login" state={{ from: location }} replace />
  return children
}

function HomeGate({ authed, onLogout }) {
  const isAuthed = authed || localStorage.getItem('seo_auth') === 'true'
  if (!isAuthed) return <LandingPage />
  return <DashboardLayout onLogout={onLogout}><ContentPage /></DashboardLayout>
}

export default function App() {
  const { authed, login, logout } = useAuth()

  return (
    <Routes>
      {/* Premium Dashboard - Full screen, no sidebar */}
      <Route path="/premium" element={<PremiumDashboard />} />
      
      {/* White CRM is the app home — including /landing (no dark marketing). */}
      <Route path="/" element={<HomeGate authed={authed} onLogout={logout} />} />
      <Route path="/landing" element={<HomeGate authed={authed} onLogout={logout} />} />
      <Route path="/revamp-preview" element={<HomeGate authed={authed} onLogout={logout} />} />

      {/* Public blog — live published SEO content */}
      <Route path="/blog" element={<BlogPage />} />

      {/* Auth screens — each page snapshots auth state once at mount to decide
          whether to redirect away; this avoids racing the in-page navigate()
          that fires right after a successful login/register in the same tick. */}
      <Route path="/login" element={<LoginPage onLogin={login} />} />
      <Route path="/register" element={<RegisterPage onLogin={login} />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      {/* Onboarding — full-screen wizard, no sidebar */}
      <Route path="/onboarding" element={
        <RequireAuth authed={authed}>
          <OnboardingPage />
        </RequireAuth>
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
      <Route path="/site-audit" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><SiteAuditPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/coming-soon/:module" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><ComingSoonPage /></DashboardLayout>
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
        <DashboardLayout onLogout={logout}><LeadsPage /></DashboardLayout>
      } />
      <Route path="/lead-engine" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><LeadEnginePage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/instant-quote" element={<InstantQuotePage />} />
      <Route path="/google-ads" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><GoogleAdsPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/indexing" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><IndexingStatusPage /></DashboardLayout>
        </RequireAuth>
      } />
      <Route path="/integrations" element={
        <RequireAuth authed={authed}>
          <DashboardLayout onLogout={logout}><IntegrationsPage /></DashboardLayout>
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
