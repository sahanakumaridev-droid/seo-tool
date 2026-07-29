import { useMemo, useState } from 'react'
import {
  ArrowRight,
  Bot,
  Check,
  Code2,
  Globe2,
  Layers,
  Search,
  Smartphone,
  Sparkles,
  Workflow,
} from 'lucide-react'

const STACK_OPTIONS = [
  { key: 'website', label: 'Website', icon: Globe2 },
  { key: 'mobile', label: 'Mobile App', icon: Smartphone },
  { key: 'ai', label: 'AI Solutions', icon: Sparkles },
  { key: 'seo', label: 'SEO / AEO / GEO', icon: Search },
  { key: 'automation', label: 'Automation', icon: Workflow },
  { key: 'software', label: 'Custom Software', icon: Code2 },
]

/** Rule-based recommendations — product logic, not fake AI scores */
const SUGGESTIONS = {
  website: ['seo', 'ai'],
  mobile: ['ai', 'automation'],
  ai: ['automation', 'data'],
  seo: ['website', 'ai'],
  automation: ['ai', 'software'],
  software: ['ai', 'automation'],
}

const REASONS = {
  website: 'A strong website compounds when SEO/AEO and AI-assisted capture sit on the same foundation.',
  mobile: 'Mobile products grow faster when AI copilots and automation reduce the ops load behind every release.',
  ai: 'AI delivers value when agents, RAG, and copilots connect to real workflows—not isolated demos.',
  seo: 'Search and AI discovery work best when site structure and content are built for humans and engines.',
  automation: 'Automation scales when AI decisions and custom software keep tools, teams, and data in sync.',
  software: 'Custom software pays off when AI and automation remove the repetitive work operators still do by hand.',
}

function buildRecommendation(selectedKeys) {
  const selected = new Set(selectedKeys)
  const scores = {}

  selectedKeys.forEach((key) => {
    ;(SUGGESTIONS[key] || []).forEach((rec) => {
      if (selected.has(rec) || rec === 'data') {
        if (rec === 'data' && !selected.has('ai') && !selected.has('software')) return
      }
      if (selected.has(rec)) return
      // Map 'data' suggestion to software/automation pairing via ai
      if (rec === 'data') return
      scores[rec] = (scores[rec] || 0) + 1
    })
  })

  const additions = Object.entries(scores)
    .sort((a, b) => b[1] - a[1])
    .map(([key]) => key)
    .filter((key) => STACK_OPTIONS.some((o) => o.key === key))
    .slice(0, 2)

  const primary = selectedKeys[0]
  const reason =
    selectedKeys.length === 0
      ? 'Select capabilities—AI, software, web, mobile, automation, or search. ZeOrbit AI will recommend a coherent stack.'
      : REASONS[primary] ||
        'This stack balances product delivery, search visibility, and operational leverage for U.S. growth teams.'

  return { additions, reason }
}

export default function GrowthStack({ onSeePlan }) {
  const [selected, setSelected] = useState(() => new Set(['website', 'ai']))

  const selectedKeys = useMemo(() => STACK_OPTIONS.filter((o) => selected.has(o.key)).map((o) => o.key), [selected])
  const selectedLabels = useMemo(
    () => STACK_OPTIONS.filter((o) => selected.has(o.key)).map((o) => o.label),
    [selected],
  )

  const { additions, reason } = useMemo(() => buildRecommendation(selectedKeys), [selectedKeys])
  const additionLabels = additions
    .map((key) => STACK_OPTIONS.find((o) => o.key === key)?.label)
    .filter(Boolean)

  function toggle(key) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }

  const progress = selected.size
  const total = STACK_OPTIONS.length
  const pct = Math.round((progress / total) * 100)

  return (
    <section id="growth-stack" className="zo-stack-section" aria-labelledby="zo-stack-title">
      <div className="rv-shell zo-stack-grid">
        <div className="zo-stack-panel">
          <div className="zo-stack-head">
            <Layers size={18} aria-hidden />
            <div>
              <h2 id="zo-stack-title">AI That Works for Your Business</h2>
              <p>
                From AI agents and intelligent search to workflow automation and custom AI integrations, we turn AI into practical systems your business can use every day.
              </p>
            </div>
          </div>

          <div className="zo-stack-progress" role="status" aria-live="polite">
            <div className="zo-stack-progress-meta">
              <span>Stack progress</span>
              <strong>{progress}/{total}</strong>
            </div>
            <div
              className="zo-stack-progress-track"
              role="progressbar"
              aria-valuemin={0}
              aria-valuemax={total}
              aria-valuenow={progress}
              aria-label="Selected capabilities"
            >
              <span style={{ width: `${pct}%` }} />
            </div>
          </div>

          <div className="zo-stack-options" role="group" aria-label="Capability selection">
            {STACK_OPTIONS.map((opt) => {
              const Icon = opt.icon
              const on = selected.has(opt.key)
              return (
                <button
                  key={opt.key}
                  type="button"
                  className={`zo-stack-option${on ? ' selected' : ''}`}
                  aria-pressed={on}
                  onClick={() => toggle(opt.key)}
                >
                  {on ? (
                    <span className="zo-stack-check" aria-hidden>
                      <Check size={12} />
                    </span>
                  ) : null}
                  <Icon size={22} aria-hidden />
                  <span>{opt.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        <div className="zo-stack-arrow" aria-hidden>
          <ArrowRight size={18} />
        </div>

        <div className="zo-stack-recommend" aria-live="polite">
          <div className="zo-stack-recommend-copy">
            <p className="zo-stack-recommend-eyebrow">
              <Bot size={14} aria-hidden /> ZeOrbit AI Recommendation
            </p>
            <p className="zo-stack-recommend-text">{reason}</p>

            <p className="zo-stack-sublabel">Selected</p>
            <div className="zo-stack-tags">
              {selectedLabels.length
                ? selectedLabels.map((label) => <span key={label}>{label}</span>)
                : <span>Select capabilities to begin</span>}
            </div>

            {additionLabels.length ? (
              <>
                <p className="zo-stack-sublabel">Recommended additions</p>
                <div className="zo-stack-tags zo-stack-tags-rec">
                  {additionLabels.map((label) => (
                    <span key={label}>{label}</span>
                  ))}
                </div>
              </>
            ) : null}

            <button
              type="button"
              className="btn zo-gradient-btn"
              onClick={onSeePlan}
              disabled={selected.size === 0}
            >
              See Your Plan <ArrowRight size={16} aria-hidden />
            </button>
          </div>
          <img
            className="zo-stack-robot"
            src="/zeorbit-robot.png"
            alt=""
            width={280}
            height={280}
            loading="lazy"
            decoding="async"
            sizes="(max-width: 860px) 160px, 210px"
          />
        </div>
      </div>
    </section>
  )
}
