import { Link } from 'react-router-dom'
import { ArrowRight, Phone } from 'lucide-react'
import RevampHeader from '../components/revamp/RevampHeader'
import ContactForm from '../components/revamp/ContactForm'
import GoogleReviews from '../components/GoogleReviews'
import SiteFooter from '../components/SiteFooter'
import { SITE_CONTACT } from '../data/revampContent'
import { NAV_PAGES } from '../data/navPages'

export default function ServicePage({ slug }) {
  const page = NAV_PAGES[slug]
  if (!page) {
    return (
      <div className="rv-page">
        <RevampHeader />
        <main className="rv-shell" style={{ padding: '80px 0' }}>
          <h1>Page not found</h1>
          <Link to="/">Back home</Link>
        </main>
      </div>
    )
  }

  return (
    <div className="rv-page zo-service-page">
      <RevampHeader />

      <section className="zo-svc-hero">
        <div className="rv-shell zo-svc-hero-grid">
          <div>
            <p className="zo-svc-eyebrow" style={{ color: page.accent }}>{page.eyebrow}</p>
            <h1>{page.title}</h1>
            <p className="zo-svc-lead">{page.lead}</p>
            <div className="zo-svc-actions">
              <a className="btn zo-gradient-btn" href={`tel:${SITE_CONTACT.phoneTel}`}>
                <Phone size={16} /> Call {SITE_CONTACT.phone}
              </a>
              <a className="btn btn-secondary zo-outline-btn" href="#contact">
                Start a Project <ArrowRight size={16} />
              </a>
            </div>
            <div className="zo-svc-stats">
              {page.stats.map((s) => (
                <div key={s.label}>
                  <strong>{s.value}</strong>
                  <span>{s.label}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="zo-svc-hero-media">
            <img
              src={page.heroImage}
              alt=""
              width={960}
              height={640}
              loading="eager"
              fetchPriority="high"
              decoding="async"
              sizes="(max-width: 860px) 100vw, 560px"
            />
            <div className="zo-svc-hero-glow" style={{ background: page.accent }} aria-hidden />
          </div>
        </div>
      </section>

      {page.highlights?.length ? (
        <section className="zo-svc-highlights">
          <div className="rv-shell zo-svc-highlights-grid">
            {page.highlights.map((h) => (
              <article key={h.title} className="zo-svc-chip">
                <h3>{h.title}</h3>
                <p>{h.copy}</p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {page.features?.length ? (
        <section className="zo-svc-features">
          <div className="rv-shell">
            <header className="zo-svc-section-head">
              <p className="zo-svc-eyebrow" style={{ color: page.accent }}>What you get</p>
              <h2>Capabilities built for how your business runs.</h2>
            </header>
            <div className="zo-svc-feature-list">
              {page.features.map((f, i) => (
                <article key={f.title} className={`zo-svc-feature${i % 2 ? ' reverse' : ''}`}>
                  <div className="zo-svc-feature-media">
                    <img
                      src={f.image}
                      alt=""
                      loading="lazy"
                      decoding="async"
                      width={720}
                      height={480}
                      sizes="(max-width: 860px) 100vw, 520px"
                    />
                  </div>
                  <div className="zo-svc-feature-copy">
                    <h3>{f.title}</h3>
                    <p>{f.copy}</p>
                    <a className="zo-text-link" href="#contact">
                      Discuss this capability <ArrowRight size={14} />
                    </a>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      {page.process?.length ? (
        <section className="zo-svc-process">
          <div className="rv-shell">
            <header className="zo-svc-section-head">
              <p className="zo-svc-eyebrow" style={{ color: page.accent }}>Process</p>
              <h2>From idea to launch—with one clear path.</h2>
            </header>
            <div className="zo-svc-process-grid">
              {page.process.map((p) => (
                <article key={p.step}>
                  <span>{p.step}</span>
                  <h3>{p.title}</h3>
                  <p>{p.copy}</p>
                </article>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      {!page.isContact ? <GoogleReviews /> : null}

      <section id="contact" className="rv-final-cta zo-svc-cta">
        <div className="rv-shell">
          <h2>{page.isContact ? 'Tell us what you need' : `Ready to start ${page.navLabel.toLowerCase()}?`}</h2>
          <p>Share goals and constraints—we&apos;ll reply with clear next steps.</p>
          <div className="rv-contact-wrap">
            <ContactForm />
          </div>
        </div>
      </section>

      {page.isContact ? <GoogleReviews /> : null}
      <SiteFooter />
    </div>
  )
}
