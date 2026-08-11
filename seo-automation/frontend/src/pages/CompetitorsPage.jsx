import { useState, useEffect, useMemo } from 'react'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts'
import { ExternalLink, X, Loader2, Sparkles } from 'lucide-react'
import { analyzeCompetitor, discoverCompetitors } from '../api'
import useProjectInfo from '../hooks/useProjectInfo'

const radarData = [
  { metric: 'Traffic', you: 72, avg: 58 },
  { metric: 'Keywords', you: 48, avg: 65 },
  { metric: 'Backlinks', you: 34, avg: 52 },
  { metric: 'Content', you: 81, avg: 60 },
  { metric: 'Tech SEO', you: 76, avg: 55 },
  { metric: 'Local SEO', you: 88, avg: 48 },
]

function isSearchHint(domain) {
  return String(domain || '').startsWith('search:')
}

function AddCompetitorModal({ businessType, city, initialUrl = '', onClose, onSaved }) {
  const [url, setUrl] = useState(initialUrl)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const run = async (targetUrl) => {
    const u = (targetUrl ?? url).trim()
    if (!u || isSearchHint(u)) {
      setError('Enter a real competitor website (example: competitor.com)')
      return
    }
    setLoading(true); setError(''); setResult(null)
    try {
      const res = await analyzeCompetitor(u, businessType || 'business', city || '')
      if (res.data?.error && !res.data?.messaging) setError(res.data.error)
      else {
        setResult(res.data)
        onSaved?.({ domain: u.replace(/^https?:\/\//, '').split('/')[0], analysis: res.data })
      }
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (initialUrl.trim() && !isSearchHint(initialUrl)) run(initialUrl)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const renderSection = (label, value) => {
    if (!value) return null
    return (
      <div className="mb-3">
        <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--text-3)' }}>{label}</div>
        <div className="text-sm whitespace-pre-line" style={{ color: 'var(--text-1)' }}>
          {Array.isArray(value) ? value.join(', ') : typeof value === 'object' ? JSON.stringify(value) : value}
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0" style={{ background: 'rgba(15,23,42,0.45)' }} />
      <div className="relative w-full max-w-lg card rounded-2xl p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold" style={{ color: 'var(--text-1)' }}>Add Competitor</h2>
          <button onClick={onClose} className="p-1 rounded" style={{ color: 'var(--text-3)' }}><X size={16} /></button>
        </div>
        <div className="flex gap-2 mb-4">
          <input
            value={url} onChange={e => setUrl(e.target.value)}
            placeholder="competitor-website.com"
            className="flex-1 rounded-lg px-3 py-2 text-sm"
            style={{ background: '#fff', border: '1px solid #94a3b8', color: '#0f172a' }}
          />
          <button onClick={() => run()} disabled={loading || !url.trim()}
            className="btn-primary px-4 py-2 rounded-lg text-white text-sm font-semibold disabled:opacity-50 flex items-center gap-1.5">
            {loading ? <Loader2 size={14} className="animate-spin" /> : null} Analyze
          </button>
        </div>
        {error && <div className="text-xs mb-2" style={{ color: '#b91c1c' }}>⚠ {error}</div>}
        {result && (
          <div className="max-h-96 overflow-y-auto pt-3" style={{ borderTop: '1px solid var(--border)' }}>
            {result.source === 'page-scan' && (
              <div className="text-[11px] mb-3" style={{ color: 'var(--text-3)' }}>
                Live page scan{result.fetched_url ? ` · ${result.fetched_url}` : ''}
              </div>
            )}
            {renderSection('Messaging', result.messaging)}
            {renderSection('Target Audience', result.target_audience)}
            {renderSection('SEO Strategy', result.seo_strategy)}
            {renderSection('Content Gaps', result.content_gaps)}
            {renderSection('Unique Selling Points', result.unique_selling_points)}
            {renderSection('Recommendations', result.recommendations)}
          </div>
        )}
      </div>
    </div>
  )
}

export default function CompetitorsPage() {
  const [showAdd, setShowAdd] = useState(false)
  const [prefillUrl, setPrefillUrl] = useState('')
  const [tracked, setTracked] = useState([])
  const project = useProjectInfo()

  const [suggestions, setSuggestions] = useState([])
  const [suggestNote, setSuggestNote] = useState('')
  const [suggestLoading, setSuggestLoading] = useState(false)
  const [suggestError, setSuggestError] = useState('')

  useEffect(() => {
    if (!project.website) {
      setSuggestions([])
      setSuggestNote('')
      return
    }
    setSuggestLoading(true)
    setSuggestError('')
    setSuggestNote('')
    discoverCompetitors(project.website, project.business_type || 'business', project.base_location || '')
      .then(res => {
        const list = res.data?.competitors || []
        if (res.data?.error && !list.length) setSuggestError(res.data.error)
        else {
          setSuggestions(list)
          if (res.data?.note) setSuggestNote(res.data.note)
        }
      })
      .catch(e => setSuggestError(e.response?.data?.detail || e.message))
      .finally(() => setSuggestLoading(false))
  }, [project.website, project.business_type, project.base_location])

  const openAnalyze = (domain) => {
    if (isSearchHint(domain)) {
      const q = domain.replace(/^search:/, '').replace(/-/g, ' ')
      window.open(`https://www.google.com/search?q=${encodeURIComponent(q)}`, '_blank', 'noopener')
      return
    }
    setPrefillUrl(domain || '')
    setShowAdd(true)
  }

  const cards = useMemo(() => {
    const fromSuggestions = suggestions.map(s => ({
      domain: s.domain,
      rationale: s.rationale || '',
      source: 'suggested',
    }))
    const fromTracked = tracked.map(t => ({
      domain: t.domain,
      rationale: 'Analyzed for your profile',
      source: 'tracked',
    }))
    const seen = new Set()
    return [...fromTracked, ...fromSuggestions].filter(c => {
      const key = (c.domain || '').toLowerCase()
      if (!key || seen.has(key)) return false
      seen.add(key)
      return true
    })
  }, [suggestions, tracked])

  return (
    <div className="space-y-5 fade-in">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-1)' }}>Competitor Analysis</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>
            Based on {project.website || 'your profile website'}
            {project.business_type ? ` · ${project.business_type}` : ''}
            {project.base_location ? ` · ${project.base_location}` : ''}
          </p>
        </div>
        <button onClick={() => openAnalyze('')} className="btn-primary px-4 py-2 rounded-lg text-white text-sm font-semibold">
          + Add Competitor
        </button>
      </div>

      {!project.website && (
        <div className="card p-4 text-sm" style={{ color: '#92400e', border: '1px solid #fcd34d', background: '#fffbeb' }}>
          Set your website in Onboarding / profile first. Competitors are discovered from that site.
        </div>
      )}

      {showAdd && (
        <AddCompetitorModal
          businessType={project.business_type}
          city={project.base_location}
          initialUrl={prefillUrl}
          onClose={() => setShowAdd(false)}
          onSaved={(row) => setTracked(prev => [row, ...prev.filter(p => p.domain !== row.domain)])}
        />
      )}

      {project.website && (
        <div className="card p-4">
          <h3 className="text-sm font-semibold mb-1 flex items-center gap-1.5" style={{ color: 'var(--text-1)' }}>
            <Sparkles size={13} style={{ color: '#4f46e5' }} /> Competitors for {project.website}
          </h3>
          <p className="text-xs mb-3" style={{ color: 'var(--text-3)' }}>
            Auto-identified from your profile website. Analyze any domain for a full breakdown.
          </p>
          {suggestLoading && <div className="text-xs py-2" style={{ color: 'var(--text-3)' }}>Looking for likely competitors…</div>}
          {suggestError && <div className="text-xs py-2" style={{ color: '#b91c1c' }}>⚠ {suggestError}</div>}
          {suggestNote && !suggestError && (
            <div className="text-[11px] mb-2" style={{ color: 'var(--text-3)' }}>{suggestNote}</div>
          )}
          {!suggestLoading && !suggestError && cards.length === 0 && (
            <div className="text-xs py-2" style={{ color: 'var(--text-3)' }}>No suggestions yet — add a competitor URL manually.</div>
          )}
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {cards.map(s => (
              <div key={s.domain} className="flex flex-col gap-2 p-3 rounded-lg"
                style={{ background: 'var(--bg-raised)', border: '1px solid var(--border-bright)' }}>
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <div className="text-xs font-semibold truncate" style={{ color: 'var(--text-1)' }}>
                      {isSearchHint(s.domain) ? 'Local SERP check' : s.domain}
                    </div>
                    <div className="text-[11px] line-clamp-2" style={{ color: 'var(--text-3)' }}>{s.rationale}</div>
                  </div>
                  {!isSearchHint(s.domain) && (
                    <a href={`https://${s.domain.replace(/^https?:\/\//, '')}`} target="_blank" rel="noreferrer"
                      style={{ color: 'var(--text-3)' }}><ExternalLink size={12} /></a>
                  )}
                </div>
                <button onClick={() => openAnalyze(s.domain)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold"
                  style={{ color: '#3730a3', background: '#eef2ff', border: '1px solid #c7d2fe' }}>
                  {isSearchHint(s.domain) ? 'Open Google' : 'Analyze'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card p-5">
        <h3 className="text-sm font-semibold mb-1" style={{ color: 'var(--text-1)' }}>
          Competitive Position <span className="font-normal" style={{ color: 'var(--text-3)' }}>(illustrative)</span>
        </h3>
        <p className="text-xs mb-4" style={{ color: 'var(--text-3)' }}>
          Relative SEO factors for planning — use Analyze above for real competitor intelligence tied to your site.
        </p>
        <ResponsiveContainer width="100%" height={220}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="var(--border)" />
            <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11, fill: '#64748b' }} />
            <Radar name="You" dataKey="you" stroke="#1D4ED8" fill="#1D4ED8" fillOpacity={0.15} strokeWidth={2} />
            <Radar name="Avg" dataKey="avg" stroke="#475569" fill="#475569" fillOpacity={0.08} strokeWidth={1.5} strokeDasharray="4 2" />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
