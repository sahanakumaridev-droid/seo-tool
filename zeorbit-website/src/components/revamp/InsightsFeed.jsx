import { useEffect, useMemo, useState } from 'react'
import { ArrowRight } from 'lucide-react'
import { listBlogPosts } from '../../api'
import { ZEORBIT_BLOG_POSTS } from '../../data/zeorbitBlog'
import { blogArticleClickProps } from '../../lib/blogUrls'
import { visibleBlogPosts } from '../../lib/blogListing'

const FALLBACK_IMAGES = [
  '/from-zeorbit/blog/small-business-website-cost-in-san-diego.jpg',
  '/from-zeorbit/blog/plumbing-website-designer.jpg',
  '/from-zeorbit/blog/wordpress-vs-shopify-plumbing-website-design.jpg',
  '/from-zeorbit/blog/website-redesign-increase-hvac-leads-in-la.jpg',
  '/from-zeorbit/blog/la-jolla-sports-website-design-services.jpg',
  '/from-zeorbit/blog/why-hvac-website-not-bringing-new-customers-la.jpg',
]

const FALLBACK_POSTS = ZEORBIT_BLOG_POSTS.map((item) => ({
  ...item,
  source: item.source || 'zeorbit.com',
}))

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function hashIndex(value, mod) {
  const str = String(value || '')
  let h = 0
  for (let i = 0; i < str.length; i += 1) h = (h * 31 + str.charCodeAt(i)) >>> 0
  return h % mod
}

function resolveImage(item, index, usedKeys) {
  const raw = item?.featured_image_url || ''
  const key = (() => {
    const m = String(raw).match(/(photo-[a-zA-Z0-9_-]+)/i)
    return (m ? m[1] : String(raw).split('?')[0]).toLowerCase()
  })()
  if (raw && key && !usedKeys.has(key)) {
    usedKeys.add(key)
    return raw
  }
  for (let i = 0; i < FALLBACK_IMAGES.length; i += 1) {
    const cand = FALLBACK_IMAGES[(hashIndex(item?.id || item?.title || index, FALLBACK_IMAGES.length) + i) % FALLBACK_IMAGES.length]
    const ck = cand
    if (!usedKeys.has(ck)) {
      usedKeys.add(ck)
      return cand
    }
  }
  return FALLBACK_IMAGES[hashIndex(item?.id || item?.title || index, FALLBACK_IMAGES.length)]
}

function PostImage({ src, alt }) {
  const [current, setCurrent] = useState(src)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    setCurrent(src)
    setFailed(false)
  }, [src])

  if (failed || !current) {
    return <div className="zo-blog-img-fallback" aria-hidden="true" />
  }

  return (
    <img
      src={current}
      alt={alt}
      loading="lazy"
      decoding="async"
      onError={() => {
        const fallback = FALLBACK_IMAGES[hashIndex(alt, FALLBACK_IMAGES.length)]
        if (current !== fallback) setCurrent(fallback)
        else setFailed(true)
      }}
    />
  )
}

function PostCard({ item, index, featured = false, usedKeys }) {
  const hrefProps = blogArticleClickProps(item)
  const image = resolveImage(item, index, usedKeys || new Set())
  const dateLabel = formatDate(item.published_at) || (item.source === 'fallback' ? 'Guide' : 'Live')
  const place = [item.city, item.state].filter(Boolean).join(', ')

  return (
    <a
      className={`zo-blog-card${featured ? ' is-featured' : ''}`}
      {...hrefProps}
    >
      <div className="zo-blog-card-media">
        <PostImage src={image} alt="" />
      </div>
      <div className="zo-blog-card-body">
        <div className="zo-blog-card-meta">
          <span className="zo-blog-card-cat">{item.category || 'Insights'}</span>
          <span>{dateLabel}</span>
          {place ? <span>{place}</span> : null}
        </div>
        <h3>{item.title}</h3>
        {item.excerpt ? <p>{item.excerpt}</p> : null}
        <span className="zo-blog-card-cta">
          Read article <ArrowRight size={15} strokeWidth={2.2} />
        </span>
      </div>
    </a>
  )
}

/**
 * Blog / Insights cards.
 * Prefers live SEO Tool posts when available; otherwise uses zeorbit.com blog content.
 */
export default function InsightsFeed({
  limit = 6,
  showViewAll = true,
  emptyUseFallback = true,
  layout = 'grid',
  preferZeorbit = false,
}) {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [category, setCategory] = useState('All')

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError('')
      try {
        if (preferZeorbit) {
          if (!cancelled) {
            setPosts(ZEORBIT_BLOG_POSTS.slice(0, limit))
          }
          return
        }
        const { data } = await listBlogPosts(0, Math.max(limit + 24, 24))
        if (cancelled) return
        const apiPosts = visibleBlogPosts(Array.isArray(data?.posts) ? data.posts : []).slice(0, limit)
        setPosts(apiPosts.length ? apiPosts : (emptyUseFallback ? ZEORBIT_BLOG_POSTS.slice(0, limit) : []))
      } catch (err) {
        if (cancelled) return
        setError(err?.message || 'Could not load blog posts')
        setPosts(emptyUseFallback ? ZEORBIT_BLOG_POSTS.slice(0, limit) : [])
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => { cancelled = true }
  }, [limit, preferZeorbit, emptyUseFallback])

  const useFallback = !loading && posts.length === 0 && emptyUseFallback
  const items = useFallback ? FALLBACK_POSTS.slice(0, limit) : posts
  const imageKeys = useMemo(() => new Set(), [items])

  const categories = useMemo(() => {
    const set = new Set()
    items.forEach((item) => {
      if (item.category) set.add(item.category)
    })
    return ['All', ...Array.from(set).slice(0, 6)]
  }, [items])

  const filtered = useMemo(() => {
    if (category === 'All') return items
    return items.filter((item) => item.category === category)
  }, [items, category])

  const isMagazine = layout === 'magazine'
  const featured = isMagazine && filtered.length > 0 ? filtered[0] : null
  const rest = featured ? filtered.slice(1) : filtered

  if (!isMagazine) {
    return (
      <div className="rv-insights-wrap">
        {loading ? <p className="rv-insights-status">Loading published insights…</p> : null}
        {!loading && error && posts.length === 0 ? (
          <p className="rv-insights-status rv-insights-error">{error}</p>
        ) : null}
        {!loading && posts.length === 0 && !useFallback ? (
          <p className="rv-insights-status">
            No published articles yet. Publish from the ZeOrbit SEO tool to populate this feed.
          </p>
        ) : null}

        <div className="rv-insights-grid">
          {items.map((item, index) => (
            <PostCard key={item.id || item.title} item={item} index={index} usedKeys={imageKeys} />
          ))}
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

  return (
    <div className="zo-blog-feed">
      {loading ? (
        <div className="zo-blog-skeleton" aria-busy="true" aria-label="Loading articles">
          <div className="zo-blog-skeleton-feature" />
          <div className="zo-blog-skeleton-grid">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="zo-blog-skeleton-card" />
            ))}
          </div>
        </div>
      ) : null}

      {!loading && error && posts.length === 0 && !useFallback ? (
        <p className="rv-insights-status rv-insights-error">{error}</p>
      ) : null}

      {!loading && posts.length === 0 && !useFallback ? (
        <p className="rv-insights-status">
          No published articles yet. Publish from the ZeOrbit SEO tool to populate this feed.
        </p>
      ) : null}

      {!loading && filtered.length > 0 ? (
        <>
          {categories.length > 2 ? (
            <div className="zo-blog-filters" role="tablist" aria-label="Filter by topic">
              {categories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  role="tab"
                  aria-selected={category === cat}
                  className={`zo-blog-filter${category === cat ? ' is-active' : ''}`}
                  onClick={() => setCategory(cat)}
                >
                  {cat}
                </button>
              ))}
            </div>
          ) : null}

          {featured ? <PostCard item={featured} index={0} featured usedKeys={imageKeys} /> : null}

          {rest.length > 0 ? (
            <div className="zo-blog-grid">
              {rest.map((item, index) => (
                <PostCard key={item.id || item.title} item={item} index={index + 1} usedKeys={imageKeys} />
              ))}
            </div>
          ) : null}
        </>
      ) : null}
    </div>
  )
}
