import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Mail, Phone } from 'lucide-react'
import Logo from './Logo'
import SocialBrandIcon from './SocialBrandIcon'
import { SITE_CONTACT } from '../data/revampContent'
import { goToHomepageTop } from '../utils/goHome'

const SERVICES = [
  { label: 'Custom Websites', to: '/website-designing#business' },
  { label: 'Shopify & Ecommerce', to: '/website-designing#ecommerce' },
  { label: 'Mobile Apps', to: '/mobile-apps' },
  { label: 'SEO & Ads', to: '/seo-ppc' },
  { label: 'API Integrations', to: '/custom-software#integrations' },
]

const RESOURCES = [
  { label: 'Blog', to: '/blog' },
  { label: 'Portfolio', to: '/portfolio' },
  { label: 'Areas We Serve', to: '/contact#areas' },
  { label: 'App Timeline', to: '/mobile-apps#timeline' },
  { label: 'Website Care', to: '/website-designing#care' },
]

const COMPANY = [
  { label: 'About ZeOrbit', to: '/' },
  { label: 'Contact', to: '/contact' },
  { label: 'Privacy Policy', to: '/privacy-policy' },
  { label: "Let's Talk", to: '/contact' },
]

export default function SiteFooter() {
  const year = new Date().getFullYear()
  const navigate = useNavigate()
  const { pathname } = useLocation()

  return (
    <footer id="about" className="zo-site-footer">
      <section className="zo-site-prefoot" aria-label="Get started">
        <div className="rv-shell zo-site-prefoot-inner">
          <div className="zo-site-prefoot-copy">
            <p className="zo-site-prefoot-kicker">Next step</p>
            <h2 className="zo-site-prefoot-h">Want a clearer plan for your site?</h2>
            <p className="zo-site-prefoot-p">
              Talk with ZeOrbit about web design, SEO, and local visibility — no pressure, just a practical next step.
            </p>
          </div>
          <div className="zo-site-prefoot-actions">
            <a className="zo-article-call" href={`tel:${SITE_CONTACT.phoneTel}`}>
              CALL NOW : {SITE_CONTACT.phone}
            </a>
            <Link className="zo-site-prefoot-quote" to="/contact">
              Get a Free Quote
            </Link>
          </div>
        </div>
      </section>

      <div className="zo-site-footer-trust" aria-label="What we help with">
        <div className="rv-shell zo-site-footer-trust-inner">
          <span className="zo-site-footer-trust-label">Trusted by businesses looking to improve</span>
          <ul className="zo-site-footer-trust-list">
            <li>SEO</li>
            <li>Performance</li>
            <li>Web Design</li>
            <li>Digital Growth</li>
          </ul>
        </div>
      </div>

      <div className="zo-site-footer-stage">
        <div className="rv-shell zo-site-footer-main">
          <div className="zo-site-footer-brand">
            <Link
              to="/"
              className="zo-site-footer-logo"
              aria-label="ZeOrbit home"
              onClick={(event) => {
                event.preventDefault()
                goToHomepageTop(navigate, pathname)
              }}
            >
              <Logo size={40} />
            </Link>
            <p>
              Helping businesses improve their visibility, websites, and digital growth with smarter SEO tools and
              strategies.
            </p>
            <div className="zo-site-footer-social">
              {SITE_CONTACT.social.map((s) => (
                <a
                  key={s.label}
                  href={s.href}
                  target="_blank"
                  rel="noreferrer"
                  aria-label={s.label}
                  className={`zo-social is-${s.label.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  <SocialBrandIcon label={s.label} />
                </a>
              ))}
            </div>
            <div className="zo-site-footer-quick">
              <a href={`tel:${SITE_CONTACT.phoneTel}`}>
                <Phone size={15} strokeWidth={2.2} />
                {SITE_CONTACT.phone}
              </a>
              <a href={`mailto:${SITE_CONTACT.email}`}>
                <Mail size={15} strokeWidth={2.2} />
                {SITE_CONTACT.email}
              </a>
              <span className="zo-site-footer-address">
                {SITE_CONTACT.address.line1}, {SITE_CONTACT.address.line2}
              </span>
            </div>
          </div>

          <div className="zo-site-footer-col">
            <h4>Services</h4>
            <ul className="zo-site-footer-list">
              {SERVICES.map((item) => (
                <li key={item.label}>
                  <Link to={item.to}>{item.label}</Link>
                </li>
              ))}
            </ul>
          </div>

          <div className="zo-site-footer-col">
            <h4>Resources</h4>
            <ul className="zo-site-footer-list">
              {RESOURCES.map((item) => (
                <li key={item.label}>
                  <Link to={item.to}>{item.label}</Link>
                </li>
              ))}
            </ul>
          </div>

          <div className="zo-site-footer-col">
            <h4>Company</h4>
            <ul className="zo-site-footer-list">
              {COMPANY.map((item) => (
                <li key={item.label}>
                  <Link to={item.to}>{item.label}</Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="zo-site-footer-bottom">
        <div className="rv-shell zo-site-footer-bottom-inner">
          <p>© {year} ZeOrbit. All Rights Reserved.</p>
        </div>
      </div>
    </footer>
  )
}
