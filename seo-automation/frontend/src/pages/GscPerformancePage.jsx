import { useEffect, useState } from 'react'
import { LineChart as ReLine, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { RefreshCw, CheckCircle2, AlertTriangle } from 'lucide-react'
import { getGscPerformance } from '../api'

export default function GscPerformancePage() {
  const [days, setDays] = useState(28)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async (d = days) => {
    setLoading(true)
    setError('')
    try {
      const res = await getGscPerformance(d)
      setData(res.data)
      if (!res.data?.ok && res.data?.detail) setError(res.data.detail)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Could not load Search Console.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load(days) }, [days])

  const conn = data?.connection || {}
  const totals = data?.totals || { clicks: 0, impressions: 0, ctr: 0, position: 0 }
  const live = !!conn.configured

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>
            Search Console
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-3)', maxWidth: 640 }}>
            Live Google Search traffic for the verified property. Data lags 2–3 days.
            This is impressions and clicks — not ChatGPT citations and not a ranking guarantee.
          </p>
        </div>
        <div className="flex gap-2">
          {[7, 28, 90].map((n) => (
            <button
              key={n}
              type="button"
              className={days === n ? 'btn btn-primary' : 'btn btn-secondary'}
              onClick={() => setDays(n)}
            >
              {n}d
            </button>
          ))}
          <button type="button" className="btn btn-secondary" onClick={() => load(days)} disabled={loading}>
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
        </div>
      </div>

      <div className="card p-4" style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
        {live ? <CheckCircle2 size={18} style={{ color: 'var(--green)', marginTop: 2 }} /> : <AlertTriangle size={18} style={{ color: 'var(--amber)', marginTop: 2 }} />}
        <div style={{ fontSize: 13, color: 'var(--text-2)', lineHeight: 1.5 }}>
          <strong style={{ color: 'var(--text-1)' }}>{live ? 'Connected' : 'Not connected'}</strong>
          {' · '}Property: {conn.gsc_site_url || '—'}
          {conn.key_exists ? ' · key file found' : ' · key file missing'}
          {conn.auth_error ? ` · ${conn.auth_error}` : ''}
          {conn.probe ? ` · ${conn.probe}` : ''}
          <div style={{ fontSize: 12, color: 'var(--text-4)', marginTop: 4 }}>
            {data?.start_date && data?.end_date ? `Window ${data.start_date} → ${data.end_date}` : conn.note}
          </div>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12 }}>
        {[
          ['Clicks', totals.clicks],
          ['Impressions', totals.impressions],
          ['CTR', `${totals.ctr}%`],
          ['Avg position', totals.position || '—'],
        ].map(([label, value]) => (
          <div key={label} className="card p-4">
            <div style={{ fontSize: 11, color: 'var(--text-4)', fontWeight: 600 }}>{label}</div>
            <div style={{ fontSize: 22, fontWeight: 750, marginTop: 6, color: 'var(--text-1)' }}>{value}</div>
          </div>
        ))}
      </div>

      <div className="card p-5" style={{ height: 280 }}>
        <h2 style={{ fontSize: 15, fontWeight: 700, margin: '0 0 12px', color: 'var(--text-1)' }}>Clicks and impressions</h2>
        {(data?.by_date || []).length === 0 ? (
          <p style={{ fontSize: 13, color: 'var(--text-3)' }}>
            {live ? 'No Search Analytics rows in this window yet. New sites often show zeros until Google has impressions.' : 'Connect Search Console to load the chart.'}
          </p>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <ReLine data={data.by_date} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="clicks" name="Clicks" stroke="#2563EB" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="impressions" name="Impressions" stroke="#94a3b8" dot={false} strokeWidth={2} />
            </ReLine>
          </ResponsiveContainer>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
        <div className="card p-5" style={{ overflowX: 'auto' }}>
          <h2 style={{ fontSize: 15, fontWeight: 700, margin: '0 0 12px', color: 'var(--text-1)' }}>Top queries</h2>
          <PerfTable rows={data?.queries} nameKey="query" />
        </div>
        <div className="card p-5" style={{ overflowX: 'auto' }}>
          <h2 style={{ fontSize: 15, fontWeight: 700, margin: '0 0 12px', color: 'var(--text-1)' }}>Top pages</h2>
          <PerfTable rows={data?.pages} nameKey="page" />
        </div>
      </div>
    </div>
  )
}

function PerfTable({ rows, nameKey }) {
  const list = rows || []
  if (!list.length) {
    return <p style={{ fontSize: 13, color: 'var(--text-3)' }}>No rows.</p>
  }
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
      <thead>
        <tr style={{ textAlign: 'left', color: 'var(--text-4)' }}>
          <th style={{ padding: '6px 4px' }}> </th>
          <th style={{ padding: '6px 4px' }}>Clicks</th>
          <th style={{ padding: '6px 4px' }}>Impr.</th>
          <th style={{ padding: '6px 4px' }}>Pos</th>
        </tr>
      </thead>
      <tbody>
        {list.slice(0, 25).map((row) => (
          <tr key={row[nameKey]} style={{ borderTop: '1px solid var(--border)' }}>
            <td style={{ padding: '7px 4px', wordBreak: 'break-all', maxWidth: 280 }}>{row[nameKey]}</td>
            <td style={{ padding: '7px 4px' }}>{row.clicks}</td>
            <td style={{ padding: '7px 4px' }}>{row.impressions}</td>
            <td style={{ padding: '7px 4px' }}>{row.position}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
