import { lazy, Suspense } from 'react'
import { MapPin, Phone } from 'lucide-react'
import { WhenVisible } from './Reveal'
import { FINAL_CTA } from '../../data/premiumHome'
import { SITE_CONTACT } from '../../data/revampContent'
import './premium-home.css'

const ContactForm = lazy(() => import('../revamp/ContactForm'))

function FinaleMaps() {
  const maps = [
    {
      key: 'sanDiego',
      title: 'San Diego HQ',
      lines: [SITE_CONTACT.address.line1, SITE_CONTACT.address.line2],
      mapsUrl: SITE_CONTACT.address.mapsUrl,
      embed: SITE_CONTACT.address.streetEmbed,
    },
    {
      key: 'elCajon',
      title: SITE_CONTACT.offices[0].label,
      lines: SITE_CONTACT.offices[0].lines,
      mapsUrl: SITE_CONTACT.offices[0].mapsUrl,
      embed: SITE_CONTACT.offices[0].streetEmbed,
    },
  ]

  return (
    <div className="cz-finale-maps" aria-label="Office locations">
      {maps.map((map) => (
        <article key={map.key} className="cz-finale-map-card">
          <WhenVisible rootMargin="240px" minHeight={180}>
            <div className="cz-finale-map-stage">
              <iframe
                className="cz-finale-map-iframe"
                title={`${map.title} map`}
                src={map.embed}
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                tabIndex={-1}
              />
            </div>
          </WhenVisible>
          <div className="cz-finale-map-pin">
            <a className="cz-finale-map-callout" href={map.mapsUrl} target="_blank" rel="noreferrer">
              <strong>{map.title}</strong>
              {map.lines.map((line) => (
                <span key={line}>{line}</span>
              ))}
            </a>
            <span className="cz-finale-map-marker" aria-hidden="true">
              <MapPin size={14} strokeWidth={2.6} />
            </span>
          </div>
        </article>
      ))}
    </div>
  )
}

export default function SiteContactFinale() {
  return (
    <section className="cz-finale" aria-label="Contact">
      <div className="cz-finale-inner">
        <div className="cz-finale-left">
          <div className="cz-finale-copy">
            <h2>{FINAL_CTA.headline}</h2>
            <p className="cz-whisper is-light">{FINAL_CTA.line}</p>
            <a className="cz-finale-quick" href={`tel:${SITE_CONTACT.phoneTel}`}>
              <Phone size={16} strokeWidth={2.2} />
              Prefer to talk? {SITE_CONTACT.phone}
            </a>
          </div>
          <FinaleMaps />
        </div>

        <div id="contact" className="cz-finale-form-card">
          <div className="cz-finale-form-head">
            <p>Project inquiry</p>
            <h3>Send a short brief</h3>
          </div>
          <WhenVisible minHeight={360}>
            <Suspense fallback={null}>
              <ContactForm hideIntro submitLabel="Send message" variant="contactPage" />
            </Suspense>
          </WhenVisible>
        </div>
      </div>
    </section>
  )
}
