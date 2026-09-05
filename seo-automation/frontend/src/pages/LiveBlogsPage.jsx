import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ExternalLink, Pencil, Globe, RefreshCw, CheckCircle2, Search } from 'lucide-react'
import { listPostedBlogs, getPage, publishToWeb, zeorbitArticleUrl, bulkUpdatePublishedContent } from '../api'

function dayKey(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toISOString().slice(0, 10)
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
  const [kind, setKind] = useState('all')
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [selected, setSelected] = useState(() => new Set())
  const [findText, setFindText] = useState('')
  const [replaceText, setReplaceText] = useState('')
  const [bulkRepublish, setBulkRepublish] = useState(true)
  const [bulkBusy, setBulkBusy] = useState(false)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await listPostedBlogs(0, 500)
      setPosts(res.data.posts || [])
      setTotal(res.data.total || 0)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Could not load published URLs.')
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

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return posts.filter((p) => {
      if (city !== 'all' && (p.city || '') !== city) return false
      if (status !== 'all' && (p.status || '') !== status) return false
      if (kind !== 'all' && (p.kind || 'blog') !== kind) return false
      const day = dayKey(p.updated_at)
      if (fromDate && day && day < fromDate) return false
      if (toDate && day && day > toDate) return false
      if (!q) return true
      const hay = [p.title, p.excerpt, p.slug, p.city, p.state, p.industry, p.focus_keyword, p.public_url]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
      return hay.includes(q)
    })
  }, [posts, search, city, status, kind, fromDate, toDate])

  const allVisibleSelected = filtered.length > 0 && filtered.every((p) => selected.has(p.slug))

  const toggleOne = (slug) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(slug)) next.delete(slug)
      else next.add(slug)
      return next
    })
  }

  const toggleAllVisible = () => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (allVisibleSelected) {
        filtered.forEach((p) => next.delete(p.slug))
      } else {
        filtered.forEach((p) => next.add(p.slug))
      }
      return next
    })
  }

  const openEdit = async (post) => {
    try {
      const res = await getPage(post.slug)
      const block = res.data.seo_block || {}
      if (!block.slug) block.slug = post.slug
      navigate(`/page-preview?slug=${encodeURIComponent(post.slug)}`, {
        state: { block, contentKind: post.kind === 'page' ? 'page' : 'post', fromLive: true },
      })
    } catch (e) {
      setError(e.response?.data?.detail || 'Could not load this URL for editing.')
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

  const runBulk = async () => {
    const slugs = [...selected]
    if (!slugs.length) {
      setError('Select one or more URLs first.')
      return
    }
    setBulkBusy(true)
    setError('')
    setFlash('')
    try {
      const res = await bulkUpdatePublishedContent({
        slugs,
        find: findText,
        replace: replaceText,
        republish: bulkRepublish,
      })
      setFlash(`Updated ${res.data.updated} URL${res.data.updated === 1 ? '' : 's'}.`)
      setSelected(new Set())
      await load()
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Bulk update failed.')
    } finally {
      setBulkBusy(false)
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
            Published URLs
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-3)', maxWidth: 680 }}>
            Every published page and blog on zeorbit.com. Filter by date, select rows, then edit in bulk or open one URL.
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
        <select value={kind} onChange={(e) => setKind(e.target.value)} className="rounded-lg px-3 py-2 text-sm" style={{ ...selectStyle, minWidth: 120 }}>
          <option value="all">All types</option>
          <option value="blog">Blogs</option>
          <option value="page">Pages</option>
        </select>
        <select value={city} onChange={(e) => setCity(e.target.value)} className="rounded-lg px-3 py-2 text-sm" style={{ ...selectStyle, minWidth: 140 }}>
          <option value="all">All cities</option>
          {cities.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={status} onChange={(e) => setStatus(e.target.value)} className="rounded-lg px-3 py-2 text-sm" style={{ ...selectStyle, minWidth: 160 }}>
          <option value="all">All statuses</option>
          {statuses.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <label className="text-xs flex items-center gap-2" style={{ color: 'var(--text-3)' }}>
          From
          <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} className="rounded-lg px-2 py-1.5 text-sm" style={selectStyle} />
        </label>
        <label className="text-xs flex items-center gap-2" style={{ color: 'var(--text-3)' }}>
          To
          <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} className="rounded-lg px-2 py-1.5 text-sm" style={selectStyle} />
        </label>
        <span className="text-xs" style={{ color: 'var(--text-3)' }}>
          {filtered.length} of {total} · {selected.size} selected
        </span>
      </div>

      <div className="card p-4 space-y-3">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <p className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>Bulk edit selected URLs</p>
          <label className="text-xs flex items-center gap-2" style={{ color: 'var(--text-3)' }}>
            <input type="checkbox" checked={bulkRepublish} onChange={(e) => setBulkRepublish(e.target.checked)} />
            Re-publish after update
          </label>
        </div>
        <div className="flex flex-wrap gap-3">
          <input
            value={findText}
            onChange={(e) => setFindText(e.target.value)}
            placeholder="Find in title, body, FAQs…"
            className="flex-1 min-w-48 rounded-lg px-3 py-2 text-sm"
            style={selectStyle}
          />
          <input
            value={replaceText}
            onChange={(e) => setReplaceText(e.target.value)}
            placeholder="Replace with…"
            className="flex-1 min-w-48 rounded-lg px-3 py-2 text-sm"
            style={selectStyle}
          />
          <button type="button" className="btn btn-primary text-sm" disabled={bulkBusy} onClick={runBulk}>
            {bulkBusy ? 'Updating…' : `Update ${selected.size || 0} URL${selected.size === 1 ? '' : 's'}`}
          </button>
        </div>
      </div>

      {loading && !posts.length ? (
        <p style={{ color: 'var(--text-muted)' }}>Loading published URLs…</p>
      ) : !posts.length ? (
        <div className="card p-6">
          <p style={{ color: 'var(--text-3)' }}>No published URLs yet. Generate in SEO Content and publish to ZeOrbit.</p>
        </div>
      ) : !filtered.length ? (
        <div className="card p-6">
          <p style={{ color: 'var(--text-3)' }}>No URLs match these filters.</p>
        </div>
      ) : (
        <div className="space-y-3">
          <label className="text-xs flex items-center gap-2" style={{ color: 'var(--text-3)' }}>
            <input type="checkbox" checked={allVisibleSelected} onChange={toggleAllVisible} />
            Select all visible
          </label>
          {filtered.map((post) => {
            const liveUrl = zeorbitArticleUrl(post.public_url || post.slug)
            return (
              <div key={post.slug} className="card p-4" style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
                <input
                  type="checkbox"
                  checked={selected.has(post.slug)}
                  onChange={() => toggleOne(post.slug)}
                  style={{ marginTop: 6 }}
                  aria-label={`Select ${post.title}`}
                />
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
                      {post.kind === 'page' ? 'Page' : 'Blog'}
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
