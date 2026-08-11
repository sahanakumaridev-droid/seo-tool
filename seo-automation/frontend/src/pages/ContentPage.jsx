import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, MapPin, Globe, Eye, X, RefreshCw, Save, CheckCircle,
         FileJson, Tag, Plus, Upload, ChevronDown, ChevronUp, Megaphone, Trash2 } from 'lucide-react'
import { generateBulk, exportJson, exportWordpress, generateSingle,
         savePage, publishToWordPress, publishBulkToWordPress, startBulkGenerateJob, getJob, publishAllToWeb, zeorbitBlogUrl,
         getNearbyCities, deletePage, listPages } from '../api'
import axios from 'axios'

const BUSINESS_TYPES = [
  'Web Design', 'Website Redesign', 'Small Business Web Design', 'WordPress Development',
  'eCommerce Development', 'Mobile App Development', 'iOS App Development', 'Android App Development',
  'App MVP Development', 'Nonprofit Website Design', 'SEO Agency',
  'Education', 'Tutoring', 'Online Courses',
  'Restaurant', 'Cafe', 'Catering',
  'Finance', 'Accounting',
  'Plumbing', 'HVAC', 'Roofing', 'Landscaping', 'Cleaning', 'Electrical', 'Painting', 'Pest Control', 'Moving',
]
const INDUSTRIES = ['Contractors', 'Healthcare', 'Retail', 'Restaurants',
  'Professional Services', 'Real Estate', 'Legal', 'Finance', 'Education', 'Other']
const KW_SUGGESTIONS = ['web design san diego', 'affordable web design', 'small business website',
  'website designer near me', 'wordpress website san diego', 'custom website design',
  'website redesign', 'mobile app development san diego', 'ecommerce website developer']
const SEO_PLUGINS = [
  { value: 'rankmath', label: 'RankMath' },
  { value: 'aioseo', label: 'All in One SEO' },
  { value: 'yoast', label: 'Yoast SEO' },
]

/** Map free-text niche / industry / keyword → category family for alignment checks. */
function categoryFamily(text) {
  const t = (text || '').toLowerCase()
  if (!t.trim()) return ''
  if (/(restaurant|cafe|catering|dining|food service|bistro)/.test(t)) return 'restaurant'
  if (/(educat|tutor|school|course|university|college|learning)/.test(t)) return 'education'
  if (/(financ|account|bank|invest|wealth|bookkeep)/.test(t)) return 'finance'
  if (/(legal|law|attorney|lawyer)/.test(t)) return 'legal'
  if (/(real estate|realtor|property)/.test(t)) return 'real_estate'
  if (/(health|dental|clinic|medical|doctor)/.test(t)) return 'healthcare'
  if (/(retail|store|shop|ecommerce|e-commerce)/.test(t) && !/web|website|design/.test(t)) return 'retail'
  if (/(plumb|hvac|roof|landscap|clean|electric|paint|pest|moving|contractor)/.test(t)) return 'contractors'
  if (/(software|engineer|coding|saas|mobile app|ios app|android|app mvp|app development)/.test(t)) return 'software'
  if (/(web design|website|wordpress|seo agency|redesign|web develop)/.test(t)) return 'web'
  if (/(professional services)/.test(t)) return 'professional'
  return ''
}

function industryFamily(industry) {
  const map = {
    Contractors: 'contractors',
    Healthcare: 'healthcare',
    Retail: 'retail',
    Restaurants: 'restaurant',
    'Professional Services': 'professional',
    'Real Estate': 'real_estate',
    Legal: 'legal',
    Finance: 'finance',
    Education: 'education',
    Other: 'other',
  }
  return map[industry] || categoryFamily(industry) || 'other'
}

/** Families that can pair with each other without a warning. */
const FAMILY_COMPAT = {
  web: new Set(['web', 'professional', 'retail', 'other', 'software']),
  software: new Set(['software', 'professional', 'other', 'web']),
  education: new Set(['education', 'professional', 'other']),
  restaurant: new Set(['restaurant', 'retail', 'other']),
  finance: new Set(['finance', 'professional', 'other']),
  legal: new Set(['legal', 'professional', 'other']),
  real_estate: new Set(['real_estate', 'professional', 'other']),
  healthcare: new Set(['healthcare', 'professional', 'other']),
  retail: new Set(['retail', 'restaurant', 'other', 'web']),
  contractors: new Set(['contractors', 'other']),
  professional: new Set(['professional', 'web', 'software', 'finance', 'legal', 'education', 'real_estate', 'healthcare', 'other']),
  other: null, // compatible with all
}

const FAMILY_LABEL = {
  web: 'Web / Digital',
  software: 'Software / Apps',
  education: 'Education',
  restaurant: 'Restaurants / Food',
  finance: 'Finance',
  legal: 'Legal',
  real_estate: 'Real Estate',
  healthcare: 'Healthcare',
  retail: 'Retail',
  contractors: 'Contractors / Trades',
  professional: 'Professional Services',
  other: 'Other',
}

function familiesCompatible(a, b) {
  if (!a || !b || a === 'other' || b === 'other') return true
  if (a === b) return true
  const set = FAMILY_COMPAT[a]
  return set ? set.has(b) : false
}

/**
 * Analyse Business Niche + Industry + Keywords for mismatched categories.
 * Returns { ok, message } — message is snackbar-ready when not ok.
 */
function analyzeCategoryAlignment(niche, industry, keywords = []) {
  const nicheFam = categoryFamily(niche)
  const indFam = industryFamily(industry)
  if (!nicheFam) return { ok: true, message: '' }

  if (indFam && indFam !== 'other' && !familiesCompatible(nicheFam, indFam)) {
    return {
      ok: false,
      message: `Please select matching categories only — Business Niche is “${FAMILY_LABEL[nicheFam] || nicheFam}” but Industry is “${FAMILY_LABEL[indFam] || indFam}”. Align niche, industry, and keywords.`,
    }
  }

  const kwText = (keywords || []).join(' ')
  const kwFam = categoryFamily(kwText)
  if (kwFam && !familiesCompatible(nicheFam, kwFam)) {
    return {
      ok: false,
      message: `Please select matching categories only — keywords look like “${FAMILY_LABEL[kwFam]}” but Business Niche is “${FAMILY_LABEL[nicheFam]}”. Use keywords for the same category.`,
    }
  }

  return { ok: true, message: '' }
}

// ── Preview Modal ──────────────────────────────────────────────
function PreviewModal({ block, businessType, targetKeywords = [], wpConfig, onClose, onRegenerate }) {
  const [tab, setTab] = useState('content')
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [publishResult, setPublishResult] = useState(null)

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

  const handlePublish = async () => {
    if (!wpConfig.wp_url) return
    setPublishing(true)
    setPublishResult(null)
    try {
      const res = await publishToWordPress(block, wpConfig)
      setPublishResult(res.data)
    } catch (e) {
      setPublishResult({ success: false, error: e.response?.data?.detail || e.message })
    } finally { setPublishing(false) }
  }

  const tabs = ['content', 'intro', 'keywords', 'questions', 'faqs', 'schema']

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
          <div className="flex items-center gap-2 flex-wrap justify-end">
            <button onClick={handleRegen} disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/8 text-slate-300 text-xs hover:bg-white/8 transition-colors disabled:opacity-50">
              <RefreshCw size={11} className={loading ? 'animate-spin' : ''} /> Regenerate
            </button>
            <button onClick={handleSave}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-colors ${saved ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-white/5 border border-white/8 text-slate-300 hover:bg-white/8'}`}>
              {saved ? <><CheckCircle size={11} /> Saved</> : <><Save size={11} /> Save</>}
            </button>
            {wpConfig.wp_url && (
              <button onClick={handlePublish} disabled={publishing}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-colors ${publishResult?.success ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-indigo-600/20 border border-indigo-600/30 text-indigo-300 hover:bg-indigo-600/30'} disabled:opacity-50`}>
                <Upload size={11} className={publishing ? 'animate-pulse' : ''} />
                {publishing ? 'Publishing...' : publishResult?.success ? 'Published!' : 'Publish to WP'}
              </button>
            )}
            <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-white/8 text-slate-400 hover:text-white transition-colors">
              <X size={16} />
            </button>
          </div>
        </div>
        {publishResult && (
          <div className={`px-6 py-2 text-xs flex items-center gap-2 ${publishResult.success ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
            {publishResult.success
              ? <>✓ Published — <a href={publishResult.post_url} target="_blank" rel="noreferrer" className="underline">{publishResult.post_url}</a></>
              : <>✗ {publishResult.error}</>}
          </div>
        )}
        <div className="flex border-b border-white/6 px-6 flex-shrink-0 overflow-x-auto">
          {tabs.map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-4 py-3 text-sm font-medium capitalize whitespace-nowrap transition-colors ${tab === t ? 'tab-active' : 'tab-inactive'}`}>
              {t === 'content' ? 'Content & Meta' : t === 'intro' ? 'Intro' : t === 'keywords' ? 'Keywords' : t === 'questions' ? 'User Questions' : t === 'faqs' ? 'FAQs' : 'Schema'}
            </button>
          ))}
        </div>
        <div className="overflow-y-auto flex-1 p-6 space-y-4">
          {tab === 'content' && (
            <>
              <MetaRow label="SEO Title" value={block.title} />
              <MetaRow label="Meta Description" value={block.meta_description} />
              <MetaRow label="URL Slug" value={block.slug || `${block.business_type?.toLowerCase().replace(/ /g,'-')}-${block.city?.toLowerCase().replace(/ /g,'-')}`} />
              <MetaRow label="H1" value={block.h1} />
              <div className="rounded-lg bg-white/3 border border-white/6 p-4">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">H2 Headings (Question-based)</div>
                <ul className="space-y-2">
                  {block.h2s?.map((h, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                      <span className="text-indigo-400 text-xs font-bold mt-0.5 flex-shrink-0">H2</span>{h}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="rounded-lg bg-white/3 border border-white/6 p-4">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">H3 Headings</div>
                <ul className="space-y-2">
                  {block.h3s?.map((h, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                      <span className="text-violet-400 text-xs font-bold mt-0.5 flex-shrink-0">H3</span>{h}
                    </li>
                  ))}
                </ul>
              </div>
              <MetaRow label="Body Content" value={block.content} multiline />
              <MetaRow label="Call to Action" value={block.cta} />
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <ScoreBar label="Readability" value={Math.round(block.readability_score || 75)} color="#1D4ED8" />
                <ScoreBar label="Keyword Density" value={Math.min(100, Math.round((block.keyword_density || 1.5) * 20))} color="#2563EB" />
                <ScoreBar label="Meta Complete" value={100} color="#10b981" />
              </div>
            </>
          )}
          {tab === 'intro' && (
            <>
              <div className="rounded-lg bg-indigo-500/8 border border-indigo-500/20 p-4 mb-2">
                <p className="text-xs text-indigo-300 mb-1 font-semibold">AI Overview Optimized Intro</p>
                <p className="text-xs text-slate-400">First 2–3 lines answer directly, include location + keyword — optimized for Google AI Overviews, Bing Copilot, and ChatGPT retrieval.</p>
              </div>
              <MetaRow label="Intro Paragraph" value={block.intro || block.content?.split('\n\n')[0]} multiline />
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
                  {block.keywords?.primary}
                </span>
              </div>
              <KwGroup label="Short-tail / Main Keywords" kws={block.keywords?.secondary?.slice(0,3) || []} color="violet" />
              <KwGroup label="Long-tail Keywords" kws={block.keywords?.long_tail || []} color="sky" />
              <KwGroup label='"Near Me" Variations' kws={block.keywords?.near_me || []} color="emerald" />
            </>
          )}
          {tab === 'questions' && (
            <div className="space-y-2">
              <div className="rounded-lg bg-amber-500/8 border border-amber-500/20 p-4 mb-2">
                <p className="text-xs text-amber-300 font-semibold mb-1">Real User Questions</p>
                <p className="text-xs text-slate-400">Sourced from Google PAA, Suggest patterns. Used as H2s and FAQs for AI Overview optimization.</p>
              </div>
              {(block.keywords?.user_questions || []).map((q, i) => (
                <div key={i} className="flex items-start gap-3 rounded-lg bg-white/3 border border-white/6 p-3">
                  <span className="text-amber-400 text-xs font-bold mt-0.5 flex-shrink-0">Q{i+1}</span>
                  <span className="text-sm text-slate-300">{q}</span>
                </div>
              ))}
            </div>
          )}
          {tab === 'faqs' && (
            <div className="space-y-3">
              <div className="text-xs text-slate-500 mb-2">{block.faqs?.length || 0} FAQs — structured for AI extraction (schema.org/FAQPage)</div>
              {block.faqs?.map((faq, i) => (
                <div key={i} className="rounded-xl bg-white/3 border border-white/6 p-4">
                  <p className="text-sm font-semibold text-indigo-300 mb-2">{faq.question}</p>
                  <p className="text-sm text-slate-400 leading-relaxed">{faq.answer}</p>
                </div>
              ))}
            </div>
          )}
          {tab === 'schema' && (
            <div className="space-y-4">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">JSON-LD Schema Markup</div>
              {block.schema_markup && Object.entries(block.schema_markup).map(([key, val]) => (
                <div key={key}>
                  <div className="text-xs text-indigo-400 font-semibold mb-1 capitalize">{key.replace('_', ' ')}</div>
                  <pre className="rounded-xl p-4 text-xs text-emerald-400 overflow-auto border leading-relaxed"
                    style={{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }}>
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

// ── WordPress Config Panel ─────────────────────────────────────
function WordPressPanel({ wpConfig, setWpConfig }) {
  const [open, setOpen] = useState(false)
  const connected = !!wpConfig.wp_url

  return (
    <div className="card border-violet-500/20">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-4"
      >
        <div className="flex items-center gap-2">
          <Globe size={15} className="text-violet-400" />
          <span className="text-sm font-semibold text-white">WordPress Auto-Publish</span>
          {connected && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">
              Configured
            </span>
          )}
        </div>
        {open ? <ChevronUp size={14} className="text-slate-500" /> : <ChevronDown size={14} className="text-slate-500" />}
      </button>
      {open && (
        <div className="px-5 pb-5 space-y-3 border-t border-white/5 pt-4">
          <p className="text-xs text-slate-500">
            Enter your WordPress credentials to auto-publish pages. Use an{' '}
            <a href="https://wordpress.org/documentation/article/application-passwords/" target="_blank" rel="noreferrer"
              className="text-indigo-400 underline">Application Password</a> (not your login password).
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">WordPress URL</label>
              <input type="url" value={wpConfig.wp_url}
                onChange={e => setWpConfig(c => ({ ...c, wp_url: e.target.value }))}
                placeholder="https://yoursite.com"
                className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Username</label>
              <input type="text" value={wpConfig.wp_username}
                onChange={e => setWpConfig(c => ({ ...c, wp_username: e.target.value }))}
                placeholder="your_wp_username"
                className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Application Password</label>
              <input type="password" value={wpConfig.wp_app_password}
                onChange={e => setWpConfig(c => ({ ...c, wp_app_password: e.target.value }))}
                placeholder="Connected on server — leave blank"
                className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">SEO Plugin</label>
              <select value={wpConfig.seo_plugin}
                onChange={e => setWpConfig(c => ({ ...c, seo_plugin: e.target.value }))}
                className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500/50">
                {SEO_PLUGINS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Publish Status</label>
            <div className="flex gap-2">
              {['draft', 'publish'].map(s => (
                <button key={s} type="button"
                  onClick={() => setWpConfig(c => ({ ...c, status: s }))}
                  className={`px-3 py-1 rounded-md text-xs font-medium capitalize transition-colors ${wpConfig.status === s ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-600/30' : 'bg-white/4 text-slate-400 border border-white/6 hover:border-white/15'}`}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Main Page ──────────────────────────────────────────────────
export default function ContentPage() {
  const DEFAULTS = { business_type: '', base_location: 'San Diego, CA', num_cities: 10, industry: 'Contractors' }
  const navigate = useNavigate()
  const [form, setForm] = useState(() => {
    try {
      const saved = JSON.parse(localStorage.getItem('seo_project') || '{}')
      // Never prefill Business Niche — user must choose it each campaign setup
      return { ...DEFAULTS, ...saved, business_type: '' }
    } catch { return DEFAULTS }
  })

  const updateForm = (updater) => {
    setForm(prev => {
      const next = typeof updater === 'function' ? updater(prev) : updater
      localStorage.setItem('seo_project', JSON.stringify(next))
      window.dispatchEvent(new Event('seo_project_updated'))
      return next
    })
  }
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  // Persist generated results across navigation (View -> back must not wipe them)
  const [pages, setPages] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('seo_pages') || '[]') } catch { return [] }
  })
  const [filter, setFilter] = useState('')
  const [exporting, setExporting] = useState('')
  const [kwInput, setKwInput] = useState('')
  const [targetKeywords, setTargetKeywords] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('seo_keywords') || '[]') } catch { return [] }
  })
  const [useAi, setUseAi] = useState(true)
  const [llmProvider, setLlmProvider] = useState('')
  const [llmAvailability, setLlmAvailability] = useState({})
  const [savedPages, setSavedPages] = useState([])
  const [deletingSlug, setDeletingSlug] = useState('')
  const [useAsync, setUseAsync] = useState(false)
  const [asyncJobId, setAsyncJobId] = useState('')
  const [jobProgress, setJobProgress] = useState(null)  // { completed, failed, total, status }
  const [wpConfig, setWpConfig] = useState({
    wp_url: 'https://zeorbit.com', wp_username: 'zeor@admnir', wp_app_password: '',
    seo_plugin: 'aioseo', status: 'publish',
  })
  const [publishingAll, setPublishingAll] = useState(false)
  const [publishResults, setPublishResults] = useState({})
  const [toast, setToast] = useState(null)
  const resultsRef = useRef(null)
  const [nearbyCities, setNearbyCities] = useState([])
  const [nearbyError, setNearbyError] = useState('')

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), type === 'warning' ? 6500 : 4000)
  }

  // Warn when niche / industry / keywords point at different categories
  useEffect(() => {
    const niche = (form.business_type || '').trim()
    if (!niche) return
    const timer = setTimeout(() => {
      const result = analyzeCategoryAlignment(niche, form.industry, targetKeywords)
      if (!result.ok) showToast(result.message, 'warning')
    }, 450)
    return () => clearTimeout(timer)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.business_type, form.industry, targetKeywords])

  // Keep results + keywords alive when navigating to a page preview and back
  useEffect(() => { sessionStorage.setItem('seo_pages', JSON.stringify(pages)) }, [pages])
  useEffect(() => { sessionStorage.setItem('seo_keywords', JSON.stringify(targetKeywords)) }, [targetKeywords])

  // Prefill from Lead Engine "Generate in SEO Content"
  useEffect(() => {
    try {
      const raw = localStorage.getItem('seo_lead_funnel')
      if (!raw) return
      const funnel = JSON.parse(raw)
      localStorage.removeItem('seo_lead_funnel')
      if (funnel.business_type) {
        updateForm(prev => ({ ...prev, business_type: funnel.business_type }))
      }
      if (Array.isArray(funnel.keywords) && funnel.keywords.length) {
        setTargetKeywords(prev => {
          const merged = [...prev]
          funnel.keywords.forEach(k => { if (k && !merged.includes(k)) merged.push(k) })
          return merged
        })
      }
      if (funnel.headline) showToast(`Funnel loaded: ${funnel.headline.slice(0, 60)}…`)
    } catch { /* ignore */ }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // AI model availability + saved location pages (for trash / restart)
  useEffect(() => {
    axios.get('/api/content/llm-providers').then(r => setLlmAvailability(r.data || {})).catch(() => {})
    listPages(0, 100).then(r => setSavedPages(Array.isArray(r.data) ? r.data : [])).catch(() => {})
  }, [pages])

  const handleDeleteSaved = async (slug) => {
    if (!slug || !confirm(`Delete location content "${slug}"? You can regenerate it after.`)) return
    setDeletingSlug(slug)
    try {
      await deletePage(slug)
      setSavedPages(prev => prev.filter(p => p.slug !== slug))
      setPages(prev => prev.filter(p => p.slug !== slug))
      showToast('Location content deleted')
    } catch (e) {
      showToast(e.response?.data?.detail || e.message, 'error')
    } finally {
      setDeletingSlug('')
    }
  }

  const handleClearResults = () => {
    if (!pages.length) return
    if (!confirm('Clear generated results from this session? Saved/published pages stay until you trash them below.')) return
    setPages([])
    sessionStorage.removeItem('seo_pages')
    showToast('Session results cleared — ready to regenerate')
  }

  // Location Expansion preview — reflect the real nearby cities for whatever
  // base_location is currently typed, instead of a hardcoded city list.
  useEffect(() => {
    const loc = form.base_location.trim()
    if (!loc) { setNearbyCities([]); setNearbyError(''); return }
    let cancelled = false
    const timer = setTimeout(async () => {
      try {
        const res = await getNearbyCities(loc, form.num_cities)
        if (cancelled) return
        setNearbyCities(res.data || [])
        setNearbyError('')
      } catch (e) {
        if (cancelled) return
        setNearbyCities([])
        setNearbyError(e.response?.data?.detail || 'Could not find that location.')
      }
    }, 500)
    return () => { cancelled = true; clearTimeout(timer) }
  }, [form.base_location, form.num_cities])

  // Poll an async job until it finishes, then drop the generated pages into
  // the results table (same review/publish flow as sync generation).
  useEffect(() => {
    if (!asyncJobId) return
    let stop = false
    const tick = async () => {
      try {
        const { data } = await getJob(asyncJobId)
        if (stop) return
        setJobProgress({ completed: data.completed, failed: data.failed, total: data.total, status: data.status })
        const finished = data.status === 'completed' || (data.completed + data.failed) >= data.total
        if (finished) {
          const done = (data.results || []).filter(r => r && !r.error)
          setPages(done)
          setLoading(false)
          setAsyncJobId('')
          setJobProgress(null)
          showToast(`${done.length} pages generated!`)
          setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 150)
        } else {
          setTimeout(tick, 2000)
        }
      } catch {
        if (!stop) setTimeout(tick, 2500)
      }
    }
    tick()
    return () => { stop = true }
  }, [asyncJobId])

  const addKeyword = (kw) => {
    const k = (kw || kwInput).trim().toLowerCase()
    if (k && !targetKeywords.includes(k)) setTargetKeywords(prev => [...prev, k])
    if (!kw) setKwInput('')
  }
  const removeKeyword = (kw) => setTargetKeywords(prev => prev.filter(k => k !== kw))

  const handleGenerate = async (e) => {
    e.preventDefault()
    const niche = (form.business_type || '').trim()
    if (!niche) {
      setError('Select or enter a Business Niche before generating pages.')
      showToast('Business Niche is required')
      document.getElementById('business-niche-section')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      return
    }
    if (!targetKeywords.length) {
      setError('Add at least one target keyword before generating pages.')
      showToast('Target keywords are required')
      document.getElementById('target-keywords-section')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      return
    }
    const alignment = analyzeCategoryAlignment(niche, form.industry, targetKeywords)
    if (!alignment.ok) {
      setError(alignment.message)
      showToast(alignment.message, 'warning')
      document.getElementById('business-niche-section')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      return
    }
    setLoading(true)
    setError('')
    setPublishResults({})
    setAsyncJobId('')
    try {
      const payload = {
        ...form,
        business_type: niche,
        num_cities: Number(form.num_cities),
        target_keywords: targetKeywords,
        use_ai: useAi,
        llm_provider: llmProvider || null,
      }
      if (useAsync) {
        const res = await startBulkGenerateJob(payload)
        setAsyncJobId(res.data.job_id)
        const existing = JSON.parse(localStorage.getItem('seo_jobs') || '[]')
        localStorage.setItem('seo_jobs', JSON.stringify([res.data.job_id, ...existing]))
        showToast(`Async job started — ID: ${res.data.job_id.slice(0, 8)}...`)
      } else {
        const res = await generateBulk(payload)
        setPages(res.data.pages)
        showToast(`${res.data.pages.length} pages generated successfully!`)
        setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100)
      }
    } catch (err) {
      setError(
        err.response?.data?.detail
        || (err.code === 'ERR_NETWORK'
            ? 'Cannot reach the backend. Start it with: uvicorn main:app --port 8000'
            : `Generation failed${err.message ? ` — ${err.message}` : ''}. Please try again.`)
      )
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

  const handlePublishSingle = async (block, index) => {
    if (!wpConfig.wp_url) return
    setPublishResults(r => ({ ...r, [index]: 'loading' }))
    try {
      const res = await publishToWordPress(block, wpConfig)
      setPublishResults(r => ({ ...r, [index]: res.data }))
    } catch (e) {
      setPublishResults(r => ({ ...r, [index]: { success: false, error: e.response?.data?.detail || e.message } }))
    }
  }
  const handlePublishAll = async () => {
    if (!wpConfig.wp_url || !pages.length) return
    setPublishingAll(true)
    try {
      const res = await publishBulkToWordPress(pages, wpConfig)
      const map = {}
      res.data.forEach((r, i) => { map[i] = r })
      setPublishResults(map)
    } catch (e) {
      setError(e.response?.data?.detail || 'WordPress publish failed.')
    } finally { setPublishingAll(false) }
  }

  const [webAll, setWebAll] = useState(null)   // { loading } | { links: [...] } | { error }
  const handlePublishAllWeb = async () => {
    if (!pages.length) return
    setWebAll({ loading: true })
    try {
      const res = await publishAllToWeb(pages)
      setWebAll({ links: res.data.published })
      showToast(`${res.data.count} pages published to ZeOrbit!`)
      window.open(zeorbitBlogUrl(), '_blank', 'noopener')
    } catch (e) {
      setWebAll({ error: e.response?.data?.detail || 'Publish failed. Please try again.' })
    }
  }

  const filtered = pages.filter(p => p.city.toLowerCase().includes(filter.toLowerCase()))
  const categoryAlignment = analyzeCategoryAlignment(
    (form.business_type || '').trim(),
    form.industry,
    targetKeywords,
  )

  return (
    <div className="space-y-5 fade-in">
      {/* Toast / snackbar */}
      {toast && (
        <div className={`fixed top-5 right-5 z-50 flex items-start gap-3 px-5 py-3 rounded-xl shadow-2xl text-sm font-semibold transition-all max-w-md
          ${toast.type === 'success' ? 'bg-emerald-500 text-white'
            : toast.type === 'warning' ? 'bg-amber-500 text-slate-900'
              : 'bg-red-500 text-white'}`}>
          <CheckCircle size={16} className="mt-0.5 flex-shrink-0" />
          <span className="leading-snug">{toast.msg}</span>
          <button onClick={() => setToast(null)} className="ml-2 opacity-70 hover:opacity-100 flex-shrink-0"><X size={14} /></button>
        </div>
      )}
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Content Generation</h1>
          <p className="text-sm text-slate-500 mt-0.5">AI-powered, SGE/Copilot/ChatGPT-optimized SEO pages at scale</p>
        </div>
      </div>

      {/* Target Keywords — required */}
      <div id="target-keywords-section" className={`card p-5 ${targetKeywords.length ? 'border-indigo-500/20' : 'border-amber-500/40'}`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Tag size={15} className="text-indigo-400" />
            <span className="text-sm font-semibold text-white">Target Keywords</span>
            <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">Required</span>
            <span className="text-xs text-slate-500">— woven into every generated page</span>
          </div>
          {targetKeywords.length > 0 && (
            <button onClick={() => setTargetKeywords([])} className="text-xs text-slate-500 hover:text-red-400 transition-colors">
              Clear all
            </button>
          )}
        </div>
        {!targetKeywords.length && (
          <div className="mb-3 text-xs text-amber-300/90">
            Add at least one keyword (type and press Enter, or pick a suggestion) before generating.
          </div>
        )}
        <div className="flex gap-2 mb-3">
          <input type="text" value={kwInput}
            onChange={e => setKwInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addKeyword() } }}
            required={targetKeywords.length === 0}
            aria-required="true"
            placeholder="e.g. web design san diego — press Enter to add"
            className={`flex-1 bg-white/4 border rounded-lg px-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 ${targetKeywords.length ? 'border-white/8' : 'border-amber-500/40'}`} />
          <button type="button" onClick={() => addKeyword()}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg bg-indigo-600/20 border border-indigo-600/30 text-indigo-300 hover:bg-indigo-600/30 transition-colors text-sm font-medium">
            <Plus size={14} /> Add
          </button>
        </div>
        {targetKeywords.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {targetKeywords.map(kw => (
              <span key={kw} className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-indigo-500/15 text-indigo-300 border border-indigo-500/25 font-medium">
                {kw}
                <button onClick={() => removeKeyword(kw)} className="hover:text-white transition-colors"><X size={10} /></button>
              </span>
            ))}
          </div>
        )}
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

      {/* Campaign Setup + City Preview */}
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Zap size={14} className="text-indigo-400" /> Campaign Setup
          </h3>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div id="business-niche-section">
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                Business Niche
                <span className="ml-2 text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">Required</span>
              </label>
              <div className="flex flex-wrap gap-1.5 mb-2">
                {BUSINESS_TYPES.map(bt => (
                  <button key={bt} type="button" onClick={() => updateForm(f => ({ ...f, business_type: bt }))}
                    className={`px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${form.business_type === bt ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-600/30' : 'bg-white/4 text-slate-400 border border-white/6 hover:border-white/15 hover:text-slate-200'}`}>
                    {bt}
                  </button>
                ))}
              </div>
              <input type="text" value={form.business_type}
                onChange={e => updateForm(f => ({ ...f, business_type: e.target.value }))}
                required
                aria-required="true"
                placeholder="Select a chip or type a custom niche…"
                className={`w-full bg-white/4 border rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 ${(form.business_type || '').trim() ? 'border-white/8' : 'border-amber-500/40'}`} />
              {!(form.business_type || '').trim() && (
                <p className="mt-1.5 text-[10px] text-amber-400">Choose a niche chip or type one — required to generate.</p>
              )}
              {(form.business_type || '').trim() && (
                <p className="mt-1.5 text-[10px] text-slate-500">This controls page topic, titles, and images.</p>
              )}
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Industry / Audience</label>
              <select
                value={form.industry}
                onChange={e => updateForm(f => ({ ...f, industry: e.target.value }))}
                className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500/50">
                {INDUSTRIES.map(i => <option key={i} value={i}>{i}</option>)}
              </select>
              <p className="mt-1.5 text-[10px] text-slate-500">Shapes copy tone. Keep it in the same category as Business Niche.</p>
            </div>
            {!categoryAlignment.ok && (
              <div className="text-[11px] leading-snug px-3 py-2 rounded-lg bg-amber-500/15 border border-amber-500/35 text-amber-200">
                {categoryAlignment.message}
              </div>
            )}
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                <MapPin size={10} className="inline mr-1" />Base Location
              </label>
              <input type="text" value={form.base_location}
                onChange={e => updateForm(f => ({ ...f, base_location: e.target.value }))}
                placeholder="e.g. San Diego, CA"
                className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
              {form.base_location.trim() && !form.base_location.includes(',') && (
                <div className="mt-1.5 text-[10px] text-amber-400">
                  Add the state (e.g. "{form.base_location.trim()}, TX") to avoid ambiguous same-named cities.
                </div>
              )}
              {nearbyError && (
                <div className="mt-1.5 text-[10px] text-red-400">{nearbyError}</div>
              )}
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Cities</label>
                <span className="text-sm font-bold text-indigo-400">{form.num_cities}</span>
              </div>
              <input type="range" min="1" max="50" value={form.num_cities}
                onChange={e => updateForm(f => ({ ...f, num_cities: Number(e.target.value) }))}
                className="w-full accent-indigo-500" />
            </div>
            {error && <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-xs">{error}</div>}

            {/* AI + Async toggles */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between px-2.5 py-2 rounded-lg bg-white/3 border border-white/6">
                <div>
                  <div className="text-xs font-semibold text-slate-300">AI Content</div>
                  <div className="text-[10px] text-slate-500">Unique copy per location</div>
                </div>
                <button type="button" onClick={() => setUseAi(a => !a)}
                  className={`w-9 h-5 rounded-full transition-colors relative flex-shrink-0 ${useAi ? 'bg-indigo-500' : 'bg-white/10'}`}>
                  <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${useAi ? 'left-4' : 'left-0.5'}`} />
                </button>
              </div>
              <div className="flex items-center justify-between px-2.5 py-2 rounded-lg bg-white/3 border border-white/6">
                <div>
                  <div className="text-xs font-semibold text-slate-300">AI Model</div>
                  <div className="text-[10px] text-slate-500">
                    {llmAvailability.active ? `Active: ${llmAvailability.active}` : 'Turn on AI Content to use'}
                  </div>
                </div>
                <select
                  value={llmProvider}
                  onChange={e => { setLlmProvider(e.target.value); if (e.target.value) setUseAi(true) }}
                  className="bg-white/5 border border-white/10 rounded-lg px-2 py-1 text-xs text-slate-200 focus:outline-none min-w-[120px]"
                >
                  <option value="">Auto</option>
                  <option value="gemini">Gemini</option>
                  <option value="anthropic">Claude</option>
                  <option value="openai">ChatGPT (GPT-4)</option>
                  <option value="groq">Groq</option>
                </select>
              </div>
              <div className="flex items-center justify-between px-2.5 py-2 rounded-lg bg-white/3 border border-white/6">
                <div>
                  <div className="text-xs font-semibold text-slate-300">⚡ Async Job (50+ pages)</div>
                  <div className="text-[10px] text-slate-500">Background processing</div>
                </div>
                <button type="button" onClick={() => setUseAsync(a => !a)}
                  className={`w-9 h-5 rounded-full transition-colors relative flex-shrink-0 ${useAsync ? 'bg-amber-500' : 'bg-white/10'}`}>
                  <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${useAsync ? 'left-4' : 'left-0.5'}`} />
                </button>
              </div>
            </div>

            {asyncJobId && (() => {
              const total = jobProgress?.total || form.num_cities
              const done = (jobProgress?.completed || 0) + (jobProgress?.failed || 0)
              const pct = total ? Math.round((done / total) * 100) : 0
              const R = 26, C = 2 * Math.PI * R
              return (
                <div className="flex flex-col items-center gap-2 py-3 rounded-xl" style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)' }}>
                  <svg width="70" height="70" viewBox="0 0 70 70" style={{ transform: 'rotate(-90deg)' }}>
                    <circle cx="35" cy="35" r={R} fill="none" stroke="var(--border-bright)" strokeWidth="6" />
                    <circle cx="35" cy="35" r={R} fill="none" stroke="var(--brand)" strokeWidth="6" strokeLinecap="round"
                      strokeDasharray={C} strokeDashoffset={C - (pct / 100) * C}
                      style={{ transition: 'stroke-dashoffset .4s ease' }} />
                  </svg>
                  <div style={{ marginTop: -52, fontSize: 15, fontWeight: 800, color: 'var(--text-1)' }}>{pct}%</div>
                  <div style={{ marginTop: 34, fontSize: 12.5, fontWeight: 600, color: 'var(--text-2)' }}>
                    Generating with AI… {done} / {total} pages
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-4)' }}>You can review &amp; publish each below when ready</div>
                </div>
              )
            })()}

            <button type="submit" disabled={loading || !!asyncJobId || !targetKeywords.length || !(form.business_type || '').trim() || !categoryAlignment.ok}
              className="btn-primary w-full py-2.5 rounded-lg text-white text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-60"
              title={
                !(form.business_type || '').trim() ? 'Select a Business Niche first'
                  : !targetKeywords.length ? 'Add at least one target keyword first'
                    : !categoryAlignment.ok ? 'Align niche, industry, and keywords to the same category'
                      : undefined
              }>
              {loading || asyncJobId
                ? <><svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.2)" strokeWidth="3"/><path d="M12 2a10 10 0 0 1 10 10" stroke="white" strokeWidth="3" strokeLinecap="round"/></svg>{asyncJobId ? 'Generating…' : `Generating ${form.num_cities} pages...`}</>
                : <><Zap size={14} />{useAsync ? 'Start Async Job' : 'Generate Pages'}{useAi ? ' (AI)' : ''}</>}
            </button>
            {!(form.business_type || '').trim() ? (
              <p className="text-[11px] text-amber-400 text-center">Select a Business Niche to enable generate.</p>
            ) : !targetKeywords.length ? (
              <p className="text-[11px] text-amber-400 text-center">Add a target keyword above to enable generate.</p>
            ) : !categoryAlignment.ok ? (
              <p className="text-[11px] text-amber-400 text-center">Please select matching categories only.</p>
            ) : null}
          </form>
        </div>

        <div className="card p-3 lg:col-span-2">
          <h4 className="text-[11px] font-semibold uppercase tracking-wider mb-2 flex items-center gap-1.5" style={{ color: 'var(--text-2)' }}>
            <Globe size={11} /> Location Expansion — {nearbyCities.length || form.num_cities} locations
          </h4>
          <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto">
            {nearbyCities.slice(0, 40).map(c => {
              const kind = c.kind || 'city'
              const style = kind === 'state'
                ? { background: '#eef2ff', border: '1px solid #6366f1', color: '#312e81' }
                : kind === 'county'
                  ? { background: '#fff7ed', border: '1px solid #ea580c', color: '#9a3412' }
                  : { background: '#f8fafc', border: '1px solid #64748b', color: '#0f172a' }
              return (
                <span
                  key={`${c.name}-${c.state}-${kind}`}
                  className="text-[11px] px-2 py-0.5 rounded font-semibold"
                  style={style}
                >
                  {kind !== 'city' && (
                    <span className="uppercase text-[9px] mr-1" style={{ opacity: 0.85, fontWeight: 800 }}>
                      {kind}
                    </span>
                  )}
                  {c.name}{c.state ? `, ${c.state}` : ''}
                </span>
              )
            })}
            {nearbyCities.length > 40 && (
              <span className="text-[11px] px-2 py-0.5 rounded font-semibold"
                style={{ background: '#eef2ff', border: '1px solid #6366f1', color: '#3730a3' }}>
                +{nearbyCities.length - 40} more
              </span>
            )}
            {!nearbyCities.length && !nearbyError && form.base_location.trim() && (
              <span className="text-xs" style={{ color: 'var(--text-3)' }}>Looking up locations…</span>
            )}
          </div>
          <p className="text-[10px] mt-2" style={{ color: 'var(--text-3)' }}>
            Tip: use a state (“Illinois, IL”), county (“Cook County, IL”), or city (“Chicago, IL”).
          </p>
        </div>
      </div>

      {/* WordPress Panel */}
      <WordPressPanel wpConfig={wpConfig} setWpConfig={setWpConfig} />

      {/* ── SUCCESS BANNER — appears immediately after generation ── */}
      {pages.length > 0 && (
        <div ref={resultsRef} className="content-action-bar rounded-xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: '#d1fae5', border: '1px solid #6ee7b7' }}>
              <CheckCircle size={18} style={{ color: '#047857' }} />
            </div>
            <div>
              <p className="font-semibold text-sm" style={{ color: '#0f172a' }}>{pages.length} SEO pages generated</p>
              <p className="text-xs mt-0.5" style={{ color: '#334155' }}>
                {form.business_type} · {form.base_location} · Ready to download or publish
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <button onClick={() => handleExport('json')} disabled={exporting === 'json'}
              className="content-btn flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm disabled:opacity-50">
              <FileJson size={14} /> {exporting === 'json' ? 'Exporting...' : 'Download JSON'}
            </button>
            <button onClick={handlePublishAllWeb} disabled={webAll?.loading}
              className="content-btn-primary flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm disabled:opacity-60">
              {webAll?.loading
                ? <><svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.3)" strokeWidth="3"/><path d="M12 2a10 10 0 0 1 10 10" stroke="#fff" strokeWidth="3" strokeLinecap="round"/></svg>Publishing all…</>
                : <><Globe size={14} /> Publish All {pages.length} to ZeOrbit</>}
            </button>
            <button onClick={() => handleExport('wp')} disabled={exporting === 'wp'}
              className="content-btn flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm disabled:opacity-50">
              <FileJson size={14} /> {exporting === 'wp' ? 'Exporting...' : 'WP Format'}
            </button>
            {wpConfig.wp_url && (
              <button onClick={handlePublishAll} disabled={publishingAll}
                className="content-btn-violet flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm disabled:opacity-50">
                <Upload size={14} /> {publishingAll ? 'Publishing...' : 'Publish All to WordPress'}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Published-to-web links panel */}
      {webAll?.error && <div className="alert alert-error">✗ {webAll.error}</div>}
      {webAll?.links && (
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle size={16} style={{ color: 'var(--green)' }} />
            <h3 className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>{webAll.links.length} pages live on ZeOrbit</h3>
            <a href={zeorbitBlogUrl()} target="_blank" rel="noreferrer" className="text-xs ml-auto" style={{ color: 'var(--brand-violet)' }}>Open blog →</a>
          </div>
          <div className="space-y-2">
            {webAll.links.map((l, i) => (
              <div key={i} className="flex items-center justify-between gap-3 rounded-lg px-3 py-2" style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)' }}>
                <div className="min-w-0">
                  <div className="text-xs font-semibold truncate" style={{ color: 'var(--text-1)' }}>{l.city}{l.state ? `, ${l.state}` : ''}</div>
                  <a href={l.public_url} target="_blank" rel="noreferrer" className="text-xs truncate block" style={{ color: 'var(--brand-violet)' }}>{l.public_url}</a>
                </div>
                <div className="flex items-center gap-1.5 flex-shrink-0">
                  <button onClick={() => navigator.clipboard?.writeText(l.public_url)}
                    className="px-2.5 py-1.5 rounded-lg text-xs" style={{ background: 'var(--bg-overlay)', border: '1px solid var(--border-bright)', color: 'var(--text-2)' }}>Copy</button>
                  <button
                    onClick={() => navigate('/google-ads', {
                      state: {
                        finalUrl: l.public_url,
                        public_url: l.public_url,
                        category: form.business_type,
                        city: l.city || '',
                        businessName: form.business_type,
                        title: l.title,
                        keywords: targetKeywords,
                      },
                    })}
                    className="px-2.5 py-1.5 rounded-lg text-xs inline-flex items-center gap-1"
                    style={{ background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.35)', color: '#a5b4fc' }}
                  >
                    <Megaphone size={11} /> Google Ads
                  </button>
                  <a href={l.public_url} target="_blank" rel="noreferrer"
                    className="px-2.5 py-1.5 rounded-lg text-xs btn-primary" style={{ color: '#fff' }}>Open</a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Results Table */}
      {pages.length > 0 && (
        <div className="card" ref={resultsRef}>
          <div className="flex items-center justify-between px-4 py-3" style={{ borderBottom: '1px solid var(--border)' }}>
            <div className="flex items-center gap-3">
              <h3 className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>{pages.length} Pages Generated</h3>
              <span className="text-xs px-2 py-0.5 rounded-full font-semibold" style={{ background: '#ecfdf5', color: '#047857', border: '1px solid #6ee7b7' }}>Complete</span>
            </div>
            <div className="flex items-center gap-2">
              <button type="button" onClick={handleClearResults}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold"
                style={{ background: '#fff', border: '1px solid #94a3b8', color: '#0f172a' }}>
                <Trash2 size={11} /> Clear session
              </button>
              <input type="text" placeholder="Filter by city..." value={filter}
                onChange={e => setFilter(e.target.value)}
                className="rounded-lg px-3 py-1.5 text-sm w-48"
                style={{ background: '#fff', border: '1px solid #94a3b8', color: '#0f172a' }} />
            </div>
          </div>
          <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th><th>City</th><th>SEO Title</th><th>Score</th><th>Primary Keyword</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((block, i) => {
                const score = Math.round(block.readability_score || 75)
                const pr = publishResults[i]
                return (
                  <tr key={`${block.city}-${i}`}>
                    <td className="text-xs font-semibold" style={{ color: 'var(--text-3)' }}>{i + 1}</td>
                    <td>
                      <div className="font-semibold text-sm" style={{ color: 'var(--text-1)' }}>{block.city}</div>
                      <div className="text-xs muted-cell">{block.state}</div>
                    </td>
                    <td className="max-w-[240px]">
                      <div className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>{block.title}</div>
                      <div className="text-xs muted-cell mt-0.5">{block.slug}</div>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="w-14 h-1.5 rounded-full overflow-hidden" style={{ background: '#e2e8f0' }}>
                          <div className="h-full rounded-full"
                            style={{ width: `${score}%`, background: score >= 75 ? '#059669' : score >= 50 ? '#d97706' : '#dc2626' }} />
                        </div>
                        <span className="text-xs font-bold" style={{ color: score >= 75 ? '#047857' : score >= 50 ? '#b45309' : '#b91c1c' }}>{score}</span>
                      </div>
                    </td>
                    <td className="text-xs font-medium max-w-[140px]" style={{ color: 'var(--text-2)' }}>{block.keywords?.primary}</td>
                    <td>
                      <div className="flex items-center gap-1.5">
                        <button onClick={() => navigate('/page-preview', { state: { block, index: i, businessType: form.business_type, wpConfig } })}
                          className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold"
                          style={{ background: '#fff', border: '1px solid var(--brand)', color: 'var(--brand-dark)' }}>
                          <Eye size={11} /> View
                        </button>
                        {block.slug && (
                          <button onClick={() => handleDeleteSaved(block.slug)} disabled={deletingSlug === block.slug}
                            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold disabled:opacity-50"
                            style={{ background: '#fff', border: '1px solid #f87171', color: '#b91c1c' }}
                            title="Trash this location content">
                            <Trash2 size={11} /> {deletingSlug === block.slug ? '…' : 'Trash'}
                          </button>
                        )}
                        {wpConfig.wp_url && (
                          <button onClick={() => handlePublishSingle(block, i)}
                            disabled={pr === 'loading'}
                            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold disabled:opacity-50"
                            style={{
                              background: pr?.success ? '#ecfdf5' : pr?.error ? '#fef2f2' : '#fff',
                              border: `1px solid ${pr?.success ? '#6ee7b7' : pr?.error ? '#fecaca' : '#94a3b8'}`,
                              color: pr?.success ? '#047857' : pr?.error ? '#b91c1c' : '#0f172a',
                            }}>
                            <Upload size={11} />
                            {pr === 'loading' ? '...' : pr?.success ? 'Done' : pr?.error ? 'Err' : 'WP'}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
          </div>
        </div>
      )}

      {/* Saved / published location content — trash & restart */}
      {savedPages.length > 0 && (
        <div className="card p-4">
          <div className="flex items-center justify-between mb-3 gap-2 flex-wrap">
            <div>
              <h3 className="text-sm font-semibold text-white">Saved location content</h3>
              <p className="text-[11px] text-slate-500 mt-0.5">Trash pages you no longer need, then regenerate for new locations above.</p>
            </div>
            <button type="button" onClick={() => { setPages([]); showToast('Ready to generate fresh locations') }}
              className="text-xs px-3 py-1.5 rounded-lg bg-indigo-500/15 border border-indigo-500/25 text-indigo-200">
              Restart generation
            </button>
          </div>
          <div className="max-h-48 overflow-y-auto divide-y divide-white/5">
            {savedPages.slice(0, 40).map(p => (
              <div key={p.slug} className="flex items-center justify-between gap-2 py-2">
                <div className="min-w-0">
                  <div className="text-xs font-medium text-slate-200 truncate">
                    {p.city || p.seo_block?.city}{p.state || p.seo_block?.state ? `, ${p.state || p.seo_block?.state}` : ''}
                  </div>
                  <div className="text-[10px] text-slate-500 truncate">{p.slug}</div>
                </div>
                <button type="button" onClick={() => handleDeleteSaved(p.slug)} disabled={deletingSlug === p.slug}
                  className="flex items-center gap-1 px-2 py-1 rounded-md text-[11px] bg-red-500/10 border border-red-500/20 text-red-300 disabled:opacity-50">
                  <Trash2 size={10} /> Trash
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  )
}
