import { lazy, Suspense, useEffect, useRef, useState } from 'react'
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
  Hotel,
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
import { Reveal, WhenVisible } from './Reveal'
import SeoOrbit from './SeoOrbit'
import { useHashScroll } from '../../hooks/useHashScroll'
import {
  HERO,
  INDUSTRIES,
  PORTFOLIO,
  SERVICE_STRIPS,
} from '../../data/premiumHome'
import { SITE_CONTACT } from '../../data/revampContent'

const PremiumGoogleReviews = lazy(() => import('./PremiumGoogleReviews'))
const SiteContactFinale = lazy(() => import('./SiteContactFinale'))

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
  Hotel,
}

function usePreferMotionVideo({ allowNarrow = false } = {}) {
  const [preferVideo, setPreferVideo] = useState(false)

  useEffect(() => {
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)')
    const narrow = window.matchMedia('(max-width: 768px)')
    const sync = () =>
      setPreferVideo(!motion.matches && (allowNarrow || !narrow.matches))
    sync()
    motion.addEventListener('change', sync)
    narrow.addEventListener('change', sync)
    return () => {
      motion.removeEventListener('change', sync)
      narrow.removeEventListener('change', sync)
    }
  }, [allowNarrow])

  return preferVideo
}

function useDeferredMotion(enabled, delayMs = 2800) {
  const [go, setGo] = useState(false)

  useEffect(() => {
    if (!enabled) {
      setGo(false)
      return undefined
    }
    let timeoutId
    const arm = () => {
      timeoutId = window.setTimeout(() => setGo(true), delayMs)
    }
    if (document.readyState === 'complete') arm()
    else window.addEventListener('load', arm)
    return () => {
      window.removeEventListener('load', arm)
      window.clearTimeout(timeoutId)
    }
  }, [enabled, delayMs])

  return go
}

function useAutoPlayVideo(enabled) {
  const videoRef = useRef(null)

  useEffect(() => {
    const el = videoRef.current
    if (!enabled || !el) return undefined

    el.muted = true
    el.defaultMuted = true
    el.volume = 0
    el.playsInline = true
    el.setAttribute('muted', '')
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
  const [videoOn, setVideoOn] = useState(false)
  const allowVideo = preferVideo && !videoFailed
  const videoRef = useAutoPlayVideo(allowVideo)

  return (
    <div className="cz-hero-bg" aria-hidden="true">
      <img
        className="cz-hero-poster"
        src="/videos/hero-agency-poster.webp"
        srcSet="/videos/hero-agency-poster-800.webp 800w, /videos/hero-agency-poster.webp 1200w, /videos/hero-agency-poster-1600.webp 1600w"
        sizes="100vw"
        width={1500}
        height={900}
        alt=""
        loading="eager"
        decoding="async"
        fetchPriority="high"
      />
      {allowVideo ? (
        <video
          ref={videoRef}
          className={`cz-hero-video${videoOn ? ' is-on' : ''}`}
          src={HERO.video}
          autoPlay
          loop
          muted
          playsInline
          preload="auto"
          disablePictureInPicture
          onPlaying={() => setVideoOn(true)}
          onCanPlay={() => setVideoOn(true)}
          onError={() => setVideoFailed(true)}
        />
      ) : null}
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

function FluidImg({ src, alt = '', eager = false, sizes = '(max-width: 768px) 100vw, 46vw' }) {
  const src800 = src.replace(/(\.[a-z0-9]+)$/i, '-800$1')
  return (
    <img
      src={src}
      srcSet={`${src800} 800w, ${src} 1400w`}
      sizes={sizes}
      alt={alt}
      loading={eager ? 'eager' : 'lazy'}
      decoding="async"
    />
  )
}

function ServiceStrip({ item }) {
  const preferVideo = usePreferMotionVideo()
  const [videoFailed, setVideoFailed] = useState(false)
  const allowVideo = useDeferredMotion(Boolean(item.video) && preferVideo, 4000) && !videoFailed
  const videoRef = useAutoPlayVideo(allowVideo)

  return (
    <Reveal eager className={`cz-strip${item.flip ? ' is-flip' : ''}`} id={item.id}>
      <div className="cz-strip-inner">
        <div className="cz-strip-copy">
          <p className="cz-strip-label">{item.label}</p>
          <h2>{item.title}</h2>
          <p>{item.line}</p>
          <Link to={item.href} className="cz-btn-solid">
            {item.cta}
            <ArrowRight size={16} strokeWidth={2.4} />
          </Link>
        </div>
        <div className="cz-strip-media">
          <FluidImg src={item.image} />
          {allowVideo ? (
            <video
              ref={videoRef}
              src={item.video}
              autoPlay
              loop
              muted
              playsInline
              preload="none"
              onError={() => setVideoFailed(true)}
            />
          ) : null}
        </div>
      </div>
    </Reveal>
  )
}

function CaseCard({ item }) {
  return (
    <Reveal eager className={`cz-case cz-case-${item.tone}${item.flip ? ' is-flip' : ''}`}>
      <Link to={item.href} className="cz-case-link">
        <div className={`cz-case-media${item.mediaFit === 'wide' ? ' is-wide' : ''}`}>
          <FluidImg src={item.image} alt={item.alt || item.title} />
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

export default function PremiumHome() {
  const preferHeroVideo = usePreferMotionVideo({ allowNarrow: true })
  useHashScroll()

  return (
    <div className="cz-page" id="main">
      <RevampHeader />

      <section id="cz-hero-dark" className="cz-hero cz-hero-film cz-hero-stagepad" aria-label="Introduction">
        <div className="cz-hero-stagepad-frame">
          <HeroVideo preferVideo={preferHeroVideo} />
          <div className="cz-hero-inner cz-hero-film-inner">
            <Reveal className="cz-hero-copy" eager>
              <p className="cz-hero-eyebrow">{HERO.eyebrow}</p>
              <h1 className="cz-hero-title">
                <span className="cz-hero-title-line">Fundamental honesty</span>
                <span className="cz-hero-title-line">is the keystone of business.</span>
              </h1>
              <p className="cz-hero-line">{HERO.line}</p>
              <div className="cz-hero-cta">
                <Link to={HERO.primaryHref} className="cz-btn-solid">
                  {HERO.primaryCta}
                  <ArrowRight size={18} strokeWidth={2.4} />
                </Link>
                <a className="cz-btn-ghost cz-hero-call" href={`tel:${SITE_CONTACT.phoneTel}`}>
                  <Phone size={18} strokeWidth={2.4} aria-hidden />
                  Call {SITE_CONTACT.phone}
                </a>
              </div>
            </Reveal>
          </div>
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
          <FluidImg src="/showcase/why-team.webp" alt="" sizes="100vw" />
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
      <WhenVisible minHeight={420}>
        <Suspense fallback={null}>
          <PremiumGoogleReviews />
        </Suspense>
      </WhenVisible>

      <WhenVisible minHeight={520}>
        <Suspense fallback={null}>
          <SiteContactFinale />
        </Suspense>
      </WhenVisible>

      <SiteFooter />
    </div>
  )
}
