import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  ArrowRight,
  Check,
  ChevronDown,
  ChevronLeft,
  FileText,
  Globe,
  Layout,
  LineChart,
  MapPin,
  Menu,
  Paintbrush,
  Phone,
  RefreshCw,
  Server,
  ShoppingBag,
  Smartphone,
  Sparkles,
  UserRound,
  Wrench,
  X,
} from 'lucide-react'
import Logo from '../Logo'
import { PRIMARY_NAV, SITE_CONTACT } from '../../data/revampContent'
import { scrollToHashId } from '../../hooks/useHashScroll'
import { goToHomepageTop } from '../../utils/goHome'

function isActive(pathname, href) {
  if (href === '/') return pathname === '/'
  return pathname === href || pathname.startsWith(`${href}/`)
}

const COUNTRIES = [
  { code: 'AU', label: 'Australia', flag: '🇦🇺' },
  { code: 'BD', label: 'Bangladesh', flag: '🇧🇩' },
  { code: 'CA', label: 'Canada', flag: '🇨🇦' },
  { code: 'DE', label: 'Germany', flag: '🇩🇪' },
  { code: 'IN', label: 'India', flag: '🇮🇳' },
  { code: 'GB', label: 'United Kingdom', flag: '🇬🇧' },
  { code: 'US', label: 'United States (Global)', flag: '🇺🇸' },
]

function CountryFlag({ code, label, emoji }) {
  const iso = String(code || '').toLowerCase()
  return (
    <span className="zo-util-flag" title={label || code} aria-hidden>
      <img
        className="zo-util-flag-img"
        src={`https://flagcdn.com/w40/${iso}.png`}
        srcSet={`https://flagcdn.com/w40/${iso}.png 1x, https://flagcdn.com/w80/${iso}.png 2x`}
        width={20}
        height={15}
        alt=""
        loading="lazy"
        decoding="async"
        onError={(event) => {
          const img = event.currentTarget
          img.style.display = 'none'
          const fallback = img.parentElement?.querySelector('.zo-util-flag-emoji')
          if (fallback) fallback.hidden = false
        }}
      />
      <span className="zo-util-flag-emoji" hidden>
        {emoji || iso.toUpperCase()}
      </span>
    </span>
  )
}

const ICON_MAP = {
  Globe,
  ShoppingBag,
  Layout,
  RefreshCw,
  Paintbrush,
  Wrench,
  Smartphone,
  Sparkles,
  FileText,
  LineChart,
  MapPin,
  Server,
}

const MEGA_BY_LABEL = {
  Websites: {
    columns: [
      {
        title: 'Hosting',
        items: [
          {
            label: 'Custom Websites',
            href: '/website-designing#business',
            icon: 'Globe',
            blurb: 'Sites built around your brand and conversion goals.',
          },
          {
            label: 'Shopify & Ecommerce',
            href: '/website-designing#ecommerce',
            icon: 'ShoppingBag',
            blurb: 'Stores that sell — design, checkout, and care.',
          },
          {
            label: 'Landing Pages',
            href: '/website-designing#landing',
            icon: 'Layout',
            blurb: 'Focused pages that turn traffic into leads.',
          },
        ],
      },
      {
        title: 'Get Online',
        items: [
          {
            label: 'Website Redesign',
            href: '/website-designing#redesign',
            icon: 'RefreshCw',
            blurb: 'Refresh outdated sites without losing SEO equity.',
          },
          {
            label: 'Care & Maintenance',
            href: '/website-designing#care',
            icon: 'Wrench',
            blurb: 'Updates, security, and ongoing support.',
          },
        ],
      },
      {
        title: 'Design',
        items: [
          {
            label: 'UI / UX Design',
            href: '/website-designing#ux',
            icon: 'Paintbrush',
            blurb: 'Interfaces that feel clear and convert better.',
          },
        ],
      },
    ],
    promo: {
      image: '/showcase/pro/ux-office-monitors.jpg',
      title: 'Talk to our sales team',
      copy: 'Get in touch with our team to find the best solution for you.',
      href: '/contact',
    },
  },
  'Mobile Apps': {
    columns: [
      {
        title: 'Build',
        items: [
          {
            label: 'iOS & Android',
            href: '/mobile-apps#native',
            icon: 'Smartphone',
            blurb: 'Native apps ready for App Store and Play.',
          },
          {
            label: 'Cross-Platform',
            href: '/mobile-apps#cross',
            icon: 'Sparkles',
            blurb: 'One codebase that ships on both platforms.',
          },
        ],
      },
      {
        title: 'Plan',
        items: [
          {
            label: 'App Timeline',
            href: '/mobile-apps#timeline',
            icon: 'FileText',
            blurb: 'How we plan, build, and launch your app.',
          },
          {
            label: 'Mobile UX / UI',
            href: '/mobile-apps#ux',
            icon: 'Paintbrush',
            blurb: 'Mobile-first flows that users finish.',
          },
        ],
      },
    ],
    promo: {
      image: '/showcase/mobile-phones-grid.png',
      title: 'Talk to our sales team',
      copy: 'Get in touch with our team to find the best solution for you.',
      href: '/contact',
    },
  },
  'SEO & Ads': {
    columns: [
      {
        title: 'SEO',
        items: [
          {
            label: 'Technical SEO',
            href: '/seo-ppc#seo',
            icon: 'Server',
            blurb: 'Crawl health, speed, and indexation fixes.',
          },
          {
            label: 'Local SEO',
            href: '/seo-ppc#local',
            icon: 'MapPin',
            blurb: 'Maps, citations, and city-level visibility.',
          },
          {
            label: 'Content SEO',
            href: '/seo-ppc#content',
            icon: 'FileText',
            blurb: 'Pages and posts that rank and convert.',
          },
        ],
      },
      {
        title: 'Ads',
        items: [
          {
            label: 'Google Ads',
            href: '/seo-ppc#ads',
            icon: 'LineChart',
            blurb: 'Search and display campaigns that pay back.',
          },
          {
            label: 'Social Ads',
            href: '/seo-ppc#social-ads',
            icon: 'Sparkles',
            blurb: 'Paid social that reaches the right audience.',
          },
        ],
      },
      {
        title: 'More',
        items: [
          {
            label: 'Blog & Insights',
            href: '/seo-ppc#blog',
            icon: 'FileText',
            blurb: 'Guides and updates from the ZeOrbit team.',
          },
          {
            label: 'Pricing',
            href: '/seo-ppc#pricing',
            icon: 'Layout',
            blurb: 'Clear packages for websites, apps, and growth.',
          },
        ],
      },
    ],
    promo: {
      image: '/showcase/growth-charts-blue.png',
      title: 'Talk to our sales team',
      copy: 'Get in touch with our team to find the best solution for you.',
      href: '/contact',
    },
  },
  'Custom Software': {
    columns: [
      {
        title: 'Platforms',
        items: [
          {
            label: 'Dashboards',
            href: '/custom-software#platforms',
            icon: 'Layout',
            blurb: 'Internal tools your team actually uses.',
          },
          {
            label: 'CRM & Workflows',
            href: '/custom-software#crm',
            icon: 'Server',
            blurb: 'Systems that match how you sell and deliver.',
          },
        ],
      },
      {
        title: 'Connect',
        items: [
          {
            label: 'API Integrations',
            href: '/custom-software#integrations',
            icon: 'Sparkles',
            blurb: 'Connect the tools you already rely on.',
          },
          {
            label: 'Automation',
            href: '/custom-software#automation',
            icon: 'Wrench',
            blurb: 'Cut busywork with reliable automations.',
          },
        ],
      },
    ],
    promo: {
      image: '/showcase/web-dashboard-product.webp',
      title: 'Talk to our sales team',
      copy: 'Get in touch with our team to find the best solution for you.',
      href: '/contact',
    },
  },
}

const MAIN_NAV = PRIMARY_NAV.filter((item) => item.label !== 'Contact')

export default function RevampHeader() {
  const [open, setOpen] = useState(false)
  const [openMenu, setOpenMenu] = useState(null)
  const [utilityOpen, setUtilityOpen] = useState(null)
  const [country, setCountry] = useState(COUNTRIES.find((c) => c.code === 'US'))
  const [mobilePanel, setMobilePanel] = useState(null)
  const headerRef = useRef(null)
  const { pathname, hash } = useLocation()
  const navigate = useNavigate()

  const activeMega = useMemo(() => (openMenu ? MEGA_BY_LABEL[openMenu] : null), [openMenu])

  const onHome = (event) => {
    event.preventDefault()
    closeMobile()
    goToHomepageTop(navigate, pathname)
  }

  useEffect(() => {
    setOpen(false)
    setOpenMenu(null)
    setUtilityOpen(null)
    setMobilePanel(null)
  }, [pathname, hash])

  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : ''
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

  useEffect(() => {
    if (!openMenu && !utilityOpen) return undefined
    const onPointer = (event) => {
      if (!headerRef.current?.contains(event.target)) {
        setOpenMenu(null)
        setUtilityOpen(null)
      }
    }
    const onKey = (event) => {
      if (event.key === 'Escape') {
        setOpenMenu(null)
        setUtilityOpen(null)
      }
    }
    document.addEventListener('pointerdown', onPointer)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('pointerdown', onPointer)
      document.removeEventListener('keydown', onKey)
    }
  }, [openMenu, utilityOpen])

  const toggleMenu = (label) => {
    setUtilityOpen(null)
    setOpenMenu((current) => (current === label ? null : label))
  }

  const toggleUtility = (key) => {
    setOpenMenu(null)
    setUtilityOpen((current) => (current === key ? null : key))
  }

  const closeMobile = () => {
    setOpen(false)
    setMobilePanel(null)
  }

  const closeMegaLink = (href) => {
    setOpenMenu(null)
    const id = href.split('#')[1]
    if (id) window.setTimeout(() => scrollToHashId(id), 40)
  }

  // Always light chrome so the logo stays readable over the dark full-bleed hero video.
  const onDark = false
  const headerClass = [
    'zo-site-header',
    'zo-host-header',
    'is-scrolled',
    open ? 'is-menu-open' : '',
    openMenu ? 'is-mega-open' : '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <header ref={headerRef} className={headerClass}>
      <div className="zo-topbar">
        <div className="zo-topbar-inner">
          <a
            className="zo-topbar-email"
            href={`mailto:${SITE_CONTACT.email}`}
            style={{ color: '#ffffff', WebkitTextFillColor: '#ffffff' }}
          >
            {SITE_CONTACT.email}
          </a>
          <a
            className="zo-topbar-phone"
            href={`tel:${SITE_CONTACT.phoneTel}`}
            aria-label={`Call ${SITE_CONTACT.phone}`}
          >
            <Phone size={13} strokeWidth={2.4} aria-hidden />
            <span>{SITE_CONTACT.phone}</span>
          </a>
        </div>
      </div>

      <div className="zo-host-bar">
        <div className="zo-host-bar-inner">
          <div className="zo-brand">
            <Link to="/" className="zo-logo" aria-label="ZeOrbit home" onClick={onHome}>
              <Logo size={36} onDark={onDark} />
            </Link>
          </div>

          <nav className="zo-nav" aria-label="Primary">
            {MAIN_NAV.map((item) => {
              const hasChildren = Boolean(item.children?.length) && Boolean(MEGA_BY_LABEL[item.label])
              const isOpen = openMenu === item.label
              const active = isActive(pathname, item.href)

              if (!hasChildren) {
                return (
                  <div key={item.label} className="zo-nav-item">
                    <Link
                      to={item.href}
                      className={active ? 'active' : undefined}
                      onClick={(event) => {
                        setOpenMenu(null)
                        if (item.href === '/') {
                          event.preventDefault()
                          goToHomepageTop(navigate, pathname)
                        }
                      }}
                    >
                      {item.label}
                    </Link>
                  </div>
                )
              }

              return (
                <div key={item.label} className={`zo-nav-item has-children${isOpen ? ' is-open' : ''}`}>
                  <button
                    type="button"
                    className={`zo-nav-trigger${active || isOpen ? ' active' : ''}`}
                    aria-expanded={isOpen}
                    aria-haspopup="true"
                    onClick={() => toggleMenu(item.label)}
                  >
                    <span>{item.label}</span>
                    <ChevronDown size={14} className="zo-nav-caret" aria-hidden />
                  </button>
                </div>
              )
            })}
          </nav>

          <div className="zo-host-actions">
            <div className={`zo-util-item${utilityOpen === 'country' ? ' is-open' : ''}`}>
              <button
                type="button"
                className="zo-util-trigger zo-lang-trigger"
                aria-expanded={utilityOpen === 'country'}
                aria-haspopup="listbox"
                onClick={() => toggleUtility('country')}
              >
                <CountryFlag code={country.code} label={country.label} emoji={country.flag} />
                <span className="zo-util-label">EN</span>
                <ChevronDown size={12} className="zo-util-caret" aria-hidden />
              </button>
              {utilityOpen === 'country' ? (
                <div className="zo-util-dropdown zo-country-dropdown" role="listbox" aria-label="Select your country">
                  <p className="zo-util-dropdown-kicker">Select your country</p>
                  <ul className="zo-country-list">
                    {COUNTRIES.map((item) => {
                      const selected = item.code === country.code
                      return (
                        <li key={item.code}>
                          <button
                            type="button"
                            role="option"
                            aria-selected={selected}
                            className={`zo-country-option${selected ? ' is-selected' : ''}`}
                            onClick={() => {
                              setCountry(item)
                              setUtilityOpen(null)
                            }}
                          >
                            <CountryFlag code={item.code} label={item.label} emoji={item.flag} />
                            <span>{item.label}</span>
                            {selected ? <Check size={16} className="zo-country-check" aria-hidden /> : null}
                          </button>
                        </li>
                      )
                    })}
                  </ul>
                  <p className="zo-country-footer">
                    Serving clients <strong>nationwide</strong>
                  </p>
                </div>
              ) : null}
            </div>

            <a className="zo-nav-icon-btn" href={`tel:${SITE_CONTACT.phoneTel}`} aria-label={`Call ${SITE_CONTACT.phone}`}>
              <Phone size={18} strokeWidth={2.2} />
            </a>
            <Link to="/contact" className="zo-nav-icon-btn" aria-label="Contact ZeOrbit" onClick={() => setOpenMenu(null)}>
              <UserRound size={18} strokeWidth={2.2} />
            </Link>
            <button
              type="button"
              className="zo-mobile-toggle"
              aria-label={open ? 'Close menu' : 'Open menu'}
              aria-expanded={open}
              onClick={() => {
                setOpen((prev) => !prev)
                setMobilePanel(null)
                setUtilityOpen(null)
                setOpenMenu(null)
              }}
            >
              {open ? <X size={22} strokeWidth={2.6} /> : <Menu size={22} strokeWidth={2.6} />}
            </button>
          </div>
        </div>
      </div>

      {activeMega ? (
        <div className="zo-mega zo-host-mega" role="menu" aria-label={`${openMenu} menu`}>
          <div className="zo-mega-grid">
            {activeMega.columns.map((column) => (
              <div key={column.title} className="zo-mega-col">
                <p className="zo-mega-col-title">{column.title}</p>
                <div className="zo-mega-col-items">
                  {column.items.map((child) => {
                    const Icon = ICON_MAP[child.icon] || Globe
                    return (
                      <Link
                        key={child.label}
                        to={child.href}
                        role="menuitem"
                        className="zo-mega-card"
                        onClick={() => closeMegaLink(child.href)}
                      >
                        <span className="zo-mega-card-icon" aria-hidden>
                          <Icon size={18} strokeWidth={2} />
                        </span>
                        <span className="zo-mega-card-copy">
                          <strong>{child.label}</strong>
                          <small>{child.blurb}</small>
                        </span>
                        <ArrowRight size={16} className="zo-mega-card-arrow" aria-hidden />
                      </Link>
                    )
                  })}
                </div>
              </div>
            ))}
            <Link to={activeMega.promo.href} className="zo-mega-promo" onClick={() => setOpenMenu(null)}>
              <img src={activeMega.promo.image} alt="" className="zo-mega-promo-media" />
              <span className="zo-mega-promo-body">
                <strong>{activeMega.promo.title}</strong>
                <small>{activeMega.promo.copy}</small>
                <span className="zo-mega-promo-arrow" aria-hidden>
                  <ArrowRight size={16} />
                </span>
              </span>
            </Link>
          </div>
        </div>
      ) : null}

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
              {MAIN_NAV.map((item) => {
                const hasChildren = Boolean(item.children?.length)
                if (!hasChildren) {
                  return (
                    <div key={item.label} className="zo-mobile-group">
                      <Link
                        to={item.href}
                        className={isActive(pathname, item.href) ? 'active' : undefined}
                        onClick={(event) => {
                          if (item.href === '/') {
                            event.preventDefault()
                            onHome(event)
                            return
                          }
                          closeMobile()
                        }}
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
              <a className="zo-mobile-call" href={`tel:${SITE_CONTACT.phoneTel}`} onClick={closeMobile}>
                Call {SITE_CONTACT.phone}
              </a>
              <Link to="/contact" className="zo-mobile-call is-secondary" onClick={closeMobile}>
                Contact us
              </Link>
            </>
          )}
        </nav>
      ) : null}
    </header>
  )
}
