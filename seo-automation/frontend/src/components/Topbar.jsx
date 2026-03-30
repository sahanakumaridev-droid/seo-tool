import { useEffect, useState } from 'react'
import { Bell, Search, ChevronDown } from 'lucide-react'
import axios from 'axios'

function useBackendStatus() {
  const [status, setStatus] = useState('checking')
  useEffect(() => {
    const check = async () => {
      try {
        await axios.get('/api/../', { timeout: 3000 })
        setStatus('online')
      } catch {
        setStatus('offline')
      }
    }
    check()
    const interval = setInterval(check, 15000)
    return () => clearInterval(interval)
  }, [])
  return status
}

export default function Topbar() {
  const backendStatus = useBackendStatus()

  const statusConfig = {
    checking: { dot: 'bg-amber-400 animate-pulse', textColor: '#F59E0B', bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.2)', label: 'Connecting...' },
    online:   { dot: 'bg-emerald-400 animate-pulse', textColor: '#10B981', bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.2)', label: 'Online' },
    offline:  { dot: 'bg-red-400', textColor: '#EF4444', bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.2)', label: 'Offline' },
  }

  const s = statusConfig[backendStatus]

  return (
    <header className="h-14 flex items-center justify-between px-6 flex-shrink-0 sticky top-0 z-30"
      style={{ background: 'var(--bg-primary)', borderBottom: '1px solid var(--border)' }}>

      {/* Search */}
      <div className="relative w-72">
        <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
        <input
          type="text"
          placeholder="Search keywords, pages, cities..."
          className="w-full rounded-lg pl-9 pr-10 py-2 text-sm transition-all"
          style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid var(--border)',
            color: 'var(--text-primary)',
          }}
        />
        <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] px-1.5 py-0.5 rounded"
          style={{ color: 'var(--text-muted)', background: 'rgba(255,255,255,0.05)' }}>⌘K</kbd>
      </div>

      <div className="flex items-center gap-3">
        {/* Status badge */}
        <div className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg transition-all"
          style={{ color: s.textColor, background: s.bg, border: `1px solid ${s.border}` }}>
          <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${s.dot}`} />
          {s.label}
        </div>

        {/* Bell */}
        <button className="relative p-2 rounded-lg transition-colors"
          style={{ color: 'var(--text-secondary)' }}
          onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; e.currentTarget.style.color = 'var(--text-primary)' }}
          onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-secondary)' }}>
          <Bell size={15} />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full" style={{ background: 'var(--brand)' }} />
        </button>

        {/* User */}
        <div className="flex items-center gap-2 pl-3 cursor-pointer hover:opacity-80 transition-opacity"
          style={{ borderLeft: '1px solid var(--border)' }}>
          <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white"
            style={{ background: 'var(--brand-grad)' }}>A</div>
          <div className="hidden md:block">
            <div className="text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>Agency Pro</div>
            <div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>admin@agency.com</div>
          </div>
          <ChevronDown size={12} style={{ color: 'var(--text-muted)' }} />
        </div>
      </div>
    </header>
  )
}
