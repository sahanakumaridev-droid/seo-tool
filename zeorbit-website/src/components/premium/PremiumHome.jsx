import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  CalendarDays,
  Car,
  ChevronDown,
  Cpu,
  Dumbbell,
  Factory,
  GraduationCap,
  HandHeart,
  HardHat,
  HeartPulse,
  Home,
  Leaf,
  LineChart,
  MapPin,
  MessagesSquare,
  Music,
  Phone,
  Plane,
  Scale,
  Scissors,
  Shield,
  Smile,
  UtensilsCrossed,
} from 'lucide-react'
import RevampHeader from '../revamp/RevampHeader'
import ContactForm from '../revamp/ContactForm'
import SiteFooter from '../SiteFooter'
import { Reveal } from './Reveal'
import {
  FILM_PANELS,
  FINAL_CTA,
  HERO,
  INDUSTRIES,
  PORTFOLIO,
  SERVICE_STRIPS,
} from '../../data/premiumHome'
import { GOOGLE_REVIEWS } from '../../data/googleReviews'
import { SITE_CONTACT } from '../../data/revampContent'

const INDUSTRY_ICONS = {
  UtensilsCrossed,
  Factory,
  Scale,
  Car,
  MapPin,
  Home,
  Dumbbell,
  Leaf,
  LineChart,
  Scissors,
  MessagesSquare,
  CalendarDays,
  Music,
  Cpu,
  Plane,
  Shield,
  HeartPulse,
  HardHat,
  GraduationCap,
  Smile,
  HandHeart,
}

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function GoogleLogo({ size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#EA4335" d="M24 9.5c3.4 0 6.4 1.2 8.8 3.5l6.6-6.6C35.4 2.5 30.1 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.7 6c1.8-5.4 6.9-9.7 13.7-9.7z" />
      <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.6c-.5 3-2.2 5.5-4.7 7.2l7.3 5.7c4.3-4 6.8-9.8 6.8-17.4z" />
      <path fill="#FBBC05" d="M10.3 19.2c-.5 1.5-.8 3.1-.8 4.8s.3 3.3.8 4.8l-7.7 6C1 31.6 0 27.9 0 24s1-7.6 2.6-10.8l7.7 6z" />
      <path fill="#34A853" d="M24 48c6.1 0 11.4-2 15.2-5.4l-7.3-5.7c-2 1.4-4.7 2.2-7.9 2.2-6.8 0-12.9-4.3-13.7-9.7l-7.7 6C6.5 42.6 14.6 48 24 48z" />
    </svg>
  )
}

function usePreferMotionVideo() {
  const [preferVideo, setPreferVideo] = useState(true)

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const sync = () => setPreferVideo(!mq.matches)
    sync()
    mq.addEventListener('change', sync)
    return () => mq.removeEventListener('change', sync)
  }, [])

  return preferVideo
}

function HeroVideo({ preferVideo }) {
  const videoRef = useRef(null)

  useEffect(() => {
    const el = videoRef.current
    if (!preferVideo || !el) return undefined
    const play = () => {
      const p = el.play()
      if (p && typeof p.catch === 'function') p.catch(() => {})
    }
    play()
    el.addEventListener('loadeddata', play)
    return () => el.removeEventListener('loadeddata', play)
  }, [preferVideo])

  return (
    <div className="cz-hero-bg" aria-hidden="true">
      {preferVideo ? (
        <video
          ref={videoRef}
          className="cz-hero-video"
          src={HERO.video}
          poster={HERO.scene}
          autoPlay
          loop
          muted
          playsInline
          preload="auto"
        />
      ) : (
        <img className="cz-hero-poster" src={HERO.scene} alt="" loading="eager" decoding="async" fetchPriority="high" />
      )}
      <div className="cz-hero-scrim" />
    </div>
  )
}

function FilmPanel({ panel }) {
  const rootRef = useRef(null)
  const preferVideo = usePreferMotionVideo()
  const [inView, setInView] = useState(false)
  const showVideo = preferVideo && panel.mediaType === 'video' && inView

  useEffect(() => {
    if (!preferVideo || panel.mediaType !== 'video') return undefined
    const el = rootRef.current
    if (!el) return undefined
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setInView(true)
      },
      { rootMargin: '240px 0px' },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [preferVideo, panel.mediaType])

  return (
    <section ref={rootRef} id={panel.id} className="cz-film-panel is-split" aria-label={panel.label}>
      <div className="cz-film-inner">
        <Reveal className="cz-film-copy" eager>
          <p className="cz-film-label">{panel.label}</p>
          <h2 className="cz-film-title">
            {panel.title.split('\n').map((line) => (
              <span key={line}>{line}</span>
            ))}
          </h2>
          <p className="cz-film-line">{panel.line}</p>
          <Link to={panel.href} className="cz-film-cta">
            {panel.cta}
            <ArrowRight size={16} strokeWidth={2.4} />
          </Link>
        </Reveal>
      </div>
      <div className="cz-film-media" aria-hidden="true">
        {showVideo ? (
          <video src={panel.media} poster={panel.poster} autoPlay loop muted playsInline preload="metadata" />
        ) : (
          <img src={panel.poster || panel.media} alt="" loading="lazy" decoding="async" />
        )}
      </div>
    </section>
  )
}

function WireFrames({ className = '' }) {
  return (
    <div className={`cz-wireframes ${className}`} aria-hidden="true">
      <svg viewBox="0 0 420 520" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect
          width="250"
          height="460"
          rx="44"
          stroke="currentColor"
          strokeWidth="2"
          transform="translate(80 40) rotate(-20 125 230)"
        />
      </svg>
    </div>
  )
}

function ServiceStrip({ item }) {
  return (
    <Reveal eager className={`cz-strip${item.flip ? ' is-flip' : ''}`} id={item.id}>
      <div className="cz-strip-copy">
        <p className="cz-strip-label">{item.label}</p>
        <h2>{item.title}</h2>
        <p>{item.line}</p>
        <Link to={item.href} className="cz-strip-cta">
          {item.cta}
          <ArrowRight size={16} strokeWidth={2.4} />
        </Link>
      </div>
      <div className="cz-strip-media">
        <img src={item.image} alt="" loading="lazy" decoding="async" />
      </div>
    </Reveal>
  )
}

function CaseCard({ item }) {
  return (
    <Reveal className={`cz-case cz-case-${item.tone}${item.flip ? ' is-flip' : ''}`}>
      <Link to={item.href} className="cz-case-link">
        <div className="cz-case-media">
          <img src={item.image} alt={item.alt || item.title} loading="lazy" decoding="async" />
          <div className="cz-case-shade" />
        </div>
        <div className="cz-case-copy">
          <h3>{item.title}</h3>
          <p className="cz-case-meta">{item.meta}</p>
          {item.copy ? <p className="cz-case-body">{item.copy}</p> : null}
          {item.result ? <p className="cz-case-result">{item.result}</p> : null}
        </div>
      </Link>
    </Reveal>
  )
}

function IndustriesExplorer() {
  const tabs = INDUSTRIES.tabs
  const [activeTab, setActiveTab] = useState(tabs[0]?.id || 'business')
  const [openLabel, setOpenLabel] = useState(null)
  const active = tabs.find((tab) => tab.id === activeTab) || tabs[0]
  const openItem = active.items.find((item) => item.label === openLabel) || null

  useEffect(() => {
    setOpenLabel(null)
  }, [activeTab])

  return (
    <div className="cz-industries-explorer">
      <div className="cz-industry-tabs" role="tablist" aria-label="Industry categories">
        {tabs.map((tab) => {
          const selected = tab.id === active.id
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={selected}
              className={`cz-industry-tab${selected ? ' is-active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          )
        })}
      </div>

      <div className="cz-industry-chips" role="tabpanel" aria-label={`${active.label} industries`}>
        {active.items.map((item) => {
          const Icon = INDUSTRY_ICONS[item.icon]
          const open = openLabel === item.label
          return (
            <button
              key={item.label}
              type="button"
              className={`cz-industry-chip${open ? ' is-open' : ''}`}
              aria-expanded={open}
              onClick={() => setOpenLabel(open ? null : item.label)}
            >
              <span className="cz-industry-chip-icon" aria-hidden="true">
                {Icon ? <Icon size={16} strokeWidth={2.2} /> : null}
              </span>
              <span>{item.label}</span>
              <ChevronDown size={15} strokeWidth={2.4} className="cz-industry-chip-caret" />
            </button>
          )
        })}
      </div>

      {openItem ? (
        <div className="cz-industry-drawer is-open" aria-live="polite">
          <div className="cz-industry-drawer-top">
            <div>
              <p className="cz-industry-drawer-kicker">{active.label}</p>
              <h3>{openItem.label}</h3>
            </div>
            <button type="button" className="cz-industry-drawer-close" onClick={() => setOpenLabel(null)}>
              Close
              <ChevronDown size={15} strokeWidth={2.4} />
            </button>
          </div>
          <p>{openItem.blurb}</p>
          <Link to="/contact" className="cz-industry-drawer-cta">
            Start a project
            <ArrowRight size={15} strokeWidth={2.4} />
          </Link>
        </div>
      ) : null}
    </div>
  )
}

function FinaleMaps() {
  const [loaded, setLoaded] = useState({ sanDiego: false, elCajon: false })
  const maps = [
    {
      key: 'sanDiego',
      title: 'San Diego HQ',
      lines: [SITE_CONTACT.address.line1, SITE_CONTACT.address.line2],
      mapsUrl: SITE_CONTACT.address.mapsUrl,
      embed:
        'https://www.google.com/maps?q=4231+Balboa+Avenue+Suite+1340+San+Diego+CA+92117&output=embed',
    },
    {
      key: 'elCajon',
      title: SITE_CONTACT.offices[0].label,
      lines: SITE_CONTACT.offices[0].lines,
      mapsUrl: SITE_CONTACT.offices[0].mapsUrl,
      embed: 'https://www.google.com/maps?q=1860+Greenfield+Dr+El+Cajon+CA+92021&output=embed',
    },
  ]

  return (
    <div className="cz-finale-maps">
      {maps.map((map) => (
        <article key={map.key} className="cz-finale-map-card">
          <header className="cz-finale-map-head">
            <span className="cz-finale-map-pin" aria-hidden="true">
              <MapPin size={16} strokeWidth={2.2} />
            </span>
            <div>
              <h3>{map.title}</h3>
              {map.lines.map((line) => (
                <p key={line}>{line}</p>
              ))}
            </div>
          </header>
          <div className="cz-finale-map">
            {loaded[map.key] ? (
              <iframe
                title={`${map.title} map`}
                src={map.embed}
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              />
            ) : (
              <button
                type="button"
                className="cz-finale-map-gate"
                onClick={() => setLoaded((prev) => ({ ...prev, [map.key]: true }))}
              >
                <MapPin size={22} strokeWidth={2.2} />
                <span>View map</span>
                <small>{map.lines.join(', ')}</small>
              </button>
            )}
          </div>
          <a className="cz-finale-map-link" href={map.mapsUrl} target="_blank" rel="noreferrer">
            Open in Google Maps
            <ArrowRight size={14} strokeWidth={2.4} />
          </a>
        </article>
      ))}
    </div>
  )
}

export default function PremiumHome() {
  const [showForm, setShowForm] = useState(false)
  const preferHeroVideo = usePreferMotionVideo()

  return (
    <div className="cz-page" id="main">
      <RevampHeader />

      {/* 1. HERO — full-bleed video (~70% visual) + content */}
      <section className="cz-hero cz-hero-film" aria-label="Introduction">
        <HeroVideo preferVideo={preferHeroVideo} />
        <div className="cz-hero-inner cz-hero-film-inner">
          <Reveal className="cz-hero-copy" eager>
            <p className="cz-hero-eyebrow">{HERO.eyebrow}</p>
            <h1 className="cz-hero-title">
              <span className="cz-hero-title-line">Digital Solutions</span>
              <span className="cz-hero-title-line">That Drive Results.</span>
            </h1>
            <p className="cz-hero-line">{HERO.line}</p>
            <div className="cz-hero-cta">
              <button type="button" className="cz-btn-solid" onClick={() => scrollTo('contact')}>
                {HERO.primaryCta}
                <ArrowRight size={18} strokeWidth={2.4} />
              </button>
            </div>
          </Reveal>
        </div>
        <div className="cz-scroll-hint" aria-hidden="true">
          <span />
        </div>
      </section>

      {/* 2. Content | image strips — not an immediate full-bleed film */}
      <section className="cz-strips" aria-label="What we build">
        <WireFrames />
        <div className="cz-strips-rail">
          {SERVICE_STRIPS.map((item) => (
            <ServiceStrip key={item.id} item={item} />
          ))}
        </div>
      </section>

      {/* 3. WORK — image cases */}
      <section id="work" className="cz-work">
        <Reveal className="cz-work-intro">
          <p className="cz-kicker">{PORTFOLIO.kicker}</p>
          <h2>{PORTFOLIO.headline}</h2>
        </Reveal>

        {PORTFOLIO.items.slice(0, 2).map((item) => (
          <CaseCard key={item.num} item={item} />
        ))}
      </section>

      {/* 4. VIDEO panel — mid page */}
      <FilmPanel panel={FILM_PANELS.afterWork} />

      {/* 5. More work images */}
      <section className="cz-work cz-work-continued" aria-label="More selected work">
        {PORTFOLIO.items.slice(2).map((item) => (
          <CaseCard key={item.num} item={item} />
        ))}
      </section>

      {/* 6. Growth band — no video; premium visual division */}
      <section id="growth" className="cz-growth-band" aria-label="Digital Marketing">
        <div className="cz-growth-band-glow" aria-hidden="true" />
        <div className="cz-growth-band-inner">
          <Reveal className="cz-growth-band-copy">
            <p className="cz-growth-band-kicker">Digital Marketing</p>
            <h2>
              Get found.
              <span>Get chosen.</span>
            </h2>
            <p>
              SEO, ads, and local growth strategies that put the right customers in front of your
              business — with reporting you can actually act on.
            </p>
            <div className="cz-growth-band-stats" aria-hidden="true">
              <div>
                <strong>SEO</strong>
                <span>Technical + local</span>
              </div>
              <div>
                <strong>Ads</strong>
                <span>Qualified demand</span>
              </div>
              <div>
                <strong>Analytics</strong>
                <span>Clear reporting</span>
              </div>
            </div>
            <Link to="/seo-ppc" className="cz-growth-band-cta">
              Explore growth
              <ArrowRight size={16} strokeWidth={2.4} />
            </Link>
          </Reveal>
          <Reveal className="cz-growth-band-visual">
            <div className="cz-growth-band-frame">
              <img
                src="/showcase/growth-dashboard-b.png"
                alt="SEO and ads growth dashboard"
                loading="lazy"
                decoding="async"
              />
            </div>
            <div className="cz-growth-band-chip cz-growth-band-chip-a">Local SEO</div>
            <div className="cz-growth-band-chip cz-growth-band-chip-b">Paid Media</div>
          </Reveal>
        </div>
      </section>

      {/* 7. INDUSTRIES */}
      <section id="industries" className="cz-industries" aria-label="Industries we serve">
        <div className="cz-industries-inner">
          <Reveal className="cz-industries-head">
            <p className="cz-industries-kicker">{INDUSTRIES.kicker}</p>
            <h2>{INDUSTRIES.title}</h2>
            <p>{INDUSTRIES.line}</p>
          </Reveal>
          <Reveal>
            <IndustriesExplorer />
          </Reveal>
        </div>
      </section>

      {/* 8. VOICES */}
      <section id="reviews" className="cz-voices">
        <Reveal className="cz-voices-head">
          <div className="cz-voices-title">
            <p className="cz-kicker">Voices</p>
            <h2>Trusted.</h2>
          </div>
          <div className="cz-voices-rating">
            <GoogleLogo size={22} />
            <strong>{SITE_CONTACT.google.rating}</strong>
            <span>on Google · {SITE_CONTACT.google.reviewCount} reviews</span>
          </div>
        </Reveal>
        <div className="cz-voices-marquee">
          <div className="cz-voices-track">
            {[...GOOGLE_REVIEWS, ...GOOGLE_REVIEWS].map((r, i) => (
              <div key={`${r.author}-${i}`} className="cz-voice">
                <div className="cz-voice-stars" aria-hidden="true">
                  {'★★★★★'}
                </div>
                <p>“{r.text}”</p>
                <footer>
                  <strong>{r.author}</strong>
                  <span>{r.when}</span>
                </footer>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 9. CONTACT */}
      <section id="contact" className="cz-finale">
        <WireFrames className="is-finale" />
        <div className="cz-finale-inner">
          <Reveal className="cz-finale-copy">
            <p className="cz-kicker is-light">Contact Us</p>
            <h2>
              {FINAL_CTA.headline.split('\n').map((line) => (
                <span key={line}>{line}</span>
              ))}
            </h2>
            <p className="cz-whisper is-light">{FINAL_CTA.line}</p>

            {showForm ? (
              <button type="button" className="cz-finale-back" onClick={() => setShowForm(false)}>
                ← Back
              </button>
            ) : (
              <div className="cz-finale-actions">
                <button type="button" className="cz-btn-solid" onClick={() => setShowForm(true)}>
                  Start a Project
                  <ArrowRight size={18} strokeWidth={2.4} />
                </button>
                <a className="cz-finale-quick" href={`tel:${SITE_CONTACT.phoneTel}`}>
                  <Phone size={16} strokeWidth={2.2} />
                  {SITE_CONTACT.phone}
                </a>
              </div>
            )}
          </Reveal>

          <Reveal className="cz-finale-visual">
            {showForm ? (
              <div className="cz-finale-form-card">
                <ContactForm />
              </div>
            ) : (
              <FinaleMaps />
            )}
          </Reveal>
        </div>
      </section>

      <SiteFooter />
    </div>
  )
}
