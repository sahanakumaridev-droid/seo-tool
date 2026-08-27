import { useEffect, useMemo, useState } from 'react'
import { ExternalLink, Globe2, RefreshCw } from 'lucide-react'
import { getSeoSitemaps } from '../api'

const TABS = [
  { id: 'index', label: 'Index' },
  { id: 'pages', label: 'Pages' },
  { id: 'locations', label: 'Location pages' },
  { id: 'posts', label: 'Posts' },
]

function UrlTable({ rows, empty }) {
  if (!rows.length) {
    return <p className="text-sm" style={{ color: 'var(--text-3)' }}>{empty}</p>
  }
  return (
    <div style={{ overflowX: 'auto' }}>
      <table className="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>URL</th>
            <th>Lastmod</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.loc}>
              <td className="text-xs font-semibold" style={{ color: 'var(--text-3)' }}>{i + 1}</td>
              <td>
                <div className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>{r.loc}</div>
                {(r.title || r.city) ? (
                  <div className="text-xs muted-cell mt-0.5">{[r.city, r.title].filter(Boolean).join(' · ')}</div>
                ) : null}
              </td>
              <td className="text-xs" style={{ color: 'var(--text-2)' }}>{r.lastmod || '—'}</td>
              <td>
                <a href={r.loc} target="_blank" rel="noreferrer"
                  className="inline-flex items-center gap-1 text-xs font-semibold"
                  style={{ color: 'var(--brand)' }}>
                  Open <ExternalLink size={11} />
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function SitemapsPage() {
  const [data, setData] = useState(null)
  const [tab, setTab] = useState('pages')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getSeoSitemaps()
      setData(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Could not load sitemaps.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const rows = useMemo(() => {
    if (!data) return []
    if (tab === 'index') return data.index || []
    if (tab === 'pages') return data.pages || []
    if (tab === 'locations') return data.location_pages || []
    return data.posts || []
  }, [data, tab])

  const counts = data?.counts || {}

  return (
    <div className="space-y-5 fade-in">
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <p className="crm-crumb">SEO &gt; Sitemaps</p>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-1)' }}>Sitemaps</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>
            View sitemap.xml, page-sitemap.xml, and post-sitemap.xml inside the SEO tool.
          </p>
        </div>
        <button type="button" onClick={load} disabled={loading}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-semibold disabled:opacity-50"
          style={{ background: '#fff', border: '1px solid #94a3b8', color: '#0f172a' }}>
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-xl p-3" style={{ background: '#FEF2F2', border: '1px solid #FECACA', color: '#7F1D1D' }}>
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {[
          { label: 'sitemap.xml', href: data?.index_url, n: 2, hint: 'Index of page + post sitemaps' },
          { label: 'page-sitemap.xml', href: data?.page_sitemap_url, n: counts.pages, hint: 'Marketing pages' },
          { label: 'post-sitemap.xml', href: data?.post_sitemap_url, n: counts.posts, hint: 'Published blog posts' },
        ].map((c) => (
          <a key={c.label} href={c.href || '#'} target="_blank" rel="noreferrer"
            className="card p-4 block hover:opacity-95">
            <div className="flex items-center gap-2 mb-1">
              <Globe2 size={16} style={{ color: 'var(--brand)' }} />
              <span className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>{c.label}</span>
            </div>
            <p className="text-xs" style={{ color: 'var(--text-3)' }}>{c.hint}</p>
            <p className="text-lg font-bold mt-2" style={{ color: 'var(--text-1)' }}>{c.n ?? '—'}</p>
          </a>
        ))}
      </div>

      <div className="card">
        <div className="flex flex-wrap gap-1 px-4 py-3" style={{ borderBottom: '1px solid var(--border)' }}>
          {TABS.map((t) => {
            const n = t.id === 'index' ? (data?.index || []).length
              : t.id === 'pages' ? counts.pages
                : t.id === 'locations' ? counts.location_pages
                  : counts.posts
            const on = tab === t.id
            return (
              <button key={t.id} type="button" onClick={() => setTab(t.id)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold"
                style={{
                  background: on ? 'var(--brand-soft, #eef2ff)' : '#fff',
                  border: `1px solid ${on ? 'var(--brand)' : '#94a3b8'}`,
                  color: on ? 'var(--brand-dark, #3730a3)' : '#0f172a',
                }}>
                {t.label} {n != null ? `(${n})` : ''}
              </button>
            )
          })}
        </div>
        <div className="p-4">
          {loading && !data ? (
            <p className="text-sm" style={{ color: 'var(--text-3)' }}>Loading sitemaps…</p>
          ) : (
            <UrlTable
              rows={rows}
              empty={tab === 'posts' ? 'No blog posts in post-sitemap.xml yet.' : 'No URLs in this sitemap.'}
            />
          )}
        </div>
      </div>
    </div>
  )
}
