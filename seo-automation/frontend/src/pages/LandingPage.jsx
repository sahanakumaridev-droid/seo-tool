import { Link } from 'react-router-dom'
import { ArrowRight, FileText, MapPin, Search } from 'lucide-react'
import Logo from '../components/Logo'

const FEATURES = [
  {
    icon: FileText,
    title: 'Pages & posts',
    body: 'Generate service pages and how-to articles as separate workflows. Pages go to page-sitemap.xml. Posts go to post-sitemap.xml.',
  },
  {
    icon: MapPin,
    title: 'Local SEO',
    body: 'San Diego County cities, communities, and streets — one URL per place, not a jammed title.',
  },
  {
    icon: Search,
    title: 'Indexing',
    body: 'Publish to ZeOrbit, then track submitted, crawled, and indexed URLs in Google Search Console.',
  },
]

export default function LandingPage() {
  return (
    <div className="seo-landing">
      <header className="seo-landing-nav">
        <Link to="/" aria-label="ZeOrbit SEO home">
          <Logo size={36} />
        </Link>
        <div className="seo-landing-nav-actions">
          <Link to="/login" className="btn btn-secondary">Sign in</Link>
          <Link to="/register" className="btn btn-primary">Start free</Link>
        </div>
      </header>

      <main className="seo-landing-main">
        <p className="seo-landing-kicker">ZeOrbit SEO Intelligence</p>
        <h1>Create local pages and blog posts that actually rank.</h1>
        <p className="seo-landing-lead">
          White-workspace tools for U.S. businesses — generate content, publish to ZeOrbit, and keep Google on the right sitemap.
        </p>
        <div className="seo-landing-cta">
          <Link to="/register" className="btn btn-primary">
            Create an account <ArrowRight size={16} />
          </Link>
          <Link to="/login" className="btn btn-secondary">I already have an account</Link>
        </div>

        <div className="seo-landing-grid">
          {FEATURES.map((f) => (
            <article key={f.title} className="seo-landing-card">
              <f.icon size={18} strokeWidth={2.1} />
              <h2>{f.title}</h2>
              <p>{f.body}</p>
            </article>
          ))}
        </div>
      </main>

      <footer className="seo-landing-foot">
        <a href="https://zeorbit.com/">zeorbit.com</a>
        <span>·</span>
        <span>© {new Date().getFullYear()} ZeOrbit</span>
      </footer>
    </div>
  )
}
