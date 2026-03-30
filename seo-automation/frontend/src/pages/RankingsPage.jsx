import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { RANKING_HISTORY, KEYWORD_DATA } from '../data/mockData'

// Invert Y axis for rankings (lower = better)
const CustomYAxis = ({ ...props }) => <YAxis {...props} reversed domain={[1, 20]} />

export default function RankingsPage() {
  const chartData = RANKING_HISTORY

  return (
    <div className="space-y-5 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Rank Tracking</h1>
          <p className="text-sm text-slate-500 mt-0.5">Position history · {KEYWORD_DATA.length} keywords tracked</p>
        </div>
        <div className="flex gap-2">
          {['7d', '30d', '90d', '1y'].map(r => (
            <button key={r} className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${r === '30d' ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-600/30' : 'text-slate-500 hover:text-slate-300 hover:bg-white/4'}`}>
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Top 3 Positions', value: KEYWORD_DATA.filter(k => k.position <= 3).length, delta: '+2', up: true },
          { label: 'Top 10 Positions', value: KEYWORD_DATA.filter(k => k.position <= 10).length, delta: '+4', up: true },
          { label: 'Avg. Position', value: (KEYWORD_DATA.reduce((s, k) => s + k.position, 0) / KEYWORD_DATA.length).toFixed(1), delta: '-1.2', up: true },
          { label: 'Position Drops', value: 2, delta: '-1', up: true },
        ].map(s => (
          <div key={s.label} className="card p-4">
            <div className="text-xs text-slate-500 mb-1">{s.label}</div>
            <div className="flex items-end gap-2">
              <span className="text-2xl font-bold text-white">{s.value}</span>
              <span className={`text-xs font-semibold mb-0.5 flex items-center gap-0.5 ${s.up ? 'text-emerald-400' : 'text-red-400'}`}>
                {s.up ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
                {s.delta}
              </span>
            </div>
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
            <span className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-indigo-400 inline-block rounded" />plumbing services sd</span>
            <span className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-violet-400 inline-block rounded" />plumber near me</span>
            <span className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-sky-400 inline-block rounded" />emergency plumber</span>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={chartData} margin={{ left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
            <CustomYAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: '#94a3b8' }}
              formatter={(v) => [`#${v}`, '']}
            />
            <Line type="monotone" dataKey="pos1" stroke="#818cf8" strokeWidth={2} dot={{ r: 3, fill: '#818cf8' }} />
            <Line type="monotone" dataKey="pos2" stroke="#a78bfa" strokeWidth={2} dot={{ r: 3, fill: '#a78bfa' }} />
            <Line type="monotone" dataKey="pos3" stroke="#38bdf8" strokeWidth={2} dot={{ r: 3, fill: '#38bdf8' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Rankings table */}
      <div className="card">
        <div className="px-5 py-4 border-b border-white/5 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">All Tracked Keywords</h3>
          <span className="text-xs text-slate-500">{KEYWORD_DATA.length} keywords</span>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Keyword</th>
              <th>Current Position</th>
              <th>Change</th>
              <th>Search Volume</th>
              <th>Best Position</th>
              <th>URL</th>
            </tr>
          </thead>
          <tbody>
            {KEYWORD_DATA.map((kw, i) => {
              const change = [-2, 1, 0, -1, 3, -1, 2, 0, -3, 1, 4, -2][i % 12]
              return (
                <tr key={kw.keyword}>
                  <td className="text-slate-200 font-medium max-w-[220px] truncate">{kw.keyword}</td>
                  <td>
                    <span className={`text-base font-bold ${kw.position <= 3 ? 'text-emerald-400' : kw.position <= 10 ? 'text-amber-400' : 'text-slate-400'}`}>
                      #{kw.position}
                    </span>
                  </td>
                  <td>
                    <span className={`flex items-center gap-1 text-xs font-semibold ${change < 0 ? 'text-emerald-400' : change > 0 ? 'text-red-400' : 'text-slate-500'}`}>
                      {change < 0 ? <TrendingUp size={11} /> : change > 0 ? <TrendingDown size={11} /> : <Minus size={11} />}
                      {change === 0 ? '—' : Math.abs(change)}
                    </span>
                  </td>
                  <td className="text-slate-300">{kw.volume.toLocaleString()}</td>
                  <td className="text-slate-400">#{Math.max(1, kw.position - 2)}</td>
                  <td className="text-xs text-indigo-400 truncate max-w-[140px]">
                    /{kw.keyword.split(' ').slice(0, 2).join('-')}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
