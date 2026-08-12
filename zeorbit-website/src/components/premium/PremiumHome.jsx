import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Bike,
  CalendarDays,
  Car,
  ChevronDown,
  Cpu,
  Dumbbell,
  Factory,
  GraduationCap,
  HandHeart,
  HardHat,
  Heart,
  HeartPulse,
  Home,
  Landmark,
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
  Users,
  UtensilsCrossed,
} from 'lucide-react'
import RevampHeader from '../revamp/RevampHeader'
import ContactForm from '../revamp/ContactForm'
import SiteFooter from '../SiteFooter'
import { Reveal } from './Reveal'
import PremiumGoogleReviews from './PremiumGoogleReviews'
import {
  AGENCY_BAND,
  EXPLORE_BAND,
  FINAL_CTA,
  HERO,
  IMPACT_BAND,
  OUR_SOLUTIONS,
  OUR_SPECIALIZATIONS,
  WHY_CHOOSE,
} from '../../data/premiumHome'
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

function ServiceFlowRow({ item }) {
  const rootRef = useRef(null)
  const preferVideo = usePreferMotionVideo()
  const [inView, setInView] = useState(false)
  const showVideo = preferVideo && item.mediaType === 'video' && inView

  useEffect(() => {
    if (!preferVideo || item.mediaType !== 'video') return undefined
    const el = rootRef.current
    if (!el) return undefined
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setInView(true)
      },
      { rootMargin: '200px 0px' },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [preferVideo, item.mediaType])

  return (
    <article
      ref={rootRef}
      id={item.id}
      className={`cz-flow-row is-${item.tone}${item.flip ? ' is-flip' : ''}`}
    >
      <div className="cz-flow-row-inner">
        <Reveal eager className="cz-flow-copy">
          <p className="cz-flow-label">{item.label}</p>
          <h3>{item.title}</h3>
          <p>{item.line}</p>
          <Link to={item.href} className="cz-flow-cta">
            {item.cta}
            <ArrowRight size={16} strokeWidth={2.4} />
          </Link>
        </Reveal>
        <Reveal eager className="cz-flow-media">
          <div className="cz-flow-media-frame">
            {showVideo ? (
              <video src={item.media} poster={item.poster} autoPlay loop muted playsInline preload="metadata" />
            ) : (
              <img src={item.poster || item.media} alt="" loading="lazy" decoding="async" />
            )}
          </div>
        </Reveal>
      </div>
    </article>
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

function DarkMapArt({ seed = 1 }) {
  const roads = [
    [4, 22, 196, 22],
    [8, 42, 192, 42],
    [12, 62, 188, 62],
    [18, 82, 182, 82],
    [36, 6, 36, 94],
    [72, 4, 72, 96],
    [108, 6, 108, 94],
    [144, 4, 144, 96],
    [176, 8, 176, 92],
  ]
  const blocks = Array.from({ length: 14 }, (_, i) => {
    const col = i % 5
    const row = Math.floor(i / 5)
    return {
      x: 16 + col * 34 + ((seed + i) % 4),
      y: 14 + row * 28 + ((seed * 2 + i) % 3),
      w: 18 + ((i + seed) % 8),
      h: 12 + ((i * seed) % 6),
    }
  })

  return (
    <svg className="cz-finale-map-art" viewBox="0 0 200 100" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <defs>
        <radialGradient id={`cz-map-glow-${seed}`} cx="52%" cy="48%" r="48%">
          <stop offset="0%" stopColor="rgba(255,90,78,0.3)" />
          <stop offset="55%" stopColor="rgba(255,90,78,0.07)" />
          <stop offset="100%" stopColor="rgba(0,0,0,0)" />
        </radialGradient>
        <pattern id={`cz-map-dots-${seed}`} width="7" height="7" patternUnits="userSpaceOnUse">
          <circle cx="1.1" cy="1.1" r="0.75" fill="rgba(255,255,255,0.13)" />
        </pattern>
      </defs>
      <rect width="200" height="100" fill="#0b0d12" />
      <rect width="200" height="100" fill={`url(#cz-map-dots-${seed})`} />
      {roads.map(([x1, y1, x2, y2], i) => (
        <line
          key={`r-${i}`}
          x1={x1}
          y1={y1}
          x2={x2}
          y2={y2}
          stroke="rgba(255,255,255,0.11)"
          strokeWidth={i < 4 ? 1.5 : 1}
        />
      ))}
      {blocks.map((b, i) => (
        <rect
          key={`b-${i}`}
          x={b.x}
          y={b.y}
          width={b.w}
          height={b.h}
          rx="1.4"
          fill="rgba(255,255,255,0.045)"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth="0.4"
        />
      ))}
      <rect width="200" height="100" fill={`url(#cz-map-glow-${seed})`} />
    </svg>
  )
}

function FinaleMaps() {
  const maps = [
    {
      key: 'sanDiego',
      title: 'San Diego HQ',
      lines: [SITE_CONTACT.address.line1, SITE_CONTACT.address.line2],
      mapsUrl: SITE_CONTACT.address.mapsUrl,
      embed:
        'https://www.google.com/maps?q=4231+Balboa+Avenue+Suite+1340+San+Diego+CA+92117&hl=en&z=15&output=embed',
      seed: 1,
    },
    {
      key: 'elCajon',
      title: SITE_CONTACT.offices[0].label,
      lines: SITE_CONTACT.offices[0].lines,
      mapsUrl: SITE_CONTACT.offices[0].mapsUrl,
      embed: 'https://www.google.com/maps?q=1860+Greenfield+Dr+El+Cajon+CA+92021&hl=en&z=15&output=embed',
      seed: 2,
    },
  ]

  return (
    <div className="cz-finale-maps">
      {maps.map((map) => (
        <article key={map.key} className="cz-finale-map-card is-preview">
          <div className="cz-finale-map-stage is-lit" aria-label={`${map.title} map preview`}>
            <DarkMapArt seed={map.seed} />
            <iframe
              className="cz-finale-map-iframe"
              title={`${map.title} map preview`}
              src={map.embed}
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              tabIndex={-1}
            />
            <div className="cz-finale-map-shade" aria-hidden="true" />

            <div className="cz-finale-map-beacon" aria-hidden="true">
              <span className="cz-finale-map-pulse" />
              <span className="cz-finale-map-pulse is-late" />
              <span className="cz-finale-map-dot">
                <MapPin size={16} strokeWidth={2.4} />
              </span>
            </div>
          </div>

          <a className="cz-finale-map-chip" href={map.mapsUrl} target="_blank" rel="noreferrer">
            Open in Maps
            <ArrowRight size={13} strokeWidth={2.4} />
          </a>

          <div className="cz-finale-map-meta">
            <div>
              <h3>{map.title}</h3>
              {map.lines.map((line) => (
                <p key={line}>{line}</p>
              ))}
            </div>
            <a className="cz-finale-map-link" href={map.mapsUrl} target="_blank" rel="noreferrer">
              Directions
              <ArrowRight size={14} strokeWidth={2.4} />
            </a>
          </div>
        </article>
      ))}
    </div>
  )
}

function SpecializationsCarousel() {
  const data = OUR_SPECIALIZATIONS
  const items = data.items
  const [index, setIndex] = useState(0)
  const [dir, setDir] = useState(1)
  const [shifting, setShifting] = useState(false)
  const [inView, setInView] = useState(true)
  const sectionRef = useRef(null)
  const shiftTimer = useRef(0)
  const total = items.length

  const pulseShift = useCallback(() => {
    setShifting(true)
    window.clearTimeout(shiftTimer.current)
    shiftTimer.current = window.setTimeout(() => setShifting(false), 520)
  }, [])

  const go = useCallback(
    (nextIndex, direction) => {
      setDir(direction)
      setIndex(nextIndex)
      pulseShift()
    },
    [pulseShift],
  )

  const prev = useCallback(() => {
    go(index <= 0 ? total - 1 : index - 1, -1)
  }, [go, index, total])

  const next = useCallback(() => {
    go(index >= total - 1 ? 0 : index + 1, 1)
  }, [go, index, total])

  useEffect(() => {
    const el = sectionRef.current
    if (!el || typeof IntersectionObserver === 'undefined') return undefined
    const io = new IntersectionObserver(
      ([entry]) => setInView(entry.isIntersecting && entry.intersectionRatio >= 0.15),
      { threshold: [0, 0.15, 0.35, 0.6] },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [])

  useEffect(() => {
    if (!inView || total < 2) return undefined
    if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return undefined
    }
    const id = window.setInterval(() => {
      setDir(1)
      setIndex((i) => (i >= total - 1 ? 0 : i + 1))
      pulseShift()
    }, 3200)
    return () => window.clearInterval(id)
  }, [inView, total, index, pulseShift])

  useEffect(() => () => window.clearTimeout(shiftTimer.current), [])

  const bgStyle = {
    '--cz-spec-i': String(index),
    '--cz-spec-dir': String(dir),
  }

  return (
    <section
      ref={sectionRef}
      id="specializations"
      className={`cz-spec${shifting ? ' is-shifting' : ''}`}
      style={bgStyle}
      aria-label="Our Specializations"
    >
      <div className="cz-spec-bg" aria-hidden="true">
        <div className="cz-spec-bg-depth" />
        <div className="cz-spec-bg-streaks">
          <span className="cz-spec-streak cz-spec-streak-a" />
          <span className="cz-spec-streak cz-spec-streak-b" />
          <span className="cz-spec-streak cz-spec-streak-c" />
          <span className="cz-spec-streak cz-spec-streak-d" />
        </div>
        <div className="cz-spec-bg-grad" />
        <div className="cz-spec-bg-bokeh">
          <span className="cz-spec-orb cz-spec-orb-a" />
          <span className="cz-spec-orb cz-spec-orb-b" />
          <span className="cz-spec-orb cz-spec-orb-c" />
          <span className="cz-spec-orb cz-spec-orb-d" />
        </div>
        <div className="cz-spec-bg-mesh">
          <div className="cz-spec-bg-mesh-spin">
            <svg className="cz-spec-mesh-svg" viewBox="0 0 1200 700" preserveAspectRatio="xMidYMid slice">
              <defs>
                <linearGradient id="czSpecMeshStroke" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#8b5cff" stopOpacity="0.95" />
                  <stop offset="35%" stopColor="#ff4fd8" stopOpacity="0.9" />
                  <stop offset="70%" stopColor="#ff5a4e" stopOpacity="0.85" />
                  <stop offset="100%" stopColor="#5ad0ff" stopOpacity="0.8" />
                </linearGradient>
                <linearGradient id="czSpecMeshFade" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#000" stopOpacity="0.05" />
                  <stop offset="100%" stopColor="#000" stopOpacity="0.72" />
                </linearGradient>
              </defs>
              <g className="cz-spec-mesh-grid" fill="none" stroke="url(#czSpecMeshStroke)" strokeWidth="1.35">
                {Array.from({ length: 16 }, (_, row) => {
                  const y0 = 80 + row * 36
                  const amp = 28 + row * 2.8
                  const d = Array.from({ length: 15 }, (__, col) => {
                    const x = col * 86
                    const y = y0 + Math.sin((col + row) * 0.62 + index * 0.35) * amp
                    return `${col === 0 ? 'M' : 'L'}${x} ${y}`
                  }).join(' ')
                  return <path key={`h-${row}`} d={d} opacity={0.22 + row * 0.04} />
                })}
                {Array.from({ length: 15 }, (_, col) => {
                  const x = col * 86
                  const d = Array.from({ length: 16 }, (__, row) => {
                    const y0 = 80 + row * 36
                    const amp = 28 + row * 2.8
                    const y = y0 + Math.sin((col + row) * 0.62 + index * 0.35) * amp
                    return `${row === 0 ? 'M' : 'L'}${x} ${y}`
                  }).join(' ')
                  return <path key={`v-${col}`} d={d} opacity={0.16 + (col % 4) * 0.05} />
                })}
              </g>
              <rect width="1200" height="700" fill="url(#czSpecMeshFade)" />
            </svg>
          </div>
        </div>
        <div className="cz-spec-bg-veil" />
      </div>

      <div className="cz-spec-shell">
        <Reveal className="cz-spec-copy">
          <h2>
            <span className="cz-spec-lead">{data.titleLead}</span>{' '}
            <span className="cz-spec-rest">{data.titleRest}</span>
          </h2>
          <p>{data.line}</p>
          <button type="button" className="cz-spec-quote" onClick={() => scrollTo('contact')}>
            {data.cta}
          </button>
        </Reveal>

        <Reveal className="cz-spec-stage">
          <div className={`cz-spec-card-viewport${shifting ? ' is-shifting' : ''}`}>
            <div
              className="cz-spec-card-track"
              style={{ '--cz-spec-x': `-${index * 100}%` }}
            >
              {items.map((item, i) => (
                <article
                  key={item.id}
                  className={`cz-spec-card${i === index ? ' is-active' : ''}`}
                  aria-hidden={i !== index}
                >
                  <div className="cz-spec-card-media" aria-hidden="true">
                    <img src={item.image} alt="" loading="lazy" decoding="async" />
                    <span className="cz-spec-card-shade" />
                    <span className="cz-spec-card-wave" />
                  </div>
                  <div className="cz-spec-card-frame">
                    <div className="cz-spec-card-body">
                      <h3>{item.title}</h3>
                      <p>{item.line}</p>
                      <Link to={item.href} className="cz-spec-more">
                        Know More
                      </Link>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>

          <div className="cz-spec-nav" aria-label="Specialization carousel">
            <button type="button" className="cz-spec-prev" onClick={prev}>
              Previous
            </button>
            <span className="cz-spec-count visually-hidden" aria-live="polite">
              Slide {index + 1} of {total}
            </span>
            <button type="button" className="cz-spec-next" onClick={next}>
              <span className="cz-spec-next-bar" aria-hidden="true" />
              Next
            </button>
          </div>
        </Reveal>
      </div>
    </section>
  )
}

function AgencyBand() {
  const data = AGENCY_BAND

  return (
    <section id="agency" className="cz-agency" aria-label="Solution-based digital marketing agency">
      <div className="cz-agency-horizon" aria-hidden="true" />
      <div className="cz-agency-shell">
        <Reveal className="cz-agency-visual">
          <img src={data.image} alt="" loading="lazy" decoding="async" className="cz-agency-wings" />
        </Reveal>
        <Reveal className="cz-agency-copy">
          <h2>{data.title}</h2>
          <p>{data.line}</p>
          <Link to={data.href} className="cz-agency-more">
            <span>{data.cta}</span>
            <span className="cz-agency-more-line" aria-hidden="true" />
            <ArrowRight size={16} strokeWidth={2.2} aria-hidden="true" />
          </Link>
        </Reveal>
      </div>
    </section>
  )
}

function WhyChooseBand() {
  const data = WHY_CHOOSE

  return (
    <section id="why-choose" className="cz-why" aria-label="Why choose ZeOrbit">
      <div className="cz-why-shell">
        <Reveal className="cz-why-copy">
          <h2>
            <span className="cz-why-lead">{data.titleLead}</span>
            <span className="cz-why-accent">{data.titleAccent}</span>
          </h2>
          <p>{data.line}</p>
          <button type="button" className="cz-why-quote" onClick={() => scrollTo('contact')}>
            <span>{data.cta}</span>
            <span className="cz-why-quote-line" aria-hidden="true" />
            <ArrowRight size={16} strokeWidth={2.2} aria-hidden="true" />
          </button>
        </Reveal>
        <Reveal className="cz-why-visual">
          <img src={data.image} alt="" loading="lazy" decoding="async" className="cz-why-bulbs" />
        </Reveal>
      </div>
    </section>
  )
}

function ImpactBand() {
  const data = IMPACT_BAND

  return (
    <section id="impact" className="cz-impact" aria-label="ZeOrbit founded and impact">
      <div className="cz-impact-glow" aria-hidden="true" />
      <div className="cz-impact-shell">
        <Reveal className="cz-impact-copy">
          <h2>
            <span className="cz-impact-year">{data.titleLead}</span>
            <span className="cz-impact-rest">{data.titleRest}</span>
          </h2>
          <p>{data.line}</p>
          <button type="button" className="cz-impact-quote" onClick={() => scrollTo('contact')}>
            <span>{data.cta}</span>
            <span className="cz-impact-quote-line" aria-hidden="true" />
            <ArrowRight size={16} strokeWidth={2.2} aria-hidden="true" />
          </button>
        </Reveal>
        <Reveal className="cz-impact-stats">
          <ul>
            {data.stats.map((stat) => (
              <li key={stat.label}>
                <strong>{stat.value}</strong>
                <span>{stat.label}</span>
              </li>
            ))}
          </ul>
        </Reveal>
      </div>
    </section>
  )
}

function ExploreBand() {
  const data = EXPLORE_BAND
  const rootRef = useRef(null)
  const bgRef = useRef(null)
  const preferVideo = usePreferMotionVideo()
  const [inView, setInView] = useState(false)
  const [playing, setPlaying] = useState(false)
  const showBgVideo = preferVideo && inView

  useEffect(() => {
    if (!preferVideo) return undefined
    const el = rootRef.current
    if (!el) return undefined
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setInView(true)
      },
      { rootMargin: '280px 0px' },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [preferVideo])

  useEffect(() => {
    const el = bgRef.current
    if (!showBgVideo || !el) return undefined
    const play = () => {
      const p = el.play()
      if (p && typeof p.catch === 'function') p.catch(() => {})
    }
    play()
    el.addEventListener('loadeddata', play)
    return () => el.removeEventListener('loadeddata', play)
  }, [showBgVideo])

  useEffect(() => {
    if (!playing) return undefined
    const onKey = (event) => {
      if (event.key === 'Escape') setPlaying(false)
    }
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [playing])

  return (
    <section ref={rootRef} id="explore" className="cz-explore" aria-label="Explore ZeOrbit">
      <div className="cz-explore-media" aria-hidden="true">
        {showBgVideo ? (
          <video
            ref={bgRef}
            className="cz-explore-bg-video"
            src={data.video}
            poster={data.poster}
            autoPlay
            loop
            muted
            playsInline
            preload="metadata"
          />
        ) : (
          <img src={data.image} alt="" loading="lazy" decoding="async" />
        )}
        <span className="cz-explore-shade" />
      </div>
      <div className="cz-explore-shell">
        <Reveal className="cz-explore-copy">
          <h2>{data.title}</h2>
          <p className="cz-explore-tag">
            <span className="cz-explore-tag-lead">{data.tagLead}</span>
            <span className="cz-explore-tag-brand">{data.tagBrand}</span>
          </p>
          <p className="cz-explore-line">{data.line}</p>
          <Link to={data.href} className="cz-explore-cta">
            <span>{data.cta}</span>
            <span className="cz-explore-cta-line" aria-hidden="true" />
            <ArrowRight size={16} strokeWidth={2.2} aria-hidden="true" />
          </Link>
        </Reveal>
        <Reveal className="cz-explore-play-wrap">
          <button
            type="button"
            className="cz-explore-play"
            aria-label="Play ZeOrbit story video"
            onClick={() => setPlaying(true)}
          >
            <span className="cz-explore-play-ring" aria-hidden="true" />
            <span className="cz-explore-play-core" aria-hidden="true">
              <Play size={22} strokeWidth={2.4} fill="currentColor" />
            </span>
          </button>
        </Reveal>
      </div>

      {playing ? (
        <div className="cz-explore-modal" role="dialog" aria-modal="true" aria-label="ZeOrbit video">
          <button type="button" className="cz-explore-modal-backdrop" aria-label="Close video" onClick={() => setPlaying(false)} />
          <div className="cz-explore-modal-panel">
            <button type="button" className="cz-explore-modal-close" onClick={() => setPlaying(false)}>
              Close
            </button>
            <video
              className="cz-explore-video"
              src={data.video}
              poster={data.poster}
              controls
              autoPlay
              playsInline
            />
          </div>
        </div>
      ) : null}
    </section>
  )
}

function SolutionsShowcase() {
  const data = OUR_SOLUTIONS
  const icons = {
    Landmark,
    Users,
    Heart,
    GraduationCap,
    Cpu,
    Dumbbell,
    Bike,
    HeartPulse,
  }

  return (
    <section id="solutions" className="cz-sol" aria-label="Our Solutions">
      <div className="cz-sol-shell">
        <Reveal className="cz-sol-head">
          <h2>{data.title}</h2>
          <p>{data.line}</p>
        </Reveal>

        <div className="cz-sol-grid">
          {data.items.map((item) => {
            const Icon = icons[item.icon] || Cpu
            return (
              <Reveal key={item.id} className="cz-sol-card-wrap">
                <Link to={item.href} className="cz-sol-card">
                  <span className="cz-sol-wave" aria-hidden="true" />
                  <span className="cz-sol-icon" aria-hidden="true">
                    <Icon size={34} strokeWidth={1.6} />
                  </span>
                  <h3>{item.title}</h3>
                  <p>{item.line}</p>
                  <span className="cz-sol-go" aria-hidden="true">
                    <ArrowRight size={16} strokeWidth={2.4} />
                  </span>
                </Link>
              </Reveal>
            )
          })}
        </div>
      </div>
    </section>
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

      {/* 2. OUR SPECIALIZATIONS — carousel */}
      <SpecializationsCarousel />

      {/* 3. AGENCY BAND — wings / solution-based marketing */}
      <AgencyBand />

      {/* 4. OUR SOLUTIONS — industry cards */}
      <SolutionsShowcase />

      {/* 5. WHY CHOOSE US — above reviews */}
      <WhyChooseBand />

      {/* 6. FOUNDED / IMPACT STATS */}
      <ImpactBand />

      {/* 7. EXPLORE / CULTURE */}
      <ExploreBand />

      {/* 8. GOOGLE REVIEWS */}
      <PremiumGoogleReviews />

      {/* 9. CONTACT */}
      <section id="contact" className="cz-finale">
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
