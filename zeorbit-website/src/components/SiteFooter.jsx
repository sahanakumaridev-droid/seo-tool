import { Link } from 'react-router-dom'
import { Mail, Phone } from 'lucide-react'
import Logo from './Logo'
import SocialBrandIcon from './SocialBrandIcon'
import { SITE_CONTACT } from '../data/revampContent'

const OFFER_LINKS = [
  { label: 'Custom Websites', to: '/website-designing#business' },
  { label: 'Shopify & Ecommerce', to: '/website-designing#ecommerce' },
  { label: 'Website Care & Hosting', to: '/website-designing#care' },
  { label: 'Mobile Apps', to: '/mobile-apps' },
  { label: 'SEO & Ads', to: '/seo-ppc' },
  { label: 'API Integrations', to: '/custom-software#integrations' },
  { label: 'Automation & Copilots', to: '/custom-software#automation' },
  { label: 'Areas We Serve', to: '/contact#areas' },
]

const SPECIAL_LINKS = [
  { label: 'Website Designing', to: '/website-designing' },
  { label: 'Mobile Apps', to: '/mobile-apps' },
  { label: 'SEO & PPC Tactics', to: '/seo-ppc' },
  { label: 'App Timeline', to: '/mobile-apps#timeline' },
  { label: 'UI / UX Design', to: '/website-designing#ux' },
  { label: 'Portfolio', to: '/portfolio' },
  { label: "Let's Talk", to: '/contact' },
  { label: 'Blogs', to: '/blog' },
]

export default function SiteFooter() {
  const year = new Date().getFullYear()

  return (
    <footer id="about" className="zo-site-footer">
      <div className="zo-site-footer-stage">
        <div className="rv-shell zo-site-footer-main">
          <div className="zo-site-footer-brand">
            <Link to="/" className="zo-site-footer-logo" aria-label="ZeOrbit home">
              <Logo size={40} />
            </Link>
            <p>
              ZeOrbit is an award-winning web and mobile app development company, building high-performing
              websites on WordPress, Shopify, Wix, and Squarespace, along with custom iOS and Android apps.
              We serve clients worldwide with strategic guidance from the first idea and design sketch to
              final launch.
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
            </div>
          </div>

          <div className="zo-site-footer-col">
            <h4>What We Offer</h4>
            <ul className="zo-site-footer-list">
              {OFFER_LINKS.map((item) => (
                <li key={item.label}>
                  <Link to={item.to}>{item.label}</Link>
                </li>
              ))}
            </ul>
          </div>

          <div className="zo-site-footer-col">
            <h4>Special Links</h4>
            <ul className="zo-site-footer-list">
              {SPECIAL_LINKS.map((item) => (
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
