import { useState, useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Search, Download, TrendingUp, Loader2 } from 'lucide-react'
import { KEYWORD_DATA, INTENT_DIST, difficultyLabel, intentColor } from '../data/mockData'
import { researchKeywords } from '../api'

const INTENTS = ['All', 'Transactional', 'Commercial', 'Informational', 'Navigational']
const DIFFICULTY_FILTERS = [
  { label: 'Any difficulty', max: 100 },
  { label: 'Easy (< 30)', max: 30 },
  { label: 'Medium (< 55)', max: 55 },
  { label: 'Hard (< 100)', max: 100 },
]

export default function KeywordsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [searching, setSearching] = useState(false)
  const [searchError, setSearchError] = useState('')
  const [searchResults, setSearchResults] = useState(null) // { primary, related }

  const [query, setQuery] = useState('')
  const [intentFilter, setIntentFilter] = useState('All')
  const [maxDifficulty, setMaxDifficulty] = useState(100)
  const [sortBy, setSortBy] = useState('volume')
  const [activeTab, setActiveTab] = useState('overview')

  const dataset = useMemo(() => {
    if (!searchResults) return KEYWORD_DATA
    const rows = [searchResults.primary, ...searchResults.related].map(k => ({
      keyword: k.keyword, volume: k.volume, difficulty: k.difficulty, cpc: k.cpc,
      intent: k.intent, trend: k.trend, serp_features: k.serp_features, position: null,
    }))
    return rows
  }, [searchResults])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchTerm.trim()) return
    setSearching(true)
    setSearchError('')
    try {
      const res = await researchKeywords(searchTerm.trim(), 'US')
      setSearchResults(res.data)
      setActiveTab('table')
    } catch {
      setSearchError('Could not fetch keyword data. Please try again.')
    }
    setSearching(false)
  }

  const filtered = dataset
    .filter(k => k.keyword.includes(query.toLowerCase()))
    .filter(k => intentFilter === 'All' || k.intent === intentFilter)
    .filter(k => k.difficulty <= maxDifficulty)
    .sort((a, b) => b[sortBy] - a[sortBy])

  const totalVolume = dataset.reduce((s, k) => s + k.volume, 0)
  const avgDiff = Math.round(dataset.reduce((s, k) => s + k.difficulty, 0) / dataset.length)
  const avgCpc = (dataset.reduce((s, k) => s + k.cpc, 0) / dataset.length).toFixed(2)

  const volumeChartData = dataset.slice(0, 8).map(k => ({
    name: k.keyword.split(' ').slice(0, 3).join(' '),
    volume: k.volume,
  }))

  return (
    <div className="space-y-5 fade-in">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>Keyword Research</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>{dataset.length} keywords {searchResults ? `for "${searchResults.primary.keyword}"` : 'tracked · San Diego Plumbing (demo)'}</p>
        </div>
        <button className="btn btn-secondary" style={{ fontSize: 13 }}>
          <Download size={13} /> Export CSV
        </button>
      </div>

      {/* Big search bar */}
      <form onSubmit={handleSearch} className="card p-4 flex items-center gap-3 flex-wrap">
        <div style={{ position: 'relative', flex: 2, minWidth: 240 }}>
          <Search size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-4)' }} />
          <input type="text" value={searchTerm} onChange={e => setSearchTerm(e.target.value)}
            placeholder="Enter a keyword, e.g. plumber near me"
            style={{ width: '100%', padding: '13px 14px 13px 40px', fontSize: 15 }} />
        </div>
        <select defaultValue="US" style={{ padding: '11px 14px', minWidth: 140 }}>
          <option value="US">🇺🇸 United States</option>
        </select>
        <select defaultValue="en" style={{ padding: '11px 14px', minWidth: 130 }}>
          <option value="en">English</option>
        </select>
        <button type="submit" disabled={searching || !searchTerm.trim()} className="btn btn-primary" style={{ padding: '11px 20px' }}>
          {searching ? <Loader2 size={15} className="animate-spin" /> : <Search size={15} />} {searching ? 'Searching…' : 'Search'}
        </button>
      </form>
      {searchError && <div className="alert alert-error">⚠ {searchError}</div>}

      {/* Summary stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Search Volume', value: totalVolume.toLocaleString(), sub: '/month' },
          { label: 'Avg. Difficulty', value: avgDiff, sub: '/ 100' },
          { label: 'Avg. CPC', value: `$${avgCpc}`, sub: 'per click' },
          { label: 'Top 3 Rankings', value: dataset.filter(k => k.position && k.position <= 3).length, sub: 'keywords' },
        ].map(s => (
          <div key={s.label} className="card p-4">
            <div className="text-xs" style={{ color: 'var(--text-3)' }}>{s.label}</div>
            <div className="text-xl font-bold" style={{ color: 'var(--text-1)' }}>{s.value}<span className="text-sm font-normal ml-1" style={{ color: 'var(--text-3)' }}>{s.sub}</span></div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-0 border-b" style={{ borderColor: 'var(--border)' }}>
        {['overview', 'table', 'gaps'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-sm font-medium capitalize transition-colors ${activeTab === tab ? 'tab-active' : 'tab-inactive'}`}
          >
            {tab === 'overview' ? 'Volume Overview' : tab === 'table' ? 'Keyword Table' : 'Keyword Gaps'}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="grid lg:grid-cols-3 gap-4">
          <div className="card p-5 lg:col-span-2">
            <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-1)' }}>Search Volume by Keyword</h3>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={volumeChartData} margin={{ left: -20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#98A2B3' }} angle={-30} textAnchor="end" axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#98A2B3' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: '#fff', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12, color: 'var(--text-1)' }}
                  labelStyle={{ color: 'var(--text-3)' }}
                  itemStyle={{ color: 'var(--text-1)' }}
                />
                <Bar dataKey="volume" fill="#FF5A4E" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="card p-5">
            <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-1)' }}>Intent Breakdown</h3>
            <div className="space-y-3">
              {INTENT_DIST.map(d => (
                <div key={d.name}>
                  <div className="flex justify-between text-xs mb-1.5">
                    <span style={{ color: 'var(--text-3)' }}>{d.name}</span>
                    <span className="font-semibold" style={{ color: 'var(--text-2)' }}>{d.value}%</span>
                  </div>
                  <div className="h-2 rounded-full overflow-hidden" style={{ background: 'var(--bg-raised)' }}>
                    <div className="h-full rounded-full transition-all duration-700" style={{ width: `${d.value}%`, background: d.color }} />
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-5 pt-4 border-t" style={{ borderColor: 'var(--border)' }}>
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: 'var(--text-3)' }}>Quick Wins</h4>
              {dataset.filter(k => k.difficulty < 30).slice(0, 3).map(k => (
                <div key={k.keyword} className="flex items-center justify-between py-2 border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
                  <span className="text-xs truncate max-w-[140px]" style={{ color: 'var(--text-2)' }}>{k.keyword}</span>
                  <span className="text-xs diff-easy px-2 py-0.5 rounded-full ml-2 flex-shrink-0">Easy</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'table' && (
        <div className="card">
          {/* Filters */}
          <div className="flex items-center gap-3 p-4 border-b flex-wrap" style={{ borderColor: 'var(--border)' }}>
            <div className="relative flex-1" style={{ minWidth: 200, maxWidth: 280 }}>
              <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-4)' }} />
              <input
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Filter keywords..."
                style={{ width: '100%', paddingLeft: 34, paddingRight: 12, paddingTop: 8, paddingBottom: 8, fontSize: 13 }}
              />
            </div>
            <div className="flex gap-1 flex-wrap">
              {INTENTS.map(i => (
                <button
                  key={i}
                  onClick={() => setIntentFilter(i)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                  style={intentFilter === i
                    ? { background: 'var(--brand-soft)', color: 'var(--brand-dark)', border: '1px solid rgba(255,90,78,0.3)' }
                    : { color: 'var(--text-3)', border: '1px solid transparent' }}
                >
                  {i}
                </button>
              ))}
            </div>
            <select value={maxDifficulty} onChange={e => setMaxDifficulty(Number(e.target.value))} style={{ padding: '8px 12px', fontSize: 12 }}>
              {DIFFICULTY_FILTERS.map(f => <option key={f.label} value={f.max}>{f.label}</option>)}
            </select>
            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value)}
              style={{ padding: '8px 12px', fontSize: 12, marginLeft: 'auto' }}
            >
              <option value="volume">Sort: Volume</option>
              <option value="difficulty">Sort: Difficulty</option>
              <option value="cpc">Sort: CPC</option>
            </select>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Keyword</th>
                  <th>Intent</th>
                  <th>Volume</th>
                  <th>Difficulty</th>
                  <th>CPC</th>
                  <th>Trend</th>
                  <th>SERP Features</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(kw => {
                  const diff = difficultyLabel(kw.difficulty)
                  return (
                    <tr key={kw.keyword}>
                      <td className="font-medium" style={{ color: 'var(--text-1)' }}>{kw.keyword}</td>
                      <td className={`text-xs font-medium ${intentColor(kw.intent)}`}>{kw.intent}</td>
                      <td className="font-medium" style={{ color: 'var(--text-2)' }}>{kw.volume.toLocaleString()}</td>
                      <td>
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${diff.cls}`}>{kw.difficulty} · {diff.label}</span>
                      </td>
                      <td style={{ color: 'var(--text-2)' }}>${kw.cpc.toFixed(2)}</td>
                      <td className="text-xs font-semibold" style={{ color: 'var(--green)' }}>{kw.trend}</td>
                      <td className="text-xs" style={{ color: 'var(--text-4)' }}>{(kw.serp_features || []).join(', ') || '—'}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'gaps' && (
        <div className="card p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={15} style={{ color: 'var(--brand)' }} />
            <h3 className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>Keyword Gap Analysis</h3>
            <span className="text-xs" style={{ color: 'var(--text-4)' }}>— keywords competitors rank for that you don't</span>
          </div>
          <table className="data-table">
            <thead>
              <tr><th>Keyword</th><th>Competitor</th><th>Their Position</th><th>Volume</th><th>Opportunity</th></tr>
            </thead>
            <tbody>
              {[
                { kw: 'plumbing inspection san diego', comp: 'sdplumbing.com', pos: 3, vol: 1200, opp: 'High' },
                { kw: 'gas line repair san diego', comp: 'allcityplumbing.com', pos: 5, vol: 980, opp: 'High' },
                { kw: 'bathroom remodel plumber', comp: 'plumbersandiego.net', pos: 4, vol: 860, opp: 'Medium' },
                { kw: 'water softener installation', comp: 'sdplumbing.com', pos: 7, vol: 720, opp: 'Medium' },
                { kw: 'tankless water heater san diego', comp: 'rooterman.com', pos: 6, vol: 640, opp: 'Medium' },
              ].map(r => (
                <tr key={r.kw}>
                  <td className="font-medium" style={{ color: 'var(--text-1)' }}>{r.kw}</td>
                  <td className="text-xs" style={{ color: 'var(--text-3)' }}>{r.comp}</td>
                  <td><span className="font-bold" style={{ color: 'var(--amber)' }}>#{r.pos}</span></td>
                  <td style={{ color: 'var(--text-2)' }}>{r.vol.toLocaleString()}</td>
                  <td>
                    <span className="text-xs px-2 py-0.5 rounded-full font-medium"
                      style={r.opp === 'High' ? { color: 'var(--green)', background: 'var(--green-soft)' } : { color: 'var(--amber)', background: 'var(--amber-soft)' }}>
                      {r.opp}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
