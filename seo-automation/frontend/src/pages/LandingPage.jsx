import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import {
  ArrowRight, Search, ShieldCheck, TrendingUp, MapPin, Pencil, Sparkles,
  Check, Rocket, Bot, FileSearch, BarChart3, Globe2, Zap, Users,
  Headphones, BadgeCheck, Clock3,
} from 'lucide-react'
import MarketingHeader from '../components/marketing/MarketingHeader'
import MarketingFooter from '../components/marketing/MarketingFooter'
import '../components/marketing/seo-site-chrome.css'
import '../components/marketing/seo-landing-host.css'

const TRUST = ['US search focus', '7-day free trial', 'No credit card', 'Cancel anytime', '24/7 email support']

const STATS = [
  ['25B+', 'Keywords tracked'],
  ['220M+', 'Domains in index'],
  ['50', 'US states covered'],
  ['140+', 'Audit checks'],
  ['35+', 'SEO tools'],
  ['4.8★', 'Customer rating'],
]

const BUILD = [
  {
    kicker: 'Site Audit',
    title: 'Find what is blocking your rankings',
    body: 'Crawl a live URL for technical, on-page, and content issues — then fix the ones that move the needle first.',
    points: ['Critical issues prioritized', 'Core Web Vitals signals', 'Indexability & sitemap checks'],
    cta: 'Run a free audit',
    to: '/register',
    icon: FileSearch,
  },
  {
    kicker: 'Keyword Research',
    title: 'Target what US customers actually search',
    body: 'Volume, difficulty, CPC, and intent in one view — so every page has a job and a keyword to win.',
    points: ['US-only search intent', 'Competitor keyword gaps', 'Cluster ideas for content'],
    cta: 'Explore keywords',
    to: '/register',
    icon: Search,
  },
  {
    kicker: 'Local SEO',
    title: 'One page per city — San Diego ready',
    body: 'Generate location pages for cities, communities, and streets, then publish into ZeOrbit sitemaps.',
    points: ['City & neighborhood pages', 'NAP consistency helpers', 'Maps + service area coverage'],
    cta: 'Build local pages',
    to: '/register',
    icon: MapPin,
  },
]

const AI_TOOLS = [
  { icon: Bot, title: 'AI Visibility', body: 'Structure copy for Google and AI answers — plus llms.txt for Gemini and ChatGPT.' },
  { icon: Pencil, title: 'Content Studio', body: 'Separate Page and Post workflows. Briefs, outlines, and publish-ready drafts.' },
  { icon: Sparkles, title: 'Smart Suggestions', body: 'Title, meta, and internal-link recommendations based on your audit and keywords.' },
  { icon: Zap, title: 'Workflow Automation', body: 'From research → draft → publish → track rankings without hopping tools.' },
]

const FEATURES = [
  { icon: Search, title: 'Keyword Research', body: 'Find demand, difficulty, and intent for United States search.' },
  { icon: ShieldCheck, title: 'Technical Site Audit', body: '140+ checks across crawlability, speed, and on-page SEO.' },
  { icon: TrendingUp, title: 'Rank Tracker', body: 'Daily positions, clicks, and impressions for keywords you care about.' },
  { icon: MapPin, title: 'Local SEO Engine', body: 'Location pages that map to how people search nearby.' },
  { icon: BarChart3, title: 'Competitive Intel', body: 'See who ranks for your terms and where you can overtake them.' },
  { icon: Globe2, title: 'Indexing & Sitemaps', body: 'Publish pages into ZeOrbit sitemaps and track Google indexing.' },
]

const STORIES = [
  {
    quote: 'ZeOrbit replaced three SEO tools for us. Audits are clear, and local pages finally rank in San Diego neighborhoods.',
    name: 'Maya Chen',
    role: 'Agency owner',
    tags: ['Local SEO', 'Site Audit'],
  },
  {
    quote: 'The keyword + content workflow is the fastest path from idea to published page we have used.',
    name: 'Jordan Blake',
    role: 'Growth lead',
    tags: ['Keywords', 'Content'],
  },
  {
    quote: 'Rank tracking and AI visibility in one workspace means we stop guessing what moved the needle.',
    name: 'Priya Nair',
    role: 'Marketing director',
    tags: ['Rank Tracker', 'AI'],
  },
]

const PLANS = [
  {
    name: 'Starter',
    price: '$49',
    period: '/mo',
    blurb: 'For founders launching SEO the right way.',
    points: ['Keyword research', 'Site audit', '5 location pages / mo', 'Email support', '7-day free trial'],
    cta: 'Start free trial',
    featured: false,
    save: null,
  },
  {
    name: 'Professional',
    price: '$149',
    period: '/mo',
    blurb: 'Everything growing US teams need in one workspace.',
    points: ['Everything in Starter', 'Unlimited local pages', 'Google indexing tracking', 'AI content + social share', 'Priority support'],
    cta: 'Start free trial',
    featured: true,
    save: 'Most popular',
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    blurb: 'Dedicated power for agencies and multi-brand orgs.',
    points: ['Unlimited projects', 'Custom integrations', 'SLA & onboarding', 'Dedicated success manager'],
    cta: 'Contact sales',
    featured: false,
    save: null,
  },
]

const STEPS = [
  { n: '01', title: 'Connect your domain', body: 'Drop in a URL. We crawl, score, and surface the highest-impact fixes.' },
  { n: '02', title: 'Pick keywords & cities', body: 'Build a focused map of US demand — national terms and local intents.' },
  { n: '03', title: 'Publish & track', body: 'Ship pages, monitor rankings, and keep improving with AI-assisted workflows.' },
]

const GUARANTEES = [
  { icon: BadgeCheck, title: '7-day free trial', body: 'Full workspace access. No credit card required to start.' },
  { icon: Clock3, title: 'Cancel anytime', body: 'Stay only while ZeOrbit is earning its place in your stack.' },
  { icon: Headphones, title: 'Human support', body: 'US-friendly support when you need a hand with audits or local SEO.' },
  { icon: Users, title: 'Built for teams', body: 'Agencies, in-house marketers, and founders share one clear workflow.' },
]

const FAQS = [
  { q: 'Is ZeOrbit only for SEO?', a: 'SEO is the core, but the workspace also covers content generation, Google indexing, social sharing, ads, and a CRM pipeline.' },
  { q: 'Does ZeOrbit support local SEO?', a: 'Yes. Generate one URL per city, community, or street — especially San Diego County — then publish to page-sitemap.xml.' },
  { q: 'Is this US-only?', a: 'ZeOrbit serves United States businesses. The marketing site and SEO workspace are gated for US visitors and search crawlers.' },
  { q: 'Do I need a credit card for the trial?', a: 'No. Start a 7-day trial, cancel anytime.' },
  { q: 'Can I migrate from another SEO tool?', a: 'Yes. Import priority keywords, connect your site, and run a fresh audit so you start from current live data — not stale exports.' },
  { q: 'What makes ZeOrbit different?', a: 'It combines research, audit, local page generation, content, and rank tracking in one US-focused workspace — instead of stitching five products together.' },
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
    <div className="mkt has-site-chrome hl">
      <MarketingHeader />

      {/* Hero — Hostinger-style dark purple stage */}
      <section className="hl-hero">
        <div className="hl-hero-glow" aria-hidden />
        <div className="hl-shell hl-hero-grid">
          <div className="hl-hero-copy">
            <h1>Rank higher. Get found. Grow faster.</h1>
            <p className="hl-lead">
              The all-in-one SEO platform for US businesses — keyword research, site audit, rank tracking, local SEO, and AI content.
            </p>
            <form className="hl-analyze" onSubmit={goAnalyze}>
              <Search size={18} aria-hidden />
              <input
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="Enter your domain, e.g. yourbusiness.com"
                aria-label="Domain to analyze"
              />
              <button type="submit" className="hl-btn hl-btn-primary">Analyze</button>
            </form>
            <div className="hl-hero-actions">
              <Link to="/register" className="hl-btn hl-btn-primary">Start 7-day free trial</Link>
              <a href="#pricing" className="hl-btn hl-btn-ghost">View plans & pricing</a>
            </div>
            <ul className="hl-trust-row">
              {TRUST.map((t) => (
                <li key={t}><Check size={14} aria-hidden /> {t}</li>
              ))}
            </ul>
          </div>

          <div className="hl-hero-visual" aria-hidden="true">
            <div className="hl-panel">
              <div className="hl-panel-head">
                <strong>Visibility overview</strong>
                <span>Last 30 days</span>
              </div>
              <div className="hl-kpis">
                <div><em>Visibility</em><b>85/100</b><small>+16%</small></div>
                <div><em>Avg. position</em><b>12.4</b><small>+3.2</small></div>
                <div><em>Clicks</em><b>24.8K</b><small>+28%</small></div>
              </div>
              <div className="hl-chart">
                <svg viewBox="0 0 320 120" fill="none" preserveAspectRatio="none">
                  <path d="M0 90 C40 80 60 70 90 72 S140 40 170 48 S230 20 260 28 S300 18 320 22" stroke="#A78BFA" strokeWidth="2.5" />
                  <path d="M0 100 C50 95 80 88 110 86 S170 70 200 74 S260 50 320 44" stroke="#673DE6" strokeWidth="2.5" />
                </svg>
              </div>
              <div className="hl-kpis hl-kpis-sm">
                <div><em>Site audit</em><b>96%</b></div>
                <div><em>Issues</em><b>142</b><small className="is-bad">3 critical</small></div>
                <div><em>Pages crawled</em><b>12,480</b></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Social proof */}
      <section className="hl-section hl-section-soft" id="stories">
        <div className="hl-shell">
          <p className="hl-eyebrow">Trusted by US growth teams</p>
          <h2 className="hl-h2">They ranked higher — now it is your turn</h2>
          <div className="hl-stories">
            {STORIES.map((s) => (
              <article key={s.name} className="hl-story">
                <p>“{s.quote}”</p>
                <div className="hl-story-meta">
                  <strong>{s.name}</strong>
                  <span>{s.role}</span>
                </div>
                <div className="hl-tags">
                  {s.tags.map((t) => <span key={t}>{t}</span>)}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Build / product blocks */}
      <section className="hl-section" id="features">
        <div className="hl-shell">
          <p className="hl-eyebrow">Build and grow</p>
          <h2 className="hl-h2">From idea to rankings — quicker and clearer</h2>
          <p className="hl-sub">
            ZeOrbit connects research, audits, local pages, and content so you spend less time switching tools and more time winning search.
          </p>
          <div className="hl-build">
            {BUILD.map((b) => (
              <article key={b.title} className="hl-build-card">
                <div className="hl-build-icon"><b.icon size={22} /></div>
                <p className="hl-kicker">{b.kicker}</p>
                <h3>{b.title}</h3>
                <p>{b.body}</p>
                <ul>
                  {b.points.map((p) => (
                    <li key={p}><Check size={14} /> {p}</li>
                  ))}
                </ul>
                <Link to={b.to} className="hl-text-link">{b.cta} <ArrowRight size={14} /></Link>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="hl-stats" id="data">
        <div className="hl-shell hl-stats-grid">
          {STATS.map(([n, l]) => (
            <div key={l}>
              <strong>{n}</strong>
              <span>{l}</span>
            </div>
          ))}
        </div>
      </section>

      {/* AI tools */}
      <section className="hl-section hl-section-purple">
        <div className="hl-shell">
          <p className="hl-eyebrow hl-eyebrow-on-dark">AI tools</p>
          <h2 className="hl-h2 hl-h2-on-dark">Human-led. AI-powered.</h2>
          <p className="hl-sub hl-sub-on-dark">
            Stay in control while ZeOrbit accelerates research, drafts, and AI-search visibility.
          </p>
          <div className="hl-ai-grid">
            {AI_TOOLS.map((t) => (
              <article key={t.title}>
                <span className="hl-ai-icon"><t.icon size={20} /></span>
                <h3>{t.title}</h3>
                <p>{t.body}</p>
              </article>
            ))}
          </div>
          <div className="hl-center-cta">
            <Link to="/register" className="hl-btn hl-btn-primary hl-btn-light">Get started free</Link>
          </div>
        </div>
      </section>

      {/* Full toolset */}
      <section className="hl-section">
        <div className="hl-shell">
          <p className="hl-eyebrow">Everything in one workspace</p>
          <h2 className="hl-h2">35+ SEO tools built for US search</h2>
          <div className="hl-feat-grid">
            {FEATURES.map((f) => (
              <article key={f.title}>
                <span className="hl-feat-icon"><f.icon size={18} /></span>
                <h3>{f.title}</h3>
                <p>{f.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="hl-section hl-section-soft">
        <div className="hl-shell">
          <p className="hl-eyebrow">How it works</p>
          <h2 className="hl-h2">Live in three clear steps</h2>
          <div className="hl-steps">
            {STEPS.map((s) => (
              <article key={s.n}>
                <span>{s.n}</span>
                <h3>{s.title}</h3>
                <p>{s.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Guarantees */}
      <section className="hl-section">
        <div className="hl-shell">
          <div className="hl-guarantee-grid">
            {GUARANTEES.map((g) => (
              <article key={g.title}>
                <g.icon size={22} />
                <h3>{g.title}</h3>
                <p>{g.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="hl-section hl-section-soft" id="pricing">
        <div className="hl-shell">
          <p className="hl-eyebrow">Plans and pricing</p>
          <h2 className="hl-h2">Pick the plan that checks your boxes</h2>
          <ul className="hl-price-perks">
            <li><Check size={14} /> 7-day free trial</li>
            <li><Check size={14} /> Cancel anytime</li>
            <li><Check size={14} /> US search focus</li>
          </ul>
          <div className="hl-plans">
            {PLANS.map((p) => (
              <article key={p.name} className={p.featured ? 'is-featured' : ''}>
                {p.save ? <span className="hl-badge">{p.save}</span> : null}
                <h3>{p.name}</h3>
                <p className="hl-plan-blurb">{p.blurb}</p>
                <div className="hl-price">
                  {p.price}
                  {p.period ? <small>{p.period}</small> : null}
                </div>
                <ul>
                  {p.points.map((x) => (
                    <li key={x}><Check size={14} /> {x}</li>
                  ))}
                </ul>
                <Link to="/register" className={p.featured ? 'hl-btn hl-btn-primary' : 'hl-btn hl-btn-outline'}>
                  {p.cta}
                </Link>
              </article>
            ))}
          </div>
          <div className="hl-help-plan">
            <div>
              <h3>Not sure which plan to choose?</h3>
              <p>Start the free trial on Professional — upgrade or downgrade anytime as your SEO workload grows.</p>
            </div>
            <Link to="/register" className="hl-btn hl-btn-primary">Start free trial</Link>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="hl-section" id="faq">
        <div className="hl-shell hl-faq-wrap">
          <p className="hl-eyebrow">FAQ</p>
          <h2 className="hl-h2">Questions, answered</h2>
          <div className="hl-faq">
            {FAQS.map((item) => (
              <details key={item.q}>
                <summary>{item.q}</summary>
                <p>{item.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="hl-final">
        <div className="hl-shell hl-final-inner">
          <h2>Ready to outrank your competition?</h2>
          <p>Join US teams using ZeOrbit to audit, publish, and climb — in one workspace.</p>
          <Link to="/register" className="hl-btn hl-btn-primary hl-btn-lg">
            Start your 7-day free trial <Rocket size={16} />
          </Link>
        </div>
      </section>

      <MarketingFooter />
    </div>
  )
}
