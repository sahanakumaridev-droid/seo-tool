import { Link, Navigate, useParams } from 'react-router-dom'
import { ArrowRight, MapPin, Phone } from 'lucide-react'
import RevampHeader from '../components/revamp/RevampHeader'
import SiteFooter from '../components/SiteFooter'
import SeoHead from '../components/SeoHead'
import ContactForm from '../components/revamp/ContactForm'
import { Reveal } from '../components/premium/Reveal'
import { AREA_HUB, AREA_PAGES, AREA_TIER_A, AREA_TIER_B, getAreaPage } from '../data/areas'
import { SITE_CONTACT } from '../data/revampContent'
import '../components/premium/premium-home.css'
import './areas-page.css'

function AreaServices({ items }) {
  return (
    <ul className="zo-area-services">
      {items.map((item) => (
        <li key={item.to}>
          <Link to={item.to}>
            <span>{item.label}</span>
            <ArrowRight size={16} strokeWidth={2.4} aria-hidden />
          </Link>
        </li>
      ))}
    </ul>
  )
}

function AreaFaq({ faqs }) {
  if (!faqs?.length) return null
  return (
    <div className="zo-area-faq">
      {faqs.map((item) => (
        <details key={item.q} className="zo-area-faq-item">
          <summary>{item.q}</summary>
          <p>{item.a}</p>
        </details>
      ))}
    </div>
  )
}

function AreasHub() {
  const featured = AREA_TIER_A.map((slug) => AREA_PAGES[slug])
  const more = AREA_TIER_B.map((slug) => AREA_PAGES[slug])

  return (
    <div className="cz-page zo-areas-page">
      <SeoHead title={AREA_HUB.metaTitle} description={AREA_HUB.metaDescription} path="/areas" />
      <RevampHeader />

      <section className="zo-areas-hero" aria-label="Areas we serve">
        <div className="zo-areas-shell">
          <p className="cz-kicker">{AREA_HUB.eyebrow}</p>
          <h1>{AREA_HUB.title}</h1>
          <p className="zo-areas-lead">{AREA_HUB.lead}</p>
          <div className="zo-areas-hero-actions">
            <Link className="cz-btn-solid" to="/contact#contact">
              Start a project
              <ArrowRight size={18} strokeWidth={2.4} />
            </Link>
            <a className="zo-areas-phone" href={`tel:${SITE_CONTACT.phoneTel}`}>
              <Phone size={16} strokeWidth={2.2} />
              {SITE_CONTACT.phone}
            </a>
          </div>
        </div>
      </section>

      <section className="zo-areas-grid-section" aria-label="Primary markets">
        <div className="zo-areas-shell">
          <div className="zo-areas-grid">
            {featured.map((city) => (
              <Reveal key={city.slug} className="zo-areas-card">
                <p className="zo-areas-card-region">{city.region}</p>
                <h2>
                  <Link to={`/areas/${city.slug}`}>{city.name}</Link>
                </h2>
                <p>{city.lead}</p>
                <Link className="zo-areas-card-link" to={`/areas/${city.slug}`}>
                  Explore {city.name}
                  <ArrowRight size={15} strokeWidth={2.4} aria-hidden />
                </Link>
              </Reveal>
            ))}
          </div>

          <div className="zo-areas-more-block">
            <p className="zo-areas-more-kicker">Also serving</p>
            <div className="zo-areas-more-grid">
              {more.map((city) => (
                <Link key={city.slug} to={`/areas/${city.slug}`} className="zo-areas-more-card">
                  <span>{city.region}</span>
                  <strong>{city.name}</strong>
                  <em>
                    View page
                    <ArrowRight size={14} strokeWidth={2.4} aria-hidden />
                  </em>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  )
}

function AreaCityPage({ page }) {
  return (
    <div className="cz-page zo-areas-page zo-area-city">
      <SeoHead
        title={page.metaTitle}
        description={page.metaDescription}
        path={`/areas/${page.slug}`}
      />
      <RevampHeader />

      <section className="zo-areas-hero" aria-label={page.label}>
        <div className="zo-areas-shell">
          <p className="cz-kicker">{page.eyebrow}</p>
          <h1>{page.title}</h1>
          <p className="zo-areas-lead">{page.lead}</p>
          <div className="zo-areas-hero-actions">
            <Link className="cz-btn-solid" to="/contact#contact">
              Get a free quote
              <ArrowRight size={18} strokeWidth={2.4} />
            </Link>
            <a className="zo-areas-phone" href={`tel:${SITE_CONTACT.phoneTel}`}>
              <Phone size={16} strokeWidth={2.2} />
              {SITE_CONTACT.phone}
            </a>
          </div>
        </div>
      </section>

      <section className="zo-area-body" aria-label={`Why ZeOrbit in ${page.name}`}>
        <div className="zo-areas-shell zo-area-split">
          <Reveal className="zo-area-copy">
            <p className="cz-kicker">Why {page.name}</p>
            <h2>We serve {page.name} with agency craft — not cookie-cutter templates.</h2>
            <ul className="zo-area-why">
              {page.why.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
            <div className="zo-area-office">
              <MapPin size={16} strokeWidth={2.2} aria-hidden />
              <div>
                <strong>San Diego HQ</strong>
                <p>
                  {SITE_CONTACT.address.line1}, {SITE_CONTACT.address.line2}
                </p>
              </div>
            </div>
          </Reveal>

          <Reveal className="zo-area-side">
            <p className="cz-kicker">What we deliver</p>
            <h2>Services for {page.name}</h2>
            <AreaServices items={page.services} />
          </Reveal>
        </div>
      </section>

      <section className="zo-area-faq-section" aria-label="FAQ">
        <div className="zo-areas-shell">
          <p className="cz-kicker">FAQ</p>
          <h2>Questions about working with us in {page.name}</h2>
          <AreaFaq faqs={page.faqs} />
        </div>
      </section>

      <section className="zo-area-contact" id="contact" aria-label="Contact">
        <div className="zo-areas-shell zo-area-contact-grid">
          <div>
            <p className="cz-kicker">Project inquiry</p>
            <h2>Tell us about your {page.name} project</h2>
            <p className="zo-areas-lead">
              Share a short brief — we’ll reply with next steps. Mention {page.name} so we can route you correctly.
            </p>
            <Link className="zo-area-all-link" to="/areas">
              View all areas
              <ArrowRight size={14} strokeWidth={2.4} aria-hidden />
            </Link>
          </div>
          <div className="zo-area-form-panel">
            <ContactForm hideIntro submitLabel="Send message" variant="contactPage" />
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  )
}

export default function AreasPage() {
  const { slug } = useParams()

  if (!slug) {
    return <AreasHub />
  }

  const page = getAreaPage(slug)
  if (!page) {
    return <Navigate to="/areas" replace />
  }

  return <AreaCityPage page={page} />
}
