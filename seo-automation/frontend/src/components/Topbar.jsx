import { useEffect, useState } from 'react'
import { Bell, Search, ChevronDown, LogOut, Menu } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function useBackendStatus() {
  const [status, setStatus] = useState('checking')
  useEffect(() => {
    const check = async () => {
      try { await axios.get('/api/../', { timeout: 3000 }); setStatus('online') }
      catch { setStatus('offline') }
    }
    check()
    const id = setInterval(check, 15000)
    return () => clearInterval(id)
  }, [])
  return status
}

export default function Topbar({ onLogout, onMenuClick }) {
  const status = useBackendStatus()
  const navigate = useNavigate()
  const [showMenu, setShowMenu] = useState(false)

  const S = {
    checking: { color: '#FBBF24', bg: 'rgba(251,191,36,0.08)', border: 'rgba(251,191,36,0.2)', label: 'Connecting' },
    online:   { color: '#34D399', bg: 'rgba(52,211,153,0.08)',  border: 'rgba(52,211,153,0.2)',  label: 'API Online' },
    offline:  { color: '#F87171', bg: 'rgba(248,113,113,0.08)', border: 'rgba(248,113,113,0.2)', label: 'Offline' },
  }[status]

  return (
    <header style={{
      height: 54, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 24px', flexShrink: 0, position: 'sticky', top: 0, zIndex: 30,
      background: 'var(--bg-base)', borderBottom: '1px solid var(--border)',
    }}>
      {/* Mobile menu toggle */}
      <button className="mobile-only" onClick={onMenuClick} aria-label="Toggle navigation"
        style={{ padding: 7, borderRadius: 8, background: 'none', border: '1px solid var(--border)', cursor: 'pointer', color: 'var(--text-2)', marginRight: 8 }}>
        <Menu size={16} />
      </button>

      {/* Search */}
      <div className="topbar-search" style={{ position: 'relative', width: 280 }}>
        <Search size={13} style={{ position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-4)', pointerEvents: 'none' }} />
        <input
          type="text"
          placeholder="Search keywords, pages, cities..."
          style={{ width: '100%', paddingLeft: 34, paddingRight: 40, paddingTop: 8, paddingBottom: 8, fontSize: 13 }}
        />
        <kbd style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', fontSize: 10, padding: '2px 5px', borderRadius: 4, color: 'var(--text-4)', background: 'var(--bg-raised)', border: '1px solid var(--border)', pointerEvents: 'none' }}>⌘K</kbd>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {/* API status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 12, padding: '4px 10px', borderRadius: 6, color: S.color, background: S.bg, border: `1px solid ${S.border}` }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: S.color, flexShrink: 0, display: 'inline-block' }} />
          {S.label}
        </div>

        {/* Bell */}
        <button style={{ position: 'relative', padding: 7, borderRadius: 8, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-3)', display: 'flex', transition: 'all 0.15s' }}
          onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-raised)'; e.currentTarget.style.color = 'var(--text-1)' }}
          onMouseLeave={e => { e.currentTarget.style.background = 'none'; e.currentTarget.style.color = 'var(--text-3)' }}>
          <Bell size={16} />
          <span style={{ position: 'absolute', top: 7, right: 7, width: 5, height: 5, borderRadius: '50%', background: 'var(--brand)' }} />
        </button>

        {/* User */}
        <div style={{ position: 'relative' }}>
          <button onClick={() => setShowMenu(m => !m)}
            style={{ display: 'flex', alignItems: 'center', gap: 8, paddingLeft: 12, background: 'none', border: 'none', cursor: 'pointer', borderLeft: '1px solid var(--border)' }}>
            <div style={{ width: 30, height: 30, borderRadius: '50%', background: 'linear-gradient(135deg,#2563EB,#1D4ED8)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 700, color: 'white', flexShrink: 0 }}>A</div>
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-1)', lineHeight: 1 }}>Admin</div>
              <div style={{ fontSize: 10, color: 'var(--text-4)', marginTop: 2 }}>admin@zeorbit.com</div>
            </div>
            <ChevronDown size={12} style={{ color: 'var(--text-4)' }} />
          </button>

          {showMenu && (
            <>
              <div style={{ position: 'fixed', inset: 0, zIndex: 40 }} onClick={() => setShowMenu(false)} />
              <div style={{ position: 'absolute', right: 0, top: 44, zIndex: 50, width: 164, borderRadius: 10, padding: 4, background: 'var(--bg-overlay)', border: '1px solid var(--border-bright)', boxShadow: '0 8px 24px rgba(0,0,0,0.5)' }}>
                <div style={{ padding: '8px 10px 6px', borderBottom: '1px solid var(--border)', marginBottom: 2 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-1)' }}>Admin</div>
                  <div style={{ fontSize: 10, color: 'var(--text-4)', marginTop: 1 }}>admin@zeorbit.com</div>
                </div>
                <button onClick={() => { onLogout?.(); navigate('/login') }}
                  style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px', borderRadius: 7, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--red)', fontSize: 13, transition: 'background 0.15s' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(248,113,113,0.08)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'none'}>
                  <LogOut size={13} /> Sign Out
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
