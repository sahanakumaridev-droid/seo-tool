import { useState, useRef, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, MapPin, Globe, Eye, X, RefreshCw, Save, CheckCircle, AlertTriangle,
         FileJson, Tag, Plus, Megaphone, Trash2, FileText, Newspaper, Sparkles, Wand2 } from 'lucide-react'
import { generateBulk, exportJson, generateSingle,
         saveEditedBlock, publishToWeb, startBulkGenerateJob, getJob, publishAllToWeb, zeorbitBlogUrl, zeorbitArticleUrl,
         getNearbyCities, getSanDiegoCounty, searchCities, getCounties, getPlaceCatalog, deletePage, listPages, suggestContentBrief } from '../api'
import axios from 'axios'
import LocationMap from '../components/LocationMap'

const BUSINESS_TYPES = [
  'Web Design', 'Website Redesign', 'Small Business Web Design', 'Small Business WordPress Web Design',
  'WordPress Development', 'WordPress Website Design',
  'eCommerce Development', 'Mobile App Development', 'iOS App Development', 'Android App Development',
  'App MVP Development', 'Nonprofit Website Design', 'SEO Agency',
  'Education', 'Tutoring', 'Online Courses',
  'Restaurant', 'Cafe', 'Catering',
  'Finance', 'Accounting',
  'Plumbing', 'HVAC', 'Roofing', 'Landscaping', 'Cleaning', 'Electrical', 'Painting', 'Pest Control', 'Moving',
]
const INDUSTRIES = [
  'Contractors', 'Healthcare', 'Retail', 'Restaurants',
  'Real Estate', 'Legal', 'Finance', 'Education', 'Nonprofit',
  'Technology', 'Home Services', 'Hospitality', 'Other',
]
const AUDIENCES = [
  'Small businesses', 'Startups', 'Local retailers', 'Healthcare practices',
  'Restaurants & hospitality', 'Nonprofits', 'Homeowners', 'Enterprise teams',
  'eCommerce brands', 'Service businesses',
]
const KW_SUGGESTIONS = ['web design san diego', 'affordable web design', 'small business website',
  'website designer near me', 'wordpress website san diego', 'custom website design',
  'website redesign', 'mobile app development san diego', 'ecommerce website developer']

function buildKeywordSuggestions({ niche, industry, city, contentKind }) {
  const cityPart = ((city || '').split(',')[0] || '').trim().toLowerCase()
  const nichePart = (niche || '').trim().toLowerCase() || 'website design'
  const indPart = (industry || '').trim().toLowerCase()
  const extras = []
  if (cityPart) {
    extras.push(
      `${nichePart} ${cityPart}`,
      `affordable ${nichePart} ${cityPart}`,
      `${nichePart} near me`,
      `wordpress website ${cityPart}`,
    )
    if (indPart) extras.push(`${indPart} website ${cityPart}`, `${indPart} web design ${cityPart}`)
  }
  if (contentKind === 'post') {
    extras.push('how to redesign a website', 'wordpress vs shopify', 'website cost for small business')
  }
  const seen = new Set()
  const out = []
  for (const s of [...KW_SUGGESTIONS, ...extras]) {
    const k = (s || '').trim().toLowerCase()
    if (!k || seen.has(k)) continue
    seen.add(k)
    out.push(k)
  }
  return out
}

/** Suggest an Industry list value from Business niche (editor can still override). */
function suggestIndustryFromNiche(niche) {
  const t = (niche || '').toLowerCase()
  if (!t.trim()) return ''
  if (/(plumb|hvac|roof|landscap|clean|electric|paint|pest|moving|contractor|remodel)/.test(t)) return 'Contractors'
  if (/(restaurant|cafe|catering|dining|food)/.test(t)) return 'Restaurants'
  if (/(health|dental|clinic|medical|doctor)/.test(t)) return 'Healthcare'
  if (/(real estate|realtor|property)/.test(t)) return 'Real Estate'
  if (/(legal|law|attorney|lawyer)/.test(t)) return 'Legal'
  if (/(financ|account|bank|invest|bookkeep)/.test(t)) return 'Finance'
  if (/(educat|tutor|school|course|university|college)/.test(t)) return 'Education'
  if (/(nonprofit|non-profit|charity)/.test(t)) return 'Nonprofit'
  if (/(retail|store|shop|ecommerce|e-commerce)/.test(t)) return 'Retail'
  if (/(hotel|hospitality|salon|spa|fitness)/.test(t)) return 'Hospitality'
  if (/(software|saas|tech|app|mobile)/.test(t)) return 'Technology'
  if (/(home service|handyman)/.test(t)) return 'Home Services'
  return ''
}

const SEARCH_INTENT_OPTIONS = [
  'Website discovery',
  'Affordable website',
  'WordPress',
  'Shopify',
  'Website redesign',
  'Lead generation',
  'New business',
  'Website vs mobile app',
  'Industry local',
]

const EMPTY_BRIEF = {
  topic_title: '',
  search_intent: '',
  customer_problem: '',
  pricing: '$500–$3,000',
  key_points: '',
  faq_ideas: '',
  cta_direction: '',
  tone_notes: '',
}

function composeBriefFromParts(briefFields, extraNotes) {
  const parts = []
  if (briefFields.topic_title?.trim()) parts.push(`Working title / topic: ${briefFields.topic_title.trim()}`)
  if (briefFields.search_intent?.trim()) parts.push(`Search intent: ${briefFields.search_intent.trim()}`)
  if (briefFields.customer_problem?.trim()) parts.push(`Customer problem: ${briefFields.customer_problem.trim()}`)
  if (briefFields.pricing?.trim()) parts.push(`Pricing: ${briefFields.pricing.trim()}`)
  if (briefFields.key_points?.trim()) parts.push(`Key points to cover:\n${briefFields.key_points.trim()}`)
  if (briefFields.faq_ideas?.trim()) parts.push(`FAQs to answer:\n${briefFields.faq_ideas.trim()}`)
  if (briefFields.cta_direction?.trim()) parts.push(`CTA direction: ${briefFields.cta_direction.trim()}`)
  if (briefFields.tone_notes?.trim()) parts.push(`Tone / voice notes: ${briefFields.tone_notes.trim()}`)
  if ((extraNotes || '').trim()) parts.push(`Extra editor notes:\n${extraNotes.trim()}`)
  return parts.join('\n\n').trim()
}

function briefHasSubstance(briefFields, extraNotes) {
  const composed = composeBriefFromParts(briefFields, extraNotes)
  return composed.length >= 8
}

const US_CITY_OPTIONS = [
  'San Diego, CA', 'Carlsbad, CA', 'Chula Vista, CA', 'Coronado, CA', 'Del Mar, CA',
  'El Cajon, CA', 'Encinitas, CA', 'Escondido, CA', 'Imperial Beach, CA', 'La Mesa, CA',
  'Lemon Grove, CA', 'National City, CA', 'Oceanside, CA', 'Poway, CA', 'San Marcos, CA',
  'Santee, CA', 'Solana Beach, CA', 'Vista, CA',
  'Spring Valley, CA', 'Lakeside, CA', 'Alpine, CA', 'Bonita, CA', 'Rancho San Diego, CA',
  'Casa de Oro, CA', 'La Presa, CA', 'Jamul, CA', 'Ramona, CA', 'San Ysidro, CA',
  'Otay Mesa, CA', 'Nestor, CA', 'Fallbrook, CA', 'Bonsall, CA', 'Valley Center, CA',
  'Julian, CA', 'Pine Valley, CA', 'Descanso, CA', 'Campo, CA', 'Boulevard, CA',
  'La Jolla, CA', 'Pacific Beach, CA', 'Mission Valley, CA',
  'Los Angeles, CA', 'San Francisco, CA', 'San Jose, CA', 'Sacramento, CA',
  'Oakland, CA', 'Fresno, CA', 'Long Beach, CA', 'Anaheim, CA', 'Riverside, CA',
  'Irvine, CA', 'Santa Ana, CA', 'Bakersfield, CA',
  'Phoenix, AZ', 'Tucson, AZ', 'Las Vegas, NV', 'Denver, CO', 'Seattle, WA',
  'Portland, OR', 'Austin, TX', 'Dallas, TX', 'Houston, TX', 'San Antonio, TX',
  'Chicago, IL', 'New York, NY', 'Miami, FL', 'Orlando, FL', 'Tampa, FL',
  'Atlanta, GA', 'Boston, MA', 'Philadelphia, PA', 'Washington, DC',
]

function locKey(value) {
  return (value || '').toLowerCase().replace(/\s+/g, ' ').trim()
}

function collectSdCatalog(sdCounty) {
  const areas = []
  const streets = []
  const pushCity = (city, parentLabel) => {
    const cityName = city?.name || parentLabel
    ;(city?.local_areas || []).forEach((name) => {
      areas.push({ name, city: cityName, kind: 'area' })
    })
    ;(city?.streets || []).forEach((name) => {
      streets.push({ name, city: cityName, kind: 'street' })
    })
    ;(city?.communities_with_streets || []).forEach((c) => {
      ;(c.streets || []).forEach((s) => {
        streets.push({ name: s, city: c.name || cityName, kind: 'street' })
      })
    })
  }
  ;(sdCounty?.cities || []).forEach((c) => pushCity(c, c.name))
  if (sdCounty?.unincorporated) pushCity(sdCounty.unincorporated, 'Unincorporated')
  return { areas, streets }
}

function placeChip(row) {
  if (row.kind === 'street') return `${row.name}, ${row.city}`
  return row.name
}

function splitLocations(raw) {
  const chunks = (raw || '').split(/[\n;]+/).flatMap((part) => {
    const tokens = part.split(',').map((t) => t.trim()).filter(Boolean)
    const out = []
    for (let i = 0; i < tokens.length; i += 1) {
      const name = tokens[i]
      const next = tokens[i + 1]
      if (next && /^[A-Za-z]{2}$/.test(next)) {
        out.push(`${name}, ${next.toUpperCase()}`)
        i += 1
      } else {
        out.push(name)
      }
    }
    return out
  })
  return chunks.filter(Boolean)
}

function AiFieldBtn({ busy, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={busy}
      className="inline-flex items-center gap-1 text-[10px] font-semibold px-1.5 py-0.5 rounded-md disabled:opacity-50"
      style={{ color: 'var(--brand-dark)', background: 'var(--brand-soft)', border: '1px solid var(--border)' }}
      title="Fill this field with AI (you can still edit)"
    >
      {busy ? <RefreshCw size={10} className="animate-spin" /> : <Wand2 size={10} />}
      AI
    </button>
  )
}

function BriefField({ label, hint, value, onChange, onAi, aiBusy, rows = 3, placeholder = '' }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5 gap-2">
        <label className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: 'var(--text-3)' }}>{label}</label>
        <AiFieldBtn busy={aiBusy} onClick={onAi} />
      </div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={rows}
        placeholder={placeholder || hint}
        className="w-full rounded-lg px-3 py-2 text-sm"
        style={{ background: '#fff', border: '1px solid var(--border-bright)', color: 'var(--text-1)', resize: 'vertical' }}
      />
      {hint ? <p className="mt-1 text-[10px] leading-relaxed" style={{ color: 'var(--text-4)' }}>{hint}</p> : null}
    </div>
  )
}

function SearchSelect({ label, required, value, onChange, options, placeholder, maxResults = 40, remoteSearch = null }) {
  const [open, setOpen] = useState(false)
  const [q, setQ] = useState('')
  const [remoteOpts, setRemoteOpts] = useState([])
  const query = (q || '').trim().toLowerCase()
  const localFiltered = (options || [])
    .filter((o) => !query || o.toLowerCase().includes(query))
    .slice(0, maxResults)
  // Merge remote US-city hits with local options (local first, then remote unique)
  const filtered = (() => {
    if (!remoteSearch) return localFiltered
    const seen = new Set(localFiltered.map((o) => locKey(o)))
    const extra = []
    for (const o of remoteOpts) {
      if (!seen.has(locKey(o))) {
        seen.add(locKey(o))
        extra.push(o)
      }
    }
    return [...localFiltered, ...extra].slice(0, maxResults)
  })()
  const exact = (options || []).some((o) => locKey(o) === locKey(value))
    || remoteOpts.some((o) => locKey(o) === locKey(value))
  const showCustom = Boolean((value || '').trim()) && !exact

  useEffect(() => {
    if (!remoteSearch || !open) return
    let cancelled = false
    const timer = setTimeout(async () => {
      try {
        const rows = await remoteSearch(q || value || '')
        if (!cancelled) setRemoteOpts(Array.isArray(rows) ? rows : [])
      } catch {
        if (!cancelled) setRemoteOpts([])
      }
    }, 220)
    return () => { cancelled = true; clearTimeout(timer) }
  }, [q, value, open, remoteSearch])

  return (
    <div style={{ position: 'relative' }}>
      <label className="block text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-3)' }}>
        {label}
        {required ? <span className="ml-2 text-[10px] font-bold uppercase px-1.5 py-0.5 rounded" style={{ background: 'var(--amber-soft)', color: 'var(--amber)' }}>Required</span> : null}
      </label>
      <input
        value={value}
        onChange={(e) => { onChange(e.target.value); setQ(e.target.value); setOpen(true) }}
        onFocus={() => { setQ(value || ''); setOpen(true) }}
        onBlur={() => setTimeout(() => setOpen(false), 160)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault()
            setOpen(false)
          }
        }}
        placeholder={placeholder}
        className="w-full rounded-lg px-3 py-2 text-sm"
        style={{ background: '#fff', border: '1px solid var(--border-bright)', color: 'var(--text-1)' }}
      />
      {open && (filtered.length > 0 || showCustom) && (
        <div className="absolute left-0 right-0 z-20 mt-1 rounded-lg overflow-hidden" style={{ background: '#fff', border: '1px solid var(--border)', boxShadow: 'var(--shadow-md)', maxHeight: 280, overflowY: 'auto' }}>
          {showCustom && (
            <button
              type="button"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => { setOpen(false) }}
              className="w-full text-left px-3 py-2 text-sm"
              style={{ color: 'var(--brand)', background: 'var(--brand-soft)' }}
            >
              Use “{(value || '').trim()}”
            </button>
          )}
          {filtered.map((opt) => (
            <button
              type="button"
              key={opt}
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => { onChange(opt); setQ(''); setOpen(false) }}
              className="w-full text-left px-3 py-2 text-sm"
              style={{ background: locKey(opt) === locKey(value) ? 'var(--brand-soft)' : 'transparent', color: 'var(--text-1)' }}
            >
              {opt}
            </button>
          ))}
        </div>
      )}
      <p className="mt-1 text-[10px]" style={{ color: 'var(--text-4)' }}>
        {remoteSearch
          ? 'Type to search 30,000+ US cities, or enter a custom place — both are saved.'
          : 'Search the list or type a custom value — both are saved.'}
      </p>
    </div>
  )
}

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
    Nonprofit: 'other',
    Technology: 'software',
    'Home Services': 'contractors',
    Hospitality: 'restaurant',
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
  // Web / app work is vertical-agnostic: "healthcare web design", "restaurant website", etc.
  if (a === 'web' || b === 'web' || a === 'software' || b === 'software') return true
  const set = FAMILY_COMPAT[a]
  return set ? set.has(b) : false
}

/**
 * Analyse Business Niche + Industry + Keywords for mismatched categories.
 * Returns { ok, message } — message is snackbar-ready when not ok.
 */
function analyzeCategoryAlignment(niche, industry, keywords = []) {
  // Industry / Audience is optional tone only — never block generate.
  return { ok: true, message: '' }
}

// ── Preview Modal ──────────────────────────────────────────────
function PreviewModal({ block, businessType, targetKeywords = [], onClose, onRegenerate }) {
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
    await saveEditedBlock(block, { businessType, applyGlobally: true })
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  const handlePublish = async () => {
    setPublishing(true)
    setPublishResult(null)
    try {
      const res = await publishToWeb(block)
      const url = zeorbitArticleUrl(res.data.public_url || res.data.slug)
      setPublishResult({ success: true, post_url: url })
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
            <h2 className="font-bold text-white text-base">{block.city}{block.state ? `, ${block.state}` : ''}{block.zip ? ` ${block.zip}` : ''}</h2>
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
            <button onClick={handlePublish} disabled={publishing}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-colors ${publishResult?.success ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-indigo-600/20 border border-indigo-600/30 text-indigo-300 hover:bg-indigo-600/30'} disabled:opacity-50`}>
              <Globe size={11} className={publishing ? 'animate-pulse' : ''} />
              {publishing ? 'Publishing...' : publishResult?.success ? 'Published!' : 'Publish to ZeOrbit'}
            </button>
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
                <ScoreBar label="Quality (need 90+)" value={Math.round(block.quality_score ?? block.readability_score ?? 0)} color="#1D4ED8" />
                <ScoreBar label="Keyword use (need 90+)" value={Math.min(100, Math.round(block.keyword_density || 0))} color="#2563EB" />
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

// ── Main Page ──────────────────────────────────────────────────
export default function ContentPage() {
  const DEFAULTS = { business_type: '', base_location: 'Chula Vista, CA', num_cities: 10, industry: '', audience: '' }
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
  const [pages, setPages] = useState([])
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
  const [jobProgress, setJobProgress] = useState(null)
  const [generateRequested, setGenerateRequested] = useState(0)
  const [publishResults, setPublishResults] = useState({})
  const [toast, setToast] = useState(null)
  const resultsRef = useRef(null)
  const [nearbyCities, setNearbyCities] = useState([])
  const [nearbyError, setNearbyError] = useState('')
  const [extraLocations, setExtraLocations] = useState([])
  const [extraLocDraft, setExtraLocDraft] = useState('')
  const [contentKind, setContentKind] = useState('') // mandatory: 'page' | 'post'
  const [customRequirements, setCustomRequirements] = useState('')
  const [briefFields, setBriefFields] = useState(() => ({ ...EMPTY_BRIEF }))
  const [briefAiBusy, setBriefAiBusy] = useState('') // '' | 'all' | field key
  const [showAdvancedBrief, setShowAdvancedBrief] = useState(true)
  const [sdCounty, setSdCounty] = useState(null)
  const [countyPick, setCountyPick] = useState('San Diego County')
  const [sdPick, setSdPick] = useState('Chula Vista')
  const [sdLayer, setSdLayer] = useState('areas')
  const [sdFilter, setSdFilter] = useState('')
  const [countyOptions, setCountyOptions] = useState([])

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), type === 'warning' ? 6500 : 4000)
  }

  // Keep only slugs in the tab — full articles live in the database.
  useEffect(() => {
    try { sessionStorage.removeItem('seo_pages') } catch { /* legacy dump */ }
  }, [])
  useEffect(() => {
    const slugs = pages.map((p) => p?.slug).filter(Boolean)
    try {
      sessionStorage.setItem('seo_page_slugs', JSON.stringify(slugs))
      if (generateRequested) sessionStorage.setItem('seo_generate_requested', String(generateRequested))
    } catch { /* slugs are tiny */ }
  }, [pages, generateRequested])
  useEffect(() => {
    try {
      sessionStorage.setItem('seo_keywords', JSON.stringify(targetKeywords))
    } catch { /* ignore */ }
  }, [targetKeywords])
  useEffect(() => {
    let cancelled = false
    const slugs = (() => {
      try {
        const raw = JSON.parse(sessionStorage.getItem('seo_page_slugs') || '[]')
        return Array.isArray(raw) ? raw.filter(Boolean).slice(0, 250) : []
      } catch { return [] }
    })()
    try {
      const n = Number(sessionStorage.getItem('seo_generate_requested') || 0)
      if (n > 0) setGenerateRequested(n)
    } catch { /* ignore */ }
    listPages(0, 250)
      .then((r) => {
        if (cancelled) return
        const rows = Array.isArray(r.data) ? r.data : []
        setSavedPages(rows)
        if (!slugs.length) return
        const bySlug = new Map(rows.map((row) => [row.slug, row.seo_block || row]))
        const restored = slugs.map((s) => bySlug.get(s)).filter(Boolean)
        if (restored.length) setPages(restored)
      })
      .catch(() => {})
    return () => { cancelled = true }
  }, [])
  useEffect(() => {
    getCounties('CA')
      .then((res) => setCountyOptions(res.data?.counties || []))
      .catch(() => setCountyOptions([]))
  }, [])
  useEffect(() => {
    const countyLabel = countyPick.includes(',') ? countyPick : `${countyPick}, CA`
    let cancelled = false
    const timer = setTimeout(() => {
      getPlaceCatalog({
        baseLocation: countyLabel,
        county: countyLabel,
        city: sdPick === 'All cities' || sdPick === 'Unincorporated' ? '' : sdPick,
      })
        .then((res) => {
          if (cancelled) return
          const data = res.data
          if (!data) return
          setSdCounty(data)
          const cities = data.incorporated_cities || []
          if (
            cities.length
            && sdPick !== 'All cities'
            && sdPick !== 'Unincorporated'
            && !cities.some((n) => locKey(n) === locKey(sdPick))
          ) {
            setSdPick('All cities')
          }
        })
        .catch(() => {
          if (!cancelled) setSdCounty((prev) => prev)
        })
    }, 280)
    return () => { cancelled = true; clearTimeout(timer) }
  }, [countyPick, sdPick])

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
    listPages(0, 250).then(r => setSavedPages(Array.isArray(r.data) ? r.data : [])).catch(() => {})
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
    sessionStorage.removeItem('seo_page_slugs')
    sessionStorage.removeItem('seo_generate_requested')
    showToast('Session results cleared — ready to regenerate')
  }

  // Location Expansion preview — nearby cities / counties / streets (Page + Blog)
  useEffect(() => {
    if (contentKind !== 'page' && contentKind !== 'post') {
      setNearbyCities([])
      setNearbyError('')
      return
    }
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
  }, [form.base_location, form.num_cities, contentKind])

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
        const finished = ['done', 'completed', 'partial', 'failed'].includes(data.status)
          || (data.completed + data.failed) >= data.total
        if (finished) {
          const raw = (data.results || []).filter(r => r && !r.error)
          const failN = data.failed || 0
          const requested = data.total || generateRequested || raw.length
          setPages(raw)
          setLoading(false)
          setAsyncJobId('')
          setJobProgress(null)
          if (!raw.length) {
            setError('Generation finished with no results. Try again.')
            showToast('Nothing generated — try again', 'warning')
          } else if (raw.length < requested || failN > 0) {
            setError(`${raw.length} of ${requested} generated. ${failN || (requested - raw.length)} did not complete.`)
            showToast(`${raw.length} of ${requested} pages generated`, 'warning')
          } else {
            setError('')
            showToast(`${raw.length} of ${requested} ${contentKind === 'post' ? 'posts' : 'pages'} generated`)
          }
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
    const k = (kw || kwInput).trim()
    if (!k) return
    setTargetKeywords((prev) => (prev.some((x) => locKey(x) === locKey(k)) ? prev : [...prev, k]))
    if (!kw) setKwInput('')
  }
  const removeKeyword = (kw) => {
    const k = (kw || '').trim().toLowerCase()
    setTargetKeywords((prev) => prev.filter((x) => x !== k))
  }
  const toggleKeyword = (kw) => {
    const k = (kw || '').trim().toLowerCase()
    if (!k) return
    setTargetKeywords((prev) => (prev.includes(k) ? prev.filter((x) => x !== k) : [...prev, k]))
  }
  const keywordSuggestions = useMemo(
    () => buildKeywordSuggestions({
      niche: form.business_type,
      industry: form.industry,
      city: form.base_location,
      contentKind,
    }),
    [form.business_type, form.industry, form.base_location, contentKind],
  )

  const sdCityNames = sdCounty?.incorporated_cities || []
  const sdCatalog = useMemo(() => collectSdCatalog(sdCounty), [sdCounty])
  const baseCityOptions = useMemo(() => {
    const sd = (sdCityNames || []).map((n) => (n.includes(',') ? n : `${n}, CA`))
    // Also surface major SD communities as base-city choices
    const areas = (sdCatalog.areas || [])
      .map((r) => r.name)
      .filter(Boolean)
      .slice(0, 80)
      .map((n) => (n.includes(',') ? n : `${n}, CA`))
    const merged = []
    const seen = new Set()
    for (const c of [...sd, ...US_CITY_OPTIONS, ...areas]) {
      const k = locKey(c)
      if (!k || seen.has(k)) continue
      seen.add(k)
      merged.push(c)
    }
    return merged
  }, [sdCityNames, sdCatalog.areas])
  const fetchCityOptions = async (q) => {
    try {
      const res = await searchCities(q || '', 50)
      return res.data?.cities || []
    } catch {
      return []
    }
  }
  const sdSearch = locKey(sdFilter)
  const sdCityChipRows = useMemo(() => {
    const names = sdCityNames.length
      ? sdCityNames
      : [...new Set(sdCatalog.areas.map((r) => r.city).filter(Boolean))]
    return names.map((name) => ({ name, city: name, kind: 'city' }))
  }, [sdCityNames, sdCatalog.areas])
  const sdMatches = useMemo(() => {
    let pool
    if (sdLayer === 'streets') pool = sdCatalog.streets
    else if (sdLayer === 'cities') pool = sdCityChipRows
    else pool = sdCatalog.areas
    let rows = pool
    // Keep city scope when a city is selected — searching must not jump county-wide.
    if (sdLayer !== 'cities' && sdPick && sdPick !== 'All cities' && sdPick !== 'Unincorporated') {
      rows = pool.filter((r) => locKey(r.city) === locKey(sdPick))
    } else if (sdPick === 'Unincorporated' && sdLayer !== 'cities') {
      rows = pool.filter((r) => locKey(r.city) === 'unincorporated' || locKey(r.city).includes('unincorporated'))
    }
    if (sdSearch) {
      rows = rows.filter(
        (r) =>
          locKey(r.name).includes(sdSearch) ||
          locKey(r.city).includes(sdSearch) ||
          locKey(placeChip(r)).includes(sdSearch),
      )
    }
    return rows
  }, [sdCatalog, sdCityChipRows, sdLayer, sdPick, sdSearch])
  const sdItems = sdMatches.map(placeChip)

  const addSdItems = (names) => {
    addExtraLocation(names.join('\n'))
  }
  const addExtraLocation = (raw) => {
    const parts = splitLocations(raw || extraLocDraft)
    if (!parts.length) return
    setExtraLocations((prev) => {
      const next = [...prev]
      parts.forEach((loc) => {
        if (!next.some((x) => locKey(x) === locKey(loc))) next.push(loc)
      })
      return next
    })
    setExtraLocDraft('')
  }
  const removeExtraLocation = (loc) => setExtraLocations(prev => prev.filter(x => locKey(x) !== locKey(loc)))

  const updateBriefField = (key, value) => {
    setBriefFields((prev) => ({ ...prev, [key]: value }))
  }

  const handleSuggestBrief = async (field = 'all', overrides = {}) => {
    setBriefAiBusy(field === 'all' || field === 'ready90' ? (field === 'ready90' ? 'ready90' : 'all') : field)
    setError('')
    try {
      const kind = overrides.contentKind || contentKind || 'page'
      const niche = overrides.business_type ?? form.business_type ?? ''
      const industry = overrides.industry ?? form.industry ?? ''
      const audience = overrides.audience ?? form.audience ?? ''
      const baseLoc = overrides.base_location ?? form.base_location ?? ''
      const kws = overrides.target_keywords ?? targetKeywords
      const briefIn = overrides.briefFields ?? briefFields
      const res = await suggestContentBrief({
        content_kind: kind,
        business_type: niche || '',
        industry: industry || '',
        audience: audience || '',
        base_location: baseLoc || '',
        target_keywords: kws,
        ...briefIn,
        extra_notes: customRequirements,
        field: field === 'ready90' ? 'all' : field,
        llm_provider: llmProvider || null,
      })
      const data = res.data || {}
      setBriefFields((prev) => {
        const next = { ...prev }
        const keys = ['topic_title', 'search_intent', 'customer_problem', 'pricing', 'key_points', 'faq_ideas', 'cta_direction', 'tone_notes']
        keys.forEach((k) => {
          if (field !== 'all' && field !== 'ready90' && field !== k) return
          if (data[k]) next[k] = data[k]
        })
        if (!(next.pricing || '').trim()) next.pricing = '$500–$3,000'
        return next
      })
      showToast(data.source === 'ai' ? 'AI filled the brief fields — edit anything manually' : 'Template brief filled — edit anything manually')
      return data
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Could not suggest brief fields. You can still type them manually.')
      showToast('Brief AI failed — type fields manually', 'warning')
      return null
    } finally {
      setBriefAiBusy('')
    }
  }

  /** Fill missing keyword / niche / location defaults so Generate can run. */
  const handleAiFillFor90 = async () => {
    setBriefAiBusy('ready90')
    setError('')
    try {
      const kind = contentKind || 'page'
      if (!contentKind) setContentKind('page')

      const niche = (form.business_type || '').trim() || 'Web Design'
      const baseLoc = (form.base_location || '').trim() || 'San Diego, CA'
      const numCities = form.num_cities >= 1 ? form.num_cities : 5
      const industry = (form.industry || '').trim() || suggestIndustryFromNiche(niche)

      setForm((f) => ({
        ...f,
        business_type: niche,
        industry,
        audience: f.audience || '',
        base_location: baseLoc,
        num_cities: numCities,
      }))

      let kws = [...targetKeywords]
      if (!kws.length) {
        const suggestions = buildKeywordSuggestions({
          niche,
          industry,
          city: baseLoc,
          contentKind: kind,
        })
        kws = suggestions.slice(0, 3)
        setTargetKeywords(kws)
      }

      setUseAi(true)
      showToast('Defaults set — Generate will fill the brief in the backend', 'success')
      document.getElementById('target-keywords-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    } catch (err) {
      setError(err.message || 'Could not set defaults')
      showToast('Fill failed', 'warning')
    } finally {
      setBriefAiBusy('')
    }
  }

  const getGenerateBlockers = () => {
    const missing = []
    if (contentKind !== 'page' && contentKind !== 'post') {
      missing.push('Select Page or Post / Blog')
    }
    if (contentKind === 'page') {
      if (!(form.business_type || '').trim()) missing.push('Business Niche')
      if (!targetKeywords.length) missing.push('At least one Target Keyword')
      if (!extraLocations.length && !(form.base_location || '').trim()) {
        missing.push('Base city')
      }
      if (!(form.num_cities >= 1)) {
        missing.push('How many locations')
      }
    }
    if (contentKind === 'post') {
      if (!targetKeywords.length) missing.push('At least one Target Keyword')
      // Niche and location are optional for blog — keyword is the article subject
    }
    return missing
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    const blockers = getGenerateBlockers()
    if (blockers.length) {
      const msg = `Add: ${blockers.join('; ')}. Brief fields are managed in the backend.`
      setError(msg)
      showToast('Add keyword, niche, and location', 'warning')
      const scrollId = !contentKind ? 'content-kind-section'
        : !targetKeywords.length ? 'target-keywords-section'
          : !(form.business_type || '').trim() ? 'business-niche-section'
            : 'target-locations-panel'
      document.getElementById(scrollId)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      return
    }

    setLoading(true)
    setError('')
    setUseAi(true)

    const niche = (form.business_type || '').trim()
    const hasBlogLocations = contentKind === 'post' && (
      !!(form.base_location || '').trim() || extraLocations.length > 0
    )
    // Page always uses locations. Blog uses them only when base/chips are set.
    const useLocations = contentKind === 'page' || hasBlogLocations
    const pageCount = useLocations
      ? Math.max(Number(form.num_cities) || 1, extraLocations.length || 0, 1)
      : 1
    setGenerateRequested(pageCount)
    // Auto async for large batches
    const runAsync = useAsync || pageCount >= 20
    setPublishResults({})
    setAsyncJobId('')
    try {
      const payload = {
        ...form,
        business_type: niche || (contentKind === 'post' ? 'Digital Services' : niche),
        industry: (() => {
          const raw = (form.industry || '').trim()
          if (!raw || raw.toLowerCase() === 'professional services') {
            return suggestIndustryFromNiche(niche) || ''
          }
          return raw
        })(),
        audience: (form.audience || '').trim(),
        num_cities: pageCount,
        base_location: useLocations ? (form.base_location || '') : '',
        target_keywords: targetKeywords.length
          ? [...targetKeywords]
          : ['website design'],
        // Manual chips first; backend fills remaining from base location
        extra_locations: useLocations ? [...extraLocations] : [],
        content_kind: contentKind,
        custom_requirements: (() => {
          const composed = composeBriefFromParts(briefFields, customRequirements)
          if (composed) return composed
          if (contentKind === 'post' && targetKeywords[0]) {
            return `Write the full post to answer this query: ${targetKeywords[0]}`
          }
          return ''
        })(),
        use_ai: true,
        llm_provider: llmProvider || null,
      }
      if (runAsync) {
        const res = await startBulkGenerateJob(payload)
        setAsyncJobId(res.data.job_id)
        setGenerateRequested(res.data.total || pageCount)
        const existing = JSON.parse(localStorage.getItem('seo_jobs') || '[]')
        localStorage.setItem('seo_jobs', JSON.stringify([res.data.job_id, ...existing]))
        showToast(`Async job started — ID: ${res.data.job_id.slice(0, 8)}...`)
      } else {
        const res = await generateBulk(payload)
        const raw = res.data.pages || []
        const requested = res.data.requested || pageCount
        setGenerateRequested(requested)
        setPages(raw)
        if (!raw.length) {
          setError('Generation produced no results. Try again.')
          showToast('Nothing generated — try again', 'warning')
        } else if (raw.length < requested || res.data.dropped) {
          setError(`${raw.length} of ${requested} generated${res.data.message ? ` — ${res.data.message}` : ''}`)
          showToast(`${raw.length} of ${requested} pages generated`, 'warning')
        } else if (res.data.message) {
          setError('')
          showToast(res.data.message, 'success')
        } else {
          setError('')
          showToast(`${raw.length} of ${requested} ${contentKind === 'post' ? 'posts' : 'pages'} generated`)
        }
        setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100)
      }
    } catch (err) {
      const detail = err.response?.data?.detail
      const detailText = Array.isArray(detail)
        ? detail.map((d) => d.msg || d).join(' ')
        : (typeof detail === 'string' ? detail : '')
      setError(
        detailText
        || (err.code === 'ERR_NETWORK'
            ? 'Cannot reach the backend. Start it with: uvicorn main:app --port 8000'
            : `Generation failed${err.message ? ` — ${err.message}` : ''}. Please try again.`)
      )
    } finally { setLoading(false) }
  }

  const handleExport = async () => {
    if (!pages.length) return
    setExporting('json')
    try {
      const res = await exportJson({ ...form, num_cities: pages.length })
      const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${form.business_type.toLowerCase() || 'seo'}-pages.json`
      a.click()
      URL.revokeObjectURL(url)
    } finally { setExporting('') }
  }

  const handlePublishSingle = async (block, index) => {
    setPublishResults(r => ({ ...r, [index]: 'loading' }))
    try {
      const res = await publishToWeb(block)
      setPublishResults(r => ({ ...r, [index]: { success: true, post_url: zeorbitArticleUrl(res.data.public_url || res.data.slug) } }))
    } catch (e) {
      setPublishResults(r => ({ ...r, [index]: { success: false, error: e.response?.data?.detail || e.message } }))
    }
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
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <p className="crm-crumb">SEO Content &gt; Content Generation</p>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-1)' }}>Content Generation</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>
            Choose Page or Post first — each uses its own workflow and sitemap.
          </p>
        </div>
      </div>
      <div className="crm-stepper" aria-label="Generation steps">
        {[
          ['1', 'Page or Post', !!contentKind],
          ['2', 'Keywords', targetKeywords.length > 0],
          ['3', contentKind === 'post' ? 'Niche (+ location optional)' : 'Niche + location', !!contentKind && (
            contentKind === 'post'
              ? !!(form.business_type || '').trim()
              : (!!(form.business_type || '').trim() && (!!extraLocations.length || !!(form.base_location || '').trim()))
          )],
          ['4', 'Generate', pages.length > 0],
        ].map(([n, label, on]) => (
          <span key={label} className={`crm-step${on ? ' is-on' : ''}`}><b>{n}</b> {label}</span>
        ))}
      </div>

      <div id="content-kind-section" className="grid sm:grid-cols-2 gap-3">
        <button
          type="button"
          aria-pressed={contentKind === 'page'}
          onClick={() => {
            setContentKind('page')
            // keep location chips for pages
          }}
          className="kind-card text-left"
          data-active={contentKind === 'page' ? 'true' : 'false'}
        >
          <div className="flex items-center gap-2 mb-1.5">
            <FileText size={16} />
            <span className="text-sm font-semibold">Page</span>
            <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded" style={{ background: 'var(--brand-soft)', color: 'var(--brand-dark)' }}>Required pick</span>
          </div>
          <p className="text-xs" style={{ color: 'var(--text-3)' }}>
            Service and location pages. Goes to <strong>page-sitemap.xml</strong>.
          </p>
        </button>
        <button
          type="button"
          aria-pressed={contentKind === 'post'}
          onClick={() => {
            setContentKind('post')
            // Keep base location + pinned cities/streets/areas (same picker as Page)
            if (!(form.num_cities >= 1)) {
              updateForm((f) => ({ ...f, num_cities: 1 }))
            }
          }}
          className="kind-card text-left"
          data-active={contentKind === 'post' ? 'true' : 'false'}
        >
          <div className="flex items-center gap-2 mb-1.5">
            <Newspaper size={16} />
            <span className="text-sm font-semibold">Post / Blog</span>
            <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded" style={{ background: 'var(--brand-soft)', color: 'var(--brand-dark)' }}>Required pick</span>
          </div>
          <p className="text-xs" style={{ color: 'var(--text-3)' }}>
            How-to articles from your keyword. Optional: base location, cities, streets, counties. Goes to <strong>post-sitemap.xml</strong>.
          </p>
        </button>
      </div>
      {!contentKind && (
        <p className="text-xs" style={{ color: 'var(--amber)' }}>Select Page or Post / Blog to open the matching generator.</p>
      )}

      {contentKind === 'page' && (
      <div
        id="target-keywords-section"
        className="card p-5"
        style={targetKeywords.length
          ? { borderColor: 'rgba(91,92,230,0.25)' }
          : { borderColor: 'var(--amber)', boxShadow: '0 0 0 1px var(--amber-soft)' }}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <Tag size={15} style={{ color: 'var(--brand)' }} />
            <span className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>Target Keywords</span>
            <span
              className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded"
              style={{ background: 'var(--amber-soft)', color: 'var(--amber)', border: '1px solid rgba(180,83,9,0.35)' }}
            >
              Required
            </span>
            <span className="text-xs" style={{ color: 'var(--text-4)' }}>— woven into every generated page</span>
          </div>
          {targetKeywords.length > 0 && (
            <button
              onClick={() => setTargetKeywords([])}
              className="text-xs transition-colors"
              style={{ color: 'var(--text-4)' }}
              onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--red)' }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-4)' }}
            >
              Clear all
            </button>
          )}
        </div>
        {!targetKeywords.length && (
          <div
            className="mb-3 text-xs font-semibold rounded-lg px-3 py-2.5"
            style={{
              color: '#92400e',
              background: 'rgba(245, 158, 11, 0.12)',
              border: '1px solid rgba(180, 83, 9, 0.35)',
            }}
          >
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
            className="flex-1 rounded-lg px-4 py-2.5 text-sm"
            style={{
              background: '#fff',
              border: `1px solid ${targetKeywords.length ? 'var(--border-bright)' : 'var(--amber)'}`,
              color: 'var(--text-1)',
            }}
          />
          <button type="button" onClick={() => addKeyword()}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-medium"
            style={{ background: 'var(--brand-soft)', color: 'var(--brand-dark)', border: '1px solid var(--border)' }}>
            <Plus size={14} /> Add
          </button>
        </div>
        {targetKeywords.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {targetKeywords.map(kw => (
              <span
                key={kw}
                className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg font-medium"
                style={{ background: 'var(--brand-soft)', color: 'var(--brand-dark)', border: '1px solid rgba(91,92,230,0.25)' }}
              >
                {kw}
                <button onClick={() => removeKeyword(kw)} style={{ color: 'inherit' }}><X size={10} /></button>
              </span>
            ))}
          </div>
        )}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs" style={{ color: 'var(--text-4)' }}>Suggestions (click to select — used in generation):</span>
          {keywordSuggestions.map((s) => {
            const on = targetKeywords.includes(s)
            return (
              <button
                key={s}
                type="button"
                onClick={() => toggleKeyword(s)}
                aria-pressed={on}
                className="text-xs px-2.5 py-1 rounded-lg border transition-colors"
                style={on
                  ? { background: 'var(--brand-soft)', borderColor: 'var(--brand)', color: 'var(--brand-dark)', fontWeight: 600 }
                  : { background: '#fff', borderColor: 'var(--border)', color: 'var(--text-3)' }}
              >
                {on ? '✓ ' : '+ '}{s}
            </button>
            )
          })}
        </div>
      </div>
      )}

      {contentKind === 'post' && (
        <div id="target-keywords-section" className="card p-5"
          style={targetKeywords.length
            ? { borderColor: 'rgba(91,92,230,0.25)' }
            : { borderColor: 'var(--amber)', boxShadow: '0 0 0 1px var(--amber-soft)' }}
        >
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            <Tag size={15} style={{ color: 'var(--brand)' }} />
            <span className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>Target Keywords</span>
            <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded" style={{ background: 'var(--amber-soft)', color: 'var(--amber)' }}>Required</span>
            <span className="text-xs" style={{ color: 'var(--text-4)' }}>— body is written from this query only</span>
          </div>
          {!targetKeywords.length && (
            <div className="mb-3 text-xs font-semibold rounded-lg px-3 py-2.5" style={{ color: '#92400e', background: 'rgba(245, 158, 11, 0.12)', border: '1px solid rgba(180, 83, 9, 0.35)' }}>
              Add the search query (e.g. how to fix a website). Title, H1, and body follow that query.
            </div>
          )}
          <div className="flex gap-2 mb-3">
            <input type="text" value={kwInput}
              onChange={e => setKwInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addKeyword() } }}
              placeholder="e.g. how to fix a website — press Enter to add"
              className="flex-1 rounded-lg px-4 py-2.5 text-sm"
              style={{ background: '#fff', border: `1px solid ${targetKeywords.length ? 'var(--border-bright)' : 'var(--amber)'}`, color: 'var(--text-1)' }} />
            <button type="button" onClick={() => addKeyword()}
              className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-medium"
              style={{ background: 'var(--brand-soft)', color: 'var(--brand-dark)', border: '1px solid var(--border)' }}>
              <Plus size={14} /> Add
            </button>
          </div>
          {targetKeywords.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {targetKeywords.map(kw => (
                <span key={kw} className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg font-medium" style={{ background: 'var(--brand-soft)', color: 'var(--brand-dark)' }}>
                  {kw}
                  <button type="button" onClick={() => removeKeyword(kw)}><X size={10} /></button>
                </span>
              ))}
            </div>
          )}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs" style={{ color: 'var(--text-4)' }}>Suggestions:</span>
            {keywordSuggestions.map((s) => {
              const on = targetKeywords.includes(s)
              return (
                <button
                  key={`post-${s}`}
                  type="button"
                  onClick={() => toggleKeyword(s)}
                  aria-pressed={on}
                  className="text-xs px-2.5 py-1 rounded-lg border transition-colors"
                  style={on
                    ? { background: 'var(--brand-soft)', borderColor: 'var(--brand)', color: 'var(--brand-dark)', fontWeight: 600 }
                    : { background: '#fff', borderColor: 'var(--border)', color: 'var(--text-3)' }}
                >
                  {on ? '✓ ' : '+ '}{s}
                </button>
              )
            })}
          </div>
        </div>
      )}

      {contentKind && (
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="card p-5">
          <h3 className="text-sm font-semibold mb-1 flex items-center gap-2" style={{ color: 'var(--text-1)' }}>
            <Zap size={14} style={{ color: 'var(--brand)' }} />
            {contentKind === 'post' ? 'Blog — AI automation' : 'Location pages — AI automation'}
          </h3>
          <p className="text-[11px] mb-4" style={{ color: 'var(--text-4)' }}>
            {contentKind === 'post'
              ? 'Keyword + niche + industry required. Base location, cities, streets, and counties are optional.'
              : 'Type keyword + niche + industry + base location. Pick cities, streets, and counties — then generate.'}
          </p>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div id="business-niche-section" className="space-y-3">
              <SearchSelect
                label="Business niche / category"
                required
                value={form.business_type}
                onChange={(v) => updateForm((f) => {
                  const next = { ...f, business_type: v }
                  // Soft-fill Industry from niche when empty or still the old catch-all
                  const curInd = (f.industry || '').trim()
                  if (!curInd || curInd.toLowerCase() === 'professional services') {
                    const suggested = suggestIndustryFromNiche(v)
                    if (suggested) next.industry = suggested
                  }
                  return next
                })}
                options={BUSINESS_TYPES}
                placeholder="e.g. Web Design, WordPress, Mobile Apps…"
              />
              <SearchSelect
                label="Industry"
                required={false}
                value={form.industry}
                onChange={(v) => updateForm((f) => ({
                  ...f,
                  industry: (v || '').trim().toLowerCase() === 'professional services' ? '' : v,
                }))}
                options={INDUSTRIES}
                placeholder="Pick from list or type — e.g. Contractors, Healthcare…"
              />
              <p className="text-[10px] -mt-1" style={{ color: 'var(--text-4)' }}>
                Who the content is for (buyer vertical). Used in titles/examples — not forced into the slug as “Professional Services”.
              </p>
            </div>
            <div>
              <SearchSelect
                label="Base location"
                required={contentKind === 'page'}
                value={form.base_location}
                onChange={(v) => updateForm((f) => ({ ...f, base_location: v }))}
                options={baseCityOptions}
                remoteSearch={fetchCityOptions}
                maxResults={50}
                placeholder={contentKind === 'post'
                  ? 'Optional — e.g. Chula Vista, CA'
                  : 'City, ZIP, county, or area — e.g. Chula Vista, CA or 91910'}
              />
              <p className="text-[10px] mt-1" style={{ color: 'var(--text-4)' }}>
                {contentKind === 'post'
                  ? 'Optional for blog. Leave blank for a national topic post, or set a base to expand cities / streets / counties.'
                  : 'Starting point for expansion: cities, ZIP codes, streets, and counties nearby.'}
              </p>
              {nearbyError && (
                <div className="mt-1.5 text-[10px]" style={{ color: 'var(--red)' }}>{nearbyError}</div>
              )}
              <div className="mt-3">
                <div className="flex justify-between items-center mb-2">
                  <label className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-3)' }}>
                    How many locations
                  </label>
                  <span className="text-sm font-bold" style={{ color: 'var(--brand)' }}>
                    {form.num_cities}
                    {extraLocations.length > 0 ? ` · ${extraLocations.length} chips` : ''}
                  </span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="250"
                  value={Math.min(250, Math.max(1, form.num_cities))}
                  onChange={(e) => updateForm((f) => ({ ...f, num_cities: Number(e.target.value) }))}
                  className="w-full accent-indigo-500"
                />
              </div>
            </div>
            {error && (
              <div
                className="rounded-xl p-3 flex gap-2"
                style={{ background: '#FEF2F2', border: '1px solid #FECACA' }}
              >
                <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" style={{ color: '#B91C1C' }} />
                <p className="text-[13px] font-medium" style={{ color: '#7F1D1D' }}>{error}</p>
              </div>
            )}

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
                    Generating… {done} / {total}
                  </div>
                  <p className="text-[11px] text-center px-3" style={{ color: 'var(--text-3)' }}>
                    If a location scores below 90%, it is generated again immediately.
                  </p>
                </div>
              )
            })()}

            <button
              type="submit"
              disabled={
                loading || !!asyncJobId
                || !(form.business_type || '').trim()
                || !targetKeywords.length
                || (contentKind === 'page' && !(form.base_location || '').trim())
              }
              className="btn-primary w-full py-2.5 rounded-lg text-white text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-60"
            >
              {loading || asyncJobId
                ? <><svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.2)" strokeWidth="3"/><path d="M12 2a10 10 0 0 1 10 10" stroke="white" strokeWidth="3" strokeLinecap="round"/></svg>Generating…</>
                : <><Zap size={14} />{
                  contentKind === 'post'
                    ? ((form.base_location || '').trim() || extraLocations.length
                      ? `Generate ${form.num_cities || 1} posts`
                      : 'Generate post')
                    : `Generate ${form.num_cities || 1} pages`
                }</>}
            </button>
            <p className="text-[10px] text-center" style={{ color: 'var(--text-3)' }}>
              Backend fills intent, problem, pricing, FAQs, and tone. Locations below 90% are generated again right away until they pass — then all results are shown.
            </p>
          </form>
        </div>

        <div id="target-locations-panel" className="card p-5 lg:col-span-2">
          <h4 className="text-sm font-semibold mb-1 flex items-center justify-between gap-2" style={{ color: 'var(--text-1)' }}>
            <span className="inline-flex items-center gap-2">
              <Globe size={14} style={{ color: 'var(--brand)' }} />
              Locations — cities, streets &amp; counties
            </span>
            {extraLocations.length > 0 && (
              <span className="inline-flex gap-2">
                <button type="button" className="text-[11px]" style={{ color: 'var(--brand)' }}
                  onClick={() => navigator.clipboard.writeText(extraLocations.join(', '))}>Copy</button>
                <button type="button" className="text-[11px]" style={{ color: 'var(--red)' }}
                  onClick={() => setExtraLocations([])}>Clear</button>
              </span>
            )}
          </h4>
          <p className="text-[12px] mb-3 leading-relaxed" style={{ color: 'var(--text-4)' }}>
            {contentKind === 'post'
              ? <>Locations are <strong>optional</strong> for blog. Set a base and pin <strong>cities</strong>, <strong>streets</strong>, or <strong>counties</strong> only if you want place-tied posts. Otherwise leave blank — body still follows your keyword query.</>
              : <>Pick a <strong>county</strong> (all 58 in California), then a city. Switching county reloads <strong>local areas</strong> and <strong>streets</strong> for that county only.</>}
          </p>
          <div className="flex flex-col gap-2 mb-3">
            <div className="flex flex-col sm:flex-row gap-1.5">
              <select
                value={countyPick}
                onChange={(e) => {
                  const v = e.target.value
                  setCountyPick(v)
                  setSdPick('All cities')
                  setSdFilter('')
                  updateForm((f) => ({ ...f, base_location: `${v}, CA` }))
                }}
                className="flex-1 bg-white border rounded-lg px-3 py-2 text-sm"
                style={{ borderColor: 'var(--border)', color: 'var(--text-1)' }}
                aria-label="County"
              >
                {(countyOptions.length ? countyOptions : [{ name: 'San Diego County' }]).map((c) => (
                  <option key={c.name} value={c.name}>{c.name}</option>
                ))}
              </select>
              <select
                value={sdPick}
                onChange={(e) => {
                  const v = e.target.value
                  setSdPick(v)
                  setSdFilter('')
                  updateForm((f) => ({
                    ...f,
                    base_location: v === 'Unincorporated' || v === 'All cities'
                      ? `${countyPick}, CA`
                      : `${v}, CA`,
                  }))
                }}
                className="flex-1 bg-white border rounded-lg px-3 py-2 text-sm"
                style={{ borderColor: 'var(--border)', color: 'var(--text-1)' }}
                aria-label="City in county"
              >
                <option value="All cities">All cities in {countyPick.replace(/ County$/i, '')}</option>
                {sdCityNames.map((n) => <option key={n} value={n}>{n}</option>)}
                <option value="Unincorporated">Unincorporated</option>
              </select>
              <div className="crm-seg" role="tablist" aria-label="Cities, local areas, or streets">
                <button type="button" aria-pressed={sdLayer === 'cities'} onClick={() => { setSdLayer('cities'); setSdFilter('') }}>Cities</button>
                <button type="button" aria-pressed={sdLayer === 'areas'} onClick={() => { setSdLayer('areas'); setSdFilter('') }}>Local areas</button>
                <button type="button" aria-pressed={sdLayer === 'streets'} onClick={() => { setSdLayer('streets'); setSdFilter('') }}>Streets</button>
              </div>
            </div>
            <div className="flex gap-1.5">
              <input
                type="search"
                value={sdFilter}
                onChange={(e) => setSdFilter(e.target.value)}
                placeholder={
                  sdLayer === 'streets'
                    ? 'Search any street…'
                    : sdLayer === 'cities'
                      ? 'Search any city…'
                      : 'Search any community / locality…'
                }
                className="flex-1 bg-white border rounded-lg px-3 py-2 text-sm"
                style={{ borderColor: 'var(--border)', color: 'var(--text-1)' }}
              />
              <button
                type="button"
                disabled={!sdItems.length}
                onClick={() => addSdItems(sdItems)}
                className="px-3 py-2 rounded-lg text-xs font-semibold text-white flex-shrink-0 disabled:opacity-50"
                style={{ background: 'var(--brand, #4f46e5)' }}
              >
                Add all {sdItems.length}
              </button>
            </div>
            <p className="text-[10px]" style={{ color: 'var(--text-3)' }}>
              Showing {sdLayer === 'streets' ? 'streets' : sdLayer === 'cities' ? 'cities' : 'local areas'} in <strong>{countyPick}</strong>
              {sdPick && sdPick !== 'All cities' ? <> · {sdPick}</> : null}
            </p>
            <div className="flex flex-wrap gap-1 max-h-28 overflow-y-auto" key={`${countyPick}-${sdPick}-${sdLayer}`}>
              {sdItems.slice(0, 80).map((name, i) => (
                <button
                  key={`${sdLayer}-${name}-${i}`}
                  type="button"
                  onClick={() => addExtraLocation(name)}
                  className="text-[11px] px-2 py-0.5 rounded font-medium"
                  style={{
                    background: extraLocations.some((x) => locKey(x) === locKey(name)) ? '#ecfdf5' : '#fff',
                    border: '1px solid var(--border)',
                    color: 'var(--text-2)',
                  }}
                >
                  {name}
                </button>
              ))}
              {sdItems.length > 80 && (
                <span className="text-[11px]" style={{ color: 'var(--text-4)' }}>+{sdItems.length - 80} more</span>
              )}
            </div>
            <div className="flex gap-1.5">
              <input type="text" value={extraLocDraft}
                onChange={e => setExtraLocDraft(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addExtraLocation() } }}
                placeholder="Or type / paste City, State, ZIP (e.g. 91910) and press Add"
                className="flex-1 bg-white border rounded-lg px-3 py-2 text-sm"
                style={{ borderColor: 'var(--border)', color: 'var(--text-1)' }} />
              <button type="button" onClick={() => addExtraLocation()}
                className="px-3 py-2 rounded-lg text-xs font-semibold text-white flex-shrink-0"
                style={{ background: 'var(--brand, #4f46e5)' }}>
                Add
              </button>
            </div>
          </div>
          {extraLocations.length > 0 && (
            <div className="mb-3">
              <p className="text-[10px] font-semibold uppercase tracking-wider mb-1.5" style={{ color: 'var(--text-3)' }}>
                Pinned for generate ({extraLocations.length})
              </p>
              <div className="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto">
                {extraLocations.map(loc => (
                  <span key={`extra-${loc}`}
                    className="text-[11px] px-2 py-0.5 rounded font-semibold inline-flex items-center gap-1"
                    style={{ background: '#ecfdf5', border: '1px solid #059669', color: '#065f46' }}>
                    {loc}
                    <button type="button" onClick={() => removeExtraLocation(loc)} aria-label={`Remove ${loc}`}
                      className="leading-none opacity-70 hover:opacity-100">×</button>
                  </span>
                ))}
              </div>
            </div>
          )}
          <p className="text-[10px] mb-2" style={{ color: 'var(--text-3)' }}>
            Auto-fill preview (cities / counties / streets from base — fills remaining slots up to {form.num_cities || 1}):
          </p>
          <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto">
            {nearbyCities.slice(0, 40).map((c) => {
              const kind = c.kind || 'city'
              const label = `${c.name}${c.state ? `, ${c.state}` : ''}`
              const style = kind === 'area'
                ? { background: '#ecfdf5', border: '1px solid #059669', color: '#065f46' }
                : kind === 'street'
                  ? { background: '#fff7ed', border: '1px solid #ea580c', color: '#9a3412' }
                  : kind === 'county'
                    ? { background: '#eff6ff', border: '1px solid #2563eb', color: '#1e40af' }
                  : { background: '#f8fafc', border: '1px solid #64748b', color: '#0f172a' }
              return (
                <button
                  key={`near-${c.name}-${c.state}-${kind}`}
                  type="button"
                  onClick={() => addExtraLocation(label)}
                  className="text-[11px] px-2 py-0.5 rounded font-semibold"
                  style={style}
                  title="Click to pin"
                >
                  {kind !== 'city' && (
                    <span className="uppercase text-[9px] mr-1" style={{ opacity: 0.85, fontWeight: 800 }}>{kind}</span>
                  )}
                  {label}
                </button>
              )
            })}
            {!nearbyCities.length && !nearbyError && form.base_location.trim() && (
              <span className="text-xs" style={{ color: 'var(--text-3)' }}>Looking up nearby places…</span>
            )}
          </div>
        </div>
      </div>
      )}

      {/* ── SUCCESS BANNER — appears immediately after generation ── */}
      {pages.length > 0 && (
        <div ref={resultsRef} className="content-action-bar rounded-xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0" style={{
              background: generateRequested && pages.length < generateRequested ? '#fef3c7' : '#d1fae5',
              border: generateRequested && pages.length < generateRequested ? '1px solid #f59e0b' : '1px solid #6ee7b7',
            }}>
              <CheckCircle size={18} style={{ color: generateRequested && pages.length < generateRequested ? '#b45309' : '#047857' }} />
            </div>
            <div>
              <p className="font-semibold text-sm" style={{ color: '#0f172a' }}>
                {generateRequested && pages.length !== generateRequested
                  ? `${pages.length} of ${generateRequested} ${pages[0]?.content_type === 'blog' || contentKind === 'post' ? 'blog posts' : 'pages'} generated`
                  : `${pages.length} ${pages[0]?.content_type === 'blog' || contentKind === 'post' ? 'blog posts' : 'pages'} generated`}
              </p>
              <p className="text-xs mt-0.5" style={{ color: '#334155' }}>
                {generateRequested && pages.length < generateRequested
                  ? `Requested ${generateRequested}. Missing pages are not skipped on purpose — generate again to fill the gap.`
                  : (pages[0]?.content_type === 'blog' || contentKind === 'post')
                    ? 'Will list on post-sitemap.xml after publish'
                    : 'Will list on page-sitemap.xml after publish'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <button onClick={handleExport} disabled={exporting === 'json'}
              className="content-btn flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm disabled:opacity-50">
              <FileJson size={14} /> {exporting === 'json' ? 'Exporting...' : 'Download JSON'}
            </button>
            <button onClick={handlePublishAllWeb} disabled={webAll?.loading}
              className="content-btn-primary flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm disabled:opacity-60">
              {webAll?.loading
                ? <><svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.3)" strokeWidth="3"/><path d="M12 2a10 10 0 0 1 10 10" stroke="#fff" strokeWidth="3" strokeLinecap="round"/></svg>Publishing all…</>
                : <><Globe size={14} /> Publish All {pages.length} to ZeOrbit</>}
            </button>
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
                  <a href={zeorbitArticleUrl(l.public_url || l.slug)} target="_blank" rel="noreferrer" className="text-xs truncate block" style={{ color: 'var(--brand-violet)' }}>{zeorbitArticleUrl(l.public_url || l.slug)}</a>
                </div>
                <div className="flex items-center gap-1.5 flex-shrink-0">
                  <button onClick={() => navigator.clipboard?.writeText(zeorbitArticleUrl(l.public_url || l.slug))}
                    className="px-2.5 py-1.5 rounded-lg text-xs" style={{ background: 'var(--bg-overlay)', border: '1px solid var(--border-bright)', color: 'var(--text-2)' }}>Copy</button>
                  <button
                    onClick={() => navigate('/google-ads', {
                      state: {
                        finalUrl: zeorbitArticleUrl(l.public_url || l.slug),
                        public_url: zeorbitArticleUrl(l.public_url || l.slug),
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
                  <a href={zeorbitArticleUrl(l.public_url || l.slug)} target="_blank" rel="noreferrer"
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
              <h3 className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>
                {pages.length} {(pages[0]?.content_type === 'blog' || contentKind === 'post') ? 'Posts' : 'Pages'} Generated
              </h3>
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
                const score = Math.round(block.quality_score ?? block.readability_score ?? 0)
                const pr = publishResults[i]
                return (
                  <tr key={`${block.city}-${i}`}>
                    <td className="text-xs font-semibold" style={{ color: 'var(--text-3)' }}>{i + 1}</td>
                    <td>
                      <div className="font-semibold text-sm" style={{ color: 'var(--text-1)' }}>{block.city || (block.content_type === 'blog' ? 'Article' : '—')}</div>
                      <div className="text-xs muted-cell">{[block.state, block.zip].filter(Boolean).join(' ') || (block.content_type === 'blog' ? 'Blog post' : '')}</div>
                    </td>
                    <td className="max-w-[240px]">
                      <div className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>{block.title}</div>
                      <div className="text-xs muted-cell mt-0.5">{block.slug}</div>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="w-14 h-1.5 rounded-full overflow-hidden" style={{ background: '#e2e8f0' }}>
                          <div className="h-full rounded-full"
                            style={{ width: `${Math.min(score, 100)}%`, background: score >= 90 ? '#059669' : score >= 75 ? '#d97706' : '#dc2626' }} />
                        </div>
                        <span className="text-xs font-bold" style={{ color: score >= 90 ? '#047857' : score >= 75 ? '#b45309' : '#b91c1c' }}>{score}</span>
                      </div>
                    </td>
                    <td className="text-xs font-medium max-w-[140px]" style={{ color: 'var(--text-2)' }}>{block.keywords?.primary}</td>
                    <td>
                      <div className="flex items-center gap-1.5">
                        <button onClick={() => navigate('/page-preview', { state: { block, index: i, businessType: form.business_type, contentKind: block.content_type === 'blog' ? 'post' : 'page' } })}
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
                        <button onClick={() => handlePublishSingle(block, i)}
                          disabled={pr === 'loading'}
                          className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold disabled:opacity-50"
                          style={{
                            background: pr?.success ? '#ecfdf5' : pr?.error ? '#fef2f2' : '#fff',
                            border: `1px solid ${pr?.success ? '#6ee7b7' : pr?.error ? '#fecaca' : '#94a3b8'}`,
                            color: pr?.success ? '#047857' : pr?.error ? '#b91c1c' : '#0f172a',
                          }}>
                          <Globe size={11} />
                          {pr === 'loading' ? '...' : pr?.success ? 'Live' : pr?.error ? 'Err' : 'Publish'}
                        </button>
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
