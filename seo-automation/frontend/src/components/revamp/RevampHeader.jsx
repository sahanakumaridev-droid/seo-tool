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
          <a className="rv-link-button" href="#contact">Contact</a>
          <button type="button" className="btn btn-primary">Start a Project</button>
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
          <button type="button" className="btn btn-primary">Start a Project</button>
        </nav>
      ) : null}
    </header>
  )
}
