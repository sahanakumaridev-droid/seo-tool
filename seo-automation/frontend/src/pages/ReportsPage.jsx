import { useEffect, useMemo, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { Download, FileText, Calendar, Loader2 } from 'lucide-react'
import { listPages, getRankings } from '../api'
import useProjectInfo from '../hooks/useProjectInfo'

function downloadText(filename, text, type = 'text/plain') {
  const blob = new Blob([text], { type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export default function ReportsPage() {
  const project = useProjectInfo()
  const [pages, setPages] = useState([])
  const [rankings, setRankings] = useState([])
  const [loading, setLoading] = useState(true)
  const [note, setNote] = useState('')

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      setLoading(true)
      try {
        const pagesRes = await listPages(0, 100)
        if (cancelled) return
        const rows = Array.isArray(pagesRes.data) ? pagesRes.data : []
        setPages(rows)
        try {
          const r = await getRankings(project.business_type || '', project.base_location || '', '')
          if (!cancelled) setRankings(r.data?.keywords || [])
        } catch { /* optional */ }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [project.business_type, project.base_location])

  const cityPerf = useMemo(() => {
    const map = {}
    pages.forEach(p => {
      const city = p.city || p.seo_block?.city || 'Unknown'
      if (!map[city]) map[city] = { city, pages: 0, score: 0 }
      map[city].pages += 1
      map[city].score += Math.round(p.seo_block?.readability_score || 75)
    })
    return Object.values(map).map(c => ({
      city: c.city,
      pages: c.pages,
      score: Math.round(c.score / c.pages),
      traffic: c.pages * 180 + (c.score % 40) * 12,
    })).slice(0, 12)
  }, [pages])

  const trafficTrend = useMemo(() => {
    const months = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']
    const base = Math.max(8, pages.length) * 90
    return months.map((month, i) => ({
      month,
      organic: Math.round(base * (0.45 + i * 0.08)),
      paid: Math.round(base * (0.08 + i * 0.015)),
    }))
  }, [pages])

  const avgScore = pages.length
    ? Math.round(pages.reduce((s, p) => s + (p.seo_block?.readability_score || 75), 0) / pages.length)
    : 0

  const reports = [
    {
      id: 'seo-performance',
      name: 'SEO Performance Summary',
      date: new Date().toLocaleString('en-US', { month: 'short', year: 'numeric' }),
      pages: pages.length,
      traffic: cityPerf.reduce((s, c) => s + c.traffic, 0) || null,
      build: () => {
        const lines = [
          `SEO Performance Report`,
          `Website: ${project.website || '—'}`,
          `Niche: ${project.business_type || '—'}`,
          `Location: ${project.base_location || '—'}`,
          `Generated: ${new Date().toISOString()}`,
          ``,
          `Pages tracked: ${pages.length}`,
          `Avg SEO score: ${avgScore}/100`,
          ``,
          `City breakdown:`,
          ...cityPerf.map(c => `- ${c.city}: ${c.pages} pages, score ${c.score}`),
          ``,
          `Top ranking keywords:`,
          ...rankings.slice(0, 15).map(k => `- ${k.keyword}: pos ${k.position} (${k.url || ''})`),
        ]
        return lines.join('\n')
      },
    },
    {
      id: 'keyword-rankings',
      name: 'Keyword Rankings Report',
      date: new Date().toLocaleString('en-US', { month: 'short', year: 'numeric' }),
      pages: rankings.length,
      traffic: null,
      build: () => {
        const header = 'keyword,position,previous,volume,url\n'
        const body = rankings.map(k =>
          `"${k.keyword}",${k.position},${k.previous_position},${k.volume},"${k.url || ''}"`
        ).join('\n')
        return header + body
      },
      ext: 'csv',
    },
    {
      id: 'content-audit',
      name: 'Content Audit Report',
      date: new Date().toLocaleString('en-US', { month: 'short', year: 'numeric' }),
      pages: pages.length,
      traffic: null,
      build: () => {
        const header = 'city,state,slug,title,primary_keyword,score\n'
        const body = pages.map(p => {
          const b = p.seo_block || {}
          return `"${p.city || b.city || ''}","${p.state || b.state || ''}","${p.slug || ''}","${(b.title || '').replace(/"/g, "'")}","${b.keywords?.primary || ''}",${Math.round(b.readability_score || 75)}`
        }).join('\n')
        return header + body
      },
      ext: 'csv',
    },
  ]

  const generateAll = () => {
    if (!pages.length && !rankings.length) {
      setNote('No pages or rankings yet — generate SEO content for your profile first.')
      return
    }
    const report = reports[0]
    downloadText(
      `${report.id}-${(project.website || 'profile').replace(/\W+/g, '-')}.txt`,
      report.build(),
    )
    setNote('Report downloaded for the current profile website.')
  }

  return (
    <div className="space-y-5 fade-in">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-xl font-bold text-white">Reports</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Live summaries from {project.website || 'your profile'} · {project.base_location || 'set a location'}
          </p>
        </div>
        <button type="button" onClick={generateAll} className="btn-primary flex items-center gap-1.5 px-4 py-2 rounded-lg text-white text-sm font-semibold">
          <FileText size={13} /> Generate Report
        </button>
      </div>

      {note && <div className="card p-3 text-xs text-slate-300">{note}</div>}
      {loading && (
        <div className="card p-6 flex items-center gap-2 text-slate-400 text-sm">
          <Loader2 size={14} className="animate-spin" /> Building report data…
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-white mb-1">Traffic Growth</h3>
          <p className="text-xs text-slate-500 mb-4">Projected from generated page volume for this profile</p>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={trafficTrend} margin={{ left: -20 }}>
              <defs>
                <linearGradient id="tGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#1D4ED8" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#1D4ED8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A3B57" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#1E2940', border: '1px solid #2A3B57', borderRadius: 8, fontSize: 12, color: '#F1F5F9' }} />
              <Area type="monotone" dataKey="organic" name="Organic" stroke="#1D4ED8" strokeWidth={2} fill="url(#tGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-5">
          <h3 className="text-sm font-semibold text-white mb-1">City Performance</h3>
          <p className="text-xs text-slate-500 mb-4">From your generated location pages</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={cityPerf.length ? cityPerf : [{ city: '—', traffic: 0 }]} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A3B57" />
              <XAxis dataKey="city" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#1E2940', border: '1px solid #2A3B57', borderRadius: 8, fontSize: 12, color: '#F1F5F9' }} />
              <Bar dataKey="traffic" name="Est. traffic" fill="#2563EB" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="px-5 py-4 border-b border-white/5">
          <h3 className="text-sm font-semibold text-white">Report Library</h3>
        </div>
        <div className="divide-y divide-white/4">
          {reports.map(r => (
            <div key={r.id} className="flex items-center justify-between px-5 py-4 hover:bg-white/2 transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                  <FileText size={13} className="text-indigo-400" />
                </div>
                <div>
                  <div className="text-sm font-medium text-slate-200">{r.name}</div>
                  <div className="text-xs text-slate-500 flex items-center gap-2 mt-0.5">
                    <Calendar size={10} /> {r.date}
                    {r.traffic != null && <span>· {Number(r.traffic).toLocaleString()} est. sessions</span>}
                    {r.pages != null && <span>· {r.pages} items</span>}
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => {
                  const body = r.build()
                  downloadText(
                    `${r.id}.${r.ext || 'txt'}`,
                    body,
                    r.ext === 'csv' ? 'text/csv' : 'text/plain',
                  )
                  setNote(`Downloaded ${r.name}`)
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/8 text-slate-300 text-xs hover:bg-white/8 transition-colors"
              >
                <Download size={11} /> Download
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Pages Generated', value: String(pages.length), sub: 'in this account' },
          { label: 'Avg. SEO Score', value: pages.length ? `${avgScore}/100` : '—', sub: 'across saved pages' },
          { label: 'Keywords Tracked', value: String(rankings.length), sub: 'rank tracking set' },
          { label: 'Profile Website', value: project.website || 'Not set', sub: 'from onboarding' },
        ].map(s => (
          <div key={s.label} className="card p-4">
            <div className="text-xs text-slate-500 mb-1">{s.label}</div>
            <div className="text-lg font-bold text-white truncate">{s.value}</div>
            <div className="text-xs text-slate-600 mt-0.5">{s.sub}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
