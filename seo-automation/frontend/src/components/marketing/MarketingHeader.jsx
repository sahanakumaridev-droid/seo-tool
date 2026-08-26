import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Logo from '../Logo'

const NAV = [
  { label: 'Features', href: '#features' },
  { label: 'Data', href: '#data' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'FAQ', href: '#faq' },
]

/**
 * Marketing header matched to zeorbit.com host chrome:
 * black email strip + main bar (logo | nav | actions).
 */
export default function MarketingHeader() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header className={`seo-site-header${scrolled ? ' is-scrolled' : ''}`}>
      <div className="seo-site-topbar">
        <div className="seo-site-topbar-inner">
          <a className="seo-site-topbar-email" href="mailto:info@zeorbit.com">
            info@zeorbit.com
          </a>
        </div>
      </div>
      <div className="seo-site-bar">
        <div className="seo-site-bar-inner">
          <Link to="/" className="seo-site-brand" aria-label="ZeOrbit home">
            <Logo size={34} onDark={!scrolled} />
          </Link>
          <nav className="seo-site-nav" aria-label="Primary">
            {NAV.map((item) => (
              <a key={item.href} href={item.href}>
                {item.label}
              </a>
            ))}
          </nav>
          <div className="seo-site-actions">
            <Link to="/login" className="seo-site-login">
              Log in
            </Link>
            <Link to="/register" className="seo-site-cta">
              Start free trial
            </Link>
          </div>
        </div>
      </div>
    </header>
  )
}
