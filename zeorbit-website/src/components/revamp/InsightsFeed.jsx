import { useEffect, useState } from 'react'
import { ArrowRight } from 'lucide-react'
import { listBlogPosts } from '../../api'
import { INSIGHTS } from '../../data/revampContent'

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

/**
 * Live Insights / Blog cards fed from published SEO content.
 * Falls back to static INSIGHTS when the API has no posts yet.
 */
export default function InsightsFeed({
  limit = 6,
  showViewAll = true,
  emptyUseFallback = true,
}) {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError('')
      try {
        const { data } = await listBlogPosts(0, limit)
        if (cancelled) return
        setPosts(Array.isArray(data?.posts) ? data.posts : [])
      } catch (err) {
        if (cancelled) return
        setError(err?.message || 'Could not load blog posts')
        setPosts([])
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => { cancelled = true }
  }, [limit])

  const useFallback = !loading && posts.length === 0 && emptyUseFallback
  const items = useFallback
    ? INSIGHTS.map((item, i) => ({
        id: `fallback-${i}`,
        category: item.category,
        title: item.title,
        excerpt: item.excerpt,
        url: '/blog',
        public_url: '/blog',
        published_at: null,
        source: 'fallback',
      }))
    : posts

  return (
    <div className="rv-insights-wrap">
      {loading ? (
        <p className="rv-insights-status">Loading published insights…</p>
      ) : null}

      {!loading && error && posts.length === 0 ? (
        <p className="rv-insights-status rv-insights-error">{error}</p>
      ) : null}

      {!loading && posts.length === 0 && !useFallback ? (
        <p className="rv-insights-status">
          No published articles yet. Publish from the ZeOrbit SEO tool to populate this feed.
        </p>
      ) : null}

      <div className="rv-insights-grid">
        {items.map((item) => {
          const href = item.url || item.public_url || '/blog'
          const external = /^https?:\/\//i.test(href)
          return (
            <a
              key={item.id || item.title}
              className="rv-insight-card rv-insight-link"
              href={href}
              {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
            >
              <p className="rv-eyebrow">{item.category || 'Insights'}</p>
              <h3>{item.title}</h3>
              <p>{item.excerpt}</p>
              <div className="rv-insight-meta">
                <span>{formatDate(item.published_at) || (item.source === 'fallback' ? 'Coming soon' : 'Live')}</span>
                <span className="rv-insight-cta">
                  Read <ArrowRight size={14} />
                </span>
              </div>
            </a>
          )
        })}
      </div>

      {showViewAll ? (
        <div className="rv-insights-more">
          <a className="btn btn-secondary" href="/blog">
            View all blog posts <ArrowRight size={16} />
          </a>
        </div>
      ) : null}
    </div>
  )
}
