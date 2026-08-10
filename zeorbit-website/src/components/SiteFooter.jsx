import { Link } from 'react-router-dom'
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
  { label: 'Portfolios', to: '/#work' },
  { label: "Let's Talk", to: '/contact' },
  { label: 'Blogs', to: '/blog' },
  { label: 'Privacy & Policy', to: '/contact' },
]

export const SOCIAL_ICONS = {
  Facebook:
    'M14 9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v7h3v-7h3l1-3h-4v-2c0-.6.4-1 1-1z',
  LinkedIn:
    'M6.5 9.5H4V20h2.5V9.5zM5.2 4A1.5 1.5 0 1 0 5.2 7a1.5 1.5 0 0 0 0-3zM20 13.3c0-3-1.6-4.4-3.7-4.4-1.7 0-2.5.9-2.9 1.6V9.5H11V20h2.5v-5.6c0-1.5.3-2.9 2.1-2.9 1.8 0 1.9 1.6 1.9 3V20H20v-6.7z',
  Instagram:
    'M7 3h10a4 4 0 0 1 4 4v10a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V7a4 4 0 0 1 4-4zm5 4.5A4.5 4.5 0 1 0 12 16.5 4.5 4.5 0 0 0 12 7.5zm0 7.2a2.7 2.7 0 1 1 0-5.4 2.7 2.7 0 0 1 0 5.4zM17.2 6.6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z',
  YouTube:
    'M21.6 8.2a2.5 2.5 0 0 0-1.8-1.8C18.2 6 12 6 12 6s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 8.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 3.8 2.5 2.5 0 0 0 1.8 1.8C5.8 18 12 18 12 18s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-3.8zM10 14.8V9.2L15.2 12 10 14.8z',
  X: 'M17.5 4h-2.3l-3.1 4.1L9 4H4.5l5.2 7.2L4.7 20h2.3l3.4-4.5L14.9 20H19.5l-5.4-7.5L17.5 4zm-1.2 14.5h-1.2L7.8 5.4h1.3l7.2 13.1z',
  Pinterest:
    'M12 3a9 9 0 0 0-3.3 17.4c-.1-.7-.2-1.8 0-2.6l1.2-5.1s-.3-.6-.3-1.5c0-1.4.8-2.4 1.8-2.4.9 0 1.3.6 1.3 1.4 0 .9-.6 2.2-.9 3.4-.2.9.5 1.7 1.5 1.7 1.8 0 3.1-2.3 3.1-5.1 0-2.1-1.4-3.7-4-3.7-2.9 0-4.7 2.2-4.7 4.6 0 .9.3 1.8.7 2.3.1.1.1.2.1.3l-.3 1c0 .2-.2.2-.3.1-1.3-.6-2-2.2-2-3.6 0-2.7 2.3-5.9 6.7-5.9 3.6 0 6 2.6 6 5.4 0 3.7-2.1 6.5-5.1 6.5-1 0-2-.6-2.3-1.2l-.6 2.4c-.2.9-.8 2-1.2 2.7A9 9 0 1 0 12 3z',
}

export default function SiteFooter() {
  const year = new Date().getFullYear()

  return (
    <footer id="about" className="zo-site-footer">
      <div className="rv-shell zo-site-footer-main">
        <div className="zo-site-footer-brand">
          <p>
            ZeOrbit builds websites on WordPress, Shopify, Wix, and Squarespace — and mobile apps for
            iOS and Android. Based in San Diego, serving clients nationwide across the United States.
          </p>
          <div className="zo-site-footer-social">
            {SITE_CONTACT.social.map((s) => (
              <a
                key={s.label}
                href={s.href}
                target="_blank"
                rel="noreferrer"
                aria-label={s.label}
                className="zo-social"
              >
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d={SOCIAL_ICONS[s.label] || SOCIAL_ICONS.X} />
                </svg>
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
          </ul>
        </div>

        <div>
          <h4>Contact</h4>
          <ul className="zo-site-footer-list zo-site-footer-contact">
            <li>
              <a
                href={SITE_CONTACT.address.mapsUrl}
                target="_blank"
                rel="noreferrer"
                className="zo-site-footer-address-link"
              >
                {SITE_CONTACT.address.line1}
                <br />
                {SITE_CONTACT.address.line2}
              </a>
            </li>
            <li>
              <a href={`tel:${SITE_CONTACT.phoneTel}`}>☏ {SITE_CONTACT.phone}</a>
            </li>
            <li>
              <a href={`mailto:${SITE_CONTACT.email}`}>✉ {SITE_CONTACT.email}</a>
            </li>
          </ul>
          <h4 className="zo-site-footer-offices-title">Other Office Locations</h4>
          <ul className="zo-site-footer-list zo-site-footer-contact">
            {SITE_CONTACT.offices.map((office) => (
              <li key={office.label}>
                <a
                  href={office.mapsUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="zo-site-footer-address-link"
                >
                  {office.lines.map((line) => (
                    <span key={line} className="zo-site-footer-office-line">
                      {line}
                    </span>
                  ))}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="zo-site-footer-bottom">
        <div className="rv-shell zo-site-footer-bottom-inner">
          <p>© {year} ZeOrbit. All Rights Reserved.</p>
          <p className="zo-site-footer-disclaimer">
            Images and content are the property of their respective owners.
          </p>
        </div>
      </div>
    </footer>
  )
}
