import { useState, useEffect } from 'react'
import { ScanSearch, RefreshCw, ExternalLink, CheckCircle2, AlertTriangle, Clock, XCircle, HelpCircle } from 'lucide-react'
import { getSeoIndexingStatus, refreshSeoIndexing } from '../api'

const STATUS_META = {
  published:     { label: 'Published',        color: 'var(--text-3)',  bg: 'var(--bg-raised)',   icon: Clock },
  sitemap_added:  { label: 'Sitemap Added',    color: 'var(--brand)',   bg: 'var(--brand-soft)',  icon: CheckCircle2 },
  discovered:     { label: 'Google Discovered',color: 'var(--amber)',   bg: 'var(--amber-soft)',  icon: HelpCircle },
  indexed:        { label: 'Indexed',          color: 'var(--green)',  bg: 'var(--green-soft)',  icon: CheckCircle2 },
  not_indexed:    { label: 'Not Indexed',      color: 'var(--amber)',  bg: 'var(--amber-soft)',  icon: AlertTriangle },
  error:          { label: 'Error',            color: 'var(--red)',    bg: 'var(--red-soft)',    icon: XCircle },
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
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const res = await getSeoIndexingStatus()
      setRows(res.data.urls || [])
      setGscConfigured(res.data.gsc_configured)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await refreshSeoIndexing()
      await load()
    } catch (e) {
      console.error(e)
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>Google Indexing</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-3)' }}>
            Free, official Google Search automation for every published blog — sitemap + Search Console, no ads, no paid tools.
          </p>
        </div>
        <button onClick={handleRefresh} disabled={refreshing}
          className="btn btn-primary flex items-center gap-2" style={{ opacity: refreshing ? 0.6 : 1 }}>
          <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} /> {refreshing ? 'Refreshing...' : 'Refresh Status'}
        </button>
      </div>

      {!gscConfigured && (
        <div className="card p-4" style={{ borderColor: 'var(--amber)' }}>
          <div className="flex items-start gap-3">
            <AlertTriangle size={16} style={{ color: 'var(--amber)', flexShrink: 0, marginTop: 2 }} />
            <p style={{ fontSize: 12.5, color: 'var(--text-3)', margin: 0, lineHeight: 1.6 }}>
              Search Console isn't configured yet — set <code>GSC_SITE_URL</code>, <code>WP_SITEMAP_URL</code> and{' '}
              <code>GOOGLE_INDEXING_KEY_FILE</code> to enable real indexing-status checks. Crawlability checks
              (HTTP status, robots.txt, noindex, canonical) still run on every publish either way.
            </p>
          </div>
        </div>
      )}

      <div className="card">
        {loading ? (
          <div className="flex items-center justify-center py-16 text-sm" style={{ color: 'var(--text-4)' }}>Loading...</div>
        ) : rows.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16" style={{ color: 'var(--text-4)' }}>
            <ScanSearch size={32} className="mb-3" style={{ opacity: 0.3 }} />
            <p className="text-sm">No published blogs tracked yet — publish one via WordPress to see it here.</p>
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
                      <ExternalLink size={9} />{row.url.replace(/^https?:\/\//, '').slice(0, 50)}
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
                  <td>{row.robots_allowed === null ? '—' : row.robots_allowed ? '✓' : '✕'}</td>
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
