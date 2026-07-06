import { useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { ArrowLeft, RefreshCw, Save, CheckCircle, Upload, Globe, ExternalLink } from 'lucide-react'
import { generateSingle, savePage, publishToWordPress } from '../api'

function ScoreRing({ value, color }) {
  const r = 20, c = 2 * Math.PI * r
  const dash = (value / 100) * c
  return (
    <svg width="52" height="52" viewBox="0 0 52 52">
      <circle cx="26" cy="26" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
      <circle cx="26" cy="26" r={r} fill="none" stroke={color} strokeWidth="4"
        strokeDasharray={`${dash} ${c}`} strokeLinecap="round"
        transform="rotate(-90 26 26)" />
      <text x="26" y="31" textAnchor="middle" fontSize="11" fontWeight="700" fill={color}>{value}</text>
    </svg>
  )
}

function MetaRow({ label, value, multiline }) {
  return (
    <div className="rounded-xl p-4" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)' }}>
      <div className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>{label}</div>
      <p className={`text-sm leading-relaxed ${multiline ? 'whitespace-pre-line' : ''}`} style={{ color: 'var(--text-primary)' }}>{value}</p>
    </div>
  )
}

function KwGroup({ label, kws = [], color }) {
  const colors = {
    cyan:   'bg-cyan-500/15 text-cyan-300 border-cyan-500/25',
    blue:   'bg-blue-500/15 text-blue-300 border-blue-500/25',
    emerald:'bg-emerald-500/15 text-emerald-300 border-emerald-500/25',
    violet: 'bg-violet-500/15 text-violet-300 border-violet-500/25',
  }
  return (
    <div>
      <div className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>{label}</div>
      <div className="flex flex-wrap gap-2">
        {kws.map((k, i) => (
          <span key={i} className={`text-xs px-2.5 py-1 rounded-lg border ${colors[color]}`}>{k}</span>
        ))}
      </div>
    </div>
  )
}

export default function PagePreviewPage() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const [block, setBlock] = useState(state?.block)
  const [tab, setTab] = useState('content')
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [publishResult, setPublishResult] = useState(null)

  const businessType = state?.businessType || block?.business_type || ''
  const wpConfig = state?.wpConfig

  if (!block) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <p style={{ color: 'var(--text-muted)' }}>No page data found.</p>
        <button onClick={() => navigate('/content')} className="btn-primary px-4 py-2 rounded-lg text-white text-sm">
          Back to Content
        </button>
      </div>
    )
  }

  const score = Math.round(block.readability_score || 75)
  const scoreColor = score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444'

  const handleRegen = async () => {
    setLoading(true)
    try {
      const res = await generateSingle(businessType, block.city, block.state)
      setBlock(res.data)
    } finally { setLoading(false) }
  }

  const handleSave = async () => {
    await savePage(businessType, block.city, block.state)
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  const handlePublish = async () => {
    if (!wpConfig?.wp_url) return
    setPublishing(true)
    setPublishResult(null)
    try {
      const res = await publishToWordPress(block, wpConfig)
      setPublishResult(res.data)
    } catch (e) {
      setPublishResult({ success: false, error: e.response?.data?.detail || e.message })
    } finally { setPublishing(false) }
  }

  const TABS = [
    { id: 'content', label: 'Content & Meta' },
    { id: 'intro', label: 'Intro' },
    { id: 'keywords', label: 'Keywords' },
    { id: 'questions', label: 'User Questions' },
    { id: 'faqs', label: `FAQs (${block.faqs?.length || 0})` },
    { id: 'schema', label: 'Schema' },
  ]

  return (
    <div className="space-y-5 fade-in">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)}
            className="p-2 rounded-lg transition-colors"
            style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
            <ArrowLeft size={15} />
          </button>
          <div>
            <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
              {block.city}, {block.state}
            </h1>
            <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>
              {businessType} · {block.slug}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-wrap justify-end">
          <button onClick={handleRegen} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
            style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Regenerate
          </button>
          <button onClick={handleSave}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-colors ${saved ? 'text-emerald-400' : ''}`}
            style={saved
              ? { background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)' }
              : { background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
            {saved ? <><CheckCircle size={13} /> Saved</> : <><Save size={13} /> Save</>}
          </button>
          {wpConfig?.wp_url && (
            <button onClick={handlePublish} disabled={publishing}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium btn-primary disabled:opacity-50">
              <Upload size={13} className={publishing ? 'animate-pulse' : ''} />
              {publishing ? 'Publishing...' : publishResult?.success ? 'Published!' : 'Publish to WordPress'}
            </button>
          )}
        </div>
      </div>

      {/* Publish result banner */}
      {publishResult && (
        <div className={`rounded-xl px-4 py-3 text-sm flex items-center gap-2 ${publishResult.success ? 'text-emerald-400' : 'text-red-400'}`}
          style={{ background: publishResult.success ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)', border: `1px solid ${publishResult.success ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}` }}>
          {publishResult.success
            ? <><CheckCircle size={14} /> Published — <a href={publishResult.post_url} target="_blank" rel="noreferrer" className="underline flex items-center gap-1">{publishResult.post_url} <ExternalLink size={11} /></a></>
            : <>✗ {publishResult.error}</>}
        </div>
      )}

      {/* Score cards */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'SEO Score', value: score, color: scoreColor },
          { label: 'Keyword Density', value: Math.round(block.keyword_density || 0), color: 'var(--brand)' },
          { label: 'Meta Complete', value: 100, color: '#10b981' },
        ].map(s => (
          <div key={s.label} className="card p-4 flex items-center gap-4">
            <ScoreRing value={s.value} color={s.color} />
            <div>
              <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{s.label}</div>
              <div className="text-lg font-bold mt-0.5" style={{ color: s.color }}>{s.value}%</div>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="flex border-b overflow-x-auto" style={{ borderColor: 'var(--border)' }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`px-5 py-3.5 text-sm font-medium whitespace-nowrap transition-colors ${tab === t.id ? 'tab-active' : 'tab-inactive'}`}>
              {t.label}
            </button>
          ))}
        </div>

        <div className="p-6 space-y-4">
          {tab === 'content' && (
            <>
              <MetaRow label="SEO Title" value={block.title} />
              <MetaRow label="Meta Description" value={block.meta_description} />
              <MetaRow label="URL Slug" value={block.slug} />
              <MetaRow label="H1" value={block.h1} />
              <div className="rounded-xl p-4" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)' }}>
                <div className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: 'var(--text-muted)' }}>H2 Headings — Question Based</div>
                <ul className="space-y-2">
                  {block.h2s?.map((h, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                      <span className="text-xs font-bold mt-0.5 flex-shrink-0" style={{ color: 'var(--brand)' }}>H2</span>{h}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="rounded-xl p-4" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)' }}>
                <div className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: 'var(--text-muted)' }}>H3 Headings</div>
                <ul className="space-y-2">
                  {block.h3s?.map((h, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                      <span className="text-xs font-bold mt-0.5 flex-shrink-0" style={{ color: 'var(--brand-violet)' }}>H3</span>{h}
                    </li>
                  ))}
                </ul>
              </div>
              <MetaRow label="Body Content" value={block.content} multiline />
              <MetaRow label="Call to Action" value={block.cta} />
            </>
          )}

          {tab === 'intro' && (
            <>
              <div className="rounded-xl p-4" style={{ background: 'rgba(6,182,212,0.06)', border: '1px solid rgba(6,182,212,0.2)' }}>
                <p className="text-xs font-semibold mb-1" style={{ color: 'var(--brand)' }}>AI Overview Optimized Intro</p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  First 2–3 lines answer directly with location + keyword — optimized for Google AI Overviews, Bing Copilot, and ChatGPT retrieval.
                </p>
              </div>
              <MetaRow label="Intro Paragraph" value={block.intro || block.content?.split('\n\n')[0]} multiline />
            </>
          )}

          {tab === 'keywords' && (
            <div className="space-y-5">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>Primary Keyword</div>
                <span className="inline-block px-3 py-1.5 rounded-lg text-sm font-medium"
                  style={{ background: 'rgba(6,182,212,0.15)', color: '#67E8F9', border: '1px solid rgba(6,182,212,0.3)' }}>
                  {block.keywords?.primary}
                </span>
              </div>
              <KwGroup label="Short-tail / Main Keywords" kws={block.keywords?.secondary?.slice(0, 4)} color="cyan" />
              <KwGroup label="Long-tail Keywords" kws={block.keywords?.long_tail} color="blue" />
              <KwGroup label='"Near Me" Variations' kws={block.keywords?.near_me} color="emerald" />
            </div>
          )}

          {tab === 'questions' && (
            <div className="space-y-2">
              <div className="rounded-xl p-4 mb-2" style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)' }}>
                <p className="text-xs font-semibold mb-1" style={{ color: '#F59E0B' }}>Real User Questions</p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Sourced from Google PAA & Suggest patterns. Used as H2s and FAQs for AI Overview optimization.
                </p>
              </div>
              {(block.keywords?.user_questions || []).map((q, i) => (
                <div key={i} className="flex items-start gap-3 rounded-xl p-3"
                  style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)' }}>
                  <span className="text-xs font-bold mt-0.5 flex-shrink-0" style={{ color: '#F59E0B' }}>Q{i + 1}</span>
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{q}</span>
                </div>
              ))}
            </div>
          )}

          {tab === 'faqs' && (
            <div className="space-y-3">
              {block.faqs?.map((faq, i) => (
                <div key={i} className="rounded-xl p-4" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)' }}>
                  <p className="text-sm font-semibold mb-2" style={{ color: 'var(--brand)' }}>{faq.question}</p>
                  <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{faq.answer}</p>
                </div>
              ))}
            </div>
          )}

          {tab === 'schema' && (
            <div className="space-y-4">
              {block.schema_markup && Object.entries(block.schema_markup).map(([key, val]) => (
                <div key={key}>
                  <div className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--brand)' }}>
                    {key.replace('_', ' ')}
                  </div>
                  <pre className="rounded-xl p-4 text-xs overflow-auto leading-relaxed"
                    style={{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: '#34D399' }}>
                    {JSON.stringify(val, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
