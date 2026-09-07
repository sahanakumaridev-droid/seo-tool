import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  ExternalLink, Zap, Target, MapPin, Megaphone, Link2,
  Rocket, Copy, ArrowRight, Star, Clock, Phone, Send,
} from 'lucide-react'
import {
  LEAD_PLATFORMS, START_WITH, TRACK_METRICS, SERVICE_FUNNELS,
  GOOGLE_ADS_KEYWORDS, LOCAL_SEO_CITIES, LOCAL_SEO_PAGES,
  LINKEDIN_TARGETS, LINKEDIN_MESSAGE, ENGINE_STACK,
  SALES_FUNNEL, SPEED_RULE,
} from '../data/leadEngine'
import { getLeads, getLeadVisitors, getLeadStats, sendLeadMessage, updateLeadStatus } from '../api'

const TABS = [
  { id: 'inbox', label: 'Inbox' },
  { id: 'platforms', label: 'Lead Platforms' },
  { id: 'engine', label: 'Own Lead Engine' },
  { id: 'funnels', label: 'Service Funnels' },
]

function leadName(lead) {
  return lead.contact_name || lead.name || lead.business_name || 'Untitled'
}

function defaultOutreach(lead) {
  const name = (lead.contact_name || lead.name || 'there').split(' ')[0]
  return {
    subject: 'Quick follow-up from ZeOrbit',
    body: `Hi ${name},\n\nThanks for visiting ZeOrbit. We build websites, apps, and SEO systems that turn traffic into customers.\n\nIf you share what you need (new site, redesign, app, or SEO), we can outline a clear next step and a timeline.\n\nReply to this email or call 619-724-9517.\n\n— ZeOrbit`,
  }
}

function InboxTab() {
  const [leads, setLeads] = useState([])
  const [visitors, setVisitors] = useState([])
  const [stats, setStats] = useState({})
  const [selected, setSelected] = useState(null)
  const [draft, setDraft] = useState({ subject: '', body: '' })
  const [sending, setSending] = useState(false)
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const [l, v, s] = await Promise.all([
        getLeads({ limit: 80 }),
        getLeadVisitors({ limit: 40 }),
        getLeadStats(),
      ])
      setLeads(Array.isArray(l.data) ? l.data : [])
      setVisitors(Array.isArray(v.data) ? v.data : [])
      setStats(s.data || {})
    } catch (e) {
      setMsg(e.response?.data?.detail || 'Could not load inbox')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const pick = (lead) => {
    setSelected(lead)
    setMsg('')
    setDraft(defaultOutreach(lead))
  }

  const send = async () => {
    if (!selected?.id) return
    setSending(true)
    setMsg('')
    try {
      await sendLeadMessage(selected.id, draft)
      setMsg('Message sent. Lead marked as contacted.')
      await updateLeadStatus(selected.id, 'contacted')
      setLeads((prev) => prev.map((l) => (l.id === selected.id ? { ...l, status: 'contacted' } : l)))
      setSelected((cur) => (cur ? { ...cur, status: 'contacted' } : cur))
    } catch (e) {
      setMsg(typeof e.response?.data?.detail === 'string' ? e.response.data.detail : 'Could not send')
    } finally {
      setSending(false)
    }
  }

  const identified = leads.filter((l) => l.email || l.phone)

  return (
    <div className="space-y-4">
      <div className="crm-kpis">
        {[
          { label: 'Contacts', value: identified.length, hint: 'Have email or phone' },
          { label: 'Visitors', value: stats.pageviews || visitors.length, hint: 'Page views — not yet identifiable' },
          { label: 'New', value: stats.by_status?.new || 0, hint: 'Waiting first message' },
          { label: 'Contacted', value: stats.by_status?.contacted || 0, hint: 'Outreach sent' },
        ].map((s) => (
          <div key={s.label} className="crm-kpi">
            <div className="lbl">{s.label}</div>
            <div className="val">{s.value}</div>
            <div className="hint">{s.hint}</div>
          </div>
        ))}
      </div>

      <div className="card p-4" style={{ background: '#fff' }}>
        <p className="text-sm" style={{ color: 'var(--text-2)', margin: 0 }}>
          You cannot legally message a visitor from a pageview alone. Chat and the contact form capture name, email, and U.S. phone so you can email them from this inbox and move them New → Contacted → Qualified → Won.
        </p>
      </div>

      <div className="crm-split">
        <div>
          <h3 className="text-sm font-semibold mb-2" style={{ color: 'var(--text-1)' }}>Captured contacts</h3>
          {loading ? (
            <p className="text-sm" style={{ color: 'var(--text-3)' }}>Loading…</p>
          ) : identified.length === 0 ? (
            <div className="card p-5">
              <p className="text-sm" style={{ color: 'var(--text-3)', margin: 0 }}>
                No contacts yet. On zeorbit.com, visitors use the chat bubble to leave name, email, and phone — then they appear here.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {identified.map((lead) => (
                <button
                  key={lead.id}
                  type="button"
                  className={`crm-card${selected?.id === lead.id ? ' selected' : ''}`}
                  style={{ width: '100%', textAlign: 'left' }}
                  onClick={() => pick(lead)}
                >
                  <div className="crm-card-title">{leadName(lead)}</div>
                  <div className="crm-card-meta">
                    {[lead.email, lead.phone, lead.service].filter(Boolean).join(' · ')}
                  </div>
                  <div className="crm-card-foot">
                    <span className={`crm-chip crm-chip-${lead.status || 'new'}`}>{lead.status || 'new'}</span>
                    <span className="crm-chip crm-chip-source">{lead.source}</span>
                  </div>
                </button>
              ))}
            </div>
          )}

          <h3 className="text-sm font-semibold mt-6 mb-2" style={{ color: 'var(--text-1)' }}>Recent visitors (anonymous)</h3>
          {visitors.length === 0 ? (
            <p className="text-xs" style={{ color: 'var(--text-3)' }}>No pageviews recorded yet.</p>
          ) : (
            <div className="card overflow-hidden">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Page</th>
                    <th>When</th>
                  </tr>
                </thead>
                <tbody>
                  {visitors.slice(0, 15).map((v) => (
                    <tr key={v.id}>
                      <td className="text-xs">{v.website || '/'}</td>
                      <td className="muted-cell">{v.created_at ? new Date(v.created_at).toLocaleString() : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <aside className="crm-drawer">
          {selected ? (
            <>
              <h2>{leadName(selected)}</h2>
              <div className="crm-field"><label>Email</label><div>{selected.email || '—'}</div></div>
              <div className="crm-field"><label>Phone</label><div>{selected.phone || '—'}</div></div>
              <div className="crm-field"><label>Notes</label><div style={{ whiteSpace: 'pre-wrap' }}>{selected.message || '—'}</div></div>
              {selected.email ? (
                <>
                  <div className="crm-field">
                    <label>Subject</label>
                    <input value={draft.subject} onChange={(e) => setDraft((d) => ({ ...d, subject: e.target.value }))}
                      style={{ width: '100%', padding: '8px 10px' }} />
                  </div>
                  <div className="crm-field">
                    <label>Message</label>
                    <textarea rows={8} value={draft.body} onChange={(e) => setDraft((d) => ({ ...d, body: e.target.value }))}
                      style={{ width: '100%', padding: '8px 10px', resize: 'vertical' }} />
                  </div>
                  <button type="button" className="btn btn-primary" onClick={send} disabled={sending} style={{ width: '100%' }}>
                    <Send size={14} /> {sending ? 'Sending…' : 'Send message'}
                  </button>
                </>
              ) : (
                <p className="text-sm" style={{ color: 'var(--text-3)' }}>No email on this record — add one in Contacts or ask them to complete chat capture.</p>
              )}
              {selected.phone ? (
                <a className="btn btn-secondary" style={{ width: '100%', marginTop: 8, justifyContent: 'center' }} href={`tel:${selected.phone}`}>
                  <Phone size={14} /> Call
                </a>
              ) : null}
              {msg ? <p className="text-xs" style={{ marginTop: 10, color: 'var(--text-2)' }}>{msg}</p> : null}
            </>
          ) : (
            <>
              <h2>Message a lead</h2>
              <p style={{ marginTop: 8, fontSize: 13, color: '#6e6e73' }}>
                Select a captured contact. SMTP must be set on the backend for email to send.
              </p>
              <Link to="/leads" className="text-xs" style={{ color: 'var(--brand)' }}>Open full Contacts CRM</Link>
            </>
          )}
        </aside>
      </div>
    </div>
  )
}

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

export default function LeadEnginePage() {
  const [tab, setTab] = useState('inbox')
  const navigate = useNavigate()

  return (
    <div className="space-y-5 fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-1)' }}>Lead Engine</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>
            Capture visitors, message them, and turn conversations into projects.
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/leads" className="btn btn-secondary">Contacts CRM</Link>
          <button type="button" onClick={() => navigate('/instant-quote')} className="btn btn-primary">
            Instant Quote
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-1 p-1 rounded-xl w-fit" style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)' }}>
        {TABS.map(t => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={tab === t.id ? 'tab-active' : 'tab-inactive'}
            style={{ padding: '8px 12px', borderRadius: 8, fontSize: 12, fontWeight: 600, border: 0, cursor: 'pointer' }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'inbox' && <InboxTab />}
      {tab === 'platforms' && <PlatformsTab />}
      {tab === 'engine' && <EngineTab onOpenQuote={() => navigate('/instant-quote')} />}
      {tab === 'funnels' && <FunnelsTab />}
    </div>
  )
}
