import { useEffect, useState } from 'react'
import { RefreshCw, Play, ExternalLink, CheckCircle2, AlertTriangle } from 'lucide-react'
import { getIndexAutomation, runIndexAutomation } from '../api'

function fmt(iso) {
  if (!iso) return 'Not run yet'
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

export default function IndexAutomationPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getIndexAutomation()
      setData(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Could not load automation status.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleRun = async () => {
    setRunning(true)
    setError('')
    try {
      const res = await runIndexAutomation()
      setData(prev => ({
        ...(prev || {}),
        last_run_at: res.data.ran_at,
        next_run_at: res.data.next_run_at,
        last_result: res.data,
        gsc_configured: res.data.gsc_configured,
      }))
      await load()
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Run failed.')
    } finally {
      setRunning(false)
    }
  }

  const last = data?.last_result || {}
  const inspected = last.inspected || []

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>
            Index Automation
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-3)', maxWidth: 640 }}>
            Runs on a timer: sitemap submit, IndexNow (Bing/Yahoo), crawl checks, and Search Console
            inspection. Google has no API for the Search Console “Request indexing” button — this
            page automates everything that is allowed.
          </p>
        </div>
        <div className="flex gap-2">
          <button type="button" onClick={load} disabled={loading} className="btn btn-secondary flex items-center gap-2">
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
          <button type="button" onClick={handleRun} disabled={running} className="btn btn-primary flex items-center gap-2">
            <Play size={14} /> {running ? 'Running…' : 'Run now'}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
        <div className="card p-4">
          <div style={{ fontSize: 11, color: 'var(--text-4)', fontWeight: 600 }}>Schedule</div>
          <div style={{ fontSize: 18, fontWeight: 700, marginTop: 6 }}>Every {data?.interval_hours || 6}h</div>
          <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 4 }}>Next: {fmt(data?.next_run_at)}</div>
        </div>
        <div className="card p-4">
          <div style={{ fontSize: 11, color: 'var(--text-4)', fontWeight: 600 }}>Last run</div>
          <div style={{ fontSize: 15, fontWeight: 650, marginTop: 6 }}>{fmt(data?.last_run_at)}</div>
          <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 4 }}>
            {last.inspect_count || 0} URLs inspected
          </div>
        </div>
        <div className="card p-4">
          <div style={{ fontSize: 11, color: 'var(--text-4)', fontWeight: 600 }}>Search Console</div>
          <div style={{ fontSize: 18, fontWeight: 700, marginTop: 6, color: data?.gsc_configured ? 'var(--green)' : 'var(--amber)' }}>
            {data?.gsc_configured ? 'Connected' : 'Off'}
          </div>
        </div>
        <div className="card p-4">
          <div style={{ fontSize: 11, color: 'var(--text-4)', fontWeight: 600 }}>IndexNow</div>
          <div style={{ fontSize: 18, fontWeight: 700, marginTop: 6, color: data?.indexnow_configured ? 'var(--green)' : 'var(--amber)' }}>
            {data?.indexnow_configured ? 'On' : 'Off'}
          </div>
        </div>
      </div>

      <div className="card p-5">
        <h2 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 10px', color: 'var(--text-1)' }}>
          Automated
        </h2>
        <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--text-2)', fontSize: 13, lineHeight: 1.65 }}>
          {(data?.does_automate || []).map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      </div>

      <div className="card p-5">
        <h2 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 10px', color: 'var(--text-1)' }}>
          Still not an API (Google does not allow)
        </h2>
        <p style={{ fontSize: 13, color: 'var(--text-3)', margin: '0 0 10px' }}>
          Ranking, Maps, and ChatGPT citations cannot be forced. For a recrawl this week on a hub
          whose last crawl is old, open the GSC link on that row (about 10 per day).
        </p>
        <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--text-2)', fontSize: 13, lineHeight: 1.65 }}>
          {(data?.cannot_automate || []).map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      </div>

      <div className="card p-5">
        <h2 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 6px', color: 'var(--text-1)' }}>
          Priority hubs
        </h2>
        <p style={{ fontSize: 12.5, color: 'var(--text-3)', margin: '0 0 12px' }}>
          Always tracked and included in IndexNow. Inspected on a rotating batch of {data?.inspect_batch || 10} per run.
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {(data?.hubs || []).map((url) => (
            <div key={url} style={{ fontSize: 13, wordBreak: 'break-all' }}>
              <a href={url} target="_blank" rel="noreferrer" style={{ color: 'var(--brand)' }}>
                {url}
              </a>
            </div>
          ))}
        </div>
      </div>

      {inspected.length > 0 && (
        <div className="card p-5" style={{ overflowX: 'auto' }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 12px', color: 'var(--text-1)' }}>
            Last inspect batch
          </h2>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
            <thead>
              <tr style={{ textAlign: 'left', color: 'var(--text-4)' }}>
                <th style={{ padding: '8px 6px' }}>URL</th>
                <th style={{ padding: '8px 6px' }}>Crawl</th>
                <th style={{ padding: '8px 6px' }}>GSC</th>
                <th style={{ padding: '8px 6px' }}>Last Google crawl</th>
                <th style={{ padding: '8px 6px' }} />
              </tr>
            </thead>
            <tbody>
              {inspected.map((row) => (
                <tr key={row.url} style={{ borderTop: '1px solid var(--border)' }}>
                  <td style={{ padding: '8px 6px', wordBreak: 'break-all' }}>{row.url}</td>
                  <td style={{ padding: '8px 6px' }}>
                    {row.crawl_ok
                      ? <span style={{ color: 'var(--green)', display: 'inline-flex', alignItems: 'center', gap: 4 }}><CheckCircle2 size={13} /> OK</span>
                      : <span style={{ color: 'var(--amber)', display: 'inline-flex', alignItems: 'center', gap: 4 }}><AlertTriangle size={13} /> {row.error || 'Fail'}</span>}
                  </td>
                  <td style={{ padding: '8px 6px' }}>{row.gsc_status || row.coverage_state || '—'}</td>
                  <td style={{ padding: '8px 6px' }}>{row.last_crawl_time ? fmt(row.last_crawl_time) : '—'}</td>
                  <td style={{ padding: '8px 6px' }}>
                    {row.inspect_link && (
                      <a href={row.inspect_link} target="_blank" rel="noreferrer" style={{ color: 'var(--brand)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                        GSC <ExternalLink size={11} />
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {(data?.runs || []).length > 0 && (
        <div className="card p-5">
          <h2 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 12px', color: 'var(--text-1)' }}>
            Run history
          </h2>
          {(data.runs || []).map((r, i) => (
            <div key={`${r.at}-${i}`} style={{ fontSize: 12.5, color: 'var(--text-3)', padding: '6px 0', borderTop: i ? '1px solid var(--border)' : undefined }}>
              {fmt(r.at)} · {r.reason} · {r.inspected} inspected · GSC {r.gsc ? 'on' : 'off'}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
