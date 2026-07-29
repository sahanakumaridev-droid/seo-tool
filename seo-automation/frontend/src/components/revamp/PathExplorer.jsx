import { useMemo, useState } from 'react'
import { ArrowRight } from 'lucide-react'
import { BUILD_PATHS } from '../../data/revampContent'

function SvgGrow() {
  return (
    <svg viewBox="0 0 320 220" className="rv-path-svg" aria-hidden="true">
      <defs>
        <linearGradient id="pg-a" x1="0" y1="1" x2="1" y2="0">
          <stop offset="0%" stopColor="#5872ff" />
          <stop offset="100%" stopColor="#22c55e" />
        </linearGradient>
        <linearGradient id="pg-b" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#dbeafe" />
          <stop offset="100%" stopColor="#eef2ff" />
        </linearGradient>
      </defs>
      <rect width="320" height="220" rx="28" fill="url(#pg-b)" />
      <path d="M36 168h248" stroke="#c7d2fe" strokeWidth="2" />
      <path
        d="M48 150c28-8 40-46 68-52s44 28 72 22 36-40 68-48"
        fill="none"
        stroke="url(#pg-a)"
        strokeWidth="6"
        strokeLinecap="round"
      />
      <circle cx="116" cy="98" r="7" fill="#5872ff" />
      <circle cx="188" cy="120" r="7" fill="#22c55e" />
      <circle cx="256" cy="72" r="8" fill="#0f172a" />
      <rect x="214" y="40" width="70" height="34" rx="12" fill="#0f172a" />
      <text x="249" y="62" textAnchor="middle" fill="#fff" fontSize="14" fontWeight="700" fontFamily="system-ui,sans-serif">
        +48%
      </text>
      <rect x="48" y="168" width="28" height="22" rx="6" fill="#93c5fd" opacity="0.7" />
      <rect x="88" y="156" width="28" height="34" rx="6" fill="#60a5fa" opacity="0.75" />
      <rect x="128" y="142" width="28" height="48" rx="6" fill="#5872ff" opacity="0.85" />
      <rect x="168" y="128" width="28" height="62" rx="6" fill="#22c55e" opacity="0.8" />
    </svg>
  )
}

function SvgAI() {
  return (
    <svg viewBox="0 0 320 220" className="rv-path-svg" aria-hidden="true">
      <defs>
        <linearGradient id="pa-a" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#8b5cf6" />
          <stop offset="100%" stopColor="#5872ff" />
        </linearGradient>
        <linearGradient id="pa-b" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f5f3ff" />
          <stop offset="100%" stopColor="#ede9fe" />
        </linearGradient>
      </defs>
      <rect width="320" height="220" rx="28" fill="url(#pa-b)" />
      <circle cx="160" cy="108" r="46" fill="url(#pa-a)" opacity="0.18" />
      <circle cx="160" cy="108" r="28" fill="url(#pa-a)" />
      <circle cx="160" cy="108" r="10" fill="#fff" />
      <circle cx="78" cy="64" r="12" fill="#fff" stroke="#a78bfa" strokeWidth="2" />
      <circle cx="242" cy="64" r="12" fill="#fff" stroke="#a78bfa" strokeWidth="2" />
      <circle cx="64" cy="148" r="10" fill="#fff" stroke="#a78bfa" strokeWidth="2" />
      <circle cx="256" cy="148" r="10" fill="#fff" stroke="#a78bfa" strokeWidth="2" />
      <path
        d="M90 70l46 28M230 70l-46 28M74 142l60-20M246 142l-60-20"
        stroke="#8b5cf6"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <rect x="96" y="172" width="128" height="24" rx="12" fill="#fff" stroke="#ddd6fe" strokeWidth="2" />
      <rect x="112" y="180" width="52" height="8" rx="4" fill="#8b5cf6" opacity="0.45" />
      <rect x="172" y="180" width="36" height="8" rx="4" fill="#5872ff" opacity="0.35" />
    </svg>
  )
}

function SvgWeb() {
  return (
    <svg viewBox="0 0 320 220" className="rv-path-svg" aria-hidden="true">
      <defs>
        <linearGradient id="pw-a" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#38bdf8" />
          <stop offset="100%" stopColor="#5872ff" />
        </linearGradient>
        <linearGradient id="pw-b" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ecfeff" />
          <stop offset="100%" stopColor="#e0f2fe" />
        </linearGradient>
      </defs>
      <rect width="320" height="220" rx="28" fill="url(#pw-b)" />
      <rect x="44" y="42" width="232" height="136" rx="16" fill="#0f172a" />
      <rect x="56" y="58" width="208" height="104" rx="10" fill="url(#pw-a)" opacity="0.95" />
      <circle cx="72" cy="50" r="3.5" fill="#f87171" />
      <circle cx="86" cy="50" r="3.5" fill="#fbbf24" />
      <circle cx="100" cy="50" r="3.5" fill="#4ade80" />
      <rect x="68" y="72" width="88" height="10" rx="5" fill="#fff" opacity="0.9" />
      <rect x="68" y="90" width="64" height="8" rx="4" fill="#fff" opacity="0.45" />
      <rect x="68" y="112" width="100" height="36" rx="10" fill="#fff" opacity="0.22" />
      <rect x="180" y="72" width="68" height="76" rx="12" fill="#fff" opacity="0.2" />
      <rect x="120" y="186" width="80" height="8" rx="4" fill="#94a3b8" opacity="0.5" />
    </svg>
  )
}

function SvgApp() {
  return (
    <svg viewBox="0 0 320 220" className="rv-path-svg" aria-hidden="true">
      <defs>
        <linearGradient id="pm-a" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#06b6d4" />
          <stop offset="100%" stopColor="#5872ff" />
        </linearGradient>
        <linearGradient id="pm-b" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#ecfeff" />
          <stop offset="100%" stopColor="#e0f2fe" />
        </linearGradient>
      </defs>
      <rect width="320" height="220" rx="28" fill="url(#pm-b)" />
      <rect x="118" y="28" width="84" height="164" rx="18" fill="#0f172a" />
      <rect x="128" y="42" width="64" height="128" rx="10" fill="url(#pm-a)" />
      <rect x="142" y="52" width="36" height="6" rx="3" fill="#fff" opacity="0.85" />
      <rect x="136" y="70" width="48" height="28" rx="8" fill="#fff" opacity="0.22" />
      <rect x="136" y="106" width="20" height="20" rx="6" fill="#fff" opacity="0.35" />
      <rect x="164" y="106" width="20" height="20" rx="6" fill="#fff" opacity="0.35" />
      <rect x="148" y="178" width="24" height="4" rx="2" fill="#64748b" />
      <rect x="54" y="78" width="52" height="72" rx="12" fill="#fff" stroke="#bae6fd" strokeWidth="2" />
      <rect x="64" y="90" width="32" height="6" rx="3" fill="#06b6d4" opacity="0.5" />
      <rect x="64" y="104" width="24" height="6" rx="3" fill="#5872ff" opacity="0.35" />
      <rect x="214" y="78" width="52" height="72" rx="12" fill="#fff" stroke="#bae6fd" strokeWidth="2" />
      <rect x="224" y="90" width="32" height="6" rx="3" fill="#5872ff" opacity="0.5" />
      <rect x="224" y="104" width="24" height="6" rx="3" fill="#06b6d4" opacity="0.35" />
    </svg>
  )
}

function SvgAutomate() {
  return (
    <svg viewBox="0 0 320 220" className="rv-path-svg" aria-hidden="true">
      <defs>
        <linearGradient id="pz-a" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f59e0b" />
          <stop offset="100%" stopColor="#5872ff" />
        </linearGradient>
        <linearGradient id="pz-b" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#fffbeb" />
          <stop offset="100%" stopColor="#eef2ff" />
        </linearGradient>
      </defs>
      <rect width="320" height="220" rx="28" fill="url(#pz-b)" />
      <rect x="48" y="56" width="72" height="48" rx="14" fill="#fff" stroke="#c7d2fe" strokeWidth="2" />
      <rect x="124" y="56" width="72" height="48" rx="14" fill="#fff" stroke="#c7d2fe" strokeWidth="2" />
      <rect x="200" y="56" width="72" height="48" rx="14" fill="url(#pz-a)" />
      <path d="M84 104v24h76v-24M160 128v24h76v-24" stroke="#94a3b8" strokeWidth="3" fill="none" />
      <rect x="48" y="128" width="72" height="48" rx="14" fill="#fff" stroke="#c7d2fe" strokeWidth="2" />
      <rect x="124" y="128" width="72" height="48" rx="14" fill="#0f172a" />
      <rect x="200" y="128" width="72" height="48" rx="14" fill="#fff" stroke="#c7d2fe" strokeWidth="2" />
      <circle cx="236" cy="80" r="6" fill="#fff" />
      <rect x="142" y="144" width="36" height="8" rx="4" fill="#fbbf24" />
      <rect x="142" y="158" width="24" height="6" rx="3" fill="#64748b" />
    </svg>
  )
}

const PATH_ART = {
  grow: SvgGrow,
  ai: SvgAI,
  website: SvgWeb,
  app: SvgApp,
  automate: SvgAutomate,
}

export default function PathExplorer({ onExploreAI, onStartProject }) {
  const [activeKey, setActiveKey] = useState('grow')

  const active = useMemo(
    () => BUILD_PATHS.find((p) => p.key === activeKey) || BUILD_PATHS[0],
    [activeKey],
  )

  return (
    <section id="paths" className="rv-paths-section" aria-label="What do you want to build">
      <div className="rv-shell">
        <header className="rv-paths-head">
          <p className="rv-eyebrow-muted">WHAT DO YOU WANT TO BUILD?</p>
          <h2>Pick a path. Reveal your stack.</h2>
          <p className="rv-paths-sub">
            Tap a capability path to open the ZeOrbit delivery stack — vector-sharp, no stock photos.
          </p>
        </header>

        <div className="rv-paths-grid" role="list">
          {BUILD_PATHS.map((path) => {
            const Art = PATH_ART[path.key]
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
                <span className="rv-path-art">{Art ? <Art /> : null}</span>
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
              {active.key === 'ai'
                ? 'Let’s build your AI advantage with agents, copilots, and production automation.'
                : 'Explore how ZeOrbit turns this path into production-grade delivery.'}
            </p>
            <div className="rv-path-actions">
              {active.key === 'ai' ? (
                <button type="button" className="btn btn-secondary" onClick={onExploreAI}>
                  Explore AI Solutions
                </button>
              ) : null}
              <button type="button" className="btn btn-primary" onClick={onStartProject}>
                Start a Project <ArrowRight size={16} />
              </button>
            </div>
          </div>

          <ul className="rv-path-stack">
            {active.items.map((item, index) => (
              <li key={item} style={{ '--rv-stack-i': index }}>
                <span className="rv-path-stack-index">{String(index + 1).padStart(2, '0')}</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
