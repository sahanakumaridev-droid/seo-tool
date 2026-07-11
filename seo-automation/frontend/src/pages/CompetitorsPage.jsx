import { useState } from 'react'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import { ExternalLink, TrendingUp, TrendingDown } from 'lucide-react'
import { COMPETITOR_DATA } from '../data/mockData'

const radarData = [
  { metric: 'Traffic', you: 72, avg: 58 },
  { metric: 'Keywords', you: 48, avg: 65 },
  { metric: 'Backlinks', you: 34, avg: 52 },
  { metric: 'Content', you: 81, avg: 60 },
  { metric: 'Tech SEO', you: 76, avg: 55 },
  { metric: 'Local SEO', you: 88, avg: 48 },
]

export default function CompetitorsPage() {
  const [selected, setSelected] = useState(null)

  return (
    <div className="space-y-5 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Competitor Analysis</h1>
          <p className="text-sm text-slate-500 mt-0.5">Tracking {COMPETITOR_DATA.length} competitors · Plumbing · San Diego</p>
        </div>
        <button className="btn-primary px-4 py-2 rounded-lg text-white text-sm font-semibold">
          + Add Competitor
        </button>
      </div>

      {/* Competitor cards */}
      <div className="grid lg:grid-cols-5 gap-3">
        {COMPETITOR_DATA.map((c, i) => (
          <div
            key={c.domain}
            onClick={() => setSelected(selected === i ? null : i)}
            className={`card card-hover p-4 cursor-pointer transition-all ${selected === i ? 'border-indigo-500/40 bg-indigo-500/5' : ''}`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-7 h-7 rounded-lg bg-white/8 flex items-center justify-center text-xs font-bold text-slate-300">
                {c.domain[0].toUpperCase()}
              </div>
              <span className="text-xs text-slate-500">DA {c.da}</span>
            </div>
            <div className="text-xs font-semibold text-slate-200 truncate mb-2">{c.domain}</div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Traffic</span>
                <span className="text-slate-300 font-medium">{(c.traffic / 1000).toFixed(1)}K</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Keywords</span>
                <span className="text-slate-300 font-medium">{c.keywords.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Overlap</span>
                <span className="text-indigo-400 font-medium">{c.overlap}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        {/* Radar comparison */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-white mb-1">Competitive Position</h3>
          <p className="text-xs text-slate-500 mb-4">You vs. market average across key SEO factors</p>
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.06)" />
              <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11, fill: '#64748b' }} />
              <Radar name="You" dataKey="you" stroke="#1D4ED8" fill="#1D4ED8" fillOpacity={0.15} strokeWidth={2} />
              <Radar name="Avg" dataKey="avg" stroke="#475569" fill="#475569" fillOpacity={0.08} strokeWidth={1.5} strokeDasharray="4 2" />
            </RadarChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 text-xs text-slate-500 mt-2">
            <span className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-indigo-500 inline-block rounded" />You</span>
            <span className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-slate-600 inline-block rounded" />Market Avg</span>
          </div>
        </div>

        {/* Traffic comparison bar */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-white mb-1">Traffic Comparison</h3>
          <p className="text-xs text-slate-500 mb-4">Estimated monthly organic sessions</p>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart
              data={[{ name: 'You', traffic: 11200 }, ...COMPETITOR_DATA.map(c => ({ name: c.domain.split('.')[0], traffic: c.traffic }))]}
              margin={{ left: -20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#2A3B57" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: '#1E2940', border: '1px solid #2A3B57', borderRadius: 8, fontSize: 12, color: '#F1F5F9' }}
                labelStyle={{ color: '#94A3B8' }}
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Bar dataKey="traffic" name="Traffic" radius={[4, 4, 0, 0]}
                fill="#1D4ED8"
                label={false}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Competitor detail table */}
      <div className="card">
        <div className="px-5 py-4 border-b border-white/5">
          <h3 className="text-sm font-semibold text-white">Competitor Overview</h3>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Domain</th>
              <th>Est. Traffic</th>
              <th>Keywords</th>
              <th>Keyword Overlap</th>
              <th>Domain Authority</th>
              <th>Keyword Gap</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {COMPETITOR_DATA.map(c => (
              <tr key={c.domain}>
                <td>
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded bg-white/8 flex items-center justify-center text-xs font-bold text-slate-400">
                      {c.domain[0].toUpperCase()}
                    </div>
                    <span className="text-slate-200 font-medium">{c.domain}</span>
                  </div>
                </td>
                <td>
                  <div className="flex items-center gap-1.5">
                    <TrendingUp size={12} className="text-emerald-400" />
                    <span className="text-slate-300">{c.traffic.toLocaleString()}</span>
                  </div>
                </td>
                <td className="text-slate-300">{c.keywords.toLocaleString()}</td>
                <td>
                  <div className="flex items-center gap-2">
                    <div className="w-20 h-1.5 rounded-full bg-white/8 overflow-hidden">
                      <div className="h-full rounded-full bg-indigo-500" style={{ width: `${c.overlap}%` }} />
                    </div>
                    <span className="text-xs text-slate-400">{c.overlap}%</span>
                  </div>
                </td>
                <td>
                  <span className={`text-sm font-bold ${c.da >= 45 ? 'text-red-400' : c.da >= 35 ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {c.da}
                  </span>
                </td>
                <td>
                  <span className="text-indigo-400 font-semibold">+{c.gap} kws</span>
                </td>
                <td>
                  <button className="p-1.5 rounded-lg hover:bg-white/8 text-slate-500 hover:text-slate-300 transition-colors">
                    <ExternalLink size={12} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
