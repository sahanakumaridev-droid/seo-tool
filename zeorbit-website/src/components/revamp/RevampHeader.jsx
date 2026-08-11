import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ChevronDown, ChevronLeft, Menu, Phone, X } from 'lucide-react'
import Logo from '../Logo'
import { PRIMARY_NAV, SITE_CONTACT } from '../../data/revampContent'

function isActive(pathname, href) {
  if (href === '/') return pathname === '/'
  return pathname === href || pathname.startsWith(`${href}/`)
}

const HEADER_SOCIAL = SITE_CONTACT.social.filter((s) =>
  ['Facebook', 'Instagram', 'YouTube', 'X', 'LinkedIn'].includes(s.label),
)

const SOCIAL_PATHS = {
  Facebook: 'M14 13.5h2.5l1-4H14v-2c0-1.03 0-2 2-2h1.5V2.14c-.326-.043-1.557-.14-2.857-.14C11.928 2 10 3.657 10 6.7v2.8H7v4h3V22h4z',
  Instagram:
    'M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm10 2H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm-5 3.5A4.5 4.5 0 1 1 7.5 12 4.5 4.5 0 0 1 12 7.5zm0 2A2.5 2.5 0 1 0 14.5 12 2.5 2.5 0 0 0 12 9.5zM17.5 6.75a1.25 1.25 0 1 1-1.25 1.25A1.25 1.25 0 0 1 17.5 6.75z',
  YouTube:
    'M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.5 12 3.5 12 3.5s-7.5 0-9.4.6A3 3 0 0 0 .5 6.2 31.5 31.5 0 0 0 0 12a31.5 31.5 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.6 9.4.6 9.4.6s7.5 0 9.4-.6a3 3 0 0 0 2.1-2.1A31.5 31.5 0 0 0 24 12a31.5 31.5 0 0 0-.5-5.8zM9.8 15.5v-7l6.2 3.5z',
  X: 'M18.244 2H21.5l-7.23 8.26L22.5 22h-6.59l-5.16-6.74L5.2 22H1.94l7.73-8.83L1.5 2h6.75l4.66 6.16L18.244 2zm-1.16 18h1.82L7.08 3.94H5.12L17.084 20z',
  LinkedIn:
    'M6.94 6.5a1.94 1.94 0 1 1-1.94-1.94A1.94 1.94 0 0 1 6.94 6.5zM7 9.25H3V21h4zm6.5 0h-3.8V21h3.8v-6.1c0-2.3 2.9-2.5 2.9 0V21H20v-7.1c0-5.1-5.5-4.9-6.5-2.4z',
}

export default function RevampHeader() {
  const [open, setOpen] = useState(false)
  const [openMenu, setOpenMenu] = useState(null)
  const [mobilePanel, setMobilePanel] = useState(null)
  const [scrolled, setScrolled] = useState(false)
  const headerRef = useRef(null)
  const { pathname } = useLocation()

  useEffect(() => {
    setOpen(false)
    setOpenMenu(null)
    setMobilePanel(null)
  }, [pathname])

  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : ''
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    if (!openMenu) return undefined
    const onPointer = (event) => {
      if (!headerRef.current?.contains(event.target)) setOpenMenu(null)
    }
    const onKey = (event) => {
      if (event.key === 'Escape') setOpenMenu(null)
    }
    document.addEventListener('pointerdown', onPointer)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('pointerdown', onPointer)
      document.removeEventListener('keydown', onKey)
    }
  }, [openMenu])

  const toggleMenu = (label) => {
    setOpenMenu((current) => (current === label ? null : label))
  }

  const closeMobile = () => {
    setOpen(false)
    setMobilePanel(null)
  }

  const headerClass = [
    'zo-site-header',
    'is-transparent',
    scrolled || open ? 'is-scrolled' : '',
    open ? 'is-menu-open' : '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <header ref={headerRef} className={headerClass}>
      <div className="zo-navbar">
        <div className="zo-navbar-inner">
          <div className="zo-brand">
            <Link to="/" className="zo-logo" aria-label="ZeOrbit home" onClick={closeMobile}>
              <Logo size={48} onDark={!scrolled && !open} />
            </Link>
          </div>

          <nav className="zo-nav" aria-label="Primary">
            {PRIMARY_NAV.map((item) => {
              const hasChildren = Boolean(item.children?.length)
              const isOpen = openMenu === item.label
              const active = isActive(pathname, item.href)

              if (!hasChildren) {
                return (
                  <div key={item.label} className="zo-nav-item">
                    <Link to={item.href} className={active ? 'active' : undefined} onClick={() => setOpenMenu(null)}>
                      {item.label}
                    </Link>
                  </div>
                )
              }

              return (
                <div key={item.label} className={`zo-nav-item${isOpen ? ' is-open' : ''}`}>
                  <button
                    type="button"
                    className={`zo-nav-trigger${active || isOpen ? ' active' : ''}`}
                    aria-expanded={isOpen}
                    aria-haspopup="true"
                    onClick={() => toggleMenu(item.label)}
                  >
                    {item.label}
                    <ChevronDown size={13} className="zo-nav-caret" aria-hidden />
                  </button>
                  {isOpen ? (
                    <div className="zo-dropdown" role="menu">
                      <Link to={item.href} className="zo-dropdown-parent" onClick={() => setOpenMenu(null)}>
                        Overview
                      </Link>
                      {item.children.map((child) => (
                        <Link key={child.label} to={child.href} role="menuitem" onClick={() => setOpenMenu(null)}>
                          {child.label}
                        </Link>
                      ))}
                    </div>
                  ) : null}
                </div>
              )
            })}
          </nav>

          <div className="zo-nav-actions">
            <a
              className="zo-phone-cta"
              href={`tel:${SITE_CONTACT.phoneTel}`}
              aria-label={`Call ${SITE_CONTACT.phone}`}
            >
              <span className="zo-phone-btn" aria-hidden>
                <Phone size={20} strokeWidth={2.6} />
              </span>
              <span className="zo-phone-number">{SITE_CONTACT.phone}</span>
            </a>
            <button
              type="button"
              className="zo-mobile-toggle"
              aria-label={open ? 'Close menu' : 'Open menu'}
              aria-expanded={open}
              onClick={() => {
                setOpen((prev) => !prev)
                setMobilePanel(null)
              }}
            >
              {open ? <X size={22} strokeWidth={2.6} /> : <Menu size={22} strokeWidth={2.6} />}
            </button>
          </div>
        </div>
      </div>

      {open ? (
        <nav className="zo-mobile-nav" aria-label="Mobile">
          {mobilePanel ? (
            <div className="zo-mobile-panel">
              <button type="button" className="zo-mobile-back" onClick={() => setMobilePanel(null)}>
                <ChevronLeft size={18} strokeWidth={2.4} />
                Back
              </button>
              <p className="zo-mobile-panel-title">{mobilePanel.label}</p>
              <Link to={mobilePanel.href} className="zo-mobile-panel-link" onClick={closeMobile}>
                Overview
              </Link>
              {mobilePanel.children.map((child) => (
                <Link key={child.label} to={child.href} className="zo-mobile-panel-link" onClick={closeMobile}>
                  {child.label}
                </Link>
              ))}
            </div>
          ) : (
            <>
              {PRIMARY_NAV.map((item) => {
                const hasChildren = Boolean(item.children?.length)
                if (!hasChildren) {
                  return (
                    <div key={item.label} className="zo-mobile-group">
                      <Link
                        to={item.href}
                        className={isActive(pathname, item.href) ? 'active' : undefined}
                        onClick={closeMobile}
                      >
                        {item.label}
                      </Link>
                    </div>
                  )
                }

                return (
                  <div key={item.label} className="zo-mobile-group">
                    <button
                      type="button"
                      className={`zo-mobile-parent${isActive(pathname, item.href) ? ' active' : ''}`}
                      onClick={() => setMobilePanel(item)}
                    >
                      <span>{item.label}</span>
                      <ChevronDown size={16} className="zo-mobile-caret is-forward" aria-hidden />
                    </button>
                  </div>
                )
              })}
              <div className="zo-mobile-social">
                {HEADER_SOCIAL.map((item) => (
                  <a
                    key={item.label}
                    href={item.href}
                    target="_blank"
                    rel="noreferrer"
                    aria-label={item.label}
                    className={`is-${item.label.toLowerCase()}`}
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path fill="currentColor" d={SOCIAL_PATHS[item.label] || SOCIAL_PATHS.X} />
                    </svg>
                  </a>
                ))}
              </div>
              <a className="zo-mobile-call" href={`tel:${SITE_CONTACT.phoneTel}`} onClick={closeMobile}>
                Call {SITE_CONTACT.phone}
              </a>
            </>
          )}
        </nav>
      ) : null}
    </header>
  )
}
