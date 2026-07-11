import { NavLink } from 'react-router-dom'
import { useState, useEffect } from 'react'
import {
  LayoutDashboard, Search, FileText, Newspaper,
  TrendingUp, BarChart2, Settings, HelpCircle, Globe,
  Share2, Briefcase, Users, MessageSquare, CreditCard, Shield, UserPlus
} from 'lucide-react'
import Logo from './Logo'

const SEO_NAV = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/content',   icon: FileText,        label: 'Content' },
  { to: '/articles',  icon: Newspaper,       label: 'Articles' },
  { to: '/keywords',  icon: Search,          label: 'Keywords' },
  { to: '/rankings',  icon: TrendingUp,      label: 'Rankings' },
  { to: '/reports',   icon: BarChart2,       label: 'Reports' },
  { to: '/wordpress', icon: Globe,           label: 'WordPress' },
]

const AUTOMATION_NAV = [
  { to: '/social',    icon: Share2,          label: 'Social Media' },
  { to: '/leads',     icon: UserPlus,        label: 'Leads' },
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
  padding: '8px 10px',
  fontSize: 13,
  textDecoration: 'none', transition: 'all 0.15s',
}

export default function Sidebar({ open = false }) {
  const project = useProjectInfo()
  const projectName = project.base_location
    ? `${project.base_location.split(',')[0]} Project`
    : 'New Project'
  const projectSub = project.business_type && project.num_cities
    ? `${project.business_type} · ${project.num_cities} cities`
    : 'Configure in Content'

  return (
    <aside className={`sidebar${open ? ' open' : ''}`}>
      {/* Logo */}
      <div style={{ padding: '18px 16px 14px', borderBottom: '1px solid var(--border)' }}>
        <div>
          <Logo size={19} />
          <div style={{ color: 'var(--text-4)', fontSize: 10, marginTop: 4, letterSpacing: '0.04em' }}>SEO Intelligence</div>
        </div>
      </div>

      {/* Project info */}
      <div style={{ padding: '8px 10px', borderBottom: '1px solid var(--border)' }}>
        <div style={{
          padding: '8px 10px', borderRadius: 8, cursor: 'pointer',
          background: 'var(--bg-raised)', border: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          transition: 'background 0.15s'
        }}
          onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-overlay)'}
          onMouseLeave={e => e.currentTarget.style.background = 'var(--bg-raised)'}>
          <div>
            <div style={{ color: 'var(--text-1)', fontSize: 12, fontWeight: 600 }}>{projectName}</div>
            <div style={{ color: 'var(--text-4)', fontSize: 10, marginTop: 1 }}>{projectSub}</div>
          </div>
          <svg width="10" height="10" viewBox="0 0 12 12" fill="none" style={{ color: 'var(--text-4)', flexShrink: 0 }}>
            <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '8px 8px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 1 }}>
        <div style={{ color: 'var(--text-4)', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', padding: '6px 8px 4px' }}>
          SEO Tools
        </div>
        {SEO_NAV.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to} end={to === '/dashboard'}
            className={({ isActive }) => (isActive ? 'nav-active' : 'nav-inactive')}
            style={navItemStyle}
          >
            {({ isActive }) => (
              <>
                <Icon size={15} style={{ color: isActive ? 'var(--brand)' : 'var(--text-3)', flexShrink: 0 }} />
                {label}
              </>
            )}
          </NavLink>
        ))}

        <div style={{ color: 'var(--text-4)', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', padding: '10px 8px 4px', marginTop: 2 }}>
          Automation
        </div>
        {AUTOMATION_NAV.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to}
            className={({ isActive }) => (isActive ? 'nav-active' : 'nav-inactive')}
            style={navItemStyle}
          >
            {({ isActive }) => (
              <>
                <Icon size={15} style={{ color: isActive ? 'var(--brand)' : 'var(--text-3)', flexShrink: 0 }} />
                {label}
              </>
            )}
          </NavLink>
        ))}

        <div style={{ color: 'var(--text-4)', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', padding: '10px 8px 4px', marginTop: 2 }}>
          Marketplace
        </div>
        {MARKETPLACE_NAV.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to}
            className={({ isActive }) => (isActive ? 'nav-active' : 'nav-inactive')}
            style={navItemStyle}
          >
            {({ isActive }) => (
              <>
                <Icon size={15} style={{ color: isActive ? 'var(--brand)' : 'var(--text-3)', flexShrink: 0 }} />
                {label}
              </>
            )}
          </NavLink>
        ))}

        <div style={{ color: 'var(--text-4)', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', padding: '10px 8px 4px', marginTop: 2 }}>
          Admin
        </div>
        <NavLink to="/admin"
          className={({ isActive }) => (isActive ? 'nav-active' : 'nav-inactive')}
          style={navItemStyle}
        >
          {({ isActive }) => (
            <>
              <Shield size={15} style={{ color: isActive ? 'var(--brand)' : 'var(--text-3)', flexShrink: 0 }} />
              Admin Panel
            </>
          )}
        </NavLink>
      </nav>

      {/* Bottom */}
      <div style={{ padding: '8px', borderTop: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: 1 }}>
        {[{ Icon: Settings, label: 'Settings' }, { Icon: HelpCircle, label: 'Help & Docs' }].map(({ Icon, label }) => (
          <button key={label} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 10px', borderRadius: 8, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-3)', fontSize: 13, width: '100%', transition: 'all 0.15s', textAlign: 'left' }}
            onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-1)'; e.currentTarget.style.background = 'var(--bg-raised)' }}
            onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-3)'; e.currentTarget.style.background = 'none' }}>
            <Icon size={14} /> {label}
          </button>
        ))}
      </div>
    </aside>
  )
}
