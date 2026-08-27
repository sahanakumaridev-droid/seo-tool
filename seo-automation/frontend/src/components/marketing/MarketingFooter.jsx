import { Link } from 'react-router-dom'
import Logo from '../Logo'
import SocialBrandIcon from '../SocialBrandIcon'
import { SITE_CONTACT, siteUrl } from '../../data/revampContent'

const WEBSITES = [
  { label: 'Custom Websites', to: '/website-designing#business' },
  { label: 'Shopify & Ecommerce', to: '/website-designing#ecommerce' },
  { label: 'Landing Pages', to: '/website-designing#landing' },
  { label: 'Website Redesign', to: '/website-designing#redesign' },
  { label: 'UI / UX Design', to: '/website-designing#ux' },
  { label: 'Care & Maintenance', to: '/website-designing#care' },
]

const APPS = [
  { label: 'iOS & Android', to: '/mobile-apps#native' },
  { label: 'Cross-Platform', to: '/mobile-apps#cross' },
  { label: 'App Timeline', to: '/mobile-apps#timeline' },
  { label: 'Mobile UX / UI', to: '/mobile-apps#ux' },
]

const GROWTH = [
  { label: 'Technical SEO', to: '/seo-ppc#seo' },
  { label: 'Local SEO', to: '/seo-ppc#local' },
  { label: 'Content SEO', to: '/seo-ppc#content' },
  { label: 'Google Ads', to: '/seo-ppc#ads' },
  { label: 'Social Ads', to: '/seo-ppc#social-ads' },
  { label: 'Pricing', to: '/seo-ppc#pricing' },
]

const SOFTWARE = [
  { label: 'Dashboards', to: '/custom-software#platforms' },
  { label: 'CRM & Workflows', to: '/custom-software#crm' },
  { label: 'API Integrations', to: '/custom-software#integrations' },
  { label: 'Automation', to: '/custom-software#automation' },
]

const RESOURCES = [
  { label: 'Blog', to: '/blog' },
  { label: 'Portfolio', to: '/portfolio' },
  { label: 'Areas We Serve', to: '/areas' },
  { label: 'Get a Free Quote', to: '/contact' },
]

const COMPANY = [
  { label: 'About ZeOrbit', to: '/' },
  { label: 'Contact', to: '/contact' },
  { label: 'Privacy Policy', to: '/privacy-policy' },
  { label: "Let's Talk", to: '/contact' },
]

const COLUMNS = [
  { title: 'Websites', items: WEBSITES },
  { title: 'Mobile Apps', items: APPS },
  { title: 'SEO & Ads', items: GROWTH },
  { title: 'Software', items: SOFTWARE },
  { title: 'Resources', items: RESOURCES },
  { title: 'Company', items: COMPANY },
]

/**
 * Marketing footer matched 1:1 to zeorbit.com SiteFooter host chrome.
 * All site links open on zeorbit.com.
 */
export default function MarketingFooter() {
  const year = new Date().getFullYear()

  return (
    <footer id="about" className="zo-site-footer zo-host-footer">
      <div className="zo-host-footer-accent" aria-hidden />

      <div className="zo-host-footer-main">
        <div className="rv-shell zo-host-footer-grid">
          {COLUMNS.map((col) => (
            <div key={col.title} className="zo-host-footer-col">
              <h4>{col.title}</h4>
              <ul>
                {col.items.map((item) => (
                  <li key={item.label}>
                    <a href={siteUrl(item.to)}>{item.label}</a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="zo-host-footer-mid">
        <div className="rv-shell zo-host-footer-mid-inner">
          <a
            href={siteUrl('/')}
            className="zo-host-footer-logo"
            aria-label="ZeOrbit website"
          >
            <Logo size={34} />
          </a>
          <div className="zo-host-footer-social">
            {SITE_CONTACT.social.map((s) => (
              <a
                key={s.label}
                href={s.href}
                target="_blank"
                rel="noreferrer"
                aria-label={s.label}
                className={`zo-host-social is-${s.label.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <SocialBrandIcon label={s.label} />
              </a>
            ))}
          </div>
        </div>
      </div>

      <div className="zo-host-footer-legal">
        <div className="rv-shell zo-host-footer-legal-inner">
          <p>
            © {year} ZeOrbit — Websites, apps, SEO, and custom software for ambitious U.S. brands.
          </p>
          <div className="zo-host-footer-legal-links">
            <a href={`mailto:${SITE_CONTACT.email}`}>{SITE_CONTACT.email}</a>
            <a href={`tel:${SITE_CONTACT.phoneTel}`}>{SITE_CONTACT.phone}</a>
            <a href={siteUrl('/privacy-policy')}>Privacy policy</a>
            <a href={siteUrl('/contact')}>Contact</a>
            <Link to="/login">Log in</Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
