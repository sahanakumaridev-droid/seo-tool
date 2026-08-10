import { useMemo, useState } from 'react'
import { ArrowRight, ChevronRight } from 'lucide-react'
import { BUILD_PATHS } from '../../data/revampContent'

export default function PathExplorer({ onExploreAI, onStartProject }) {
  const [activeKey, setActiveKey] = useState('website')

  const active = useMemo(
    () => BUILD_PATHS.find((p) => p.key === activeKey) || BUILD_PATHS[0],
    [activeKey],
  )

  return (
    <section id="paths" className="rv-paths-section" aria-label="What do you want to build">
      <div className="rv-shell">
        <header className="rv-paths-head">
          <p className="rv-eyebrow-muted">OUR WORK</p>
          <h2>Pick a path. See how we engineer it.</h2>
          <p className="rv-paths-sub">
            Choose AI, web, mobile, automation, or growth—then review the challenge, solution, technology, and outcome ZeOrbit builds for U.S. businesses.
          </p>
        </header>

        <div className="rv-paths-grid" role="list">
          {BUILD_PATHS.map((path) => {
            const selected = path.key === activeKey
            return (
              <button
                key={path.key}
                type="button"
                role="listitem"
                className={`rv-path-card${selected ? ' selected' : ''}`}
                aria-pressed={selected}
                onClick={() => setActiveKey(path.key)}
              >
                <span className="rv-path-art">
                  <img
                    src={path.cardImage}
                    alt=""
                    loading="lazy"
                    decoding="async"
                    width={640}
                    height={460}
                    sizes="(max-width: 640px) 100vw, (max-width: 1100px) 45vw, 220px"
                  />
                </span>
                <span className="rv-path-meta">
                  <span className="rv-path-label">{path.label}</span>
                  <span className="rv-path-eyebrow">{path.eyebrow}</span>
                </span>
              </button>
            )
          })}
        </div>

        <div className="rv-path-reveal" aria-live="polite">
          <div className="rv-path-reveal-copy">
            <p className="rv-path-reveal-eyebrow">{active.eyebrow}</p>
            <h3>{active.revealTitle}</h3>
            <p className="rv-path-reveal-body">
              {active.revealBody || 'Explore how ZeOrbit turns this path into production-ready delivery.'}
            </p>
            <div className="rv-path-actions">
              {active.key === 'ai' && onExploreAI ? (
                <button type="button" className="btn btn-secondary" onClick={onExploreAI}>
                  Explore AI Capabilities
                </button>
              ) : null}
              <button type="button" className="btn btn-primary" onClick={onStartProject}>
                Start a Project <ArrowRight size={16} />
              </button>
            </div>
          </div>

          <div className="rv-path-reveal-visual">
            <img
              src={active.revealImage}
              alt=""
              loading="lazy"
              decoding="async"
              width={960}
              height={640}
              sizes="(max-width: 860px) 100vw, 480px"
            />
          </div>

          <ul className="rv-path-stack">
            {active.items.map((item, index) => (
              <li key={item} style={{ '--rv-stack-i': index }}>
                <span className="rv-path-stack-index">{String(index + 1).padStart(2, '0')}</span>
                <span>{item}</span>
                <ChevronRight size={16} className="rv-path-stack-chevron" aria-hidden />
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
