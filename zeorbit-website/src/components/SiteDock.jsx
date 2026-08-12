import { useEffect, useId, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Accessibility,
  Contrast,
  Eye,
  Home,
  LayoutGrid,
  Link2,
  MessageCircle,
  Moon,
  Move,
  Search,
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
  const [searchOpen, setSearchOpen] = useState(false)
  const [a11yOpen, setA11yOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [a11yFlags, setA11yFlags] = useState(() =>
    Object.fromEntries(A11Y_OPTIONS.map((o) => [o.id, false])),
  )
  const inputRef = useRef(null)
  const searchTitleId = useId()
  const a11yTitleId = useId()
  const navigate = useNavigate()

  useEffect(() => {
    const root = document.documentElement
    A11Y_OPTIONS.forEach((opt) => {
      root.classList.toggle(opt.className, Boolean(a11yFlags[opt.id]))
    })
  }, [a11yFlags])

  useEffect(() => {
    if (!searchOpen && !a11yOpen) return undefined
    const onKey = (e) => {
      if (e.key === 'Escape') {
        setSearchOpen(false)
        setA11yOpen(false)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [searchOpen, a11yOpen])

  useEffect(() => {
    if (!searchOpen) return undefined
    const t = window.setTimeout(() => inputRef.current?.focus(), 40)
    return () => window.clearTimeout(t)
  }, [searchOpen])

  const submitSearch = (e) => {
    e.preventDefault()
    const q = query.trim()
    setSearchOpen(false)
    if (!q) return
    navigate(`/seo-ppc#blog`)
  }

  const toggleFlag = (id) => {
    setA11yFlags((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const resetA11y = () => {
    setA11yFlags(Object.fromEntries(A11Y_OPTIONS.map((o) => [o.id, false])))
  }

  const a11yActive = Object.values(a11yFlags).some(Boolean)

  return (
    <>
      <nav className="zo-site-dock" aria-label="Quick tools">
        <Link to="/" className="zo-site-dock-btn" aria-label="Home" title="Home">
          <Home size={18} strokeWidth={2.1} />
        </Link>
        <a href="/#solutions" className="zo-site-dock-btn" aria-label="Sitemap" title="Sitemap">
          <LayoutGrid size={18} strokeWidth={2.1} />
        </a>
        <button
          type="button"
          className="zo-site-dock-btn"
          aria-label="Search"
          title="Search"
          onClick={() => {
            setA11yOpen(false)
            setSearchOpen(true)
          }}
        >
          <Search size={18} strokeWidth={2.1} />
        </button>
        <button
          type="button"
          className={`zo-site-dock-btn${a11yOpen || a11yActive ? ' is-active' : ''}`}
          aria-label="Accessibility tools"
          aria-expanded={a11yOpen}
          title="Accessibility"
          onClick={() => {
            setSearchOpen(false)
            setA11yOpen((v) => !v)
          }}
        >
          <Accessibility size={18} strokeWidth={2.1} />
        </button>
        <Link to="/contact" className="zo-site-dock-contact" aria-label="Contact">
          <MessageCircle size={17} strokeWidth={2.1} />
          <span>Contact</span>
        </Link>
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

      {searchOpen ? (
        <div className="zo-site-search" role="dialog" aria-modal="true" aria-labelledby={searchTitleId}>
          <button
            type="button"
            className="zo-site-search-backdrop"
            aria-label="Close search"
            onClick={() => setSearchOpen(false)}
          />
          <form className="zo-site-search-panel" onSubmit={submitSearch}>
            <div className="zo-site-search-head">
              <h2 id={searchTitleId}>Search</h2>
              <button type="button" aria-label="Close" onClick={() => setSearchOpen(false)}>
                <X size={18} strokeWidth={2.2} />
              </button>
            </div>
            <input
              ref={inputRef}
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search blogs and topics…"
              autoComplete="off"
            />
            <button type="submit" className="zo-site-search-go">
              Search
            </button>
          </form>
        </div>
      ) : null}
    </>
  )
}
