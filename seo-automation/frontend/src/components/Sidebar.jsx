import { NavLink } from 'react-router-dom'
import { useState, useEffect } from 'react'
import {
  LayoutDashboard, Search, FileText, Newspaper, TrendingUp, BarChart2,
  HelpCircle, Globe, Share2, Briefcase, Users, MessageSquare, CreditCard, Shield,
  UserPlus, Target, ChevronDown, Megaphone, Activity, MapPin, ScanSearch,
} from 'lucide-react'
import Logo from './Logo'

// Flat nav of only what's actually built. More SEO modules (backlinks, local
// SEO, AI visibility, etc.) get added here once they're real pages — no
// "Coming Soon" placeholders cluttering the list in the meantime.
// SEO Content leads the list — it's the primary, day-to-day feature and the
// post-login landing page (see App.jsx).
const SEO_NAV = [
  { to: '/content',    icon: LayoutDashboard, label: 'SEO Content' },
  { to: '/dashboard',  icon: Activity,        label: 'Overview' },
  { to: '/keywords',   icon: Search,          label: 'Keyword Research' },
  { to: '/site-audit', icon: Target,          label: 'Site Audit' },
  { to: '/rankings',   icon: TrendingUp,      label: 'Rankings' },
  { to: '/competitors',icon: Users,           label: 'Competitors' },
  { to: '/reports',    icon: BarChart2,       label: 'Reports' },
]

const CONTENT_AUTOMATION_NAV = [
  { to: '/articles',    icon: Newspaper,       label: 'Articles' },
  { to: '/wordpress',   icon: Globe,           label: 'WordPress' },
  { to: '/indexing',    icon: ScanSearch,      label: 'Google Indexing' },
  { to: '/social',      icon: Share2,          label: 'Social Media' },
  { to: '/gbp',         icon: MapPin,          label: 'Google Business Profile' },
  { to: '/google-ads',  icon: Megaphone,       label: 'Google Ads' },
  { to: '/leads',       icon: UserPlus,        label: 'Leads' },
]

const MARKETPLACE_NAV = [
  { to: '/marketplace',    icon: Briefcase,      label: 'Browse Requests' },
  { to: '/my-requests',    icon: FileText,       label: 'My Requests' },
  { to: '/professionals',  icon: Users,          label: 'Find Professionals' },
  { to: '/messages',       icon: MessageSquare,  label: 'Messages' },
  { to: '/credits',        icon: CreditCard,     label: 'Credits' },
]

function useProjectInfo() {
  const read = () => {
    try { return JSON.parse(localStorage.getItem('seo_project') || '{}') } catch { return {} }
  }
  const [info, setInfo] = useState(read)
  useEffect(() => {
    const handler = () => setInfo(read())
    window.addEventListener('seo_project_updated', handler)
    return () => window.removeEventListener('seo_project_updated', handler)
  }, [])
  return info
}

const navItemStyle = {
  display: 'flex', alignItems: 'center', gap: 10,
  padding: '7px 10px',
  fontSize: 13,
  textDecoration: 'none', transition: 'all 0.15s',
}

function NavItem({ to, icon: Icon, label, indent }) {
  return (
    <NavLink to={to} className={({ isActive }) => (isActive ? 'nav-active' : 'nav-inactive')}
      style={{ ...navItemStyle, paddingLeft: indent ? 30 : 10 }}>
      {({ isActive }) => (
        <>
          {Icon && <Icon size={15} style={{ color: isActive ? 'var(--brand)' : 'var(--text-3)', flexShrink: 0 }} />}
          {label}
        </>
      )}
    </NavLink>
  )
}

export default function Sidebar({ open = false }) {
  const project = useProjectInfo()
  const projectName = project.business_name || (project.base_location ? `${project.base_location.split(',')[0]} Project` : 'New Workspace')
  const projectSub = project.website || 'Configure in Onboarding'

  return (
    <aside className={`sidebar${open ? ' open' : ''}`}>
      {/* Logo */}
      <div style={{ padding: '18px 16px 14px', borderBottom: '1px solid var(--border)' }}>
        <Logo size={30} />
        <div style={{ color: 'var(--text-4)', fontSize: 10, marginTop: 4, letterSpacing: '0.04em' }}>SEO Intelligence</div>
      </div>

      {/* Workspace / project info */}
      <div style={{ padding: '8px 10px', borderBottom: '1px solid var(--border)' }}>
        <div style={{
          padding: '8px 10px', borderRadius: 8, cursor: 'pointer',
          background: 'var(--bg-raised)', border: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ minWidth: 0 }}>
            <div style={{ color: 'var(--text-1)', fontSize: 12, fontWeight: 600 }} className="truncate">{projectName}</div>
            <div style={{ color: 'var(--text-4)', fontSize: 10, marginTop: 1 }} className="truncate">{projectSub}</div>
          </div>
          <ChevronDown size={12} style={{ color: 'var(--text-4)', flexShrink: 0 }} />
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '8px 8px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 1 }}>
        {SEO_NAV.map(item => <NavItem key={item.to} {...item} />)}

        <div style={{ color: 'var(--text-4)', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', padding: '14px 10px 4px' }}>
          Content Automation
        </div>
        {CONTENT_AUTOMATION_NAV.map(item => <NavItem key={item.to} {...item} />)}

        <div style={{ color: 'var(--text-4)', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', padding: '14px 10px 4px' }}>
          Marketplace
        </div>
        {MARKETPLACE_NAV.map(item => <NavItem key={item.to} {...item} />)}

        <div style={{ color: 'var(--text-4)', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', padding: '14px 10px 4px' }}>
          Admin
        </div>
        <NavItem to="/admin" icon={Shield} label="Admin Panel" />
      </nav>

      {/* Bottom */}
      <div style={{ padding: '8px', borderTop: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: 1 }}>
        {[{ Icon: HelpCircle, label: 'Help & Docs' }].map(({ Icon, label }) => (
          <button key={label} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 10px', borderRadius: 8, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-3)', fontSize: 13, width: '100%', textAlign: 'left' }}>
            <Icon size={14} /> {label}
          </button>
        ))}
      </div>
    </aside>
  )
}
