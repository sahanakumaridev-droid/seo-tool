import { Link } from 'react-router-dom'
import Logo from '../Logo'
import SocialBrandIcon from '../SocialBrandIcon'

const COLUMNS = [
  {
    title: 'Product',
    items: [
      { label: 'Features', href: '#features' },
      { label: 'Keyword Research', to: '/keywords' },
      { label: 'Site Audit', to: '/site-audit' },
      { label: 'Rank Tracker', to: '/rankings' },
      { label: 'Content Tools', to: '/content' },
      { label: 'Pricing', href: '#pricing' },
    ],
  },
  {
    title: 'Workspace',
    items: [
      { label: 'Dashboard', to: '/dashboard' },
      { label: 'Articles', to: '/articles' },
      { label: 'Leads', to: '/leads' },
      { label: 'Google Ads', to: '/google-ads' },
      { label: 'Integrations', to: '/integrations' },
    ],
  },
  {
    title: 'Company',
    items: [
      { label: 'ZeOrbit.com', href: 'https://zeorbit.com/', external: true },
      { label: 'Areas We Serve', href: 'https://zeorbit.com/areas', external: true },
      { label: 'Contact', href: 'https://zeorbit.com/contact', external: true },
      { label: 'Log in', to: '/login' },
      { label: 'Start free trial', to: '/register' },
    ],
  },
  {
    title: 'Legal',
    items: [
      { label: 'Privacy Policy', href: 'https://zeorbit.com/privacy-policy', external: true },
      { label: 'Terms', href: 'https://zeorbit.com/', external: true },
    ],
  },
]

/** Same social set as zeorbit.com SiteFooter */
const SOCIAL = [
  { label: 'Facebook', href: 'https://www.facebook.com/zeorbit.web.designers.mobileapp.developers' },
  { label: 'Instagram', href: 'https://www.instagram.com/zeorbit/' },
  { label: 'LinkedIn', href: 'https://www.linkedin.com/company/zeorbit/' },
  { label: 'YouTube', href: 'https://www.youtube.com/@ZeOrbit-Firm' },
  { label: 'X', href: 'https://twitter.com/orbit_ze' },
  { label: 'Pinterest', href: 'https://www.pinterest.com/zeorbitsd/' },
  { label: 'Apple Maps', href: 'https://maps.apple/p/VA-_LREgJ5PzDV' },
  { label: 'Google Maps', href: 'https://maps.app.goo.gl/teVefHUc3yycwkcA7' },
  { label: 'Yelp', href: 'https://www.yelp.com/biz/zeorbit-san-diego-2' },
]

function FooterLink({ item }) {
  if (item.to) {
    return <Link to={item.to}>{item.label}</Link>
  }
  if (item.external) {
    return (
      <a href={item.href} target="_blank" rel="noreferrer">
        {item.label}
      </a>
    )
  }
  return <a href={item.href}>{item.label}</a>
}

/**
 * Marketing footer matched to zeorbit.com host footer:
 * logo-blue accent bar, link columns, logo + social icons, legal row.
 */
export default function MarketingFooter() {
  const year = new Date().getFullYear()

  return (
    <footer className="seo-site-footer">
      <div className="seo-site-footer-accent" aria-hidden />

      <div className="seo-site-footer-main">
        <div className="seo-site-shell seo-site-footer-grid">
          {COLUMNS.map((col) => (
            <div key={col.title} className="seo-site-footer-col">
              <h4>{col.title}</h4>
              <ul>
                {col.items.map((item) => (
                  <li key={item.label}>
                    <FooterLink item={item} />
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="seo-site-footer-mid">
        <div className="seo-site-shell seo-site-footer-mid-inner">
          <a className="seo-site-footer-logo" href="https://zeorbit.com/" target="_blank" rel="noreferrer" aria-label="ZeOrbit website">
            <Logo size={34} />
          </a>
          <div className="seo-site-footer-social">
            {SOCIAL.map((s) => (
              <a
                key={s.label}
                href={s.href}
                target="_blank"
                rel="noreferrer"
                aria-label={s.label}
                className={`seo-site-social is-${s.label.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <SocialBrandIcon label={s.label} />
              </a>
            ))}
          </div>
        </div>
      </div>

      <div className="seo-site-footer-legal">
        <div className="seo-site-shell seo-site-footer-legal-inner">
          <p>© {year} ZeOrbit — SEO Intelligence Platform for U.S. businesses.</p>
          <div className="seo-site-footer-legal-links">
            <a href="mailto:info@zeorbit.com">info@zeorbit.com</a>
            <a href="tel:+16197249517">619-724-9517</a>
            <a href="https://zeorbit.com/privacy-policy" target="_blank" rel="noreferrer">
              Privacy policy
            </a>
            <a href="https://zeorbit.com/contact" target="_blank" rel="noreferrer">
              Contact
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
