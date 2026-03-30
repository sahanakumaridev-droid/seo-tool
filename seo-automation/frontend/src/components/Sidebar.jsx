import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Search, FileText,
  TrendingUp, BarChart2, Zap, Settings, HelpCircle
} from 'lucide-react'

const NAV = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/content', icon: FileText, label: 'Content' },
  { to: '/keywords', icon: Search, label: 'Keywords' },
  { to: '/rankings', icon: TrendingUp, label: 'Rankings' },
  { to: '/reports', icon: BarChart2, label: 'Reports' },
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 py-5" style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ background: 'var(--brand-grad)', boxShadow: '0 0 12px rgba(99,102,241,0.4)' }}>
          <Zap size={14} className="text-white" />
        </div>
        <div>
          <span className="font-bold text-sm tracking-tight" style={{ color: 'var(--text-primary)' }}>ZEORBIT</span>
          <div className="text-[10px] leading-none mt-0.5" style={{ color: 'var(--text-muted)' }}>SEO Intelligence</div>
        </div>
      </div>

      {/* Project selector */}
      <div className="px-4 py-3" style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors"
          style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)' }}
          onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
          onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}>
          <div>
            <div className="text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>San Diego Project</div>
            <div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Plumbing · 50 cities</div>
          </div>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style={{ color: 'var(--text-muted)' }}>
            <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-3 space-y-0.5">
        <div className="text-[10px] font-semibold uppercase tracking-wider px-3 py-2" style={{ color: 'var(--text-muted)' }}>
          Main
        </div>
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150
              ${isActive ? 'nav-active' : 'nav-inactive'}`
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={15} style={{ color: isActive ? '#A5B4FC' : 'var(--text-muted)' }} />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div className="px-3 py-4 space-y-0.5" style={{ borderTop: '1px solid var(--border)' }}>
        <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors nav-inactive">
          <Settings size={14} /> Settings
        </button>
        <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors nav-inactive">
          <HelpCircle size={14} /> Help & Docs
        </button>
      </div>
    </aside>
  )
}
