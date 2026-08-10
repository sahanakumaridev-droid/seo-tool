import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  ExternalLink, Zap, Target, MapPin, Megaphone, Link2,
  Rocket, CheckCircle2, Copy, ArrowRight, Star, Clock,
} from 'lucide-react'
import {
  LEAD_PLATFORMS, START_WITH, TRACK_METRICS, SERVICE_FUNNELS,
  GOOGLE_ADS_KEYWORDS, LOCAL_SEO_CITIES, LOCAL_SEO_PAGES,
  LINKEDIN_TARGETS, LINKEDIN_MESSAGE, BUDGET_PLAN, ENGINE_STACK,
  SALES_FUNNEL, SPEED_RULE,
} from '../data/leadEngine'

const TABS = [
  { id: 'platforms', label: 'Lead Platforms' },
  { id: 'engine', label: 'Own Lead Engine' },
  { id: 'funnels', label: 'Service Funnels' },
  { id: 'budget', label: 'Budget & Playbook' },
]

function Stars({ n }) {
  return (
    <span className="inline-flex gap-0.5" aria-label={`${n} of 5`}>
      {Array.from({ length: 5 }, (_, i) => (
        <Star key={i} size={11} className={i < n ? 'text-amber-400 fill-amber-400' : 'text-slate-600'} />
      ))}
    </span>
  )
}

function PlatformsTab() {
  const [showAll, setShowAll] = useState(false)
  const rows = useMemo(
    () => [...LEAD_PLATFORMS].sort((a, b) => b.priority - a.priority || a.name.localeCompare(b.name)),
    [],
  )
  const visible = showAll ? rows : rows.filter(p => p.start || p.priority >= 4)

  return (
    <div className="space-y-5">
      <div className="card p-5 border-amber-500/20">
        <div className="flex items-start gap-3">
          <Zap size={18} className="text-amber-400 mt-0.5 shrink-0" />
          <div>
            <h2 className="text-sm font-semibold text-white">Lead platforms playbook (free)</h2>
            <p className="text-sm text-slate-400 mt-1">
              Do not sign up for all at once. Start with <strong className="text-slate-200">{START_WITH.join(' + ')}</strong> for 60–90 days and track CPA — not vanity lead count.
            </p>
            <p className="text-xs text-slate-500 mt-2 flex items-start gap-1.5">
              <Clock size={12} className="mt-0.5 shrink-0" /> {SPEED_RULE}
            </p>
          </div>
        </div>
      </div>

      <div className="card overflow-hidden">
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Platform</th>
                <th>Best for</th>
                <th>Website</th>
                <th>Apps</th>
                <th>Quality</th>
                <th>Take</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {visible.map(p => (
                <tr key={p.name}>
                  <td>
                    <div className="font-semibold text-slate-200">{p.name}</div>
                    {p.start && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
                        Start here
                      </span>
                    )}
                    <div className="text-[11px] text-slate-500 mt-1">{p.costNote}</div>
                  </td>
                  <td className="text-slate-400 text-xs max-w-[180px]">{p.bestFor}</td>
                  <td><Stars n={p.websiteLeads} /></td>
                  <td><Stars n={p.appLeads} /></td>
                  <td className="text-slate-300 text-xs">{p.quality}</td>
                  <td className="text-slate-400 text-xs max-w-[220px]">{p.take}</td>
                  <td>
                    <a href={p.url} target="_blank" rel="noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-indigo-400 hover:underline">
                      Open <ExternalLink size={10} />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 border-t border-white/6">
          <button type="button" onClick={() => setShowAll(v => !v)}
            className="text-xs text-indigo-400 hover:underline">
            {showAll ? 'Show priority platforms only' : `Show all ${LEAD_PLATFORMS.length} platforms`}
          </button>
        </div>
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-semibold text-white mb-3">Track for 60–90 days</h3>
        <div className="flex flex-wrap gap-2">
          {TRACK_METRICS.map(m => (
            <span key={m} className="text-xs px-2.5 py-1 rounded-lg bg-white/4 border border-white/8 text-slate-300">
              {m}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

function EngineTab({ onOpenQuote }) {
  const navigate = useNavigate()
  return (
    <div className="space-y-5">
      <div className="card p-5">
        <h2 className="text-sm font-semibold text-white mb-1">ZeOrbit owned lead engine</h2>
        <p className="text-sm text-slate-400">
          Build two channels at once: marketplace platforms for near-term opportunities, plus Google + landing pages + LinkedIn + local SEO so you own your pipeline long-term.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-3">
        {ENGINE_STACK.map(item => (
          <div key={item.name} className="card p-4 flex items-start gap-3">
            <Target size={16} className="text-indigo-400 mt-0.5 shrink-0" />
            <div>
              <div className="text-sm font-semibold text-slate-200">{item.name}</div>
              <div className="text-xs text-slate-500 mt-0.5">{item.role}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
          <Rocket size={14} className="text-indigo-400" /> Sales funnel
        </h3>
        <div className="flex flex-wrap items-center gap-2">
          {SALES_FUNNEL.map((step, i) => (
            <div key={step} className="flex items-center gap-2">
              <span className="text-xs px-2.5 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 font-medium">
                {step}
              </span>
              {i < SALES_FUNNEL.length - 1 && <ArrowRight size={12} className="text-slate-600" />}
            </div>
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-3">
        <div className="card p-5 space-y-3">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Megaphone size={14} className="text-sky-400" /> Google Ads → landing page
          </h3>
          <p className="text-xs text-slate-400">
            Never send high-intent search to the homepage. Match the ad to a dedicated service page.
          </p>
          <ul className="space-y-1.5">
            {GOOGLE_ADS_KEYWORDS.map(kw => (
              <li key={kw} className="text-xs text-slate-300 flex items-center gap-2">
                <span className="w-1 h-1 rounded-full bg-sky-400" /> {kw}
              </li>
            ))}
          </ul>
          <button type="button" onClick={() => navigate('/google-ads')}
            className="text-xs text-indigo-400 hover:underline inline-flex items-center gap-1">
            Open Google Ads module <ArrowRight size={11} />
          </button>
        </div>

        <div className="card p-5 space-y-3">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Link2 size={14} className="text-blue-400" /> LinkedIn outreach
          </h3>
          <p className="text-xs text-slate-400">Prioritize prospecting over LinkedIn ads. Target:</p>
          <div className="flex flex-wrap gap-1.5">
            {LINKEDIN_TARGETS.map(t => (
              <span key={t} className="text-[11px] px-2 py-0.5 rounded bg-white/4 border border-white/8 text-slate-400">{t}</span>
            ))}
          </div>
          <div className="rounded-lg bg-white/3 border border-white/8 p-3 text-xs text-slate-300 italic">
            “{LINKEDIN_MESSAGE}”
          </div>
          <button type="button" onClick={() => navigator.clipboard?.writeText(LINKEDIN_MESSAGE)}
            className="text-xs text-indigo-400 hover:underline inline-flex items-center gap-1">
            <Copy size={11} /> Copy message
          </button>
        </div>
      </div>

      <div className="card p-5 space-y-3">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <MapPin size={14} className="text-emerald-400" /> Local SEO (cheapest long-term)
        </h3>
        <p className="text-xs text-slate-400">
          Build real local pages — not thin city stubs. Each needs content, examples, testimonials, and projects.
        </p>
        <div className="flex flex-wrap gap-2 mb-2">
          {LOCAL_SEO_PAGES.map(p => (
            <span key={p} className="text-xs px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">{p}</span>
          ))}
        </div>
        <div className="flex flex-wrap gap-1.5">
          {LOCAL_SEO_CITIES.map(c => (
            <span key={c} className="text-[11px] px-2 py-0.5 rounded bg-white/4 border border-white/8 text-slate-400">{c}</span>
          ))}
        </div>
        <button type="button" onClick={() => navigate('/content')}
          className="text-xs text-indigo-400 hover:underline inline-flex items-center gap-1">
          Generate city SEO pages in Content <ArrowRight size={11} />
        </button>
      </div>

      <div className="card p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-indigo-500/20">
        <div>
          <h3 className="text-sm font-semibold text-white">Instant Quote funnel</h3>
          <p className="text-xs text-slate-400 mt-1">
            Service → budget → timeline → contact. Captures intent before the sales call.
          </p>
        </div>
        <div className="flex gap-2">
          <button type="button" onClick={onOpenQuote}
            className="btn-primary px-4 py-2 rounded-lg text-sm font-semibold text-white">
            Preview funnel
          </button>
          <Link to="/instant-quote"
            className="px-4 py-2 rounded-lg text-sm border border-white/10 text-slate-300 hover:bg-white/4">
            Public link
          </Link>
        </div>
      </div>
    </div>
  )
}

function FunnelsTab() {
  const navigate = useNavigate()
  const [copied, setCopied] = useState('')

  const copySlug = async (slug) => {
    try {
      await navigator.clipboard.writeText(slug)
      setCopied(slug)
      setTimeout(() => setCopied(''), 1500)
    } catch { /* ignore */ }
  }

  const openInContent = (funnel) => {
    try {
      localStorage.setItem('seo_lead_funnel', JSON.stringify({
        business_type: funnel.businessType,
        keywords: funnel.keywords,
        headline: funnel.headline,
        slug: funnel.slug,
      }))
    } catch { /* ignore */ }
    navigate('/content')
  }

  return (
    <div className="space-y-5">
      <div className="card p-5">
        <h2 className="text-sm font-semibold text-white mb-1">Separate lead funnels (not one generic page)</h2>
        <p className="text-sm text-slate-400">
          Do not advertise only as “Web Design & Mobile App Development.” Match exact search intent with dedicated landing pages.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-3">
        {SERVICE_FUNNELS.map(f => (
          <div key={f.id} className="card p-4 space-y-3">
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="text-xs text-indigo-400 font-medium">{f.label}</div>
                <h3 className="text-sm font-semibold text-white mt-1">{f.headline}</h3>
              </div>
              <button type="button" onClick={() => copySlug(f.slug)}
                className="text-[11px] text-slate-500 hover:text-slate-300 shrink-0 inline-flex items-center gap-1">
                <Copy size={10} /> {copied === f.slug ? 'Copied' : f.slug}
              </button>
            </div>
            <div className="flex flex-wrap gap-1">
              {f.keywords.map(kw => (
                <span key={kw} className="text-[10px] px-1.5 py-0.5 rounded bg-white/4 text-slate-500">{kw}</span>
              ))}
            </div>
            <div className="flex items-center justify-between gap-2 pt-1">
              <span className="text-xs text-emerald-400/90">{f.cta}</span>
              <button type="button" onClick={() => openInContent(f)}
                className="text-xs px-3 py-1.5 rounded-lg bg-indigo-600/20 border border-indigo-600/30 text-indigo-300 hover:bg-indigo-600/30">
                Generate in SEO Content
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function BudgetTab() {
  const total = BUDGET_PLAN.reduce((s, b) => s + b.amount, 0)
  return (
    <div className="space-y-5">
      <div className="card p-5">
        <h2 className="text-sm font-semibold text-white mb-1">~$3,000 / month test budget</h2>
        <p className="text-sm text-slate-400">
          After 60 days, kill the most expensive channel (by cost per acquired customer) and move budget to the winner.
          Measure CPA, not lead volume — 8 leads that close 3 × $5k projects beat 50 cheap tire-kickers.
        </p>
      </div>

      <div className="card overflow-hidden">
        <table className="data-table">
          <thead>
            <tr>
              <th>Channel</th>
              <th>Share</th>
              <th>Amount</th>
              <th>Note</th>
            </tr>
          </thead>
          <tbody>
            {BUDGET_PLAN.map(b => (
              <tr key={b.channel}>
                <td className="font-semibold text-slate-200">{b.channel}</td>
                <td className="text-slate-400 text-xs">{b.pct}%</td>
                <td className="text-emerald-400 text-sm font-medium">${b.amount.toLocaleString()}</td>
                <td className="text-slate-500 text-xs">{b.note}</td>
              </tr>
            ))}
            <tr>
              <td className="font-semibold text-white">Total</td>
              <td />
              <td className="text-white font-semibold">${total.toLocaleString()}</td>
              <td className="text-slate-500 text-xs">Adjust after 60-day review</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="card p-5 space-y-2">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <CheckCircle2 size={14} className="text-emerald-400" /> North star
        </h3>
        <p className="text-sm text-slate-400">
          Build toward <strong className="text-slate-200">Google + local SEO + direct outreach</strong> as the core engine,
          with marketplaces as supplemental — not the business model.
        </p>
      </div>
    </div>
  )
}

export default function LeadEnginePage() {
  const [tab, setTab] = useState('platforms')
  const navigate = useNavigate()

  return (
    <div className="space-y-6 fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white">Lead Engine</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Free ZeOrbit playbook — marketplace platforms + owned funnels for web design & app development
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/leads"
            className="px-3 py-2 rounded-lg text-xs border border-white/10 text-slate-300 hover:bg-white/4">
            Open Leads CRM
          </Link>
          <button type="button" onClick={() => navigate('/instant-quote')}
            className="btn-primary px-4 py-2 rounded-lg text-sm font-semibold text-white">
            Instant Quote
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-1 p-1 rounded-xl bg-white/3 border border-white/8 w-fit">
        {TABS.map(t => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              tab === t.id
                ? 'bg-indigo-600/30 text-indigo-200 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 border border-transparent'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'platforms' && <PlatformsTab />}
      {tab === 'engine' && <EngineTab onOpenQuote={() => navigate('/instant-quote')} />}
      {tab === 'funnels' && <FunnelsTab />}
      {tab === 'budget' && <BudgetTab />}
    </div>
  )
}
