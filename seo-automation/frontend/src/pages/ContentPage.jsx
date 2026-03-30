import { useState } from 'react'
import { Zap, MapPin, Globe, Eye, X, RefreshCw, Save, CheckCircle, FileJson, Tag, Plus } from 'lucide-react'
import { generateBulk, exportJson, exportWordpress, generateSingle, savePage } from '../api'

const BUSINESS_TYPES = ['Plumbing', 'HVAC', 'Roofing', 'Landscaping', 'Cleaning', 'Electrical', 'Painting', 'SEO Agency', 'Pest Control', 'Moving']
const SD_CITIES_PREVIEW = ['San Diego','La Jolla','Chula Vista','El Cajon','Escondido','Oceanside','Carlsbad','Vista','San Marcos','Santee','Poway','La Mesa','National City','Coronado','Encinitas']
const KW_SUGGESTIONS = ['emergency plumber san diego', 'drain cleaning near me', 'licensed plumber ca', 'same day plumbing service', 'water heater repair', 'pipe leak repair']

// ── Preview Modal ──────────────────────────────────────────────
function PreviewModal({ block, businessType, targetKeywords = [], onClose, onRegenerate }) {
  const [tab, setTab] = useState('content')
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)

  const handleRegen = async () => {
    setLoading(true)
    try {
      const res = await generateSingle(businessType, block.city, block.state)
      onRegenerate(res.data)
    } finally { setLoading(false) }
  }

  const handleSave = async () => {
    await savePage(businessType, block.city, block.state)
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
      <div className="relative w-full max-w-3xl max-h-[90vh] flex flex-col card rounded-2xl shadow-2xl overflow-hidden"
        onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/6 flex-shrink-0">
          <div>
            <h2 className="font-bold text-white text-base">{block.city}, {block.state}</h2>
            <p className="text-xs text-slate-500 mt-0.5">{businessType} · SEO Page Preview</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handleRegen} disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/8 text-slate-300 text-xs hover:bg-white/8 transition-colors disabled:opacity-50">
              <RefreshCw size={11} className={loading ? 'animate-spin' : ''} /> Regenerate
            </button>
            <button onClick={handleSave}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-colors ${saved ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-white/5 border border-white/8 text-slate-300 hover:bg-white/8'}`}>
              {saved ? <><CheckCircle size={11} /> Saved</> : <><Save size={11} /> Save</>}
            </button>
            <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-white/8 text-slate-400 hover:text-white transition-colors">
              <X size={16} />
            </button>
          </div>
        </div>
        <div className="flex border-b border-white/6 px-6 flex-shrink-0">
          {['content', 'keywords', 'faqs', 'schema'].map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-4 py-3 text-sm font-medium capitalize transition-colors ${tab === t ? 'tab-active' : 'tab-inactive'}`}>
              {t === 'content' ? 'Content & Meta' : t === 'keywords' ? 'Keywords' : t === 'faqs' ? 'FAQs' : 'Schema'}
            </button>
          ))}
        </div>
        <div className="overflow-y-auto flex-1 p-6 space-y-4">
          {tab === 'content' && (
            <>
              <MetaRow label="SEO Title" value={block.title} />
              <MetaRow label="Meta Description" value={block.meta_description} />
              <MetaRow label="H1" value={block.h1} />
              <div className="rounded-lg bg-white/3 border border-white/6 p-4">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">H2 Headings</div>
                <ul className="space-y-2">
                  {block.h2s.map((h, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                      <span className="text-indigo-400 text-xs font-bold mt-0.5 flex-shrink-0">H2</span>{h}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="rounded-lg bg-white/3 border border-white/6 p-4">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">H3 Headings</div>
                <ul className="space-y-2">
                  {block.h3s.map((h, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                      <span className="text-violet-400 text-xs font-bold mt-0.5 flex-shrink-0">H3</span>{h}
                    </li>
                  ))}
                </ul>
              </div>
              <MetaRow label="Body Content" value={block.content} multiline />
              <MetaRow label="Call to Action" value={block.cta} />
              <div className="grid grid-cols-3 gap-4">
                <ScoreBar label="Readability" value={Math.round(block.readability_score || 75)} color="#6366f1" />
                <ScoreBar label="Keyword Density" value={Math.min(100, Math.round((block.keyword_density || 1.5) * 20))} color="#8b5cf6" />
                <ScoreBar label="Meta Complete" value={100} color="#10b981" />
              </div>
            </>
          )}
          {tab === 'keywords' && (
            <>
              {targetKeywords.length > 0 && (
                <div className="rounded-lg bg-indigo-500/8 border border-indigo-500/20 p-4">
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Your Target Keywords</div>
                  <div className="flex flex-wrap gap-2">
                    {targetKeywords.map((k, i) => (
                      <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-indigo-500/20 text-indigo-200 border border-indigo-500/30 font-medium">{k}</span>
                    ))}
                  </div>
                </div>
              )}
              <div>
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Primary Keyword</div>
                <span className="inline-block px-3 py-1.5 rounded-lg bg-indigo-500/20 text-indigo-200 border border-indigo-500/30 text-sm font-medium">
                  {block.keywords.primary}
                </span>
              </div>
              <KwGroup label="Secondary Keywords" kws={block.keywords.secondary} color="violet" />
              <KwGroup label="Long-tail Keywords" kws={block.keywords.long_tail} color="sky" />
              <KwGroup label='"Near Me" Variations' kws={block.keywords.near_me} color="emerald" />
            </>
          )}
          {tab === 'faqs' && (
            <div className="space-y-3">
              {block.faqs.map((faq, i) => (
                <div key={i} className="rounded-xl bg-white/3 border border-white/6 p-4">
                  <p className="text-sm font-semibold text-indigo-300 mb-2">{faq.question}</p>
                  <p className="text-sm text-slate-400 leading-relaxed">{faq.answer}</p>
                </div>
              ))}
            </div>
          )}
          {tab === 'schema' && (
            <div>
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">JSON-LD Schema Markup</div>
              <pre className="rounded-xl p-4 text-xs text-emerald-400 overflow-auto border leading-relaxed"
                style={{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }}>
                {JSON.stringify(block.schema_markup, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function MetaRow({ label, value, multiline }) {
  return (
    <div className="rounded-lg bg-white/3 border border-white/6 p-4">
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{label}</div>
      <p className={`text-sm text-slate-200 leading-relaxed ${multiline ? 'whitespace-pre-line' : ''}`}>{value}</p>
    </div>
  )
}

function KwGroup({ label, kws, color }) {
  const colors = {
    violet: 'bg-violet-500/15 text-violet-300 border-violet-500/25',
    sky: 'bg-sky-500/15 text-sky-300 border-sky-500/25',
    emerald: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/25',
  }
  return (
    <div>
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{label}</div>
      <div className="flex flex-wrap gap-2">
        {kws.map((k, i) => (
          <span key={i} className={`text-xs px-2.5 py-1 rounded-lg border ${colors[color]}`}>{k}</span>
        ))}
      </div>
    </div>
  )
}

function ScoreBar({ label, value, color }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1.5">
        <span className="text-slate-500">{label}</span>
        <span className="text-slate-300 font-semibold">{value}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-white/6 overflow-hidden">
        <div className="h-full rounded-full" style={{ width: `${value}%`, background: color }} />
      </div>
    </div>
  )
}

// ── Main Page ──────────────────────────────────────────────────
export default function ContentPage() {
  const [form, setForm] = useState({ business_type: 'Plumbing', base_location: 'San Diego, CA', num_cities: 10 })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [pages, setPages] = useState([])
  const [filter, setFilter] = useState('')
  const [exporting, setExporting] = useState('')
  const [preview, setPreview] = useState(null)
  const [kwInput, setKwInput] = useState('')
  const [targetKeywords, setTargetKeywords] = useState([])

  const addKeyword = (kw) => {
    const k = (kw || kwInput).trim().toLowerCase()
    if (k && !targetKeywords.includes(k)) setTargetKeywords(prev => [...prev, k])
    if (!kw) setKwInput('')
  }
  const removeKeyword = (kw) => setTargetKeywords(prev => prev.filter(k => k !== kw))

  const handleGenerate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await generateBulk({ ...form, num_cities: Number(form.num_cities), target_keywords: targetKeywords })
      setPages(res.data.pages)
    } catch (err) {
      setError(err.response?.data?.detail || 'Backend not running. Start uvicorn on port 8000.')
    } finally { setLoading(false) }
  }

  const handleExport = async (type) => {
    if (!pages.length) return
    setExporting(type)
    try {
      const res = type === 'json'
        ? await exportJson({ ...form, num_cities: pages.length })
        : await exportWordpress({ ...form, num_cities: pages.length })
      const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${type}-${form.business_type.toLowerCase()}.json`
      a.click()
      URL.revokeObjectURL(url)
    } finally { setExporting('') }
  }

  const filtered = pages.filter(p => p.city.toLowerCase().includes(filter.toLowerCase()))

  return (
    <div className="space-y-5 fade-in">

      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Content Generation</h1>
          <p className="text-sm text-slate-500 mt-0.5">Generate location-optimized SEO pages at scale</p>
        </div>
        {pages.length > 0 && (
          <div className="flex gap-2">
            <button onClick={() => handleExport('json')} disabled={exporting === 'json'}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-white/5 border border-white/8 text-slate-300 text-sm hover:bg-white/8 transition-colors disabled:opacity-50">
              <FileJson size={14} /> {exporting === 'json' ? 'Exporting...' : 'Download JSON'}
            </button>
            <button onClick={() => handleExport('wp')} disabled={exporting === 'wp'}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-white/5 border border-white/8 text-slate-300 text-sm hover:bg-white/8 transition-colors disabled:opacity-50">
              <Globe size={14} /> {exporting === 'wp' ? 'Exporting...' : 'Download WordPress'}
            </button>
          </div>
        )}
      </div>

      {/* ── TARGET KEYWORDS — full width, always on top ── */}
      <div className="card p-5 border-indigo-500/20">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Tag size={15} className="text-indigo-400" />
            <span className="text-sm font-semibold text-white">Target Keywords</span>
            <span className="text-xs text-slate-500">— added keywords get woven into every generated page</span>
          </div>
          {targetKeywords.length > 0 && (
            <button onClick={() => setTargetKeywords([])}
              className="text-xs text-slate-500 hover:text-red-400 transition-colors">
              Clear all
            </button>
          )}
        </div>

        {/* Input row */}
        <div className="flex gap-2 mb-3">
          <input
            type="text"
            value={kwInput}
            onChange={e => setKwInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addKeyword() } }}
            placeholder="Type a keyword and press Enter — e.g. emergency plumber san diego"
            className="flex-1 bg-white/4 border border-white/8 rounded-lg px-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50"
          />
          <button type="button" onClick={() => addKeyword()}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg bg-indigo-600/20 border border-indigo-600/30 text-indigo-300 hover:bg-indigo-600/30 transition-colors text-sm font-medium">
            <Plus size={14} /> Add
          </button>
        </div>

        {/* Added keywords */}
        {targetKeywords.length > 0 ? (
          <div className="flex flex-wrap gap-2 mb-3">
            {targetKeywords.map(kw => (
              <span key={kw} className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-indigo-500/15 text-indigo-300 border border-indigo-500/25 font-medium">
                {kw}
                <button onClick={() => removeKeyword(kw)} className="hover:text-white transition-colors">
                  <X size={10} />
                </button>
              </span>
            ))}
          </div>
        ) : null}

        {/* Suggestions */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-slate-600">Suggestions:</span>
          {KW_SUGGESTIONS.filter(s => !targetKeywords.includes(s)).map(s => (
            <button key={s} onClick={() => addKeyword(s)}
              className="text-xs px-2.5 py-1 rounded-lg bg-white/4 border border-white/6 text-slate-500 hover:text-slate-200 hover:border-white/15 transition-colors">
              + {s}
            </button>
          ))}
        </div>
      </div>

      {/* ── CAMPAIGN SETUP + CITY PREVIEW ── */}
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Zap size={14} className="text-indigo-400" /> Campaign Setup
          </h3>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Business Niche</label>
              <div className="flex flex-wrap gap-1.5 mb-2">
                {BUSINESS_TYPES.map(bt => (
                  <button key={bt} type="button" onClick={() => setForm(f => ({ ...f, business_type: bt }))}
                    className={`px-2.5 py-1 rounded-md text-xs font-medium transition-colors
                      ${form.business_type === bt
                        ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-600/30'
                        : 'bg-white/4 text-slate-400 border border-white/6 hover:border-white/15 hover:text-slate-200'}`}>
                    {bt}
                  </button>
                ))}
              </div>
              <input type="text" value={form.business_type}
                onChange={e => setForm(f => ({ ...f, business_type: e.target.value }))}
                placeholder="Custom niche..."
                className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                <MapPin size={10} className="inline mr-1" />Base Location
              </label>
              <input type="text" value={form.base_location}
                onChange={e => setForm(f => ({ ...f, base_location: e.target.value }))}
                placeholder="e.g. San Diego, CA"
                className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Cities</label>
                <span className="text-sm font-bold text-indigo-400">{form.num_cities}</span>
              </div>
              <input type="range" min="1" max="50" value={form.num_cities}
                onChange={e => setForm(f => ({ ...f, num_cities: Number(e.target.value) }))}
                className="w-full accent-indigo-500" />
            </div>
            {error && <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-xs">{error}</div>}
            <button type="submit" disabled={loading}
              className="btn-primary w-full py-2.5 rounded-lg text-white text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-60">
              {loading
                ? <><svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.2)" strokeWidth="3"/><path d="M12 2a10 10 0 0 1 10 10" stroke="white" strokeWidth="3" strokeLinecap="round"/></svg>Generating {form.num_cities} pages...</>
                : <><Zap size={14} />Generate Pages</>}
            </button>
          </form>
        </div>

        <div className="card p-4 lg:col-span-2">
          <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Globe size={11} /> Location Expansion — {form.num_cities} cities
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {SD_CITIES_PREVIEW.slice(0, form.num_cities).map(c => (
              <span key={c} className="text-xs px-2 py-1 rounded bg-white/5 border border-white/8 text-slate-400">{c}</span>
            ))}
            {form.num_cities > 15 && (
              <span className="text-xs px-2 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                +{form.num_cities - 15} more cities
              </span>
            )}
          </div>
        </div>
      </div>

      {/* ── RESULTS TABLE ── */}
      {pages.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
            <div className="flex items-center gap-3">
              <h3 className="text-sm font-semibold text-white">{pages.length} Pages Generated</h3>
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">Complete</span>
            </div>
            <input type="text" placeholder="Filter by city..." value={filter}
              onChange={e => setFilter(e.target.value)}
              className="bg-white/4 border border-white/8 rounded-lg px-3 py-1.5 text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 w-48" />
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th><th>City</th><th>SEO Title</th><th>SEO Score</th><th>Primary Keyword</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((block, i) => {
                const score = Math.round(block.readability_score || 75)
                return (
                  <tr key={`${block.city}-${i}`}>
                    <td className="text-slate-600 text-xs">{i + 1}</td>
                    <td>
                      <div className="font-semibold text-slate-200">{block.city}</div>
                      <div className="text-xs text-slate-500">{block.state}</div>
                    </td>
                    <td className="max-w-[260px]">
                      <div className="text-slate-300 text-xs truncate">{block.title}</div>
                      <div className="text-slate-600 text-xs truncate mt-0.5">{block.meta_description}</div>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 rounded-full bg-white/8 overflow-hidden">
                          <div className="h-full rounded-full"
                            style={{ width: `${score}%`, background: score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444' }} />
                        </div>
                        <span className={`text-xs font-bold ${score >= 75 ? 'text-emerald-400' : score >= 50 ? 'text-amber-400' : 'text-red-400'}`}>{score}</span>
                      </div>
                    </td>
                    <td className="text-xs text-slate-400 max-w-[160px] truncate">{block.keywords?.primary}</td>
                    <td>
                      <button onClick={() => setPreview({ block, index: i })}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/15 border border-indigo-600/25 text-indigo-300 text-xs hover:bg-indigo-600/25 transition-colors">
                        <Eye size={11} /> View
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {preview && (
        <PreviewModal
          block={preview.block}
          businessType={form.business_type}
          targetKeywords={targetKeywords}
          onClose={() => setPreview(null)}
          onRegenerate={(newBlock) => {
            setPages(prev => prev.map((p, i) => i === preview.index ? newBlock : p))
            setPreview({ block: newBlock, index: preview.index })
          }}
        />
      )}
    </div>
  )
}
