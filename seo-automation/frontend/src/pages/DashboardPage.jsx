import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import {
  FileText, CheckCircle2, FileEdit, TrendingUp, Search as SearchIcon,
  Sparkles, Image as ImageIcon, Zap, ArrowRight, Clock, Plus,
} from 'lucide-react'
import { TRAFFIC_TREND } from '../data/mockData'
import { listPages } from '../api'

/* ── Small building blocks ─────────────────────────────────── */
const TONES = {
  blue:   { fg: 'var(--brand)',  bg: 'var(--brand-soft)' },
  green:  { fg: 'var(--green)',  bg: 'var(--green-soft)' },
  amber:  { fg: 'var(--amber)',  bg: 'var(--amber-soft)' },
  violet: { fg: '#2563EB',       bg: '#F5F0FF' },
  slate:  { fg: 'var(--text-2)', bg: 'var(--bg-raised)' },
}

function StatCard({ icon: Icon, label, value, delta, deltaUp = true, tone = 'blue' }) {
  const t = TONES[tone]
  return (
    <div className="card card-hover p-5">
      <div className="flex items-start justify-between">
        <div style={{ width: 42, height: 42, borderRadius: 12, background: t.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon size={20} style={{ color: t.fg }} />
        </div>
        {delta && (
          <span className="text-xs font-semibold px-2 py-1 rounded-full"
            style={{ color: deltaUp ? 'var(--green)' : 'var(--red)', background: deltaUp ? 'var(--green-soft)' : 'var(--red-soft)' }}>
            {delta}
          </span>
        )}
      </div>
      <div className="mt-4">
        <div className="font-display" style={{ fontSize: 30, fontWeight: 800, color: 'var(--text-1)', lineHeight: 1.1 }}>{value}</div>
        <div className="text-sm mt-1" style={{ color: 'var(--text-3)' }}>{label}</div>
      </div>
    </div>
  )
}

function SectionHead({ title, sub, action }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div>
        <h2 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-1)' }}>{title}</h2>
        {sub && <p className="text-xs mt-0.5" style={{ color: 'var(--text-3)' }}>{sub}</p>}
      </div>
      {action}
    </div>
  )
}

// Big primary entry card (SEO Pages / Blog Creation)
function EntryCard({ icon: Icon, title, desc, cta, tint, tint2, onClick }) {
  const [hov, setHov] = useState(false)
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      className="card"
      style={{
        textAlign: 'left', cursor: 'pointer', padding: 24,
        display: 'flex', flexDirection: 'column', gap: 14,
        borderColor: hov ? tint : 'var(--border)',
        boxShadow: hov ? `0 16px 40px rgba(0,0,0,0.5), 0 0 0 1px ${tint}` : 'var(--shadow-sm)',
        transform: hov ? 'translateY(-3px)' : 'none',
        transition: 'transform .18s, box-shadow .18s, border-color .18s',
        position: 'relative', overflow: 'hidden',
      }}
    >
      {/* glow */}
      <div style={{ position: 'absolute', top: -40, right: -40, width: 160, height: 160, borderRadius: '50%',
        background: `radial-gradient(circle, ${tint}22 0%, transparent 70%)`, pointerEvents: 'none' }} />
      <div style={{ width: 46, height: 46, borderRadius: 12, background: `linear-gradient(135deg, ${tint}, ${tint2})`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: `0 6px 18px ${tint}55` }}>
        <Icon size={22} color="#fff" />
      </div>
      <div>
        <div className="font-display" style={{ fontSize: 19, fontWeight: 800, color: 'var(--text-1)' }}>{title}</div>
        <p style={{ fontSize: 13, color: 'var(--text-3)', marginTop: 5, lineHeight: 1.55, maxWidth: 360 }}>{desc}</p>
      </div>
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7, marginTop: 2,
        fontSize: 13.5, fontWeight: 700, color: tint }}>
        {cta} <ArrowRight size={16} style={{ transform: hov ? 'translateX(3px)' : 'none', transition: 'transform .18s' }} />
      </span>
    </button>
  )
}

const ChartTip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="card px-3 py-2 text-xs" style={{ boxShadow: 'var(--shadow-md)' }}>
      <div style={{ color: 'var(--text-3)', marginBottom: 4 }}>{label}</div>
      {payload.map(p => (
        <div key={p.name} className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span style={{ color: 'var(--text-2)' }}>{p.name}:</span>
          <span style={{ color: 'var(--text-1)', fontWeight: 700 }}>{p.value?.toLocaleString?.() ?? p.value}</span>
        </div>
      ))}
    </div>
  )
}

const STATUS_STYLE = {
  published: { color: 'var(--green)', bg: 'var(--green-soft)', label: 'Published' },
  draft:     { color: 'var(--amber)', bg: 'var(--amber-soft)', label: 'Draft' },
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const [pages, setPages] = useState([])

  useEffect(() => {
    listPages(0, 100).then(r => setPages(r.data || [])).catch(() => setPages([]))
  }, [])

  const total = pages.length
  const published = pages.filter(p => p.seo_block?.wp_post_url).length
  const drafts = Math.max(total - published, 0)
  const recent = pages.slice(0, 6)

  const STATS = [
    { icon: FileText,     label: 'Total Blogs',      value: total || '—',  delta: total ? `+${total}` : '', tone: 'blue' },
    { icon: CheckCircle2, label: 'Published',        value: published,     delta: '', tone: 'green' },
    { icon: FileEdit,     label: 'Drafts',           value: drafts,        delta: '', tone: 'amber' },
    { icon: TrendingUp,   label: 'Organic Traffic',  value: '11.2K',       delta: '+18%', tone: 'violet' },
    { icon: SearchIcon,   label: 'Keywords',         value: '48',          delta: '+6', tone: 'blue' },
    { icon: Sparkles,     label: 'AI Credits',       value: '2,450',       delta: '', tone: 'green' },
    { icon: ImageIcon,    label: 'Images Generated', value: total * 3 || 0, delta: '', tone: 'violet' },
  ]

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display" style={{ fontSize: 26, fontWeight: 800, color: 'var(--text-1)' }}>Dashboard</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-3)' }}>Welcome back — here's what's happening with your content.</p>
        </div>
        <button onClick={() => navigate('/articles')}
          className="btn-primary flex items-center gap-2 rounded-xl"
          style={{ padding: '11px 18px', fontSize: 14 }}>
          <Plus size={16} /> Generate Content
        </button>
      </div>

      {/* ── Two main entry points ── */}
      <div className="dash-entry" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
        <EntryCard
          icon={Zap}
          title="SEO Pages"
          desc="Generate SGE/ChatGPT-optimized SEO pages for every U.S. city — at scale."
          cta="Create SEO Pages"
          tint="#3B82F6" tint2="#2563EB"
          onClick={() => navigate('/content')}
        />
        <EntryCard
          icon={FileText}
          title="Blog Creation"
          desc="Turn one keyword into unique, internally-linked blog articles per city."
          cta="Create a Blog"
          tint="#34D399" tint2="#059669"
          onClick={() => navigate('/articles')}
        />
      </div>

      {/* KPI grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
        {STATS.slice(0, 4).map(s => <StatCard key={s.label} {...s} />)}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
        {STATS.slice(4).map(s => <StatCard key={s.label} {...s} />)}
      </div>

      {/* Charts + activity */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }} className="dash-charts">
        <div className="card p-5">
          <SectionHead title="Organic Traffic" sub="Sessions over the last 8 months"
            action={<span className="text-xs font-semibold" style={{ color: 'var(--green)' }}>▲ 18% vs last period</span>} />
          <ResponsiveContainer width="100%" height={230}>
            <AreaChart data={TRAFFIC_TREND} margin={{ top: 4, right: 8, left: -18, bottom: 0 }}>
              <defs>
                <linearGradient id="og" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#2563EB" stopOpacity={0.22} />
                  <stop offset="100%" stopColor="#2563EB" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#EEF1F5" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTip />} />
              <Area type="monotone" dataKey="organic" name="Organic" stroke="#2563EB" strokeWidth={2.5} fill="url(#og)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-5">
          <SectionHead title="Recent Activity" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {[
              { icon: CheckCircle2, tone: 'green',  text: 'Blog published to WordPress', time: '2m ago' },
              { icon: ImageIcon,    tone: 'violet', text: '3 AI images generated', time: '4m ago' },
              { icon: Sparkles,     tone: 'blue',   text: 'SEO optimization complete', time: '6m ago' },
              { icon: FileText,     tone: 'amber',  text: 'New draft saved', time: '1h ago' },
              { icon: TrendingUp,   tone: 'green',  text: 'Keyword moved to #3', time: '3h ago' },
            ].map((a, i) => {
              const t = TONES[a.tone]
              return (
                <div key={i} className="flex items-center gap-3">
                  <div style={{ width: 34, height: 34, borderRadius: 9, background: t.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <a.icon size={16} style={{ color: t.fg }} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="text-sm" style={{ color: 'var(--text-1)' }}>{a.text}</div>
                    <div className="flex items-center gap-1 text-xs mt-0.5" style={{ color: 'var(--text-4)' }}>
                      <Clock size={10} /> {a.time}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Recent blogs */}
      <div className="card">
        <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: '1px solid var(--border)' }}>
          <SectionHead title="Recent Blogs" sub={total ? `${total} total` : 'Generate your first blog to see it here'} />
          <button onClick={() => navigate('/articles')} className="text-xs font-semibold flex items-center gap-1" style={{ color: 'var(--brand)' }}>
            View all <ArrowRight size={13} />
          </button>
        </div>
        {recent.length === 0 ? (
          <div className="flex flex-col items-center justify-center text-center" style={{ padding: '48px 20px' }}>
            <div style={{ width: 52, height: 52, borderRadius: 14, background: 'var(--brand-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Zap size={24} style={{ color: 'var(--brand)' }} />
            </div>
            <p className="text-sm mt-3" style={{ color: 'var(--text-2)', fontWeight: 600 }}>No blogs yet</p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-4)' }}>Click “Generate Content” to create your first SEO blog.</p>
          </div>
        ) : (
          <table className="data-table">
            <thead><tr><th>Title</th><th>Location</th><th>SEO Score</th><th>Status</th></tr></thead>
            <tbody>
              {recent.map((p, i) => {
                const b = p.seo_block || {}
                const score = Math.round(b.readability_score || 78)
                const st = b.wp_post_url ? STATUS_STYLE.published : STATUS_STYLE.draft
                return (
                  <tr key={i} style={{ cursor: 'pointer' }}
                    onClick={() => navigate('/page-preview', { state: { block: b, businessType: b.business_type, wpConfig: {} } })}>
                    <td style={{ maxWidth: 320 }}>
                      <div style={{ color: 'var(--text-1)', fontWeight: 600 }} className="truncate">{b.title || p.slug}</div>
                      <div className="text-xs truncate" style={{ color: 'var(--text-4)' }}>/{p.slug}</div>
                    </td>
                    <td>{b.city}{b.state ? `, ${b.state}` : ''}</td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div style={{ width: 60, height: 6, borderRadius: 4, background: 'var(--bg-raised)', overflow: 'hidden' }}>
                          <div style={{ height: '100%', width: `${score}%`, background: score >= 75 ? 'var(--green)' : score >= 50 ? 'var(--amber)' : 'var(--red)' }} />
                        </div>
                        <span className="text-xs font-bold" style={{ color: score >= 75 ? 'var(--green)' : 'var(--amber)' }}>{score}</span>
                      </div>
                    </td>
                    <td><span className="text-xs font-semibold px-2.5 py-1 rounded-full" style={{ color: st.color, background: st.bg }}>{st.label}</span></td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
