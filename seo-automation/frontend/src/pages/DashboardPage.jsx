import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { TrendingUp, Search, FileText, Globe, ArrowUpRight, AlertCircle, Briefcase, Users, MessageSquare, Zap } from 'lucide-react'
import StatCard from '../components/StatCard'
import { TRAFFIC_TREND, INTENT_DIST, CITIES_DATA, KEYWORD_DATA } from '../data/mockData'
import { useState, useEffect } from 'react'
import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || '/api'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="card px-3 py-2 text-xs shadow-xl">
      <div className="text-slate-400 mb-1">{label}</div>
      {payload.map(p => (
        <div key={p.name} className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-slate-300">{p.name}:</span>
          <span className="text-white font-semibold">{p.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  )
}

export default function DashboardPage() {
  const topKws = KEYWORD_DATA.slice(0, 5)
  const [mpStats, setMpStats] = useState(null)

  useEffect(() => {
    const token = localStorage.getItem('mp_token')
    if (!token) return
    axios.get(`${BASE}/marketplace/admin/stats`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => setMpStats(r.data)).catch(() => {})
  }, [])

  return (
    <div className="space-y-6 fade-in">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Overview</h1>
          <p className="text-sm text-slate-500 mt-0.5">San Diego Plumbing · Last 30 days</p>
        </div>
        <div className="flex items-center gap-2">
          <select className="rounded-lg px-3 py-2 text-sm transition-all"
            style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)', color: 'var(--text-primary)' }}>
            <option>Last 30 days</option>
            <option>Last 90 days</option>
            <option>Last 12 months</option>
          </select>
          <button className="btn-primary flex items-center gap-1.5 px-4 py-2 rounded-lg text-white text-sm font-semibold">
            <ArrowUpRight size={14} /> Export Report
          </button>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Organic Traffic" value="11,200" delta="+18%" sub="vs last month" accent="indigo"
          icon={<TrendingUp size={14} className="text-indigo-400" />} />
        <StatCard label="Tracked Keywords" value="48" delta="+6" sub="ranking in top 20" accent="violet"
          icon={<Search size={14} className="text-violet-400" />} />
        <StatCard label="Pages Generated" value="50" delta="+50" sub="this month" accent="emerald"
          icon={<FileText size={14} className="text-emerald-400" />} />
        <StatCard label="Cities Covered" value="50" delta="+50" sub="San Diego area" accent="sky"
          icon={<Globe size={14} className="text-sky-400" />} />
      </div>

      {/* Marketplace KPIs */}
      {mpStats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total Users"    value={mpStats.total_users}         delta="" sub="on platform"    accent="indigo"
            icon={<Users size={14} className="text-indigo-400" />} />
          <StatCard label="Open Requests"  value={mpStats.open_requests}       delta="" sub="awaiting quotes" accent="emerald"
            icon={<Briefcase size={14} className="text-emerald-400" />} />
          <StatCard label="Total Quotes"   value={mpStats.total_quotes}        delta="" sub="submitted"      accent="violet"
            icon={<FileText size={14} className="text-violet-400" />} />
          <StatCard label="Credits Sold"   value={mpStats.total_credits_sold}  delta="" sub="all time"       accent="amber"
            icon={<Zap size={14} className="text-amber-400" />} />
        </div>
      )}

      {/* Charts row */}
      <div className="grid lg:grid-cols-3 gap-4">
        {/* Traffic trend */}
        <div className="card p-5 lg:col-span-2">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-sm font-semibold text-white">Organic Traffic Trend</h2>
              <p className="text-xs text-slate-500 mt-0.5">Monthly organic vs paid sessions</p>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-500">
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-0.5 rounded bg-indigo-500 inline-block" />Organic</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-0.5 rounded bg-slate-600 inline-block" />Paid</span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={TRAFFIC_TREND} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="orgGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="organic" name="Organic" stroke="#6366f1" strokeWidth={2} fill="url(#orgGrad)" />
              <Area type="monotone" dataKey="paid" name="Paid" stroke="#475569" strokeWidth={1.5} fill="none" strokeDasharray="4 2" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Intent distribution */}
        <div className="card p-5">
          <h2 className="text-sm font-semibold text-white mb-1">Keyword Intent</h2>
          <p className="text-xs text-slate-500 mb-4">Distribution across tracked keywords</p>
          <div className="flex justify-center mb-4">
            <PieChart width={140} height={140}>
              <Pie data={INTENT_DIST} cx={65} cy={65} innerRadius={42} outerRadius={62} paddingAngle={3} dataKey="value">
                {INTENT_DIST.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
            </PieChart>
          </div>
          <div className="space-y-2">
            {INTENT_DIST.map(d => (
              <div key={d.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: d.color }} />
                  <span className="text-slate-400">{d.name}</span>
                </div>
                <span className="text-slate-200 font-semibold">{d.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid lg:grid-cols-2 gap-4">
        {/* Top keywords */}
        <div className="card">
          <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
            <h2 className="text-sm font-semibold text-white">Top Keywords</h2>
            <a href="/keywords" className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">View all →</a>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Keyword</th>
                <th>Position</th>
                <th>Volume</th>
                <th>Difficulty</th>
              </tr>
            </thead>
            <tbody>
              {topKws.map(kw => (
                <tr key={kw.keyword}>
                  <td className="text-slate-200 max-w-[180px] truncate">{kw.keyword}</td>
                  <td>
                    <span className={`font-bold ${kw.position <= 3 ? 'text-emerald-400' : kw.position <= 10 ? 'text-amber-400' : 'text-slate-400'}`}>
                      #{kw.position}
                    </span>
                  </td>
                  <td className="text-slate-300">{kw.volume.toLocaleString()}</td>
                  <td>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${kw.difficulty < 30 ? 'diff-easy' : kw.difficulty < 55 ? 'diff-medium' : 'diff-hard'}`}>
                      {kw.difficulty}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* City coverage */}
        <div className="card">
          <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
            <h2 className="text-sm font-semibold text-white">City Coverage</h2>
            <a href="/content" className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">Manage →</a>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>City</th>
                <th>SEO Score</th>
                <th>Traffic</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {CITIES_DATA.map(c => (
                <tr key={c.city}>
                  <td className="text-slate-200 font-medium">{c.city}</td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 rounded-full bg-white/8 overflow-hidden">
                        <div className="h-full rounded-full bg-indigo-500" style={{ width: `${c.score}%` }} />
                      </div>
                      <span className="text-xs text-slate-400">{c.score}</span>
                    </div>
                  </td>
                  <td className="text-slate-300">{c.traffic.toLocaleString()}</td>
                  <td>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${c.status === 'live' ? 'text-emerald-400 bg-emerald-400/10' : 'text-amber-400 bg-amber-400/10'}`}>
                      {c.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alerts */}
      <div className="card p-4">
        <div className="flex items-center gap-2 mb-3">
          <AlertCircle size={14} className="text-amber-400" />
          <h2 className="text-sm font-semibold text-white">Insights & Recommendations</h2>
        </div>
        <div className="grid md:grid-cols-3 gap-3">
          {[
            { color: 'border-indigo-500/30 bg-indigo-500/5', icon: '🎯', text: '12 keywords ranking on page 2 — optimize content to push to page 1' },
            { color: 'border-amber-500/30 bg-amber-500/5', icon: '⚠️', text: '8 city pages have SEO score below 75 — review and regenerate' },
            { color: 'border-emerald-500/30 bg-emerald-500/5', icon: '📈', text: '"drain cleaning san diego" moved from #6 to #3 this week' },
          ].map((a, i) => (
            <div key={i} className={`rounded-lg border p-3 ${a.color}`}>
              <div className="text-base mb-1">{a.icon}</div>
              <p className="text-xs text-slate-400 leading-relaxed">{a.text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Marketplace quick links */}
      <div className="card p-5">
        <div className="flex items-center gap-2 mb-4">
          <Briefcase size={14} className="text-indigo-400" />
          <h2 className="text-sm font-semibold text-white">Marketplace</h2>
          <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400">New</span>
        </div>
        <div className="grid md:grid-cols-3 gap-3">
          {[
            { href: '/marketplace',   icon: '🔍', title: 'Browse Requests',     desc: 'Find clients looking for SEO, web dev, and marketing services', color: 'border-indigo-500/30 bg-indigo-500/5' },
            { href: '/professionals', icon: '👥', title: 'Find Professionals',  desc: 'Hire verified SEO experts and digital marketers', color: 'border-violet-500/30 bg-violet-500/5' },
            { href: '/credits',       icon: '⚡', title: 'Buy Credits',         desc: 'Get credits to respond to leads and unlock premium features', color: 'border-amber-500/30 bg-amber-500/5' },
          ].map(item => (
            <a key={item.href} href={item.href}
              className={`rounded-xl border p-4 block transition-all hover:scale-[1.01] ${item.color}`}
              style={{ textDecoration: 'none' }}>
              <div className="text-xl mb-2">{item.icon}</div>
              <p className="text-sm font-semibold text-white">{item.title}</p>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">{item.desc}</p>
            </a>
          ))}
        </div>
      </div>
    </div>
  )
}
