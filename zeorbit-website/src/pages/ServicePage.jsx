import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ArrowRight, CheckCircle2, ChevronDown, Mail, MapPin, Phone } from 'lucide-react'
import RevampHeader from '../components/revamp/RevampHeader'
import ContactForm from '../components/revamp/ContactForm'
import SiteFooter from '../components/SiteFooter'
import ServiceOffers from '../components/ServiceOffers'
import ServiceStudio from '../components/ServiceStudio'
import GrowthPanel from '../components/GrowthPanel'
import WorkCarousel from '../components/WorkCarousel'
import PricingPlans from '../components/PricingPlans'
import { Reveal } from '../components/premium/Reveal'
import { SITE_CONTACT } from '../data/revampContent'
import { NAV_PAGES } from '../data/navPages'
import { AREA_CHIPS, AREA_PAGES } from '../data/areas'
import { useHashScroll, scrollToHashId } from '../hooks/useHashScroll'
import '../components/premium/premium-home.css'
import './website-design-page.css'

function scrollToContact() {
  scrollToHashId('contact')
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
  const { hash } = useLocation()
  useHashScroll()
  const formFirst = hash === '#contact'

  const maps = [
    {
      key: 'sanDiego',
      title: 'San Diego HQ',
      address: `${SITE_CONTACT.address.line1}, ${SITE_CONTACT.address.line2}`,
      mapsUrl: SITE_CONTACT.address.mapsUrl,
      embed: SITE_CONTACT.address.streetEmbed,
    },
    {
      key: 'elCajon',
      title: SITE_CONTACT.offices[0].label,
      address: SITE_CONTACT.offices[0].lines.join(', '),
      mapsUrl: SITE_CONTACT.offices[0].mapsUrl,
      embed: SITE_CONTACT.offices[0].streetEmbed,
    },
  ]

  const places = [
    {
      title: 'San Diego HQ',
      lines: [SITE_CONTACT.address.line1, SITE_CONTACT.address.line2],
      mapsUrl: SITE_CONTACT.address.mapsUrl,
    },
    {
      title: SITE_CONTACT.offices[0].label,
      lines: SITE_CONTACT.offices[0].lines,
      mapsUrl: SITE_CONTACT.offices[0].mapsUrl,
    },
  ]

  return (
    <div className={`cz-page zo-contact-page${formFirst ? ' is-form-first' : ''}`}>
      <RevampHeader />

      {formFirst ? null : (
      <section className="zo-contact-hero" aria-label="Contact">
        <div className="zo-contact-hero-frame">
          <div className="zo-contact-hero-bg" aria-hidden="true">
            <iframe
              title="San Diego HQ street map"
              src={SITE_CONTACT.address.streetEmbed}
              loading="eager"
              referrerPolicy="no-referrer-when-downgrade"
              tabIndex={-1}
            />
            <div className="zo-contact-hero-shade" />
          </div>
          <div className="zo-contact-hero-inner">
            <h1>Contact Us</h1>
            <p>
              Our main focus is to achieve a good reputation amongst our clients. We work on Website Design,
              software development and marketing projects.
            </p>
            <div className="zo-contact-hero-actions">
              <a className="cz-btn-solid" href="#contact">
                Start a Project
                <ArrowRight size={18} strokeWidth={2.4} />
              </a>
              <a className="zo-contact-hero-phone" href={`tel:${SITE_CONTACT.phoneTel}`}>
                <Phone size={16} strokeWidth={2.2} />
                {SITE_CONTACT.phone}
              </a>
            </div>
          </div>
        </div>
      </section>
      )}

      <section className={`zo-contact-body${formFirst ? ' is-form-first' : ''}`} aria-label="Contact details and form">
        <div className={`zo-contact-split${formFirst ? ' is-form-only' : ''}`}>
          {formFirst ? null : (
            <Reveal className="zo-contact-aside">
              <p className="cz-kicker">San Diego · Nationwide</p>
              <h2>Get in touch</h2>
              <p className="zo-contact-lead">{page.lead}</p>

              <div className="zo-contact-lines">
                <a className="zo-contact-line" href={`tel:${SITE_CONTACT.phoneTel}`}>
                  <span className="zo-contact-line-icon">
                    <Phone size={16} strokeWidth={2.2} />
                  </span>
                  <span>
                    <strong>Call</strong>
                    <b>{SITE_CONTACT.phone}</b>
                  </span>
                </a>
                <a className="zo-contact-line" href={`mailto:${SITE_CONTACT.email}`}>
                  <span className="zo-contact-line-icon">
                    <Mail size={16} strokeWidth={2.2} />
                  </span>
                  <span>
                    <strong>Email</strong>
                    <b>{SITE_CONTACT.email}</b>
                  </span>
                </a>
              </div>

              <div className="zo-contact-places">
                {places.map((place) => (
                  <article key={place.title} className="zo-contact-place">
                    <MapPin size={16} strokeWidth={2.2} />
                    <div>
                      <h3>{place.title}</h3>
                      {place.lines.map((line) => (
                        <p key={line}>{line}</p>
                      ))}
                      <a href={place.mapsUrl} target="_blank" rel="noreferrer">
                        Open in Maps
                        <ArrowRight size={13} strokeWidth={2.4} />
                      </a>
                    </div>
                  </article>
                ))}
              </div>
            </Reveal>
          )}

          <div id="contact" className="zo-contact-form-panel">
            <div className="zo-contact-form-head">
              <p>Project inquiry</p>
              <h3>Send a short brief</h3>
            </div>
            <ContactForm hideIntro submitLabel="Send message" variant="contactPage" />
          </div>
        </div>
      </section>

      {formFirst ? null : (
      <section className="zo-contact-map" aria-label="Find ZeOrbit on the map">
        <div className="zo-contact-map-inner">
          <p className="cz-kicker">Studios</p>
          <h2>Visit us in California.</h2>
          <div className="zo-contact-maps">
            {maps.map((map) => (
              <article key={map.key} className="zo-contact-map-card">
                <div className="zo-contact-map-frame">
                  <iframe
                    title={`${map.title} map`}
                    src={map.embed}
                    loading="lazy"
                    referrerPolicy="no-referrer-when-downgrade"
                    tabIndex={-1}
                  />
                </div>
                <div className="cz-finale-map-pin">
                  <a className="cz-finale-map-callout" href={map.mapsUrl} target="_blank" rel="noreferrer">
                    <strong>{map.title}</strong>
                    <span>{map.address}</span>
                  </a>
                  <span className="cz-finale-map-marker" aria-hidden="true">
                    <MapPin size={14} strokeWidth={2.6} />
                  </span>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
      )}

      {formFirst || !page.areas ? null : (
        <section id="areas" className="zo-contact-areas" aria-label="Areas we serve">
          <div className="zo-contact-areas-inner">
            <div className="zo-contact-areas-head">
              <div>
                <p className="cz-kicker">{page.areas.title}</p>
                <h2>San Diego based. Nationwide reach.</h2>
                <p className="zo-contact-lead">{page.areas.lead}</p>
              </div>
              <Link className="zo-contact-areas-cta" to="/areas">
                Explore all areas
                <ArrowRight size={16} strokeWidth={2.4} aria-hidden />
              </Link>
            </div>

            <div className="zo-contact-areas-featured" aria-label="Primary markets">
              {AREA_CHIPS.filter((a) => AREA_PAGES[a.slug]?.tier !== 'b').map((area) => {
                const city = AREA_PAGES[area.slug]
                return (
                  <Link key={area.label} to={`/areas/${area.slug}`} className="zo-contact-area-card">
                    <span className="zo-contact-area-card-region">{city?.region}</span>
                    <strong>{city?.name || area.label}</strong>
                    <span className="zo-contact-area-card-blurb">{city?.lead}</span>
                    <span className="zo-contact-area-card-go">
                      View page
                      <ArrowRight size={14} strokeWidth={2.4} aria-hidden />
                    </span>
                  </Link>
                )
              })}
            </div>

            <div className="zo-contact-areas-secondary">
              <p>Also serving</p>
              <div className="zo-contact-area-tags">
                {AREA_CHIPS.filter((a) => AREA_PAGES[a.slug]?.tier === 'b').map((area) => (
                  <Link key={area.label} to={`/areas/${area.slug}`} className="zo-contact-area-tag">
                    {area.label}
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      <SiteFooter />
    </div>
  )
}


function ServiceLanding({ page }) {
  const [openFaq, setOpenFaq] = useState(-1)
  useHashScroll()
  const isProHero = page.heroTone === 'pro'

  return (
    <div className="cz-page wds-page" data-hero={page.heroTone || 'light'}>
      <RevampHeader />

      <section className={`wds-hero${isProHero ? ' wds-hero-pro' : ''}`} aria-label={page.navLabel}>
        {isProHero ? (
          <>
            <div className="wds-hero-atmosphere" aria-hidden="true">
              <div className="wds-hero-glow" />
              <div className="wds-hero-grain" />
            </div>
            <div className="wds-hero-inner wds-hero-split">
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
              <div className="wds-hero-visual" aria-hidden="true">
                <img
                  className="wds-hero-device is-ui-board"
                  src={page.image}
                  alt=""
                  width={1500}
                  height={1500}
                  loading="eager"
                  decoding="async"
                  fetchPriority="high"
                />
              </div>
            </div>
          </>
        ) : (
          <>
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
          </>
        )}
      </section>

      <section className="wds-proof" aria-label="Capabilities">
        <div className="cz-rail wds-proof-row">
          {page.proof.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </section>

      <ServiceOffers items={page.services} onCta={scrollToContact} />

      <ServiceStudio page={page} />

      <section className="wds-section wds-section-snow">
        <div className="cz-rail">
          <Reveal className="wds-section-head">
            <p className="cz-kicker">Our Work</p>
            <h2>Proof in the product.</h2>
            <p className="cz-whisper">Imagery from real builds and growth systems — not stock filler.</p>
          </Reveal>
          <WorkCarousel items={page.work} />
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

      {page.pricing ? <PricingPlans pricing={page.pricing} onCta={scrollToContact} /> : null}

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
            <GrowthPanel metrics={page.growth.metrics} />
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

      <section className="wds-final">
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
          <div id="contact" className="wds-final-form">
            <div className="wds-final-form-head">
              <p>Project inquiry</p>
              <h3>Send a short brief</h3>
            </div>
            <ContactForm hideIntro submitLabel="Get a free quote" />
          </div>
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
