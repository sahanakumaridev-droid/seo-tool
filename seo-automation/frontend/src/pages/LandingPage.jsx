import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import {
  ArrowRight, Search, ShieldCheck, TrendingUp, MapPin, Pencil, Sparkles,
  Check, Rocket,
} from 'lucide-react'
import Logo from '../components/Logo'

const STATS = [
  ['25B+', 'Keywords'],
  ['220M+', 'Domains'],
  ['50', 'US States'],
  ['140+', 'Audit Checks'],
  ['35+', 'SEO Tools'],
  ['7-Day', 'Free Trial'],
]

const FEATURES = [
  { icon: Search, title: 'Keyword Research', body: 'Find what US customers actually type — then build pages that match intent.', tone: '#2563eb' },
  { icon: ShieldCheck, title: 'Site Audit', body: 'Crawl a live URL for technical, on-page, and content issues you can fix today.', tone: '#16a34a' },
  { icon: TrendingUp, title: 'Rank Tracker', body: 'Watch positions, clicks, and impressions for the keywords you care about.', tone: '#7c3aed' },
  { icon: MapPin, title: 'Local SEO', body: 'One page per city, community, or street — San Diego County ready.', tone: '#dc2626' },
  { icon: Pencil, title: 'Content Tools', body: 'Separate Page and Post workflows. Publish to ZeOrbit sitemaps.', tone: '#7c3aed' },
  { icon: Sparkles, title: 'AI Visibility', body: 'Copy structured for Google and AI answers — plus llms.txt for Gemini and ChatGPT.', tone: '#7c3aed' },
]

const PLANS = [
  { name: 'Starter', price: '$49', period: '/mo', points: ['Keyword research', 'Site audit', '5 location pages / mo', 'Email support'], cta: 'Start free trial', featured: false },
  { name: 'Professional', price: '$149', period: '/mo', points: ['Everything in Starter', 'Unlimited local pages', 'Google indexing tracking', 'AI content + social share'], cta: 'Start free trial', featured: true },
  { name: 'Enterprise', price: 'Custom', period: '', points: ['Unlimited projects', 'Dedicated support', 'Custom integrations', 'SLA'], cta: 'Contact sales', featured: false },
]

const FAQS = [
  { q: 'Is ZeOrbit only for SEO?', a: 'SEO is the core, but the workspace also covers content generation, Google indexing, social sharing, ads, and a CRM pipeline.' },
  { q: 'Does ZeOrbit support local SEO?', a: 'Yes. Generate one URL per city, community, or street — especially San Diego County — then publish to page-sitemap.xml.' },
  { q: 'Is this US-only?', a: 'ZeOrbit serves United States businesses. The marketing site and SEO workspace are gated for US visitors and search crawlers.' },
  { q: 'Do I need a credit card for the trial?', a: 'No. Start a 7-day trial, cancel anytime.' },
]

export default function LandingPage() {
  const navigate = useNavigate()
  const [domain, setDomain] = useState('')

  const goAnalyze = (e) => {
    e.preventDefault()
    const raw = domain.trim()
    if (raw) {
      try {
        const project = JSON.parse(localStorage.getItem('seo_project') || '{}')
        project.website = /^https?:\/\//i.test(raw) ? raw : `https://${raw}`
        localStorage.setItem('seo_project', JSON.stringify(project))
      } catch { /* ignore */ }
    }
    navigate('/login', { state: { from: { pathname: '/site-audit' } } })
  }

  return (
    <div className="mkt">
      <header className="mkt-nav">
        <Link to="/" aria-label="ZeOrbit home" className="mkt-logo">
          <Logo size={34} />
        </Link>
        <nav className="mkt-links">
          <a href="#features">Features</a>
          <a href="#data">Data</a>
          <a href="#pricing">Pricing</a>
          <a href="#faq">FAQ</a>
        </nav>
        <div className="mkt-nav-actions">
          <Link to="/login" className="mkt-login">Log in</Link>
          <Link to="/register" className="btn btn-primary">Start free trial</Link>
        </div>
      </header>

      <section className="mkt-hero">
        <div className="mkt-hero-copy">
          <h1>Rank higher. Get found. Grow faster.</h1>
          <p>
            Everything you need for SEO — keyword research, site audit, rank tracking, local SEO, content & more.
            Powered by data. Driven by AI.
          </p>
          <form className="mkt-analyze" onSubmit={goAnalyze}>
            <Search size={16} />
            <input
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="Enter a domain, e.g. yourbusiness.com"
            />
            <button type="submit" className="btn btn-primary">Analyze</button>
          </form>
          <div className="mkt-hero-cta">
            <Link to="/register" className="btn btn-primary">Start 7-day free trial</Link>
            <a href="#pricing" className="btn btn-secondary">View pricing</a>
          </div>
          <div className="mkt-trust">
            <span>US search only</span>
            <span>No credit card</span>
            <span>Cancel anytime</span>
          </div>
        </div>
        <div className="mkt-hero-card" aria-hidden="true">
          <div className="mkt-card-head">
            <strong>Overview</strong>
            <span>Last 30 days</span>
          </div>
          <div className="mkt-kpis">
            <div><em>Visibility Score</em><b>85/100</b><small>+16%</small></div>
            <div><em>Avg. Position</em><b>12.4</b><small>+3.2</small></div>
            <div><em>Clicks</em><b>24.8K</b><small>+28%</small></div>
          </div>
          <div className="mkt-chart">
            <svg viewBox="0 0 320 120" fill="none" preserveAspectRatio="none">
              <path d="M0 90 C40 80 60 70 90 72 S140 40 170 48 S230 20 260 28 S300 18 320 22" stroke="#7c3aed" strokeWidth="2.5" />
              <path d="M0 100 C50 95 80 88 110 86 S170 70 200 74 S260 50 320 44" stroke="#2563eb" strokeWidth="2.5" />
            </svg>
            <div className="mkt-chart-legend"><span>Clicks</span><span>Impressions</span></div>
          </div>
          <div className="mkt-kpis mkt-kpis-sm">
            <div><em>Site Audit</em><b>96%</b></div>
            <div><em>Issues</em><b>142</b><small className="is-bad">3 Critical</small></div>
            <div><em>Crawled Pages</em><b>12,480</b></div>
          </div>
        </div>
      </section>

      <section id="data" className="mkt-stats">
        {STATS.map(([n, l]) => (
          <div key={l}><strong>{n}</strong><span>{l}</span></div>
        ))}
      </section>

      <section id="features" className="mkt-features">
        <h2>Everything SEO teams need</h2>
        <div className="mkt-feat-grid">
          {FEATURES.map((f) => (
            <article key={f.title}>
              <span className="mkt-feat-icon" style={{ color: f.tone, background: `${f.tone}14` }}><f.icon size={18} /></span>
              <h3>{f.title}</h3>
              <p>{f.body}</p>
              <Link to="/register">Learn more <ArrowRight size={14} /></Link>
            </article>
          ))}
        </div>
      </section>

      <section id="pricing" className="mkt-pricing">
        <h2>Simple pricing. Transparent value.</h2>
        <div className="mkt-plans">
          {PLANS.map((p) => (
            <article key={p.name} className={p.featured ? 'is-featured' : ''}>
              {p.featured ? <span className="mkt-badge">Most Popular</span> : null}
              <h3>{p.name}</h3>
              <div className="mkt-price">{p.price}<small>{p.period}</small></div>
              <ul>
                {p.points.map((x) => (
                  <li key={x}><Check size={14} /> {x}</li>
                ))}
              </ul>
              <Link to={p.cta.includes('Contact') ? '/register' : '/register'} className={p.featured ? 'btn btn-primary' : 'btn btn-secondary'}>
                {p.cta}
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section id="faq" className="mkt-faq">
        <h2>FAQ</h2>
        {FAQS.map((item) => (
          <details key={item.q}>
            <summary>{item.q}</summary>
            <p>{item.a}</p>
          </details>
        ))}
      </section>

      <section className="mkt-final">
        <div>
          <h2>Ready to outrank your competition?</h2>
          <Link to="/register" className="btn btn-primary">Start your 7-day free trial <Rocket size={16} /></Link>
        </div>
      </section>

      <footer className="mkt-foot">
        <div>
          <Logo size={28} />
          <p>All-in-one SEO platform for US businesses.</p>
        </div>
        <div className="mkt-foot-cols">
          <div><strong>Product</strong><a href="#features">Features</a><a href="#pricing">Pricing</a></div>
          <div><strong>Company</strong><a href="https://zeorbit.com/">zeorbit.com</a><Link to="/login">Log in</Link></div>
          <div><strong>Legal</strong><span>© {new Date().getFullYear()} ZeOrbit</span></div>
        </div>
      </footer>
    </div>
  )
}
