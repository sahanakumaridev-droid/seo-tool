import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import Logo from '../Logo'
import { PRIMARY_NAV } from '../../data/revampContent'

export default function RevampHeader() {
  const [open, setOpen] = useState(false)

  return (
    <header className="rv-header">
      <div className="rv-header-inner">
        <a href="/" className="rv-logo-wrap" aria-label="ZeOrbit home">
          <Logo size={32} />
        </a>

        <nav className="rv-desktop-nav" aria-label="Primary">
          {PRIMARY_NAV.map((item) => (
            <a key={item.label} href={item.href}>{item.label}</a>
          ))}
        </nav>

        <div className="rv-header-actions">
          <a className="rv-link-button" href="/login">LOG IN</a>
          <a className="btn btn-primary" href="/register">TRY FREE FOR 7 DAYS</a>
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
          <a href="/login" onClick={() => setOpen(false)}>LOG IN</a>
          <a className="btn btn-primary" href="/register" onClick={() => setOpen(false)}>TRY FREE FOR 7 DAYS</a>
        </nav>
      ) : null}
    </header>
  )
}
