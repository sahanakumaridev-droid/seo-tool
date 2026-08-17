import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ChevronDown, ChevronLeft, Menu, Phone, X } from 'lucide-react'
import Logo from '../Logo'
import SocialBrandIcon from '../SocialBrandIcon'
import { PRIMARY_NAV, SITE_CONTACT } from '../../data/revampContent'
import { scrollToHashId } from '../../hooks/useHashScroll'

function isActive(pathname, href) {
  if (href === '/') return pathname === '/'
  return pathname === href || pathname.startsWith(`${href}/`)
}

function socialSlug(label) {
  return label.toLowerCase().replace(/\s+/g, '-')
}

const HEADER_SOCIAL = SITE_CONTACT.social.filter((s) =>
  ['Facebook', 'Instagram', 'LinkedIn', 'YouTube', 'X', 'Pinterest', 'Apple Maps', 'Google Maps', 'Yelp'].includes(
    s.label,
  ),
)


export default function RevampHeader() {
  const [open, setOpen] = useState(false)
  const [openMenu, setOpenMenu] = useState(null)
  const [mobilePanel, setMobilePanel] = useState(null)
  const headerRef = useRef(null)
  const { pathname, hash } = useLocation()

  useEffect(() => {
    setOpen(false)
    setOpenMenu(null)
    setMobilePanel(null)
  }, [pathname, hash])

  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : ''
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

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

  const headerClass = ['zo-site-header', 'is-solid', open ? 'is-menu-open' : ''].filter(Boolean).join(' ')

  return (
    <header ref={headerRef} className={headerClass}>
      <div className="zo-topbar" aria-label="Social links">
        <div className="zo-topbar-inner">
          <a className="zo-topbar-tagline" href={`mailto:${SITE_CONTACT.email}`}>
            {SITE_CONTACT.email}
          </a>
          <div className="zo-topbar-social">
            {HEADER_SOCIAL.map((item) => (
              <a
                key={item.label}
                href={item.href}
                target="_blank"
                rel="noreferrer"
                aria-label={item.label}
                className={`zo-topbar-social-link is-${socialSlug(item.label)}`}
              >
                <SocialBrandIcon label={item.label} />
              </a>
            ))}
          </div>
        </div>
      </div>

      <div className="zo-navbar">
        <div className="zo-navbar-inner">
          <div className="zo-brand">
            <Link to="/" className="zo-logo" aria-label="ZeOrbit home" onClick={closeMobile}>
              <Logo size={48} onDark={false} />
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
                <div
                  key={item.label}
                  className={`zo-nav-item has-children${isOpen ? ' is-open' : ''}`}
                  onMouseEnter={() => setOpenMenu(item.label)}
                  onMouseLeave={() => setOpenMenu(null)}
                >
                  <div className="zo-nav-parent">
                    <Link
                      to={item.href}
                      className={`zo-nav-parent-link${active ? ' active' : ''}`}
                      onClick={() => setOpenMenu(null)}
                    >
                      {item.label}
                    </Link>
                    <button
                      type="button"
                      className={`zo-nav-caret-btn${active || isOpen ? ' active' : ''}`}
                      aria-expanded={isOpen}
                      aria-label={`${item.label} sections`}
                      onClick={(event) => {
                        event.preventDefault()
                        event.stopPropagation()
                        toggleMenu(item.label)
                      }}
                    >
                      <ChevronDown size={13} className="zo-nav-caret" aria-hidden />
                    </button>
                  </div>
                  {isOpen ? (
                    <div className="zo-dropdown" role="menu">
                      {item.children.map((child) => (
                        <Link
                          key={child.label}
                          to={child.href}
                          role="menuitem"
                          onClick={() => {
                            setOpenMenu(null)
                            const id = child.href.split('#')[1]
                            if (id) window.setTimeout(() => scrollToHashId(id), 40)
                          }}
                        >
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
              {mobilePanel.children.map((child) => (
                <Link
                  key={child.label}
                  to={child.href}
                  className="zo-mobile-panel-link"
                  onClick={() => {
                    closeMobile()
                    const id = child.href.split('#')[1]
                    if (id) window.setTimeout(() => scrollToHashId(id), 80)
                  }}
                >
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
                  <div key={item.label} className="zo-mobile-group is-split">
                    <Link
                      to={item.href}
                      className={`zo-mobile-parent-link${isActive(pathname, item.href) ? ' active' : ''}`}
                      onClick={closeMobile}
                    >
                      {item.label}
                    </Link>
                    <button
                      type="button"
                      className="zo-mobile-parent-more"
                      aria-label={`${item.label} sections`}
                      onClick={() => setMobilePanel(item)}
                    >
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
                    className={`is-${socialSlug(item.label)}`}
                  >
                    <SocialBrandIcon label={item.label} />
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
