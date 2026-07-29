import { useId, useState } from 'react'
import Logo from '../Logo'

/** Order: Web → Mobile → AI → Software → SEO → Data → Automation */
const CAPABILITIES = [
  { key: 'web', title: 'Web', copy: 'Websites built for conversion, SEO, and AI search.' },
  { key: 'mobile', title: 'Mobile', copy: 'iOS and Android apps with secure product backends.' },
  { key: 'ai', title: 'AI', copy: 'Agents, GenAI, RAG, and model integrations in real workflows.' },
  { key: 'software', title: 'Software', copy: 'Custom systems and dashboards that fit how you operate.' },
  { key: 'seo', title: 'SEO', copy: 'SEO, AEO, and GEO for modern discovery.' },
  { key: 'data', title: 'Data', copy: 'Pipelines and analytics that drive decisions.' },
  { key: 'automation', title: 'Automation', copy: 'Workflows that remove repetitive operational work.' },
]

export default function HeroOrbit({ onSelect }) {
  const [activeKey, setActiveKey] = useState('ai')
  const [paused, setPaused] = useState(false)
  const labelId = useId()
  const n = CAPABILITIES.length
  const active = CAPABILITIES.find((c) => c.key === activeKey) || CAPABILITIES[0]

  function activate(item) {
    setActiveKey(item.key)
    onSelect?.(item)
  }

  return (
    <div
      className={`zo-orbit-wrap${paused ? ' is-paused' : ''}`}
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocusCapture={() => setPaused(true)}
      onBlurCapture={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget)) setPaused(false)
      }}
    >
      {/* Desktop / tablet orbit */}
      <div className="zo-orbit zo-orbit-desktop" role="list" aria-labelledby={labelId}>
        <div className="zo-orbit-ring" aria-hidden />
        <div className="zo-orbit-ring zo-orbit-ring-2" aria-hidden />
        <div className="zo-orbit-core" aria-hidden>
          <Logo size={28} />
        </div>

        <div className="zo-orbit-spin" style={{ '--zo-orbit-n': n }}>
          {CAPABILITIES.map((item, index) => {
            const selected = item.key === activeKey
            const angle = (360 / n) * index
            return (
              <button
                key={item.key}
                type="button"
                role="listitem"
                className={`zo-orbit-card${selected ? ' active' : ''}`}
                style={{ '--zo-orbit-a': `${angle}deg` }}
                aria-pressed={selected}
                aria-label={`${item.title}: ${item.copy}`}
                onMouseEnter={() => activate(item)}
                onFocus={() => activate(item)}
                onClick={() => activate(item)}
              >
                <span className="zo-orbit-card-tilt">
                  <span className="zo-orbit-card-face">
                    <strong>{item.title}</strong>
                  </span>
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Mobile: tappable chips (no cramped orbit) */}
      <div className="zo-orbit-mobile" role="list" aria-label="ZeOrbit capabilities">
        <div className="zo-orbit-mobile-core" aria-hidden>
          <Logo size={24} />
        </div>
        <div className="zo-orbit-mobile-chips">
          {CAPABILITIES.map((item) => {
            const selected = item.key === activeKey
            return (
              <button
                key={item.key}
                type="button"
                role="listitem"
                className={`zo-orbit-chip${selected ? ' active' : ''}`}
                aria-pressed={selected}
                onClick={() => activate(item)}
              >
                {item.title}
              </button>
            )
          })}
        </div>
      </div>

      <div className="zo-orbit-detail" aria-live="polite">
        <p id={labelId} className="zo-orbit-detail-title">{active.title}</p>
        <p className="zo-orbit-detail-copy">{active.copy}</p>
      </div>
      <p className="zo-orbit-hint zo-orbit-hint-desktop">Hover or focus a capability to pause and explore.</p>
      <p className="zo-orbit-hint zo-orbit-hint-mobile">Tap a capability to learn more.</p>
    </div>
  )
}
