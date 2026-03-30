import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { Download, FileText, Calendar } from 'lucide-react'
import { TRAFFIC_TREND, CITIES_DATA } from '../data/mockData'

const REPORTS = [
  { name: 'Monthly SEO Performance', date: 'Mar 2026', pages: 50, traffic: 11200, status: 'ready' },
  { name: 'Keyword Rankings Report', date: 'Mar 2026', pages: 12, traffic: null, status: 'ready' },
  { name: 'Competitor Analysis', date: 'Feb 2026', pages: 5, traffic: null, status: 'ready' },
  { name: 'Content Audit Report', date: 'Feb 2026', pages: 50, traffic: 9800, status: 'ready' },
]

export default function ReportsPage() {
  return (
    <div className="space-y-5 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Reports</h1>
          <p className="text-sm text-slate-500 mt-0.5">Performance summaries and exports</p>
        </div>
        <button className="btn-primary flex items-center gap-1.5 px-4 py-2 rounded-lg text-white text-sm font-semibold">
          <FileText size={13} /> Generate Report
        </button>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        {/* Traffic summary */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-white mb-1">Traffic Growth</h3>
          <p className="text-xs text-slate-500 mb-4">8-month organic traffic trend</p>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={TRAFFIC_TREND} margin={{ left: -20 }}>
              <defs>
                <linearGradient id="tGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 12 }} labelStyle={{ color: '#94a3b8' }} />
              <Area type="monotone" dataKey="organic" name="Organic" stroke="#6366f1" strokeWidth={2} fill="url(#tGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* City performance */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-white mb-1">City Performance</h3>
          <p className="text-xs text-slate-500 mb-4">Traffic by city page</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={CITIES_DATA} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="city" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 12 }} labelStyle={{ color: '#94a3b8' }} />
              <Bar dataKey="traffic" name="Traffic" fill="#8b5cf6" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Report library */}
      <div className="card">
        <div className="px-5 py-4 border-b border-white/5">
          <h3 className="text-sm font-semibold text-white">Report Library</h3>
        </div>
        <div className="divide-y divide-white/4">
          {REPORTS.map(r => (
            <div key={r.name} className="flex items-center justify-between px-5 py-4 hover:bg-white/2 transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                  <FileText size={13} className="text-indigo-400" />
                </div>
                <div>
                  <div className="text-sm font-medium text-slate-200">{r.name}</div>
                  <div className="text-xs text-slate-500 flex items-center gap-2 mt-0.5">
                    <Calendar size={10} /> {r.date}
                    {r.traffic && <span>· {r.traffic.toLocaleString()} sessions</span>}
                    {r.pages && <span>· {r.pages} pages</span>}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">
                  {r.status}
                </span>
                <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/8 text-slate-300 text-xs hover:bg-white/8 transition-colors">
                  <Download size={11} /> Download
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Pages Generated', value: '50', sub: 'this month' },
          { label: 'Avg. SEO Score', value: '81/100', sub: 'across all pages' },
          { label: 'Total Organic Traffic', value: '11,200', sub: 'monthly sessions' },
          { label: 'Cost Saved vs Agency', value: '$8,400', sub: 'estimated monthly' },
        ].map(s => (
          <div key={s.label} className="card p-4">
            <div className="text-xs text-slate-500 mb-1">{s.label}</div>
            <div className="text-xl font-bold text-white">{s.value}</div>
            <div className="text-xs text-slate-600 mt-0.5">{s.sub}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
