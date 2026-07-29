import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import Logo from '../components/Logo'
import InsightsFeed from '../components/revamp/InsightsFeed'

export default function BlogPage() {
  return (
    <div className="rv-page">
      <header className="rv-header">
        <div className="rv-header-inner">
          <a href="/" className="rv-logo-wrap" aria-label="ZeOrbit home">
            <Logo size={32} />
          </a>
          <nav className="rv-desktop-nav" aria-label="Primary">
            <Link to="/">Home</Link>
            <Link to="/blog">Blog</Link>
            <a href="/#contact">Contact</a>
          </nav>
          <div className="rv-header-actions">
            <Link className="btn btn-primary" to="/login">Start a Project</Link>
          </div>
        </div>
      </header>

      <main className="rv-section" style={{ paddingTop: 120 }}>
        <div className="rv-shell">
          <p className="rv-eyebrow">Blog · Insights</p>
          <h1 className="rv-blog-title">Published SEO intelligence</h1>
          <p className="rv-blog-lead">
            Live articles from the ZeOrbit SEO tool — every page published to the web
            (and tracked WordPress posts) appears here automatically.
          </p>

          <p style={{ marginBottom: 24 }}>
            <Link to="/" className="rv-link-button" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <ArrowLeft size={16} /> Back to home
            </Link>
          </p>

          <InsightsFeed limit={48} showViewAll={false} emptyUseFallback={false} />
        </div>
      </main>
    </div>
  )
}
