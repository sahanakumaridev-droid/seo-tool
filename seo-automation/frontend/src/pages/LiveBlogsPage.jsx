import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ExternalLink, Pencil, Globe, RefreshCw, CheckCircle2, Search } from 'lucide-react'
import { listPostedBlogs, getPage, publishToWeb, zeorbitArticleUrl } from '../api'

function monthKey(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

function monthLabel(key) {
  if (!key) return ''
  const [y, m] = key.split('-')
  const d = new Date(Number(y), Number(m) - 1, 1)
  return d.toLocaleString(undefined, { month: 'long', year: 'numeric' })
}

export default function LiveBlogsPage() {
  const navigate = useNavigate()
  const [posts, setPosts] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [republishing, setRepublishing] = useState('')
  const [flash, setFlash] = useState('')
  const [search, setSearch] = useState('')
  const [city, setCity] = useState('all')
  const [status, setStatus] = useState('all')
  const [month, setMonth] = useState('all')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await listPostedBlogs(0, 200)
      setPosts(res.data.posts || [])
      setTotal(res.data.total || 0)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Could not load posted blogs.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const cities = useMemo(() => {
    const set = new Set(posts.map((p) => (p.city || '').trim()).filter(Boolean))
    return [...set].sort((a, b) => a.localeCompare(b))
  }, [posts])

  const statuses = useMemo(() => {
    const set = new Set(posts.map((p) => (p.status || '').trim()).filter(Boolean))
    return [...set].sort((a, b) => a.localeCompare(b))
  }, [posts])

  const months = useMemo(() => {
    const set = new Set(posts.map((p) => monthKey(p.updated_at)).filter(Boolean))
    return [...set].sort().reverse()
  }, [posts])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return posts.filter((p) => {
      if (city !== 'all' && (p.city || '') !== city) return false
      if (status !== 'all' && (p.status || '') !== status) return false
      if (month !== 'all' && monthKey(p.updated_at) !== month) return false
      if (!q) return true
      const hay = [p.title, p.excerpt, p.slug, p.city, p.state, p.industry, p.focus_keyword, p.public_url]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
      return hay.includes(q)
    })
  }, [posts, search, city, status, month])

  const openEdit = async (post) => {
    try {
      const res = await getPage(post.slug)
      const block = res.data.seo_block || {}
      if (!block.slug) block.slug = post.slug
      navigate(`/page-preview?slug=${encodeURIComponent(post.slug)}`, {
        state: { block, contentKind: 'post', fromLive: true },
      })
    } catch (e) {
      setError(e.response?.data?.detail || 'Could not load this blog for editing.')
    }
  }

  const republish = async (post) => {
    setRepublishing(post.slug)
    setError('')
    setFlash('')
    try {
      const res = await getPage(post.slug)
      const block = res.data.seo_block || {}
      if (!block.slug) block.slug = post.slug
      const pub = await publishToWeb(block)
      const liveUrl = zeorbitArticleUrl(pub.data.public_url || pub.data.slug)
      setFlash(`Re-published: ${post.title}`)
      window.open(liveUrl, '_blank', 'noopener')
      await load()
    } catch (e) {
      const d = e.response?.data?.detail
      setError(typeof d === 'object' && d?.message ? d.message : (typeof d === 'string' ? d : 'Re-publish failed.'))
    } finally {
      setRepublishing('')
    }
  }

  const selectStyle = {
    background: 'var(--bg-raised)',
    border: '1px solid var(--border)',
    color: 'var(--text-1)',
  }

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>
            Posted Blogs
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-3)', maxWidth: 640 }}>
            Blogs already published on zeorbit.com. Edit, then re-publish to update the same page.
          </p>
        </div>
        <button type="button" onClick={load} disabled={loading} className="btn btn-secondary flex items-center gap-2">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {error ? (
        <div className="rounded-lg px-4 py-3 text-sm" style={{ background: 'var(--red-soft)', color: 'var(--red)' }}>{error}</div>
      ) : null}
      {flash ? (
        <div className="rounded-lg px-4 py-3 text-sm flex items-center gap-2" style={{ background: 'var(--green-soft)', color: 'var(--green)' }}>
          <CheckCircle2 size={16} /> {flash}
        </div>
      ) : null}

      <div className="flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-48">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-3)' }} />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search title, keyword, city, URL…"
            className="w-full pl-8 pr-3 py-2 rounded-lg text-sm"
            style={selectStyle}
          />
        </div>
        <select value={city} onChange={(e) => setCity(e.target.value)} className="rounded-lg px-3 py-2 text-sm" style={{ ...selectStyle, minWidth: 140 }}>
          <option value="all">All cities</option>
          {cities.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={status} onChange={(e) => setStatus(e.target.value)} className="rounded-lg px-3 py-2 text-sm" style={{ ...selectStyle, minWidth: 160 }}>
          <option value="all">All statuses</option>
          {statuses.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={month} onChange={(e) => setMonth(e.target.value)} className="rounded-lg px-3 py-2 text-sm" style={{ ...selectStyle, minWidth: 170 }}>
          <option value="all">All dates</option>
          {months.map((m) => <option key={m} value={m}>{monthLabel(m)}</option>)}
        </select>
        <span className="text-xs" style={{ color: 'var(--text-3)' }}>
          {filtered.length} of {total}
        </span>
      </div>

      {loading && !posts.length ? (
        <p style={{ color: 'var(--text-muted)' }}>Loading posted blogs…</p>
      ) : !posts.length ? (
        <div className="card p-6">
          <p style={{ color: 'var(--text-3)' }}>No posted blogs yet. Generate a post in SEO Content and publish it to ZeOrbit.</p>
        </div>
      ) : !filtered.length ? (
        <div className="card p-6">
          <p style={{ color: 'var(--text-3)' }}>No blogs match these filters.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((post) => {
            const liveUrl = zeorbitArticleUrl(post.public_url || post.slug)
            return (
              <div key={post.slug} className="card p-4" style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
                {post.featured_image_url ? (
                  <img
                    src={post.featured_image_url}
                    alt=""
                    style={{ width: 88, height: 64, objectFit: 'cover', borderRadius: 8, flexShrink: 0 }}
                  />
                ) : null}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="flex items-center gap-2 flex-wrap">
                    <h2 className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>{post.title}</h2>
                    <span
                      className="text-[10px] font-bold uppercase tracking-wide px-2 py-0.5 rounded-full"
                      style={{ background: 'var(--green-soft)', color: 'var(--green)' }}
                    >
                      Posted
                    </span>
                    <span className="text-[10px] uppercase" style={{ color: 'var(--text-muted)' }}>{post.status}</span>
                  </div>
                  {post.excerpt ? (
                    <p className="text-xs mt-1" style={{ color: 'var(--text-3)' }}>{post.excerpt}</p>
                  ) : null}
                  <p className="text-xs mt-1 truncate" style={{ color: 'var(--text-muted)' }}>{liveUrl}</p>
                  {post.updated_at ? (
                    <p className="text-[11px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
                      Updated {new Date(post.updated_at).toLocaleString()}
                    </p>
                  ) : null}
                </div>
                <div className="flex flex-col gap-2" style={{ flexShrink: 0 }}>
                  <button type="button" className="btn btn-secondary flex items-center gap-1.5 text-xs" onClick={() => openEdit(post)}>
                    <Pencil size={12} /> Edit
                  </button>
                  <button
                    type="button"
                    className="btn btn-primary flex items-center gap-1.5 text-xs"
                    disabled={republishing === post.slug}
                    onClick={() => republish(post)}
                  >
                    <Globe size={12} /> {republishing === post.slug ? 'Publishing…' : 'Re-publish'}
                  </button>
                  <a href={liveUrl} target="_blank" rel="noopener noreferrer" className="btn btn-secondary flex items-center gap-1.5 text-xs">
                    <ExternalLink size={12} /> View on site
                  </a>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
