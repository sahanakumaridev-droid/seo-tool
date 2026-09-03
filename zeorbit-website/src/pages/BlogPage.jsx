import { useEffect, useMemo, useState } from 'react'
import { ArrowRight, Search } from 'lucide-react'
import RevampHeader from '../components/revamp/RevampHeader'
import SiteFooter from '../components/SiteFooter'
import { listBlogPosts } from '../api'
import { ZEORBIT_BLOG } from '../data/zeorbitBlog'
import { isOffsiteBlogHref, toSiteBlogHref } from '../lib/blogUrls'

const STOCK_FALLBACKS = [
  'https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?auto=format&fit=crop&w=1400&q=80',
  'https://images.unsplash.com/photo-1559028012-481c04fa702d?auto=format&fit=crop&w=1400&q=80',
  'https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?auto=format&fit=crop&w=1400&q=80',
  'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1400&q=80',
  'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1400&q=80',
  'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1400&q=80',
  'https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1400&q=80',
  'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1400&q=80',
  'https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=1400&q=80',
  'https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&w=1400&q=80',
  'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?auto=format&fit=crop&w=1400&q=80',
  'https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1400&q=80',
]

function imageKey(url) {
  if (!url) return ''
  const m = String(url).match(/(photo-[a-zA-Z0-9_-]+)/i)
  return (m ? m[1] : String(url).split('?')[0]).toLowerCase()
}

/** Ensure the listing never shows the same stock photo twice in one view. */
function withUniqueImages(items) {
  const seen = new Set()
  let fi = 0
  return items.map((item) => {
    const key = imageKey(item.featured_image_url)
    if (key && !seen.has(key)) {
      seen.add(key)
      return item
    }
    let next = STOCK_FALLBACKS[fi % STOCK_FALLBACKS.length]
    fi += 1
    let guard = 0
    while (seen.has(imageKey(next)) && guard < STOCK_FALLBACKS.length) {
      next = STOCK_FALLBACKS[fi % STOCK_FALLBACKS.length]
      fi += 1
      guard += 1
    }
    seen.add(imageKey(next))
    return { ...item, featured_image_url: next, _imageRemapped: true }
  })
}

function cleanExcerpt(text) {
  const t = (text || '').trim()
  if (!t || /published live seo article/i.test(t)) return ''
  return t
}

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function PostImage({ src, alt, className = '' }) {
  const [failed, setFailed] = useState(false)
  if (failed || !src) return <div className={`zo-blog-img-fallback ${className}`.trim()} aria-hidden="true" />
  return (
    <img
      src={src}
      alt={alt || ''}
      className={className}
      loading="lazy"
      decoding="async"
      onError={() => setFailed(true)}
    />
  )
}

function postLinkProps(item) {
  const href = toSiteBlogHref(item)
  if (isOffsiteBlogHref(href)) {
    return { href, target: '_blank', rel: 'noopener noreferrer' }
  }
  return { href }
}

export default function BlogPage() {
  const [topic, setTopic] = useState('All')
  const [query, setQuery] = useState('')
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const { data } = await listBlogPosts(0, 60)
        const apiPosts = Array.isArray(data?.posts) ? data.posts : []
        if (!cancelled) setPosts(apiPosts)
      } catch {
        if (!cancelled) setPosts([])
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => { cancelled = true }
  }, [])

  const topics = useMemo(() => {
    const set = new Set(posts.map((p) => p.category).filter(Boolean))
    return ['All', ...Array.from(set).slice(0, 8)]
  }, [posts])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return withUniqueImages(
      posts.filter((p) => {
        if (topic !== 'All' && p.category !== topic) return false
        if (!q) return true
        return (
          (p.title || '').toLowerCase().includes(q) ||
          (p.excerpt || '').toLowerCase().includes(q) ||
          (p.category || '').toLowerCase().includes(q)
        )
      }),
    )
  }, [posts, topic, query])

  const featured = filtered[0] || null
  const rest = featured ? filtered.slice(1) : []
  const secondary = rest.slice(0, 2)
  const grid = rest.slice(2)

  return (
    <div className="rv-page zo-blog-page">
      <RevampHeader />

      <section className="zo-blog-hero" aria-label="Blog">
        <div className="rv-shell zo-blog-hero-inner">
          <div className="zo-blog-hero-copy">
            <p className="zo-blog-eyebrow">{ZEORBIT_BLOG.eyebrow}</p>
            <h1>{ZEORBIT_BLOG.title}</h1>
            <p className="zo-blog-lead">{ZEORBIT_BLOG.lead}</p>
          </div>

          <div className="zo-blog-toolbar">
            <label className="zo-blog-search">
              <Search size={16} strokeWidth={2.2} aria-hidden="true" />
              <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search articles"
                aria-label="Search articles"
              />
            </label>
            <div className="zo-blog-filters" role="tablist" aria-label="Filter by topic">
              {topics.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  role="tab"
                  aria-selected={topic === cat}
                  className={`zo-blog-filter${topic === cat ? ' is-active' : ''}`}
                  onClick={() => setTopic(cat)}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      <main className="zo-blog-main">
        <div className="rv-shell zo-blog-layout">
          {loading && !featured ? (
            <p className="zo-blog-empty">Loading articles…</p>
          ) : featured ? (
            <a className="zo-blog-feature" {...postLinkProps(featured)}>
              <div className="zo-blog-feature-media">
                <PostImage src={featured.featured_image_url} alt="" />
                <div className="zo-blog-feature-shade" aria-hidden />
              </div>
              <div className="zo-blog-feature-copy">
                <div className="zo-blog-card-meta">
                  <span className="zo-blog-card-cat">{featured.category}</span>
                  <span>{formatDate(featured.published_at)}</span>
                </div>
                <h2>{featured.title}</h2>
                {cleanExcerpt(featured.excerpt) ? <p>{cleanExcerpt(featured.excerpt)}</p> : null}
                <span className="zo-blog-card-cta">
                  Read article <ArrowRight size={16} strokeWidth={2.2} />
                </span>
              </div>
            </a>
          ) : (
            <p className="zo-blog-empty">
              {posts.length === 0
                ? 'No articles published yet. New posts from the SEO tool will appear here.'
                : 'No articles match that search.'}
            </p>
          )}

          {secondary.length > 0 ? (
            <div className="zo-blog-secondary">
              {secondary.map((item) => (
                <a
                  key={item.id}
                  className="zo-blog-secondary-card"
                  {...postLinkProps(item)}
                >
                  <div className="zo-blog-secondary-media">
                    <PostImage src={item.featured_image_url} alt="" />
                  </div>
                  <div className="zo-blog-secondary-body">
                    <div className="zo-blog-card-meta">
                      <span className="zo-blog-card-cat">{item.category}</span>
                      <span>{formatDate(item.published_at)}</span>
                    </div>
                    <h3>{item.title}</h3>
                    <span className="zo-blog-card-cta">
                      Read article <ArrowRight size={14} strokeWidth={2.2} />
                    </span>
                  </div>
                </a>
              ))}
            </div>
          ) : null}

          {grid.length > 0 ? (
            <section className="zo-blog-more" aria-label="More articles">
              <div className="zo-blog-more-head">
                <h2>More from ZeOrbit</h2>
              </div>
              <div className="zo-blog-grid">
                {grid.map((item) => (
                  <a
                    key={item.id}
                    className="zo-blog-card"
                    {...postLinkProps(item)}
                  >
                    <div className="zo-blog-card-media">
                      <PostImage src={item.featured_image_url} alt="" />
                    </div>
                    <div className="zo-blog-card-body">
                      <div className="zo-blog-card-meta">
                        <span className="zo-blog-card-cat">{item.category}</span>
                        <span>{formatDate(item.published_at)}</span>
                      </div>
                      <h3>{item.title}</h3>
                      {cleanExcerpt(item.excerpt) ? <p>{cleanExcerpt(item.excerpt)}</p> : null}
                      <span className="zo-blog-card-cta">
                        Read article <ArrowRight size={14} strokeWidth={2.2} />
                      </span>
                    </div>
                  </a>
                ))}
              </div>
            </section>
          ) : null}
        </div>
      </main>

      <SiteFooter />
    </div>
  )
}
