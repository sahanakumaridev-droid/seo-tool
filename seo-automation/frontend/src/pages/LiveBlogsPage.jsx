import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ExternalLink, Pencil, Globe, RefreshCw, CheckCircle2 } from 'lucide-react'
import { listPostedBlogs, getPage, publishToWeb, zeorbitArticleUrl } from '../api'

export default function LiveBlogsPage() {
  const navigate = useNavigate()
  const [posts, setPosts] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [republishing, setRepublishing] = useState('')
  const [flash, setFlash] = useState('')

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

      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{total} posted {total === 1 ? 'blog' : 'blogs'}</p>

      {loading && !posts.length ? (
        <p style={{ color: 'var(--text-muted)' }}>Loading posted blogs…</p>
      ) : !posts.length ? (
        <div className="card p-6">
          <p style={{ color: 'var(--text-3)' }}>No posted blogs yet. Generate a post in SEO Content and publish it to ZeOrbit.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {posts.map((post) => {
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
