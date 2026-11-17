import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Search, Newspaper, TrendingUp, BarChart2,
  HelpCircle, Share2, Users, Shield,
  UserPlus, Target, ChevronDown, Megaphone, ScanSearch, Plug, Rocket, Globe2, Building2, Server,
  Trophy, Bot, Hand, LineChart, Rss,
} from 'lucide-react'
import Logo from './Logo'
import useProjectInfo from '../hooks/useProjectInfo'

const CRM_NAV = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/leads',     icon: UserPlus, label: 'Contacts' },
  { to: '/prospects', icon: Building2, label: 'Prospects' },
]

const SEO_NAV = [
  { to: '/top3',       icon: Trophy,          label: 'Top 3 Engine' },
  { to: '/content',    icon: LayoutDashboard, label: 'SEO Content' },
  { to: '/write',      icon: Newspaper,       label: 'Generate Blog' },
  { to: '/keywords',   icon: Search,          label: 'Keyword Research' },
  { to: '/site-audit', icon: Target,          label: 'Site Audit' },
  { to: '/sitemaps',   icon: Globe2,          label: 'Sitemaps' },
  { to: '/indexing',   icon: ScanSearch,      label: 'Indexing' },
  { to: '/gsc',        icon: LineChart,       label: 'Search Console' },
  { to: '/rankings',   icon: TrendingUp,      label: 'Rankings' },
  { to: '/competitors',icon: Users,           label: 'Competitors' },
  { to: '/reports',    icon: BarChart2,       label: 'Reports' },
]

const CONTENT_AUTOMATION_NAV = [
  { to: '/posted-blogs', icon: Rss,            label: 'Published URLs' },
  { to: '/articles',    icon: Newspaper,       label: 'Articles' },
  { to: '/index-automation', icon: Bot,            label: 'Index Automation' },
  { to: '/daily-10',         icon: Hand,           label: 'Daily 10%' },
  { to: '/social',      icon: Share2,          label: 'Social Media' },
  { to: '/google-ads',  icon: Megaphone,       label: 'Google Ads' },
  { to: '/lead-engine', icon: Rocket,          label: 'Lead Engine' },
  { to: '/integrations',icon: Plug,            label: 'API Integrations' },
  { to: '/custom-plugin', icon: Server,        label: 'Custom Plugin' },
  { to: '/news-feeds', icon: Rss,              label: 'News Feeds' },
]

function NavItem({ to, icon: Icon, label, end }) {
  const location = useLocation()
  const contentHome = to === '/content' && (location.pathname === '/' || location.pathname === '/landing' || location.pathname === '/revamp-preview')
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) => ((isActive || contentHome) ? 'nav-active' : 'nav-inactive')}
      style={{
        display: 'flex', alignItems: 'center', gap: 8,
        padding: '7px 10px',
        fontSize: 12.5,
        textDecoration: 'none',
        transition: 'background 150ms ease, color 150ms ease',
      }}
    >
      {Icon && <Icon size={14} style={{ flexShrink: 0, opacity: 0.9 }} />}
      {label}
    </NavLink>
  )
}

function isAdmin() {
  try { return JSON.parse(localStorage.getItem('mp_user') || '{}').role === 'admin' } catch { return false }
}

export default function Sidebar({ open = false }) {
  const project = useProjectInfo()
  const admin = isAdmin()
  const projectName = project.business_name || (project.base_location ? `${project.base_location.split(',')[0]} Project` : 'New Workspace')
  const projectSub = project.website || 'zeorbit.com'

  return (
    <aside className={`sidebar${open ? ' open' : ''}`}>
      <div className="sidebar-logo">
        <Logo size={34} onDark />
        <div className="sidebar-kicker">CRM + SEO</div>
      </div>

      <div className="sidebar-project">
        <div className="sidebar-project-btn">
          <div style={{ minWidth: 0 }}>
            <div className="name truncate">{projectName}</div>
            <div className="sub truncate">{projectSub}</div>
          </div>
          <ChevronDown size={12} style={{ color: 'var(--sidebar-muted)', flexShrink: 0 }} />
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="sidebar-section">CRM</div>
        {CRM_NAV.map(item => <NavItem key={item.to} {...item} />)}

        <div className="sidebar-section">SEO</div>
        {SEO_NAV.map(item => <NavItem key={item.to} {...item} />)}

        <div className="sidebar-section">Content Automation</div>
        {CONTENT_AUTOMATION_NAV.map(item => <NavItem key={item.to} {...item} />)}

        {admin && (
          <>
            <div className="sidebar-section">Admin</div>
            <NavItem to="/admin" icon={Shield} label="Admin Panel" />
          </>
        )}
      </nav>

      <div className="sidebar-foot">
        <button type="button" className="sidebar-help">
          <HelpCircle size={14} /> Help & Docs
        </button>
      </div>
    </aside>
  )
}
