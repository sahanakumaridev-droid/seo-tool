import { useEffect, useMemo, useState } from 'react'
import { LineChart as ReLine, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { CheckCircle2, AlertTriangle, Plus, Download, Copy, ExternalLink, Search, X } from 'lucide-react'
import { getGscConnection, getGscPerformance, inspectSeoIndexingUrl } from '../api'

const RANGES = [
  { id: '1', label: '24 hours', days: 1 },
  { id: '7', label: '7 days', days: 7 },
  { id: '28', label: '28 days', days: 28 },
  { id: '90', label: '3 months', days: 90 },
  { id: 'custom', label: 'Custom', days: null },
]

const SEARCH_TYPES = [
  { id: 'web', label: 'Web' },
  { id: 'image', label: 'Image' },
  { id: 'video', label: 'Video' },
  { id: 'news', label: 'News' },
  { id: 'discover', label: 'Discover' },
]

const FILTER_KINDS = [
  { id: 'query', label: 'Query' },
  { id: 'page', label: 'Page' },
  { id: 'device', label: 'Device' },
  { id: 'country', label: 'Country' },
]

function emptyDraft() {
  return { query: '', page: '', device: '', country: '' }
}

function csvEscape(v) {
  const s = String(v ?? '')
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}

export default function GscPerformancePage() {
  const [rangeId, setRangeId] = useState('28')
  const [customStart, setCustomStart] = useState('')
  const [customEnd, setCustomEnd] = useState('')
  const [searchType, setSearchType] = useState('web')
  const [applied, setApplied] = useState(emptyDraft)
  const [addOpen, setAddOpen] = useState(false)
  const [addKind, setAddKind] = useState('query')
  const [addValue, setAddValue] = useState('')
  const [typeOpen, setTypeOpen] = useState(false)
  const [tab, setTab] = useState('pages')
  const [sortKey, setSortKey] = useState('clicks')
  const [sortDir, setSortDir] = useState('desc')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [inspectMsg, setInspectMsg] = useState('')

  const range = RANGES.find((r) => r.id === rangeId) || RANGES[2]
  const params = useMemo(() => {
    const p = { search_type: searchType }
    if (rangeId === 'custom' && customStart && customEnd) {
      p.start_date = customStart
      p.end_date = customEnd
      p.days = 28
    } else {
      p.days = range.days || 28
    }
    if (applied.query) p.query = applied.query
    if (applied.page) p.page = applied.page
    if (applied.device) p.device = applied.device
    if (applied.country) p.country = applied.country
    return p
  }, [rangeId, range.days, customStart, customEnd, searchType, applied])

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [connRes, perfRes] = await Promise.all([
        getGscConnection().catch(() => null),
        getGscPerformance(params),
      ])
      const perf = perfRes?.data || {}
      const conn = { ...(perf.connection || {}), ...(connRes?.data || {}) }
      setData({ ...perf, connection: conn })
      if (perf.ok === false && perf.detail && conn.configured !== true) setError(perf.detail)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Could not load Search Console.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [JSON.stringify(params)])

  const conn = data?.connection || {}
  const totals = data?.totals || { clicks: 0, impressions: 0, ctr: 0, position: 0 }
  const live = conn.configured !== false
  const property = conn.gsc_site_url || 'https://zeorbit.com/'
  const typeLabel = SEARCH_TYPES.find((t) => t.id === searchType)?.label || 'Web'

  const commitFilter = (kind, value) => {
    const v = (value || '').trim()
    if (!v) return
    setApplied((prev) => ({ ...prev, [kind]: v }))
    setAddOpen(false)
    setAddValue('')
  }

  const clearFilter = (kind) => {
    setApplied((prev) => ({ ...prev, [kind]: '' }))
  }

  const rows = useMemo(() => {
    const list = tab === 'pages' ? (data?.pages || []) : (data?.queries || [])
    const key = tab === 'pages' ? 'page' : 'query'
    const sorted = [...list].sort((a, b) => {
      const av = a[sortKey] ?? 0
      const bv = b[sortKey] ?? 0
      if (typeof av === 'string') return sortDir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av)
      return sortDir === 'asc' ? av - bv : bv - av
    })
    return { key, list: sorted }
  }, [data, tab, sortKey, sortDir])

  const toggleSort = (key) => {
    if (sortKey === key) setSortDir((d) => (d === 'desc' ? 'asc' : 'desc'))
    else { setSortKey(key); setSortDir('desc') }
  }

  const exportCsv = () => {
    const header = [tab === 'pages' ? 'Page' : 'Query', 'Clicks', 'Impressions', 'CTR', 'Position']
    const lines = [header.join(',')]
    rows.list.forEach((r) => {
      lines.push([r[rows.key], r.clicks, r.impressions, r.ctr, r.position].map(csvEscape).join(','))
    })
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `search-console-${tab}.csv`
    a.click()
    URL.revokeObjectURL(a.href)
  }

  const inspectUrl = async (url) => {
    setInspectMsg('Inspecting…')
    try {
      const res = await inspectSeoIndexingUrl({ url })
      const d = res.data || {}
      setInspectMsg(d.status || d.coverage_state || d.detail || 'Inspected')
    } catch (e) {
      setInspectMsg(e.response?.data?.detail || e.message || 'Inspect failed')
    }
  }

  const copyText = async (text) => {
    try { await navigator.clipboard.writeText(text) } catch { /* ignore */ }
  }

  return (
    <div className="gsc-perf fade-in">
      <div className="gsc-perf-head">
        <div>
          <p className="crm-crumb">Search Console · {property}</p>
          <h1>Performance</h1>
          <p className="gsc-perf-sub">
            Filter like Google Search Console. Data lags 2–3 days.
            {data?.start_date && data?.end_date ? ` · ${data.start_date} → ${data.end_date}` : ''}
            {loading ? ' · Updating…' : ' · Last update just now'}
          </p>
        </div>
        <button type="button" className="gsc-export" onClick={exportCsv}>
          <Download size={14} /> Export
        </button>
      </div>

      <div className="gsc-toolbar">
        <div className="gsc-range" role="tablist" aria-label="Date range">
          {RANGES.map((r) => (
            <button
              key={r.id}
              type="button"
              aria-pressed={rangeId === r.id}
              className={rangeId === r.id ? 'is-on' : ''}
              onClick={() => setRangeId(r.id)}
            >
              {r.label}
            </button>
          ))}
        </div>
        {rangeId === 'custom' && (
          <div className="gsc-custom">
            <input type="date" value={customStart} onChange={(e) => setCustomStart(e.target.value)} aria-label="Start date" />
            <span>to</span>
            <input type="date" value={customEnd} onChange={(e) => setCustomEnd(e.target.value)} aria-label="End date" />
          </div>
        )}

        <div className="gsc-chips">
          <div className="gsc-chip-wrap">
            <button type="button" className="gsc-chip" onClick={() => setTypeOpen((o) => !o)}>
              Search type: {typeLabel}
            </button>
            {typeOpen && (
              <div className="gsc-menu">
                {SEARCH_TYPES.map((t) => (
                  <button key={t.id} type="button" onClick={() => { setSearchType(t.id); setTypeOpen(false) }}>
                    {t.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {FILTER_KINDS.filter((k) => applied[k.id]).map((k) => (
            <span key={k.id} className="gsc-chip is-filter">
              {k.label}: +{applied[k.id]}
              <button type="button" aria-label={`Remove ${k.label} filter`} onClick={() => clearFilter(k.id)}>
                <X size={12} />
              </button>
            </span>
          ))}

          <div className="gsc-chip-wrap">
            <button type="button" className="gsc-add" onClick={() => setAddOpen((o) => !o)}>
              <Plus size={14} /> Add filter
            </button>
            {addOpen && (
              <div className="gsc-menu gsc-menu-wide">
                <label>
                  Filter
                  <select value={addKind} onChange={(e) => setAddKind(e.target.value)}>
                    {FILTER_KINDS.map((k) => <option key={k.id} value={k.id}>{k.label}</option>)}
                  </select>
                </label>
                {addKind === 'device' ? (
                  <label>
                    Device
                    <select value={addValue} onChange={(e) => setAddValue(e.target.value)}>
                      <option value="">Choose…</option>
                      <option value="DESKTOP">Desktop</option>
                      <option value="MOBILE">Mobile</option>
                      <option value="TABLET">Tablet</option>
                    </select>
                  </label>
                ) : (
                  <label>
                    Contains
                    <input
                      autoFocus
                      value={addValue}
                      onChange={(e) => setAddValue(e.target.value)}
                      onKeyDown={(e) => { if (e.key === 'Enter') commitFilter(addKind, addValue) }}
                      placeholder={addKind === 'query' ? 'e.g. mobile' : addKind === 'page' ? 'e.g. /local-seo' : 'e.g. usa'}
                    />
                  </label>
                )}
                <button type="button" className="gsc-apply" onClick={() => commitFilter(addKind, addValue)}>Apply</button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="card p-4" style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
        {live ? <CheckCircle2 size={18} style={{ color: 'var(--green)', marginTop: 2 }} /> : <AlertTriangle size={18} style={{ color: 'var(--amber)', marginTop: 2 }} />}
        <div style={{ fontSize: 13, color: 'var(--text-2)', lineHeight: 1.5 }}>
          <strong style={{ color: 'var(--text-1)' }}>{live ? 'Connected' : 'Not connected'}</strong>
          {' · '}{property}
          {inspectMsg ? ` · ${inspectMsg}` : ''}
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="gsc-kpis">
        {[
          ['Clicks', totals.clicks],
          ['Impressions', totals.impressions],
          ['CTR', `${totals.ctr}%`],
          ['Avg position', totals.position || '—'],
        ].map(([label, value]) => (
          <div key={label} className="card p-4">
            <div className="gsc-kpi-l">{label}</div>
            <div className="gsc-kpi-v">{value}</div>
          </div>
        ))}
      </div>

      <div className="card p-5" style={{ height: 280 }}>
        <h2 className="gsc-h2">Clicks and impressions</h2>
        {(data?.by_date || []).length === 0 ? (
          <p className="gsc-empty">
            {live ? 'No rows in this filter window yet.' : 'Search Console credentials are missing on the server.'}
          </p>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <ReLine data={data.by_date} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="clicks" name="Clicks" stroke="#1a73e8" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="impressions" name="Impressions" stroke="#7b61ff" dot={false} strokeWidth={2} />
            </ReLine>
          </ResponsiveContainer>
        )}
      </div>

      <div className="card p-0 gsc-table-card">
        <div className="gsc-table-head">
          <div className="gsc-tabs">
            <button type="button" className={tab === 'pages' ? 'is-on' : ''} onClick={() => setTab('pages')}>Top pages</button>
            <button type="button" className={tab === 'queries' ? 'is-on' : ''} onClick={() => setTab('queries')}>Top queries</button>
          </div>
          <span className="gsc-muted">{rows.list.length} rows</span>
        </div>
        <div className="gsc-table-scroll">
          <table className="gsc-table">
            <thead>
              <tr>
                <th>{tab === 'pages' ? 'Pages' : 'Queries'}</th>
                <th>
                  <button type="button" className="gsc-sort" onClick={() => toggleSort('clicks')}>
                    Clicks {sortKey === 'clicks' ? (sortDir === 'desc' ? '↓' : '↑') : ''}
                  </button>
                </th>
                <th>
                  <button type="button" className="gsc-sort is-impr" onClick={() => toggleSort('impressions')}>
                    Impressions {sortKey === 'impressions' ? (sortDir === 'desc' ? '↓' : '↑') : ''}
                  </button>
                </th>
                <th>
                  <button type="button" className="gsc-sort" onClick={() => toggleSort('position')}>
                    Pos {sortKey === 'position' ? (sortDir === 'desc' ? '↓' : '↑') : ''}
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.list.length === 0 && (
                <tr><td colSpan={4} className="gsc-empty" style={{ padding: 20 }}>No rows for these filters.</td></tr>
              )}
              {rows.list.map((row) => {
                const name = row[rows.key]
                return (
                  <tr key={name}>
                    <td>
                      <div className="gsc-url">
                        <span title={name}>{name}</span>
                        <span className="gsc-row-actions">
                          <button type="button" title="Copy" onClick={() => copyText(name)}><Copy size={13} /></button>
                          {tab === 'pages' && (
                            <>
                              <a href={name} target="_blank" rel="noreferrer" title="Open"><ExternalLink size={13} /></a>
                              <button type="button" title="Inspect URL" onClick={() => inspectUrl(name)}><Search size={13} /></button>
                            </>
                          )}
                        </span>
                      </div>
                    </td>
                    <td className="num">{row.clicks}</td>
                    <td className="num impr">{row.impressions}</td>
                    <td className="num">{row.position}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
