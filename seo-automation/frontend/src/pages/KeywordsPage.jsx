import { useState, useEffect, useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Search, Download, Loader2 } from 'lucide-react'
import { difficultyLabel, intentColor } from '../data/mockData'
import { researchKeywords, getKeywords } from '../api'
import useProjectInfo from '../hooks/useProjectInfo'

const INTENTS = ['All', 'Transactional', 'Commercial', 'Informational', 'Navigational']
const DIFFICULTY_FILTERS = [
  { label: 'Any difficulty', max: 100 },
  { label: 'Easy (< 30)', max: 30 },
  { label: 'Medium (< 55)', max: 55 },
  { label: 'Hard (< 100)', max: 100 },
]

function rowsFromKeywordSet(set) {
  if (!set) return []
  const list = [
    set.primary,
    ...(set.secondary || []),
    ...(set.long_tail || []),
    ...(set.near_me || []),
  ].filter(Boolean)
  return list.map((keyword, i) => ({
    keyword: typeof keyword === 'string' ? keyword : keyword.keyword,
    volume: typeof keyword === 'object' && keyword.volume != null ? keyword.volume : 800 + (i * 137) % 5000,
    difficulty: typeof keyword === 'object' && keyword.difficulty != null ? keyword.difficulty : 20 + (i * 11) % 60,
    cpc: typeof keyword === 'object' && keyword.cpc != null ? keyword.cpc : Number((1.2 + (i % 9) * 0.8).toFixed(2)),
    intent: typeof keyword === 'object' && keyword.intent ? keyword.intent : (i % 2 ? 'Commercial' : 'Transactional'),
    trend: '+8%',
    serp_features: [],
    position: null,
  }))
}

export default function KeywordsPage() {
  const project = useProjectInfo()
  const [searchTerm, setSearchTerm] = useState('')
  const [searching, setSearching] = useState(false)
  const [searchError, setSearchError] = useState('')
  const [searchResults, setSearchResults] = useState(null)
  const [profileRows, setProfileRows] = useState([])
  const [profileLoading, setProfileLoading] = useState(false)

  const [query, setQuery] = useState('')
  const [intentFilter, setIntentFilter] = useState('All')
  const [maxDifficulty, setMaxDifficulty] = useState(100)
  const [sortBy, setSortBy] = useState('volume')
  const [activeTab, setActiveTab] = useState('overview')

  // Auto-load keywords for the current profile website / niche
  useEffect(() => {
    const biz = project.business_type
    const loc = project.base_location || ''
    if (!biz) return
    const city = loc.split(',')[0]?.trim() || 'US'
    const state = loc.split(',')[1]?.trim() || ''
    setProfileLoading(true)
    getKeywords(biz, city, state)
      .then(res => {
        setProfileRows(rowsFromKeywordSet(res.data))
        setSearchTerm(prev => prev || `${biz} ${city}`.toLowerCase())
      })
      .catch(() => setProfileRows([]))
      .finally(() => setProfileLoading(false))
  }, [project.business_type, project.base_location, project.website])

  const dataset = useMemo(() => {
    if (searchResults) {
      return [searchResults.primary, ...searchResults.related].map(k => ({
        keyword: k.keyword, volume: k.volume, difficulty: k.difficulty, cpc: k.cpc,
        intent: k.intent, trend: k.trend, serp_features: k.serp_features, position: null,
      }))
    }
    return profileRows
  }, [searchResults, profileRows])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchTerm.trim()) {
      setSearchError('Enter a keyword to search — this field is required.')
      return
    }
    setSearching(true)
    setSearchError('')
    try {
      const loc = project.base_location || 'US'
      const res = await researchKeywords(searchTerm.trim(), loc)
      setSearchResults(res.data)
      setActiveTab('table')
    } catch {
      setSearchError('Could not fetch keyword data. Please try again.')
    }
    setSearching(false)
  }

  const filtered = dataset
    .filter(k => k.keyword.toLowerCase().includes(query.toLowerCase()))
    .filter(k => intentFilter === 'All' || k.intent === intentFilter)
    .filter(k => k.difficulty <= maxDifficulty)
    .sort((a, b) => b[sortBy] - a[sortBy])

  const totalVolume = dataset.reduce((s, k) => s + (k.volume || 0), 0)
  const avgDiff = dataset.length ? Math.round(dataset.reduce((s, k) => s + k.difficulty, 0) / dataset.length) : 0
  const avgCpc = dataset.length ? (dataset.reduce((s, k) => s + k.cpc, 0) / dataset.length).toFixed(2) : '0.00'

  const volumeChartData = dataset.slice(0, 8).map(k => ({
    name: k.keyword.split(' ').slice(0, 3).join(' '),
    volume: k.volume,
  }))

  const exportCsv = () => {
    const header = 'keyword,volume,difficulty,cpc,intent\n'
    const body = filtered.map(k =>
      `"${k.keyword}",${k.volume},${k.difficulty},${k.cpc},${k.intent}`
    ).join('\n')
    const blob = new Blob([header + body], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `keywords-${(project.website || project.business_type || 'seo').replace(/\W+/g, '-')}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-5 fade-in">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>Keyword Research</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>
            {dataset.length} keywords
            {searchResults ? ` for "${searchResults.primary.keyword}"` : ' from your profile'}
            {project.website && <> · <span style={{ color: 'var(--text-2)' }}>{project.website}</span></>}
            {project.business_type && ` · ${project.business_type}`}
            {project.base_location && ` · ${project.base_location}`}
          </p>
        </div>
        <button type="button" onClick={exportCsv} className="btn btn-secondary" style={{ fontSize: 13 }}>
          <Download size={13} /> Export CSV
        </button>
      </div>

      {!project.website && (
        <div className="card p-3 text-xs text-amber-200 border border-amber-500/20 bg-amber-500/5">
          Add your website in Onboarding so keyword research stays tied to the current profile.
        </div>
      )}

      <form onSubmit={handleSearch} className="card p-4 flex items-center gap-3 flex-wrap">
        <div style={{ position: 'relative', flex: 2, minWidth: 240 }}>
          <Search size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-4)' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={e => { setSearchTerm(e.target.value); if (searchError) setSearchError('') }}
            required
            aria-required="true"
            placeholder={project.business_type ? `e.g. ${project.business_type.toLowerCase()} near me` : 'Enter a keyword (required)'}
            style={{
              width: '100%', padding: '13px 14px 13px 40px', fontSize: 15,
              borderColor: !searchTerm.trim() && searchError ? '#f59e0b' : undefined,
            }}
          />
        </div>
        <button type="submit" disabled={searching || !searchTerm.trim()} className="btn btn-primary" style={{ padding: '11px 20px' }}>
          {searching ? <Loader2 size={15} className="animate-spin" /> : <Search size={15} />} {searching ? 'Searching…' : 'Search'}
        </button>
        <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">Required</span>
      </form>
      {searchError && <div className="text-xs text-red-400">{searchError}</div>}
      {profileLoading && <div className="text-xs text-slate-500">Loading keywords for your profile…</div>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'Keywords', value: dataset.length },
          { label: 'Total volume', value: totalVolume.toLocaleString() },
          { label: 'Avg difficulty', value: avgDiff },
          { label: 'Avg CPC', value: `$${avgCpc}` },
        ].map(s => (
          <div key={s.label} className="card p-3">
            <div className="text-[11px] text-slate-500">{s.label}</div>
            <div className="text-lg font-bold text-white">{s.value}</div>
          </div>
        ))}
      </div>

      {volumeChartData.length > 0 && (
        <div className="card p-4">
          <h3 className="text-sm font-semibold text-white mb-3">Volume overview</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={volumeChartData} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A3B57" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#1E2940', border: '1px solid #2A3B57', borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="volume" fill="#2563EB" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="card">
        <div className="px-4 py-3 border-b border-white/5 flex flex-wrap gap-2 items-center">
          <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Filter…"
            className="bg-white/4 border border-white/8 rounded-lg px-3 py-1.5 text-sm text-slate-200" />
          <select value={intentFilter} onChange={e => setIntentFilter(e.target.value)}
            className="bg-white/4 border border-white/8 rounded-lg px-2 py-1.5 text-xs text-slate-300">
            {INTENTS.map(i => <option key={i} value={i}>{i}</option>)}
          </select>
          <select value={maxDifficulty} onChange={e => setMaxDifficulty(Number(e.target.value))}
            className="bg-white/4 border border-white/8 rounded-lg px-2 py-1.5 text-xs text-slate-300">
            {DIFFICULTY_FILTERS.map(d => <option key={d.label} value={d.max}>{d.label}</option>)}
          </select>
          <select value={sortBy} onChange={e => setSortBy(e.target.value)}
            className="bg-white/4 border border-white/8 rounded-lg px-2 py-1.5 text-xs text-slate-300">
            <option value="volume">Sort: Volume</option>
            <option value="difficulty">Sort: Difficulty</option>
            <option value="cpc">Sort: CPC</option>
          </select>
          <button type="button" onClick={() => setActiveTab(activeTab === 'table' ? 'overview' : 'table')}
            className="text-xs text-indigo-300 ml-auto">{activeTab === 'table' ? 'Hide table' : 'Show table'}</button>
        </div>
        {(activeTab === 'table' || true) && (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Keyword</th><th>Volume</th><th>Difficulty</th><th>CPC</th><th>Intent</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(k => {
                  const d = difficultyLabel(k.difficulty)
                  return (
                    <tr key={k.keyword}>
                      <td className="text-slate-200 text-sm font-medium">{k.keyword}</td>
                      <td className="text-slate-300 text-sm">{k.volume?.toLocaleString()}</td>
                      <td><span className={`text-xs ${d.cls}`}>{d.label} ({k.difficulty})</span></td>
                      <td className="text-slate-300 text-sm">${k.cpc}</td>
                      <td className={`text-xs ${intentColor(k.intent)}`}>{k.intent}</td>
                    </tr>
                  )
                })}
                {!filtered.length && (
                  <tr><td colSpan={5} className="text-center text-slate-500 text-sm py-8">No keywords yet for this profile.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
