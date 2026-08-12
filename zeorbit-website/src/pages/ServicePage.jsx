import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ArrowRight, CheckCircle2, ChevronDown, Mail, MapPin, Phone } from 'lucide-react'
import RevampHeader from '../components/revamp/RevampHeader'
import ContactForm from '../components/revamp/ContactForm'
import SiteFooter from '../components/SiteFooter'
import { Reveal } from '../components/premium/Reveal'
import { SITE_CONTACT } from '../data/revampContent'
import { NAV_PAGES } from '../data/navPages'
import { ZEORBIT_BLOG_POSTS } from '../data/zeorbitBlog'
import '../components/premium/premium-home.css'
import './website-design-page.css'

function scrollToContact() {
  document.getElementById('wds-contact')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function useHashScroll() {
  const { hash, pathname } = useLocation()
  useEffect(() => {
    if (!hash) return undefined
    const id = decodeURIComponent(hash.replace('#', ''))
    let tries = 0
    let timer = 0

    const go = () => {
      const el = document.getElementById(id)
      if (el) {
        el.scrollIntoView({ behavior: 'auto', block: 'start' })
        return
      }
      tries += 1
      if (tries < 16) timer = window.setTimeout(go, 20)
    }

    timer = window.setTimeout(go, 0)
    return () => window.clearTimeout(timer)
  }, [hash, pathname])
}

function FaqItem({ item, open, onToggle }) {
  return (
    <div className={`wds-faq-item${open ? ' is-open' : ''}`}>
      <button type="button" className="wds-faq-q" onClick={onToggle} aria-expanded={open}>
        <span>{item.q}</span>
        <ChevronDown size={18} className="wds-faq-caret" />
      </button>
      {open ? <p className="wds-faq-a">{item.a}</p> : null}
    </div>
  )
}

function ContactPageLayout({ page }) {
  const [showMaps, setShowMaps] = useState({ sanDiego: false, elCajon: false })
  useHashScroll()

  const maps = [
    {
      key: 'sanDiego',
      title: 'San Diego HQ',
      address: `${SITE_CONTACT.address.line1}, ${SITE_CONTACT.address.line2}`,
      mapsUrl: SITE_CONTACT.address.mapsUrl,
      embed:
        'https://www.google.com/maps?q=4231+Balboa+Avenue+Suite+1340+San+Diego+CA+92117&output=embed',
    },
    {
      key: 'elCajon',
      title: SITE_CONTACT.offices[0].label,
      address: SITE_CONTACT.offices[0].lines.join(', '),
      mapsUrl: SITE_CONTACT.offices[0].mapsUrl,
      embed:
        'https://www.google.com/maps?q=1860+Greenfield+Dr+El+Cajon+CA+92021&output=embed',
    },
  ]

  return (
    <div className="rv-page zo-contact-page">
      <RevampHeader />

      <section className="zo-contact-banner" aria-label="Contact">
        <div className="zo-contact-banner-bg" aria-hidden="true">
          <img
            src="/showcase/contact-us-hero.png"
            alt=""
            loading="eager"
            decoding="async"
            fetchPriority="high"
          />
          <div className="zo-contact-banner-shade" />
          <div className="zo-contact-banner-embers" />
        </div>
        <div className="rv-shell zo-contact-banner-inner">
          <h1>Contact Us</h1>
          <p className="zo-contact-banner-line">{page.lead}</p>
        </div>
      </section>

      <section className="zo-contact-panel" aria-label="Contact details and form">
        <div className="rv-shell zo-contact-layout">
          <div className="zo-contact-copy">
            <p className="zo-contact-eyebrow">Contact us</p>
            <h2>Get in touch</h2>
            <p className="zo-contact-lead">{page.lead}</p>

            <div className="zo-contact-offices">
              <h3>Office Locations</h3>

              <article className="zo-contact-office">
                <h4>Our Balboa Avenue, San Diego, California</h4>
                <p className="zo-contact-office-label">Address</p>
                <ul>
                  <li>
                    {SITE_CONTACT.address.line1}, <strong>{SITE_CONTACT.address.line2}</strong>
                  </li>
                  <li>Customer Service</li>
                  <li>
                    <a href={`tel:${SITE_CONTACT.phoneTel}`}>{SITE_CONTACT.phone}</a>
                  </li>
                  <li>
                    <a href={`mailto:${SITE_CONTACT.email}`}>{SITE_CONTACT.email}</a>
                  </li>
                </ul>
                <a
                  className="zo-contact-office-map"
                  href={SITE_CONTACT.address.mapsUrl}
                  target="_blank"
                  rel="noreferrer"
                >
                  <MapPin size={15} strokeWidth={2.2} />
                  Open in Maps
                </a>
              </article>

              <article className="zo-contact-office">
                <h4>Other Office Locations</h4>
                <ul>
                  {SITE_CONTACT.offices.map((office) => (
                    <li key={office.label}>
                      {office.lines[0]} <strong>{office.lines[1]}</strong>
                    </li>
                  ))}
                </ul>
              </article>
            </div>

            <div className="zo-contact-quick">
              <a className="zo-contact-quick-btn is-primary" href={`tel:${SITE_CONTACT.phoneTel}`}>
                <Phone size={18} strokeWidth={2.2} />
                Call {SITE_CONTACT.phone}
              </a>
              <a className="zo-contact-quick-btn" href={`mailto:${SITE_CONTACT.email}`}>
                <Mail size={18} strokeWidth={2.2} />
                {SITE_CONTACT.email}
              </a>
            </div>
          </div>

          <div className="zo-contact-form-panel" id="contact">
            <div className="zo-contact-form-head">
              <p className="zo-contact-form-kicker">Feel free to contact us</p>
              <h2>Send a message</h2>
              <p>Share a short brief and we&apos;ll follow up with clear next steps.</p>
            </div>
            <ContactForm hideIntro submitLabel="Send message" variant="contactPage" />
          </div>
        </div>
      </section>

      <section className="zo-contact-agent" aria-label="Request a quote">
        <div className="zo-contact-agent-bg" aria-hidden="true">
          <img src="/from-zeorbit/contact/agent.jpg" alt="" loading="lazy" decoding="async" />
          <div className="zo-contact-agent-shade" />
        </div>
        <div className="rv-shell zo-contact-agent-inner">
          <h2>An agent is standing by to assist you with a quote.</h2>
          <div className="zo-contact-agent-actions">
            <a className="cz-btn-solid" href={`tel:${SITE_CONTACT.phoneTel}`}>
              Call {SITE_CONTACT.phone}
              <Phone size={16} strokeWidth={2.4} />
            </a>
            <a className="zo-contact-agent-ghost" href="#contact">
              Request a quote
              <ArrowRight size={16} strokeWidth={2.4} />
            </a>
          </div>
        </div>
      </section>

      <section className="zo-contact-map" aria-label="Find ZeOrbit on the map">
        <div className="rv-shell">
          <div className="zo-contact-maps-grid">
            {maps.map((map) => (
              <div key={map.key} className="zo-contact-map-card">
                <div className="zo-contact-map-card-head">
                  <h3>{map.title}</h3>
                  <p>{map.address}</p>
                </div>
                <div className="zo-contact-map-frame">
                  {showMaps[map.key] ? (
                    <iframe
                      title={`${map.title} map`}
                      src={map.embed}
                      loading="lazy"
                      referrerPolicy="no-referrer-when-downgrade"
                      allowFullScreen
                    />
                  ) : (
                    <button
                      type="button"
                      className="zo-contact-map-gate"
                      onClick={() => setShowMaps((prev) => ({ ...prev, [map.key]: true }))}
                    >
                      <img src="/from-zeorbit/contact/map.jpg" alt="" loading="lazy" decoding="async" />
                      <span>
                        <MapPin size={18} strokeWidth={2.2} />
                        Load map
                      </span>
                    </button>
                  )}
                </div>
                <a className="zo-contact-map-open" href={map.mapsUrl} target="_blank" rel="noreferrer">
                  Open in Google Maps
                  <ArrowRight size={14} strokeWidth={2.4} />
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {page.areas ? (
        <section id="areas" className="zo-contact-areas" aria-label="Areas we serve">
          <div className="rv-shell">
            <p className="zo-contact-eyebrow">{page.areas.title}</p>
            <h2>Built for brands that mean business.</h2>
            <p className="zo-contact-lead">{page.areas.lead}</p>
            <div className="zo-contact-area-tags">
              {page.areas.items.map((area) => (
                <span key={area}>{area}</span>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      <SiteFooter />
    </div>
  )
}


function ServiceLanding({ page }) {
  const [openFaq, setOpenFaq] = useState(0)
  useHashScroll()

  return (
    <div className="cz-page wds-page" data-hero={page.heroTone || 'light'}>
      <RevampHeader />

      <section className="wds-hero" aria-label={page.navLabel}>
        <div className="wds-hero-bg" aria-hidden="true">
          <img
            src={page.image}
            alt=""
            width={1400}
            height={900}
            loading="eager"
            decoding="async"
            fetchPriority="high"
          />
          <div className="wds-hero-shade" />
          <div className="wds-hero-grain" />
        </div>
        <div className="wds-hero-inner">
          <Reveal className="wds-hero-copy" eager>
            <p className="wds-hero-eyebrow">{page.eyebrow}</p>
            <h1>{page.title}</h1>
            <p className="wds-hero-lead">{page.lead}</p>
            <div className="wds-hero-cta">
              <button type="button" className="cz-btn-solid" onClick={scrollToContact}>
                Get a free quote
                <ArrowRight size={18} strokeWidth={2.4} />
              </button>
              <a className="wds-hero-ghost" href={`tel:${SITE_CONTACT.phoneTel}`}>
                <Phone size={15} strokeWidth={2.4} />
                Call {SITE_CONTACT.phone}
              </a>
            </div>
          </Reveal>
        </div>
      </section>

      <section className="wds-proof" aria-label="Capabilities">
        <div className="cz-rail wds-proof-row">
          {page.proof.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </section>

      <section className="wds-section">
        <div className="cz-rail">
          <Reveal className="wds-section-head">
            <p className="cz-kicker">What we deliver</p>
            <h2>Focused capabilities — not a recycled checklist.</h2>
            <p className="cz-whisper">
              Every item below is unique to {page.navLabel.toLowerCase()}. Pick a path and we’ll scope it clearly.
            </p>
          </Reveal>
          <div className="wds-service-grid">
            {page.services.map((item) => (
              <Reveal key={item.id} className="wds-service" id={item.id}>
                <button type="button" className="wds-service-btn" onClick={scrollToContact}>
                  <div className="wds-service-media">
                    <img src={item.image} alt="" loading="lazy" decoding="async" />
                  </div>
                  <div className="wds-service-body">
                    <h3>{item.title}</h3>
                    <p>{item.copy}</p>
                    <span>
                      {item.cta} <ArrowRight size={14} strokeWidth={2.2} />
                    </span>
                  </div>
                </button>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="wds-section wds-section-snow">
        <div className="cz-rail">
          <Reveal className="wds-section-head">
            <p className="cz-kicker">Selected work</p>
            <h2>Proof in the product.</h2>
            <p className="cz-whisper">Imagery from real builds and growth systems — not stock filler.</p>
          </Reveal>
          <div className="wds-work-grid">
            {page.work.map((item, i) => (
              <Reveal key={item.title} className="wds-work-card">
                <div className="wds-work-media">
                  <img src={item.image} alt="" loading="lazy" decoding="async" />
                </div>
                <div className="wds-work-meta">
                  <h3>{item.title}</h3>
                  <p>{item.meta}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="wds-section">
        <div className="cz-rail">
          <Reveal className="wds-section-head">
            <p className="cz-kicker">How we work</p>
            <h2>A clear path from brief to launch.</h2>
          </Reveal>
          <ol className="wds-process">
            {page.process.map((step) => (
              <Reveal as="li" key={step.title} className="wds-process-step">
                <h3>{step.title}</h3>
                <p>{step.copy}</p>
              </Reveal>
            ))}
          </ol>
        </div>
      </section>

      {page.growth ? (
        <section className="wds-growth">
          <div className="cz-rail wds-growth-grid">
            <Reveal className="wds-growth-copy">
              <p className="cz-kicker is-light">{page.growth.kicker}</p>
              <h2>{page.growth.title}</h2>
              <p className="wds-growth-lead">{page.growth.lead}</p>
              <ul>
                {page.growth.points.map((point) => (
                  <li key={point}>
                    <CheckCircle2 size={18} strokeWidth={2} />
                    {point}
                  </li>
                ))}
              </ul>
              <button type="button" className="cz-btn-solid" onClick={scrollToContact}>
                {page.growth.cta}
                <ArrowRight size={18} strokeWidth={2.4} />
              </button>
            </Reveal>
            <Reveal className="wds-growth-media">
              <img src={page.growth.image} alt="" loading="lazy" decoding="async" />
            </Reveal>
          </div>
        </section>
      ) : null}

      {page.slug === 'seo-ppc' ? (
        <section id="blog" className="wds-section wds-blog-section" aria-label="Blog and insights">
          <div className="cz-rail">
            <Reveal className="wds-section-head">
              <p className="cz-kicker">Blog & insights</p>
              <h2>Ideas that help you get found.</h2>
              <p className="cz-whisper">
                Practical notes on SEO, ads, websites, and growth — kept inside SEO & Ads so strategy and
                content stay in one place.
              </p>
            </Reveal>
            <div className="wds-blog-grid">
              {ZEORBIT_BLOG_POSTS.slice(0, 6).map((post) => (
                <Reveal key={post.id || post.title} className="wds-blog-card">
                  <a
                    href={post.url || post.public_url || '#'}
                    className="wds-blog-card-link"
                    target="_blank"
                    rel="noreferrer"
                  >
                    <div className="wds-blog-card-media">
                      {post.featured_image_url ? (
                        <img src={post.featured_image_url} alt="" loading="lazy" decoding="async" />
                      ) : (
                        <div className="wds-blog-card-fallback" aria-hidden="true" />
                      )}
                    </div>
                    <div className="wds-blog-card-body">
                      {post.category ? <p className="wds-blog-card-cat">{post.category}</p> : null}
                      <h3>{post.title}</h3>
                      {post.excerpt ? <p>{post.excerpt}</p> : null}
                      <span>
                        Read article <ArrowRight size={14} strokeWidth={2.2} />
                      </span>
                    </div>
                  </a>
                </Reveal>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      <section className="wds-section wds-section-snow">
        <div className="cz-rail wds-faq-rail">
          <Reveal className="wds-section-head">
            <p className="cz-kicker">FAQ</p>
            <h2>Questions specific to this service.</h2>
          </Reveal>
          <div className="wds-faq-list">
            {page.faqs.map((item, i) => (
              <FaqItem
                key={item.q}
                item={item}
                open={openFaq === i}
                onToggle={() => setOpenFaq(openFaq === i ? -1 : i)}
              />
            ))}
          </div>
        </div>
      </section>

      <section id="wds-contact" className="wds-final">
        <div className="cz-rail wds-final-inner">
          <Reveal className="wds-final-copy">
            <p className="wds-final-eyebrow">{page.finalCta.kicker}</p>
            <h2>{page.finalCta.title}</h2>
            <p>{page.finalCta.lead}</p>
            <a className="wds-final-call" href={`tel:${SITE_CONTACT.phoneTel}`}>
              <Phone size={16} strokeWidth={2.2} />
              Prefer to talk? {SITE_CONTACT.phone}
            </a>
          </Reveal>
          <Reveal className="wds-final-form" eager>
            <div className="wds-final-form-head">
              <p>Project inquiry</p>
              <h3>Send a short brief</h3>
            </div>
            <ContactForm hideIntro submitLabel="Get a free quote" />
          </Reveal>
        </div>
      </section>

      <SiteFooter />
    </div>
  )
}

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

  if (page.isContact) {
    return <ContactPageLayout page={page} />
  }

  return <ServiceLanding page={page} />
}
