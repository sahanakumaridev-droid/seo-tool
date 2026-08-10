import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, Minus, Search } from 'lucide-react'
import { getRankings } from '../api'
import useProjectInfo from '../hooks/useProjectInfo'

const LINE_COLORS = ['#2563EB', '#3B82F6', '#60A5FA']

// Invert Y axis for rankings (lower = better)
const CustomYAxis = ({ ...props }) => <YAxis {...props} reversed domain={[1, 'dataMax + 5']} />

function buildChartData(keywords) {
  const top = keywords.slice(0, 3)
  if (!top.length) return []
  return top[0].history.map((point, i) => {
    const row = { date: point.date }
    top.forEach((kw, idx) => { row[`pos${idx + 1}`] = kw.history[i]?.position })
    return row
  })
}

export default function RankingsPage() {
  const project = useProjectInfo()
  const businessType = project.business_type
  const baseLocation = project.base_location
  const website = project.website
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!businessType || !baseLocation) return
    setLoading(true)
    setError('')
    getRankings(businessType, baseLocation, website)
      .then(res => setData(res.data))
      .catch(e => setError(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [businessType, baseLocation, website])

  if (!businessType || !baseLocation) {
    return (
      <div className="space-y-5 fade-in">
        <div>
          <h1 className="text-xl font-bold text-white">Rank Tracking</h1>
          <p className="text-sm text-slate-500 mt-0.5">Position history for your tracked keywords</p>
        </div>
        <div className="card flex flex-col items-center justify-center py-16 text-slate-500">
          <Search size={32} className="mb-3 opacity-30" />
          <p className="text-sm">Set up your business in SEO Content or Onboarding first — Rank Tracking follows whatever business type and location you're targeting there.</p>
        </div>
      </div>
    )
  }

  const keywords = data?.keywords || []
  const chartData = buildChartData(keywords)

  return (
    <div className="space-y-5 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Rank Tracking</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {businessType} · {baseLocation} · {keywords.length} keywords tracked
          </p>
        </div>
      </div>

      {loading && (
        <div className="card flex items-center justify-center py-16 text-slate-500 text-sm">Loading rankings...</div>
      )}
      {error && <div className="alert alert-error">⚠ {error}</div>}

      {!loading && !error && keywords.length > 0 && (
        <>
          {/* Summary */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Top 3 Positions', value: keywords.filter(k => k.position <= 3).length },
              { label: 'Top 10 Positions', value: keywords.filter(k => k.position <= 10).length },
              { label: 'Avg. Position', value: (keywords.reduce((s, k) => s + k.position, 0) / keywords.length).toFixed(1) },
              { label: 'Improved', value: keywords.filter(k => k.previous_position > k.position).length },
            ].map(s => (
              <div key={s.label} className="card p-4">
                <div className="text-xs text-slate-500 mb-1">{s.label}</div>
                <div className="text-2xl font-bold text-white">{s.value}</div>
              </div>
            ))}
          </div>

          {/* Chart */}
          <div className="card p-5">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h3 className="text-sm font-semibold text-white">Position History</h3>
                <p className="text-xs text-slate-500 mt-0.5">Lower is better · Top 3 tracked keywords</p>
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-500">
                {keywords.slice(0, 3).map((kw, i) => (
                  <span key={kw.keyword} className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 inline-block rounded" style={{ background: LINE_COLORS[i] }} />
                    {kw.keyword}
                  </span>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={chartData} margin={{ left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A3B57" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <CustomYAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: '#1E2940', border: '1px solid #2A3B57', borderRadius: 8, fontSize: 12, color: '#F1F5F9' }}
                  labelStyle={{ color: '#94A3B8' }}
                  formatter={(v) => [`#${v}`, '']}
                />
                {keywords.slice(0, 3).map((_, i) => (
                  <Line key={i} type="monotone" dataKey={`pos${i + 1}`} stroke={LINE_COLORS[i]} strokeWidth={2} dot={{ r: 3, fill: LINE_COLORS[i] }} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Rankings table */}
          <div className="card">
            <div className="px-5 py-4 border-b border-white/5 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">All Tracked Keywords</h3>
              <span className="text-xs text-slate-500">{keywords.length} keywords</span>
            </div>
            <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Keyword</th>
                  <th>Current Position</th>
                  <th>Change</th>
                  <th>Search Volume</th>
                  <th>URL</th>
                </tr>
              </thead>
              <tbody>
                {keywords.map(kw => {
                  const change = kw.previous_position - kw.position
                  return (
                    <tr key={kw.keyword}>
                      <td className="text-slate-200 font-medium max-w-[220px] truncate">{kw.keyword}</td>
                      <td>
                        <span className={`text-base font-bold ${kw.position <= 3 ? 'text-emerald-400' : kw.position <= 10 ? 'text-amber-400' : 'text-slate-400'}`}>
                          #{kw.position}
                        </span>
                      </td>
                      <td>
                        <span className={`flex items-center gap-1 text-xs font-semibold ${change > 0 ? 'text-emerald-400' : change < 0 ? 'text-red-400' : 'text-slate-500'}`}>
                          {change > 0 ? <TrendingUp size={11} /> : change < 0 ? <TrendingDown size={11} /> : <Minus size={11} />}
                          {change === 0 ? '—' : Math.abs(change)}
                        </span>
                      </td>
                      <td className="text-slate-300">{kw.volume.toLocaleString()}</td>
                      <td className="text-xs max-w-[140px] truncate">
                        <a href={kw.url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline">{kw.url}</a>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
