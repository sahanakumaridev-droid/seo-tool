import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Search, Download, Filter, TrendingUp } from 'lucide-react'
import { KEYWORD_DATA, INTENT_DIST, difficultyLabel, intentColor } from '../data/mockData'

const INTENTS = ['All', 'Transactional', 'Commercial', 'Informational']

export default function KeywordsPage() {
  const [query, setQuery] = useState('')
  const [intentFilter, setIntentFilter] = useState('All')
  const [sortBy, setSortBy] = useState('volume')
  const [activeTab, setActiveTab] = useState('overview')

  const filtered = KEYWORD_DATA
    .filter(k => k.keyword.includes(query.toLowerCase()))
    .filter(k => intentFilter === 'All' || k.intent === intentFilter)
    .sort((a, b) => b[sortBy] - a[sortBy])

  const totalVolume = KEYWORD_DATA.reduce((s, k) => s + k.volume, 0)
  const avgDiff = Math.round(KEYWORD_DATA.reduce((s, k) => s + k.difficulty, 0) / KEYWORD_DATA.length)
  const avgCpc = (KEYWORD_DATA.reduce((s, k) => s + k.cpc, 0) / KEYWORD_DATA.length).toFixed(2)

  const volumeChartData = KEYWORD_DATA.slice(0, 8).map(k => ({
    name: k.keyword.split(' ').slice(0, 3).join(' '),
    volume: k.volume,
  }))

  return (
    <div className="space-y-5 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Keyword Intelligence</h1>
          <p className="text-sm text-slate-500 mt-0.5">{KEYWORD_DATA.length} keywords tracked · San Diego Plumbing</p>
        </div>
        <button className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white/5 border border-white/8 text-slate-300 text-sm hover:bg-white/8 transition-colors">
          <Download size={13} /> Export CSV
        </button>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Total Search Volume', value: totalVolume.toLocaleString(), sub: '/month' },
          { label: 'Avg. Difficulty', value: avgDiff, sub: '/ 100' },
          { label: 'Avg. CPC', value: `$${avgCpc}`, sub: 'per click' },
          { label: 'Top 3 Rankings', value: KEYWORD_DATA.filter(k => k.position <= 3).length, sub: 'keywords' },
        ].map(s => (
          <div key={s.label} className="card p-4">
            <div className="text-xs text-slate-500 mb-1">{s.label}</div>
            <div className="text-xl font-bold text-white">{s.value}<span className="text-sm font-normal text-slate-500 ml-1">{s.sub}</span></div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-0 border-b border-white/6">
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
            <h3 className="text-sm font-semibold text-white mb-4">Search Volume by Keyword</h3>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={volumeChartData} margin={{ left: -20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A3B57" />
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} angle={-30} textAnchor="end" axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: '#1E2940', border: '1px solid #2A3B57', borderRadius: 8, fontSize: 12, color: '#F1F5F9' }}
                  labelStyle={{ color: '#94A3B8' }}
                  itemStyle={{ color: '#F1F5F9' }}
                />
                <Bar dataKey="volume" fill="#1D4ED8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-white mb-4">Intent Breakdown</h3>
            <div className="space-y-3">
              {INTENT_DIST.map(d => (
                <div key={d.name}>
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="text-slate-400">{d.name}</span>
                    <span className="text-slate-200 font-semibold">{d.value}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/6 overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-700" style={{ width: `${d.value}%`, background: d.color }} />
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-5 pt-4 border-t border-white/5">
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Quick Wins</h4>
              {KEYWORD_DATA.filter(k => k.difficulty < 30).slice(0, 3).map(k => (
                <div key={k.keyword} className="flex items-center justify-between py-2 border-b border-white/4 last:border-0">
                  <span className="text-xs text-slate-300 truncate max-w-[140px]">{k.keyword}</span>
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
          <div className="flex items-center gap-3 p-4 border-b border-white/5">
            <div className="relative flex-1 max-w-xs">
              <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Filter keywords..."
                className="w-full bg-white/4 border border-white/8 rounded-lg pl-9 pr-3 py-2 text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50"
              />
            </div>
            <div className="flex gap-1">
              {INTENTS.map(i => (
                <button
                  key={i}
                  onClick={() => setIntentFilter(i)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
                    ${intentFilter === i ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-600/30' : 'text-slate-500 hover:text-slate-300 hover:bg-white/4'}`}
                >
                  {i}
                </button>
              ))}
            </div>
            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value)}
              className="bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none ml-auto"
            >
              <option value="volume">Sort: Volume</option>
              <option value="difficulty">Sort: Difficulty</option>
              <option value="cpc">Sort: CPC</option>
            </select>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Keyword</th>
                <th>Intent</th>
                <th>Volume</th>
                <th>Difficulty</th>
                <th>CPC</th>
                <th>Trend</th>
                <th>Position</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(kw => {
                const diff = difficultyLabel(kw.difficulty)
                return (
                  <tr key={kw.keyword}>
                    <td className="text-slate-200 font-medium">{kw.keyword}</td>
                    <td className={`text-xs font-medium ${intentColor(kw.intent)}`}>{kw.intent}</td>
                    <td className="text-slate-300 font-medium">{kw.volume.toLocaleString()}</td>
                    <td>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${diff.cls}`}>{kw.difficulty} · {diff.label}</span>
                    </td>
                    <td className="text-slate-300">${kw.cpc.toFixed(2)}</td>
                    <td className="text-emerald-400 text-xs font-semibold">{kw.trend}</td>
                    <td>
                      <span className={`font-bold text-sm ${kw.position <= 3 ? 'text-emerald-400' : kw.position <= 10 ? 'text-amber-400' : 'text-slate-400'}`}>
                        #{kw.position}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'gaps' && (
        <div className="card p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={15} className="text-indigo-400" />
            <h3 className="text-sm font-semibold text-white">Keyword Gap Analysis</h3>
            <span className="text-xs text-slate-500">— keywords competitors rank for that you don't</span>
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
                  <td className="text-slate-200 font-medium">{r.kw}</td>
                  <td className="text-slate-400 text-xs">{r.comp}</td>
                  <td><span className="text-amber-400 font-bold">#{r.pos}</span></td>
                  <td className="text-slate-300">{r.vol.toLocaleString()}</td>
                  <td>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${r.opp === 'High' ? 'text-emerald-400 bg-emerald-400/10' : 'text-amber-400 bg-amber-400/10'}`}>
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
