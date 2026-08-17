import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  CalendarDays,
  Car,
  Cog,
  Cpu,
  Droplets,
  Dumbbell,
  GraduationCap,
  Handshake,
  HardHat,
  HeartPulse,
  Home,
  LineChart,
  MapPin,
  MessagesSquare,
  Music,
  Phone,
  Plane,
  Scale,
  Scissors,
  ShieldPlus,
  Smile,
  UtensilsCrossed,
} from 'lucide-react'
import RevampHeader from '../revamp/RevampHeader'
import SiteFooter from '../SiteFooter'
import ContactForm from '../revamp/ContactForm'
import { Reveal } from './Reveal'
import PremiumGoogleReviews from './PremiumGoogleReviews'
import SeoOrbit from './SeoOrbit'
import { useHashScroll } from '../../hooks/useHashScroll'
import {
  FINAL_CTA,
  HERO,
  INDUSTRIES,
  PORTFOLIO,
  SERVICE_STRIPS,
} from '../../data/premiumHome'
import { SITE_CONTACT } from '../../data/revampContent'

const INDUSTRY_ICONS = {
  UtensilsCrossed,
  Cog,
  Scale,
  Car,
  MapPin,
  Home,
  Dumbbell,
  Droplets,
  LineChart,
  Scissors,
  MessagesSquare,
  CalendarDays,
  Music,
  Cpu,
  Plane,
  ShieldPlus,
  HeartPulse,
  HardHat,
  GraduationCap,
  Smile,
  Handshake,
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

function useAutoPlayVideo(enabled) {
  const videoRef = useRef(null)

  useEffect(() => {
    const el = videoRef.current
    if (!enabled || !el) return undefined

    el.muted = true
    el.defaultMuted = true
    el.playsInline = true
    el.setAttribute('playsinline', '')
    el.setAttribute('webkit-playsinline', 'true')

    const play = () => {
      const run = el.play()
      if (run && typeof run.catch === 'function') run.catch(() => {})
    }

    play()
    el.addEventListener('loadeddata', play)
    el.addEventListener('canplay', play)
    document.addEventListener('touchstart', play, { once: true, passive: true })
    document.addEventListener('visibilitychange', play)
    const retryA = window.setTimeout(play, 400)
    const retryB = window.setTimeout(play, 1600)
    return () => {
      el.removeEventListener('loadeddata', play)
      el.removeEventListener('canplay', play)
      document.removeEventListener('touchstart', play)
      document.removeEventListener('visibilitychange', play)
      window.clearTimeout(retryA)
      window.clearTimeout(retryB)
    }
  }, [enabled])

  return videoRef
}

function HeroVideo({ preferVideo }) {
  const [videoFailed, setVideoFailed] = useState(false)
  const showVideo = preferVideo && !videoFailed
  const videoRef = useAutoPlayVideo(showVideo)

  return (
    <div className="cz-hero-bg" aria-hidden="true">
      {showVideo ? (
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
          disablePictureInPicture
          onError={() => setVideoFailed(true)}
        />
      ) : (
        <img className="cz-hero-poster" src={HERO.scene} alt="" loading="eager" decoding="async" fetchPriority="high" />
      )}
      <div className="cz-hero-scrim" />
    </div>
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
  const preferVideo = usePreferMotionVideo()
  const [videoFailed, setVideoFailed] = useState(false)
  const showVideo = Boolean(item.video) && preferVideo && !videoFailed
  const videoRef = useAutoPlayVideo(showVideo)

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
        {showVideo ? (
          <video
            ref={videoRef}
            src={item.video}
            poster={item.image}
            autoPlay
            loop
            muted
            playsInline
            preload="auto"
            onError={() => setVideoFailed(true)}
          />
        ) : (
          <img src={item.image} alt="" loading="lazy" decoding="async" />
        )}
      </div>
    </Reveal>
  )
}

function CaseCard({ item }) {
  return (
    <Reveal eager className={`cz-case cz-case-${item.tone}${item.flip ? ' is-flip' : ''}`}>
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
          <span className="cz-case-cta">
            View work
            <ArrowRight size={16} strokeWidth={2.4} />
          </span>
        </div>
      </Link>
    </Reveal>
  )
}

function IndustriesExplorer() {
  const items = INDUSTRIES.items
  const [openLabel, setOpenLabel] = useState(null)
  const openItem = items.find((item) => item.label === openLabel) || null

  return (
    <div className="cz-industries-explorer">
      <div className="cz-industries-grid">
        {items.map((item) => {
          const Icon = INDUSTRY_ICONS[item.icon]
          const open = openLabel === item.label
          return (
            <button
              key={item.label}
              type="button"
              className={`cz-industry-item${open ? ' is-open' : ''}`}
              aria-expanded={open}
              onClick={() => setOpenLabel(open ? null : item.label)}
            >
              <span className="cz-industry-item-icon" aria-hidden="true">
                {Icon ? <Icon size={18} strokeWidth={1.8} /> : null}
              </span>
              <span>{item.label}</span>
            </button>
          )
        })}
      </div>

      {openItem ? (
        <div className="cz-industry-drawer is-open" aria-live="polite">
          <div className="cz-industry-drawer-top">
            <h3>{openItem.label}</h3>
            <button type="button" className="cz-industry-drawer-close" onClick={() => setOpenLabel(null)}>
              Close
            </button>
          </div>
          <p>{openItem.blurb}</p>
          <Link to="/contact#contact" className="cz-industry-drawer-cta">
            Start a project
            <ArrowRight size={15} strokeWidth={2.4} />
          </Link>
        </div>
      ) : null}
    </div>
  )
}

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

export default function PremiumHome() {
  const preferHeroVideo = usePreferMotionVideo()
  useHashScroll()

  return (
    <div className="cz-page" id="main">
      <RevampHeader />

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
              <Link to="/contact#contact" className="cz-btn-solid">
                {HERO.primaryCta}
                <ArrowRight size={18} strokeWidth={2.4} />
              </Link>
            </div>
          </Reveal>
        </div>
        <div className="cz-scroll-hint" aria-hidden="true">
          <span />
        </div>
      </section>

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
        <Reveal eager className="cz-work-intro">
          <p className="cz-kicker">{PORTFOLIO.kicker}</p>
          <h2>{PORTFOLIO.headline}</h2>
          <Link to="/portfolio" className="cz-link">
            See all work
            <ArrowRight size={16} strokeWidth={2.4} />
          </Link>
        </Reveal>

        {PORTFOLIO.items.slice(0, 2).map((item) => (
          <CaseCard key={item.num} item={item} />
        ))}
      </section>

      <section id="growth" className="cz-growth-band" aria-label="Digital Marketing">
        <div className="cz-growth-band-glow" aria-hidden="true" />
        <div className="cz-growth-band-inner">
          <Reveal className="cz-growth-band-copy" eager>
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
          <Reveal className="cz-growth-band-visual" eager>
            <SeoOrbit />
          </Reveal>
        </div>
      </section>

      {/* 5. More work images */}
      <section className="cz-work cz-work-continued" aria-label="More of our work">
        {PORTFOLIO.items.slice(2).map((item) => (
          <CaseCard key={item.num} item={item} />
        ))}
      </section>

      {/* 6. INDUSTRIES */}
      <section id="industries" className="cz-industries" aria-label="Industries we serve">
        <div className="cz-industries-bg" aria-hidden="true">
          <img src="/showcase/why-team.png" alt="" loading="lazy" decoding="async" />
        </div>
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

      {/* 8. GOOGLE REVIEWS */}
      <PremiumGoogleReviews />

      {/* 9. CONTACT — inquiry form on the home screen */}
      <section className="cz-finale" aria-label="Contact">
        <div className="cz-finale-inner">
          <div className="cz-finale-left">
            <Reveal className="cz-finale-copy">
              <h2>{FINAL_CTA.headline}</h2>
              <p className="cz-whisper is-light">{FINAL_CTA.line}</p>
              <a className="cz-finale-quick" href={`tel:${SITE_CONTACT.phoneTel}`}>
                <Phone size={16} strokeWidth={2.2} />
                Prefer to talk? {SITE_CONTACT.phone}
              </a>
            </Reveal>
            <FinaleMaps />
          </div>

          <div id="contact" className="cz-finale-form-card">
            <div className="cz-finale-form-head">
              <p>Project inquiry</p>
              <h3>Send a short brief</h3>
            </div>
            <ContactForm hideIntro submitLabel="Send message" variant="contactPage" />
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  )
}
