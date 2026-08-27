import { useState, useEffect } from 'react'
import { ScanSearch, RefreshCw, ExternalLink, CheckCircle2, AlertTriangle, Clock, XCircle, HelpCircle, Rocket } from 'lucide-react'
import { getSeoIndexingStatus, getSeoIndexingSetup, pushAllSeoIndexing, refreshSeoIndexing, inspectSeoIndexingUrl, notifyBingIndexing } from '../api'

const STATUS_META = {
  published:              { label: 'Submitted',     color: 'var(--text-3)',  bg: 'var(--bg-raised)',   icon: Clock },
  published_awaiting_gsc: { label: 'Submitted',     color: 'var(--amber)',   bg: 'var(--amber-soft)',  icon: AlertTriangle },
  sitemap_added:          { label: 'Submitted',     color: 'var(--brand)',   bg: 'var(--brand-soft)',  icon: CheckCircle2 },
  sitemap_submitted:      { label: 'Submitted',     color: 'var(--brand)',   bg: 'var(--brand-soft)',  icon: CheckCircle2 },
  submitted:              { label: 'Submitted',     color: 'var(--brand)',   bg: 'var(--brand-soft)',  icon: CheckCircle2 },
  crawled:                { label: 'Crawled',       color: 'var(--amber)',   bg: 'var(--amber-soft)',  icon: Clock },
  discovered:             { label: 'Crawled',       color: 'var(--amber)',   bg: 'var(--amber-soft)',  icon: HelpCircle },
  indexed:                { label: 'Indexed',       color: 'var(--green)',   bg: 'var(--green-soft)',  icon: CheckCircle2 },
  not_indexed:            { label: 'Not Indexed',   color: 'var(--amber)',   bg: 'var(--amber-soft)',  icon: AlertTriangle },
  error:                  { label: 'Error / Failed', color: 'var(--red)',    bg: 'var(--red-soft)',    icon: XCircle },
}

function StatusBadge({ status }) {
  const meta = STATUS_META[status] || STATUS_META.published
  const Icon = meta.icon
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5, borderRadius: 6, padding: '3px 9px',
      fontSize: 11.5, fontWeight: 600, color: meta.color, background: meta.bg,
    }}>
      <Icon size={12} /> {meta.label}
    </span>
  )
}

export default function IndexingStatusPage() {
  const [rows, setRows] = useState([])
  const [gscConfigured, setGscConfigured] = useState(false)
  const [mode, setMode] = useState('crawl')
  const [demo, setDemo] = useState(false)
  const [setup, setSetup] = useState(null)
  const [bing, setBing] = useState(null)
  const [bingNote, setBingNote] = useState('')
  const [notifyingBing, setNotifyingBing] = useState(false)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [pushing, setPushing] = useState(false)
  const [pushNote, setPushNote] = useState('')
  const [inspectUrl, setInspectUrl] = useState('')
  const [inspecting, setInspecting] = useState(false)
  const [inspectError, setInspectError] = useState('')
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [res, setupRes] = await Promise.all([
        getSeoIndexingStatus(),
        getSeoIndexingSetup().catch(() => null),
      ])
      setRows(res.data.urls || [])
      setGscConfigured(!!res.data.gsc_configured)
      setDemo(!!res.data.demo)
      setMode(res.data.mode || (res.data.demo ? 'demo' : res.data.gsc_configured ? 'gsc' : 'crawl'))
      if (setupRes?.data) setSetup(setupRes.data)
      setBing(setupRes?.data?.bing || res.data.bing || null)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Could not load indexing status. Is the API running?')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      const res = await refreshSeoIndexing()
      if (res.data?.urls?.length) {
        setRows(res.data.urls)
        setDemo(!!res.data.demo)
        setMode(res.data.mode || mode)
      } else {
        await load()
      }
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Refresh failed.')
    } finally {
      setRefreshing(false)
    }
  }

  const handlePushAll = async () => {
    setPushing(true)
    setPushNote('')
    try {
      const res = await pushAllSeoIndexing()
      setRows(res.data.urls || [])
      setMode(res.data.mode || mode)
      setGscConfigured(!!res.data.gsc_configured)
      const sm = res.data.sitemap || {}
      setPushNote(
        res.data.gsc_configured
          ? `Tracked ${res.data.pages_tracked_new || 0} new pages. Sitemap submit: ${sm.ok ? 'OK' : (sm.detail || 'failed')}.`
          : (res.data.next || 'Search Console not connected yet — finish setup below.')
      )
      const setupRes = await getSeoIndexingSetup().catch(() => null)
      if (setupRes?.data) setSetup(setupRes.data)
      if (res.data.bing) setBing(res.data.bing)
      else if (setupRes?.data?.bing) setBing(setupRes.data.bing)
    } catch (e) {
      setPushNote(e.response?.data?.detail || 'Push failed.')
    } finally {
      setPushing(false)
    }
  }

  const handleInspect = async (e) => {
    e.preventDefault()
    setInspectError('')
    setInspecting(true)
    try {
      const res = await inspectSeoIndexingUrl({ url: inspectUrl.trim() })
      if (res.data?.url) {
        setRows(prev => {
          const next = prev.filter(r => r.url !== res.data.url.url)
          return [res.data.url, ...next]
        })
        setMode(res.data.mode || mode)
        setInspectUrl('')
      }
    } catch (err) {
      setInspectError(err.response?.data?.detail || 'Could not inspect URL.')
    } finally {
      setInspecting(false)
    }
  }

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>Search Indexing</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-3)' }}>
            Get published blogs into <strong>Google</strong>, <strong>Bing</strong>, and Yahoo (Yahoo uses Bing). Safari / iPhone search mostly uses Google + Bing.
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button onClick={handlePushAll} disabled={pushing} className="btn btn-primary flex items-center gap-2">
            <Rocket size={14} /> {pushing ? 'Pushing…' : 'Push all to Google'}
          </button>
          <button
            type="button"
            onClick={async () => {
              setNotifyingBing(true)
              setBingNote('')
              try {
                const res = await notifyBingIndexing()
                setBingNote(
                  res.data.ok
                    ? `IndexNow accepted ${res.data.count} blog URLs for Bing / Yahoo.`
                    : (res.data.detail || 'IndexNow ping did not succeed.')
                )
              } catch (e) {
                setBingNote(e.response?.data?.detail || 'Bing notify failed.')
              } finally {
                setNotifyingBing(false)
              }
            }}
            disabled={notifyingBing}
            className="btn btn-secondary flex items-center gap-2"
          >
            {notifyingBing ? 'Notifying…' : 'Notify Bing / Yahoo'}
          </button>
          <button onClick={handleRefresh} disabled={refreshing}
            className="btn btn-secondary flex items-center gap-2" style={{ opacity: refreshing ? 0.6 : 1 }}>
            <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} /> {refreshing ? 'Refreshing...' : 'Refresh next 12'}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">⚠ {error}</div>}

      {pushNote && (
        <div className={`alert ${gscConfigured ? 'alert-success' : 'alert-warning'}`}>
          {gscConfigured ? <CheckCircle2 size={15} /> : <AlertTriangle size={15} />}
          <div>{pushNote}</div>
        </div>
      )}

      {!gscConfigured && (
        <div className="card p-4 border border-amber-500/25 bg-amber-500/5">
          <div className="flex items-start gap-2 text-sm text-amber-100">
            <AlertTriangle size={16} className="mt-0.5 shrink-0 text-amber-400" />
            <div>
              <strong className="text-amber-200">Indexing status needs Google Search Console.</strong>
              <p className="text-xs text-slate-400 mt-1">
                Crawl-ready means the live URL is public. Indexing is confirmed against{" "}
                <strong>https://www.zeorbit.com/</strong> in Search Console. Add the service-account
                email as Owner on that property (not the old nip.io host). Until then we show crawl / sitemap status only.
              </p>
            </div>
          </div>
        </div>
      )}

      {bingNote && (
        <div className="alert alert-success">
          <CheckCircle2 size={15} />
          <div>{bingNote}</div>
        </div>
      )}

      {bing && (
        <div className="card p-5">
          <h2 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 6px', color: 'var(--text-1)' }}>
            Bing, Yahoo & other search — findings
          </h2>
          <p style={{ fontSize: 12.5, color: 'var(--text-3)', margin: '0 0 14px' }}>
            {bing.post_count || 0} blogs in the live post sitemap. {bing.yahoo_note} {bing.safari_note}
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {(bing.steps || []).map(step => (
              <div key={step.id} style={{
                display: 'flex', alignItems: 'flex-start', gap: 10,
                padding: '10px 12px', borderRadius: 8, border: '1px solid var(--border)',
              }}>
                <span style={{
                  width: 22, height: 22, borderRadius: 999, flexShrink: 0, marginTop: 1,
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                  background: step.done ? 'var(--green-soft)' : 'var(--bg-raised)',
                  color: step.done ? 'var(--green)' : 'var(--text-4)', fontSize: 12, fontWeight: 700,
                }}>
                  {step.done ? '✓' : '·'}
                </span>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-1)' }}>{step.label}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2, wordBreak: 'break-all' }}>
                    {step.href ? (
                      <a href={step.href} target="_blank" rel="noreferrer" style={{ color: 'var(--brand)' }}>
                        {step.detail} <ExternalLink size={10} style={{ display: 'inline' }} />
                      </a>
                    ) : step.detail}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      {setup && (
        <div className="card p-5">
          <h2 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 6px', color: 'var(--text-1)' }}>
            Setup checklist {setup.ready ? '— live' : '— finish to appear in Google Search'}
          </h2>
          <p style={{ fontSize: 12.5, color: 'var(--text-3)', margin: '0 0 14px' }}>
            Organic Google results need Search Console. Run <code>{setup.setup_cmd}</code> once, then click Push all.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {(setup.steps || []).map(step => (
              <div key={step.id} style={{
                display: 'flex', alignItems: 'flex-start', gap: 10,
                padding: '10px 12px', borderRadius: 8, border: '1px solid var(--border)',
              }}>
                <span style={{
                  width: 22, height: 22, borderRadius: 999, flexShrink: 0, marginTop: 1,
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                  background: step.done ? 'var(--green-soft)' : 'var(--bg-raised)',
                  color: step.done ? 'var(--green)' : 'var(--text-4)', fontSize: 12, fontWeight: 700,
                }}>
                  {step.done ? '✓' : '·'}
                </span>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-1)' }}>{step.label}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2, wordBreak: 'break-all' }}>
                    {step.href ? (
                      <a href={step.href} target="_blank" rel="noreferrer" style={{ color: 'var(--brand)' }}>
                        {step.detail} <ExternalLink size={10} style={{ display: 'inline' }} />
                      </a>
                    ) : step.detail}
                  </div>
                </div>
              </div>
            ))}
          </div>
          {setup.sitemap_url && (
            <p style={{ fontSize: 12.5, color: 'var(--text-4)', margin: '12px 0 0' }}>
              Sitemap:{' '}
              <a href={setup.sitemap_url} target="_blank" rel="noreferrer" style={{ color: 'var(--brand)' }}>
                {setup.sitemap_url}
              </a>
            </p>
          )}
        </div>
      )}

      {mode === 'gsc' && (
        <div className="alert alert-success">
          <CheckCircle2 size={15} />
          <div><strong>Live Search Console.</strong> Sitemap + URL Inspection are connected. Ranking still takes time.</div>
        </div>
      )}
      {mode === 'crawl' && !demo && (
        <div className="alert alert-warning">
          <AlertTriangle size={15} />
          <div>
            <strong>Pages are published, but Google Search Console is not connected yet.</strong>{' '}
            Finish the checklist above (service account JSON). Until then Google may not discover new pages quickly.
          </div>
        </div>
      )}
      {demo && (
        <div className="alert alert-warning">
          <AlertTriangle size={15} />
          <div><strong>Demo sample data.</strong> Set <code>DEMO_MODE=false</code> and push real URLs.</div>
        </div>
      )}

      <form onSubmit={handleInspect} className="card p-4 flex gap-3 items-end" style={{ flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 220 }}>
          <label style={{ display: 'block', fontSize: 12.5, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>
            Inspect any public URL
          </label>
          <input
            type="url"
            required
            value={inspectUrl}
            onChange={e => setInspectUrl(e.target.value)}
            placeholder="https://zeorbit.com/web-design-san-diego"
            style={{ width: '100%', padding: '10px 12px' }}
          />
        </div>
        <button type="submit" disabled={inspecting || !inspectUrl.trim()} className="btn btn-secondary">
          <ScanSearch size={14} /> {inspecting ? 'Checking…' : 'Inspect'}
        </button>
        {inspectError && <div className="alert alert-error" style={{ width: '100%', margin: 0 }}>⚠ {inspectError}</div>}
      </form>

      <div className="card">
        {loading ? (
          <div className="flex items-center justify-center py-16 text-sm" style={{ color: 'var(--text-4)' }}>Loading...</div>
        ) : rows.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16" style={{ color: 'var(--text-4)' }}>
            <ScanSearch size={32} className="mb-3" style={{ opacity: 0.3 }} />
            <p className="text-sm">No URLs yet — click <strong>Push all to Google</strong> or publish via Articles.</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>URL</th>
                <th>Status</th>
                <th>HTTP</th>
                <th>Robots</th>
                <th>Noindex</th>
                <th>Canonical</th>
                <th>Last Checked</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(row => (
                <tr key={row.id}>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--text-1)' }}>{row.title || '—'}</div>
                    <a href={row.url} target="_blank" rel="noreferrer"
                      style={{ fontSize: 11.5, color: 'var(--brand)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                      <ExternalLink size={9} />{String(row.url || '').replace(/^https?:\/\//, '').slice(0, 50)}
                    </a>
                    {row.error_message && (
                      <div style={{ fontSize: 11, color: 'var(--red)', marginTop: 3 }}>{row.error_message}</div>
                    )}
                    {row.coverage_state && (
                      <div style={{ fontSize: 11, color: 'var(--text-4)', marginTop: 3 }}>{row.coverage_state}</div>
                    )}
                  </td>
                  <td><StatusBadge status={row.status} /></td>
                  <td style={{ color: 'var(--text-3)' }}>{row.http_status ?? '—'}</td>
                  <td>{row.robots_allowed == null ? '—' : row.robots_allowed ? '✓' : '✕'}</td>
                  <td>{row.has_noindex ? '⚠' : '✓'}</td>
                  <td>{row.canonical_ok ? '✓' : '—'}</td>
                  <td style={{ color: 'var(--text-4)', fontSize: 12 }}>
                    {row.last_inspected_at ? new Date(row.last_inspected_at).toLocaleString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
