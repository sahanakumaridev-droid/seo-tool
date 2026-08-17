import { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, ArrowUpRight, X } from 'lucide-react'
import RevampHeader from '../components/revamp/RevampHeader'
import SiteFooter from '../components/SiteFooter'
import SeoHead from '../components/SeoHead'
import { Reveal } from '../components/premium/Reveal'
import {
  PORTFOLIO_FILTERS,
  PORTFOLIO_ITEMS,
  PORTFOLIO_PAGE,
  PORTFOLIO_SECTIONS,
} from '../data/portfolio'
import '../components/premium/premium-home.css'
import './portfolio-page.css'

function itemLabel(item) {
  if (item.title) return item.title
  if (item.category === 'apps') return 'Mobile app design'
  if (item.category === 'flyers') return 'Flyer design'
  if (item.category === 'logos') return 'Logo design'
  return 'Portfolio piece'
}

function PortfolioImage({ item, eager = false }) {
  const [src, setSrc] = useState(item.image)
  return (
    <img
      src={src}
      alt={itemLabel(item)}
      loading={eager ? 'eager' : 'lazy'}
      decoding="async"
      onError={() => {
        if (item.remote && src !== item.remote) setSrc(item.remote)
      }}
    />
  )
}

function PortfolioCard({ item, heading: Heading = 'h2', eager = false, onOpen }) {
  const label = itemLabel(item)
  const className = [
    'zo-port-card',
    `is-${item.category}`,
    item.fit === 'contain' ? 'is-contain' : '',
  ]
    .filter(Boolean)
    .join(' ')

  const inner = (
    <>
      <div className="zo-port-media">
        <PortfolioImage item={item} eager={eager} />
        <span className="zo-port-visit">
          {item.href ? 'Visit live site' : 'View'}
          {item.href ? <ArrowUpRight size={14} strokeWidth={2.4} /> : null}
        </span>
      </div>
      <div className="zo-port-meta">
        <div>
          {item.title ? <Heading>{item.title}</Heading> : <Heading className="is-quiet">{label}</Heading>}
          <p>{item.meta}</p>
        </div>
        {item.href ? <ArrowUpRight size={18} strokeWidth={2.2} aria-hidden="true" /> : null}
      </div>
    </>
  )

  if (item.href) {
    return (
      <a className={className} href={item.href} target="_blank" rel="noreferrer" aria-label={`${label} — visit live site`}>
        {inner}
      </a>
    )
  }

  return (
    <button
      type="button"
      className={className}
      onClick={(event) => onOpen(item, event.currentTarget)}
      aria-label={`View ${label}`}
    >
      {inner}
    </button>
  )
}

export default function PortfolioPage() {
  const [filter, setFilter] = useState('all')
  const [openItem, setOpenItem] = useState(null)
  const closeRef = useRef(null)
  const lastFocusRef = useRef(null)

  useEffect(() => {
    if (!openItem) return undefined
    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    closeRef.current?.focus()
    const onKey = (e) => {
      if (e.key === 'Escape') setOpenItem(null)
    }
    window.addEventListener('keydown', onKey)
    return () => {
      document.body.style.overflow = prevOverflow
      window.removeEventListener('keydown', onKey)
      lastFocusRef.current?.focus?.()
    }
  }, [openItem])

  const grouped = useMemo(() => {
    const next = { websites: [], apps: [], flyers: [], logos: [] }
    for (const item of PORTFOLIO_ITEMS) {
      next[item.category]?.push(item)
    }
    return next
  }, [])

  const counts = useMemo(() => {
    const next = { all: PORTFOLIO_ITEMS.length }
    for (const item of PORTFOLIO_ITEMS) {
      next[item.category] = (next[item.category] || 0) + 1
    }
    return next
  }, [])

  const openPreview = (item, trigger) => {
    lastFocusRef.current = trigger || document.activeElement
    setOpenItem(item)
  }

  const visibleSections =
    filter === 'all' ? PORTFOLIO_FILTERS.filter((tab) => tab.id !== 'all') : PORTFOLIO_FILTERS.filter((tab) => tab.id === filter)

  return (
    <div className="cz-page zo-portfolio-page">
      <SeoHead
        title="Our Work — ZeOrbit Web, App & Brand Portfolio"
        description="Selected websites, mobile apps, flyers, and logos designed and built by ZeOrbit for businesses across California and beyond."
        path="/portfolio"
      />
      <RevampHeader />

      <section className="zo-port-hero">
        <div className="cz-rail zo-port-hero-inner">
          <Reveal eager>
            <p className="cz-kicker">{PORTFOLIO_PAGE.eyebrow}</p>
            <h1>{PORTFOLIO_PAGE.title}</h1>
            <p className="zo-port-lead">{PORTFOLIO_PAGE.lead}</p>
          </Reveal>
        </div>
      </section>

      <section className="zo-port-body" aria-label="Portfolio">
        <div className="cz-rail">
          <div className="zo-port-filters" role="tablist" aria-label="Filter work">
            {PORTFOLIO_FILTERS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                role="tab"
                aria-selected={filter === tab.id}
                className={filter === tab.id ? 'is-on' : ''}
                onClick={() => setFilter(tab.id)}
              >
                {tab.label}
                <span>{counts[tab.id] || 0}</span>
              </button>
            ))}
          </div>

          {visibleSections.map((section) => {
            const copy = PORTFOLIO_SECTIONS[section.id]
            const items = grouped[section.id] || []
            return (
              <section key={section.id} className="zo-port-section" aria-labelledby={`port-${section.id}`}>
                {filter === 'all' ? (
                  <div className="zo-port-section-head">
                    <h2 id={`port-${section.id}`}>{copy.title}</h2>
                    <p>{copy.lead}</p>
                  </div>
                ) : (
                  <h2 id={`port-${section.id}`} className="sr-only">
                    {copy.title}
                  </h2>
                )}
                <div className={`zo-port-grid is-${section.id}`}>
                  {items.map((item, index) => (
                    <PortfolioCard
                      key={item.id}
                      item={item}
                      heading={filter === 'all' ? 'h3' : 'h2'}
                      eager={section.id === 'websites' && index < 3}
                      onOpen={openPreview}
                    />
                  ))}
                </div>
              </section>
            )
          })}
        </div>
      </section>

      <section className="zo-port-cta">
        <div className="cz-rail zo-port-cta-inner">
          <h2>Want work like this for your brand?</h2>
          <p>Tell us what you need to launch. We’ll map a realistic build and a clear first step.</p>
          <Link to="/contact#contact" className="cz-btn-solid">
            Start a project
            <ArrowRight size={18} strokeWidth={2.4} />
          </Link>
        </div>
      </section>

      {openItem ? (
        <div className="zo-port-lightbox" role="dialog" aria-modal="true" aria-label={itemLabel(openItem)}>
          <button type="button" className="zo-port-lightbox-back" aria-label="Close" onClick={() => setOpenItem(null)} />
          <div className="zo-port-lightbox-card">
            <button
              ref={closeRef}
              type="button"
              className="zo-port-lightbox-close"
              aria-label="Close"
              onClick={() => setOpenItem(null)}
            >
              <X size={18} strokeWidth={2.2} />
            </button>
            <PortfolioImage item={openItem} eager />
            <div className="zo-port-lightbox-meta">
              <h3>{itemLabel(openItem)}</h3>
              <p>{openItem.meta}</p>
            </div>
          </div>
        </div>
      ) : null}

      <SiteFooter />
    </div>
  )
}
