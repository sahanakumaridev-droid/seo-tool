import { Link } from 'react-router-dom'
import Logo from './Logo'
import { SITE_CONTACT } from '../data/revampContent'

const OFFER_LINKS = [
  { label: 'AI Solutions & AI Agents', to: '/#growth-stack' },
  { label: 'Custom Software', to: '/custom-software' },
  { label: 'Website Designing', to: '/website-designing' },
  { label: 'Mobile Apps', to: '/mobile-apps' },
  { label: 'Business Automation', to: '/#paths' },
  { label: 'SEO & PPC Tactics', to: '/seo-ppc' },
  { label: 'Ecommerce Optimization', to: '/website-designing' },
  { label: 'Data Processing & Analytics', to: '/custom-software' },
]

const SPECIAL_LINKS = [
  { label: 'Home', to: '/' },
  { label: 'Blog', to: '/blog' },
  { label: 'Contact', to: '/contact' },
  { label: "Let's Talk", to: '/contact' },
]

export default function SiteFooter() {
  const year = new Date().getFullYear()

  return (
    <footer id="about" className="zo-site-footer">
      <div className="rv-shell zo-site-footer-main">
        <div className="zo-site-footer-brand">
          <Logo size={32} onDark />
          <p>
            ZeOrbit is a San Diego–based AI, software, web, mobile, and digital growth technology partner—
            building products and systems that help U.S. businesses automate, scale, and grow.
          </p>
          <div className="zo-site-footer-social">
            {SITE_CONTACT.social.map((s) => (
              <a key={s.label} href={s.href} target="_blank" rel="noreferrer">
                {s.label}
              </a>
            ))}
          </div>
        </div>

        <div>
          <h4>What We Offer</h4>
          <ul className="zo-site-footer-list">
            {OFFER_LINKS.map((item) => (
              <li key={item.label}>
                <Link to={item.to}>{item.label}</Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h4>Special Links</h4>
          <ul className="zo-site-footer-list">
            {SPECIAL_LINKS.map((item) => (
              <li key={item.label}>
                <Link to={item.to}>{item.label}</Link>
              </li>
            ))}
            <li>
              <a href={SITE_CONTACT.google.reviewsUrl} target="_blank" rel="noreferrer">
                Google Reviews
              </a>
            </li>
          </ul>
        </div>

        <div>
          <h4>Let&apos;s Talk</h4>
          <ul className="zo-site-footer-list zo-site-footer-contact">
            <li>{SITE_CONTACT.address.line1}</li>
            <li>{SITE_CONTACT.address.line2}</li>
            <li>
              <a href={`tel:${SITE_CONTACT.phoneTel}`}>☏ {SITE_CONTACT.phone}</a>
            </li>
            <li>
              <a href={`mailto:${SITE_CONTACT.email}`}>{SITE_CONTACT.email}</a>
            </li>
          </ul>
          <h4 className="zo-site-footer-offices-title">Other Office Locations</h4>
          <ul className="zo-site-footer-list zo-site-footer-contact">
            {SITE_CONTACT.offices.map((office) => (
              <li key={office.label}>
                <strong>{office.label}</strong>
                {office.lines.map((line) => (
                  <span key={line} className="zo-site-footer-office-line">{line}</span>
                ))}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="zo-site-footer-bottom">
        <div className="rv-shell zo-site-footer-bottom-inner">
          <p>Copyright © {year} ZeOrbit. All Rights Reserved.</p>
          <p className="zo-site-footer-disclaimer">
            All images and content are the property of their respective owners where noted.
          </p>
        </div>
      </div>
    </footer>
  )
}
