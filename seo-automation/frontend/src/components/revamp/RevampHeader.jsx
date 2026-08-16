import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import Logo from '../Logo'
import { PRIMARY_NAV } from '../../data/revampContent'

export default function RevampHeader() {
  const [open, setOpen] = useState(false)
  const authed = typeof window !== 'undefined' && localStorage.getItem('seo_auth') === 'true'

  return (
    <header className="rv-header">
      <div className="rv-header-inner">
        <a href="/" className="rv-logo-wrap" aria-label="ZeOrbit home">
          <Logo size={28} onDark />
        </a>

        <nav className="rv-desktop-nav" aria-label="Primary">
          {PRIMARY_NAV.map((item) => (
            <a key={item.label} href={item.href}>{item.label}</a>
          ))}
        </nav>

        <div className="rv-header-actions">
          {authed ? (
            <a className="btn btn-primary" href="/content">Dashboard</a>
          ) : (
            <>
              <a className="rv-link-button" href="/login">Log in</a>
              <a className="btn btn-primary" href="/register">Get started</a>
            </>
          )}
          <button
            type="button"
            className="rv-mobile-toggle"
            aria-label={open ? 'Close menu' : 'Open menu'}
            onClick={() => setOpen((prev) => !prev)}
          >
            {open ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </div>

      {open ? (
        <nav className="rv-mobile-nav" aria-label="Mobile">
          {PRIMARY_NAV.map((item) => (
            <a key={item.label} href={item.href} onClick={() => setOpen(false)}>{item.label}</a>
          ))}
          {authed ? (
            <a className="btn btn-primary" href="/content" onClick={() => setOpen(false)}>Dashboard</a>
          ) : (
            <>
              <a href="/login" onClick={() => setOpen(false)}>Log in</a>
              <a className="btn btn-primary" href="/register" onClick={() => setOpen(false)}>Get started</a>
            </>
          )}
        </nav>
      ) : null}
    </header>
  )
}
