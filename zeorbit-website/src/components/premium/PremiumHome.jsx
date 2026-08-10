import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  CalendarDays,
  Car,
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
  Play,
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
  const [preferVideo, setPreferVideo] = useState(false)

  useEffect(() => {
    const mq = window.matchMedia('(min-width: 768px) and (prefers-reduced-motion: no-preference)')
    const sync = () => setPreferVideo(mq.matches)
    sync()
    mq.addEventListener('change', sync)
    return () => mq.removeEventListener('change', sync)
  }, [])

  return preferVideo
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
    <section ref={rootRef} id={panel.id} className="cz-film-panel" aria-label={panel.label}>
      <div className="cz-film-media" aria-hidden="true">
        {showVideo ? (
          <video src={panel.media} poster={panel.poster} autoPlay loop muted playsInline preload="metadata" />
        ) : (
          <img src={panel.poster || panel.media} alt="" loading="lazy" decoding="async" />
        )}
        <div className="cz-film-scrim" />
      </div>
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
    </section>
  )
}

function ServiceStrip({ item }) {
  return (
    <Reveal className={`cz-strip${item.flip ? ' is-flip' : ''}`} id={item.id}>
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

function FinaleMap() {
  const [loadMap, setLoadMap] = useState(false)
  return (
    <div className="cz-finale-map">
      {loadMap ? (
        <iframe
          title="ZeOrbit San Diego office"
          src="https://maps.google.com/maps?q=4231%20Balboa%20Avenue%20Suite%201340%20San%20Diego%20CA%2092117&t=&z=14&ie=UTF8&iwloc=&output=embed"
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
        />
      ) : (
        <button type="button" className="cz-finale-map-gate" onClick={() => setLoadMap(true)}>
          <MapPin size={22} strokeWidth={2.2} />
          <span>View map</span>
          <small>{SITE_CONTACT.address.line1}, San Diego</small>
        </button>
      )}
    </div>
  )
}

export default function PremiumHome() {
  const [showForm, setShowForm] = useState(false)
  const preferHeroVideo = usePreferMotionVideo()

  return (
    <div className="cz-page">
      <RevampHeader />

      {/* 1. HERO — video on desktop, poster on mobile */}
      <section className="cz-hero cz-hero-film" aria-label="Introduction">
        <div className="cz-hero-bg" aria-hidden="true">
          {preferHeroVideo ? (
            <video
              src={HERO.video}
              poster={HERO.scene}
              autoPlay
              loop
              muted
              playsInline
              preload="metadata"
            />
          ) : (
            <img src={HERO.scene} alt="" loading="eager" decoding="async" fetchPriority="high" />
          )}
          <div className="cz-hero-scrim" />
        </div>
        <div className="cz-hero-inner cz-hero-film-inner">
          <Reveal className="cz-hero-copy" eager>
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
              <button type="button" className="cz-btn-ghost" onClick={() => scrollTo('work')}>
                {HERO.secondaryCta}
                <Play size={13} strokeWidth={2.4} fill="currentColor" />
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

      {/* 6. VIDEO panel — before industries */}
      <FilmPanel panel={FILM_PANELS.beforeReviews} />

      {/* 7. INDUSTRIES */}
      <section id="industries" className="cz-industries" aria-label="Industries we serve">
        <div className="cz-industries-bg" aria-hidden="true">
          <img src={INDUSTRIES.image} alt="" loading="lazy" decoding="async" />
          <div className="cz-industries-shade" />
        </div>
        <div className="cz-industries-inner">
          <Reveal className="cz-industries-head">
            <p className="cz-industries-kicker">{INDUSTRIES.kicker}</p>
            <h2>{INDUSTRIES.title}</h2>
            <p>{INDUSTRIES.line}</p>
          </Reveal>
          <div className="cz-industries-grid">
            {INDUSTRIES.items.map((item) => {
              const Icon = INDUSTRY_ICONS[item.icon]
              return (
                <div key={item.label} className="cz-industry">
                  {Icon ? <Icon size={22} strokeWidth={2.2} aria-hidden="true" /> : null}
                  <span>{item.label}</span>
                </div>
              )
            })}
          </div>
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

      {/* 6. FINAL CTA */}
      <section id="contact" className="cz-finale">
        <div className="cz-finale-inner">
          <Reveal className="cz-finale-copy">
            <p className="cz-kicker is-light">Let's talk</p>
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
              <FinaleMap />
            )}
          </Reveal>
        </div>
      </section>

      <SiteFooter />
    </div>
  )
}
