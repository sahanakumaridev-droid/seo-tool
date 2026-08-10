import { useMemo, useState } from 'react'
import { ArrowRight, ArrowUpRight, Search } from 'lucide-react'
import RevampHeader from '../components/revamp/RevampHeader'
import SiteFooter from '../components/SiteFooter'
import { ZEORBIT_BLOG, ZEORBIT_BLOG_POSTS } from '../data/zeorbitBlog'

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

export default function BlogPage() {
  const [topic, setTopic] = useState('All')
  const [query, setQuery] = useState('')

  const topics = useMemo(() => {
    const set = new Set(ZEORBIT_BLOG_POSTS.map((p) => p.category).filter(Boolean))
    return ['All', ...Array.from(set)]
  }, [])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return ZEORBIT_BLOG_POSTS.filter((p) => {
      if (topic !== 'All' && p.category !== topic) return false
      if (!q) return true
      return (
        p.title.toLowerCase().includes(q) ||
        (p.excerpt || '').toLowerCase().includes(q) ||
        (p.category || '').toLowerCase().includes(q)
      )
    })
  }, [topic, query])

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
          {featured ? (
            <a
              className="zo-blog-feature"
              href={featured.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <div className="zo-blog-feature-media">
                <PostImage src={featured.featured_image_url} alt="" />
              </div>
              <div className="zo-blog-feature-copy">
                <div className="zo-blog-card-meta">
                  <span className="zo-blog-card-cat">{featured.category}</span>
                  <span>{formatDate(featured.published_at)}</span>
                </div>
                <h2>{featured.title}</h2>
                {featured.excerpt ? <p>{featured.excerpt}</p> : null}
                <span className="zo-blog-card-cta">
                  Read on ZeOrbit <ArrowUpRight size={16} strokeWidth={2.2} />
                </span>
              </div>
            </a>
          ) : (
            <p className="zo-blog-empty">No articles match that search.</p>
          )}

          {secondary.length > 0 ? (
            <div className="zo-blog-secondary">
              {secondary.map((item) => (
                <a
                  key={item.id}
                  className="zo-blog-secondary-card"
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
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
                <a href={ZEORBIT_BLOG.sourceUrl} target="_blank" rel="noopener noreferrer">
                  View all on zeorbit.com <ArrowUpRight size={15} />
                </a>
              </div>
              <div className="zo-blog-grid">
                {grid.map((item) => (
                  <a
                    key={item.id}
                    className="zo-blog-card"
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
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
                      {item.excerpt ? <p>{item.excerpt}</p> : null}
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
