import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Mail, Menu, Phone, X } from 'lucide-react'
import Logo from '../Logo'
import { PRIMARY_NAV, SITE_CONTACT } from '../../data/revampContent'

function isActive(pathname, href) {
  if (href === '/') return pathname === '/'
  return pathname === href || pathname.startsWith(`${href}/`)
}

export default function RevampHeader() {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()

  return (
    <header className="zo-site-header">
      <div className="zo-topbar">
        <div className="rv-shell zo-topbar-inner">
          <a href={`mailto:${SITE_CONTACT.email}`} className="zo-topbar-email">
            <Mail size={13} aria-hidden />
            {SITE_CONTACT.email}
          </a>
          <div className="zo-topbar-social">
            {SITE_CONTACT.social.filter((s) => s.label === 'Facebook').map((s) => (
              <a key={s.label} href={s.href} target="_blank" rel="noreferrer" aria-label={s.label}>
                {s.label}
              </a>
            ))}
          </div>
        </div>
      </div>

      <div className="zo-navbar">
        <div className="rv-shell zo-navbar-inner">
          <Link to="/" className="zo-logo" aria-label="ZeOrbit home" onClick={() => setOpen(false)}>
            <Logo size={44} />
          </Link>

          <nav className="zo-nav" aria-label="Primary">
            {PRIMARY_NAV.map((item) => (
              <Link
                key={item.label}
                to={item.href}
                className={isActive(pathname, item.href) ? 'active' : undefined}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="zo-nav-actions">
            <a
              className="zo-phone-cta"
              href={`tel:${SITE_CONTACT.phoneTel}`}
              aria-label={`Call ${SITE_CONTACT.phone}`}
            >
              <span className="zo-phone-btn" aria-hidden>
                <Phone size={18} />
              </span>
              <span className="zo-phone-number">{SITE_CONTACT.phone}</span>
            </a>
            <button
              type="button"
              className="zo-mobile-toggle"
              aria-label={open ? 'Close menu' : 'Open menu'}
              onClick={() => setOpen((prev) => !prev)}
            >
              {open ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </div>

      {open ? (
        <nav className="zo-mobile-nav" aria-label="Mobile">
          {PRIMARY_NAV.map((item) => (
            <Link
              key={item.label}
              to={item.href}
              className={isActive(pathname, item.href) ? 'active' : undefined}
              onClick={() => setOpen(false)}
            >
              {item.label}
            </Link>
          ))}
          <a className="zo-mobile-call" href={`tel:${SITE_CONTACT.phoneTel}`} onClick={() => setOpen(false)}>
            Call {SITE_CONTACT.phone}
          </a>
        </nav>
      ) : null}
    </header>
  )
}
