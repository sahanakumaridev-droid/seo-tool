import { useEffect, useId, useState } from 'react'
import {
  Accessibility,
  Contrast,
  Eye,
  Link2,
  Moon,
  Move,
  Type,
  Underline,
  X,
  ZoomIn,
} from 'lucide-react'

const A11Y_OPTIONS = [
  { id: 'text', label: 'Larger text', icon: Type, className: 'zo-a11y-text' },
  { id: 'contrast', label: 'High contrast', icon: Contrast, className: 'zo-a11y-contrast' },
  { id: 'links', label: 'Underline links', icon: Underline, className: 'zo-a11y-links' },
  { id: 'readable', label: 'Readable font', icon: ZoomIn, className: 'zo-a11y-readable' },
  { id: 'spacing', label: 'More spacing', icon: Move, className: 'zo-a11y-spacing' },
  { id: 'motion', label: 'Reduce motion', icon: Eye, className: 'zo-a11y-motion' },
  { id: 'focus', label: 'Stronger focus', icon: Link2, className: 'zo-a11y-focus' },
  { id: 'dark', label: 'Dark assist', icon: Moon, className: 'zo-a11y-dark' },
]

export default function SiteDock() {
  const [a11yOpen, setA11yOpen] = useState(false)
  const [a11yFlags, setA11yFlags] = useState(() =>
    Object.fromEntries(A11Y_OPTIONS.map((o) => [o.id, false])),
  )
  const a11yTitleId = useId()

  useEffect(() => {
    const root = document.documentElement
    A11Y_OPTIONS.forEach((opt) => {
      root.classList.toggle(opt.className, Boolean(a11yFlags[opt.id]))
    })
  }, [a11yFlags])

  useEffect(() => {
    if (!a11yOpen) return undefined
    const onKey = (e) => {
      if (e.key === 'Escape') setA11yOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [a11yOpen])

  const toggleFlag = (id) => {
    setA11yFlags((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const resetA11y = () => {
    setA11yFlags(Object.fromEntries(A11Y_OPTIONS.map((o) => [o.id, false])))
  }

  const a11yActive = Object.values(a11yFlags).some(Boolean)

  return (
    <>
      <nav className="zo-site-dock zo-site-dock--a11y-only" aria-label="Accessibility">
        <button
          type="button"
          className={`zo-site-dock-btn${a11yOpen || a11yActive ? ' is-active' : ''}`}
          aria-label="Accessibility tools"
          aria-expanded={a11yOpen}
          title="Accessibility"
          onClick={() => setA11yOpen((v) => !v)}
        >
          <Accessibility size={18} strokeWidth={2.1} />
        </button>
      </nav>

      {a11yOpen ? (
        <div className="zo-a11y-panel" role="dialog" aria-modal="true" aria-labelledby={a11yTitleId}>
          <button
            type="button"
            className="zo-site-search-backdrop"
            aria-label="Close accessibility tools"
            onClick={() => setA11yOpen(false)}
          />
          <div className="zo-a11y-card">
            <div className="zo-site-search-head">
              <h2 id={a11yTitleId}>Accessibility tools</h2>
              <button type="button" aria-label="Close" onClick={() => setA11yOpen(false)}>
                <X size={18} strokeWidth={2.2} />
              </button>
            </div>
            <p className="zo-a11y-lead">Turn on the options you need. Changes apply instantly across the site.</p>
            <div className="zo-a11y-grid">
              {A11Y_OPTIONS.map((opt) => {
                const Icon = opt.icon
                const on = a11yFlags[opt.id]
                return (
                  <button
                    key={opt.id}
                    type="button"
                    className={`zo-a11y-option${on ? ' is-on' : ''}`}
                    aria-pressed={on}
                    onClick={() => toggleFlag(opt.id)}
                  >
                    <span className="zo-a11y-option-icon" aria-hidden="true">
                      <Icon size={18} strokeWidth={2.1} />
                    </span>
                    <span>{opt.label}</span>
                  </button>
                )
              })}
            </div>
            <div className="zo-a11y-actions">
              <button type="button" className="zo-a11y-reset" onClick={resetA11y}>
                Reset all
              </button>
              <a className="zo-a11y-skip" href="#main">
                Skip to content
              </a>
            </div>
          </div>
        </div>
      ) : null}
    </>
  )
}
