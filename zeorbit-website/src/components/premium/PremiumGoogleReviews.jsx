import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { GOOGLE_PROFILE, GOOGLE_REVIEWS } from '../../data/googleReviews'

const AUTOPLAY_MS = 4200

function GoogleMark({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#EA4335" d="M24 9.5c3.4 0 6.4 1.2 8.8 3.5l6.6-6.6C35.4 2.5 30.1 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.7 6c1.8-5.4 6.9-9.7 13.7-9.7z" />
      <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.6c-.5 3-2.2 5.5-4.7 7.2l7.3 5.7c4.3-4 6.8-9.8 6.8-17.4z" />
      <path fill="#FBBC05" d="M10.3 19.2c-.5 1.5-.8 3.1-.8 4.8s.3 3.3.8 4.8l-7.7 6C1 31.6 0 27.9 0 24s1-7.6 2.6-10.8l7.7 6z" />
      <path fill="#34A853" d="M24 48c6.1 0 11.4-2 15.2-5.4l-7.3-5.7c-2 1.4-4.7 2.2-7.9 2.2-6.8 0-12.9-4.3-13.7-9.7l-7.7 6C6.5 42.6 14.6 48 24 48z" />
    </svg>
  )
}

function Face({ review }) {
  const [failed, setFailed] = useState(false)
  if (failed || !review.avatar) return null
  return <img src={review.avatar} alt="" loading="lazy" decoding="async" onError={() => setFailed(true)} />
}

function Avatar({ review }) {
  const [failed, setFailed] = useState(false)
  const initial = review.author.trim().charAt(0).toUpperCase()

  return (
    <div className="cz-gr-avatar" aria-hidden="true">
      {!failed && review.avatar ? (
        <img src={review.avatar} alt="" loading="lazy" decoding="async" onError={() => setFailed(true)} />
      ) : (
        <span className="cz-gr-avatar-fallback">{initial}</span>
      )}
      <span className="cz-gr-avatar-blinds" />
    </div>
  )
}

function ReviewCard({ review }) {
  return (
    <article className="cz-gr-card">
      <div className="cz-gr-card-top">
        <Avatar review={review} />
        <p className="cz-gr-quote">“{review.text}”</p>
      </div>
      <div className="cz-gr-card-bottom">
        <div>
          <strong>{review.author}</strong>
          <span>GOOGLE REVIEW</span>
        </div>
        <div className="cz-gr-rating-pill" aria-label={`${review.rating} out of 5 stars`}>
          {review.rating.toFixed(1)}★
        </div>
      </div>
    </article>
  )
}

export default function PremiumGoogleReviews() {
  const reviews = GOOGLE_REVIEWS
  const [index, setIndex] = useState(0)
  const [perView, setPerView] = useState(2)
  const [stepPx, setStepPx] = useState(0)
  const [paused, setPaused] = useState(false)
  const viewportRef = useRef(null)
  const trackRef = useRef(null)

  useEffect(() => {
    const sync = () => {
      const w = window.innerWidth
      setPerView(w < 720 ? 1 : 2)
    }
    sync()
    window.addEventListener('resize', sync)
    return () => window.removeEventListener('resize', sync)
  }, [])

  const maxIndex = Math.max(0, reviews.length - perView)

  const measure = useCallback(() => {
    const slide = trackRef.current?.querySelector('.cz-gr-slide')
    const track = trackRef.current
    if (!slide || !track) return
    const gap = parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap) || 22
    setStepPx(slide.getBoundingClientRect().width + gap)
  }, [])

  useEffect(() => {
    measure()
    const ro = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(measure) : null
    if (viewportRef.current && ro) ro.observe(viewportRef.current)
    window.addEventListener('resize', measure)
    return () => {
      ro?.disconnect()
      window.removeEventListener('resize', measure)
    }
  }, [measure, perView, reviews.length])

  useEffect(() => {
    setIndex((i) => Math.min(i, maxIndex))
  }, [maxIndex])

  const pages = useMemo(() => maxIndex + 1, [maxIndex])

  const prev = useCallback(() => {
    setIndex((i) => (i <= 0 ? maxIndex : i - 1))
  }, [maxIndex])

  const next = useCallback(() => {
    setIndex((i) => (i >= maxIndex ? 0 : i + 1))
  }, [maxIndex])

  useEffect(() => {
    if (paused || maxIndex < 1) return undefined
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return undefined
    const id = window.setInterval(() => {
      setIndex((i) => (i >= maxIndex ? 0 : i + 1))
    }, AUTOPLAY_MS)
    return () => window.clearInterval(id)
  }, [paused, maxIndex])

  const faceAvatars = reviews.slice(0, 3)
  const offset = stepPx > 0 ? -(index * stepPx) : 0

  return (
    <section id="reviews" className="cz-gr" aria-label="Google reviews">
      <div className="cz-gr-shell">
        <header className="cz-gr-head">
          <div className="cz-gr-head-copy">
            <h2>What Our Clients Say</h2>
            <a className="cz-gr-google-meta" href={GOOGLE_PROFILE.reviewsUrl} target="_blank" rel="noreferrer">
              <GoogleMark size={18} />
              <strong>{GOOGLE_PROFILE.rating}</strong>
              <span>on Google</span>
            </a>
          </div>
          <div className="cz-gr-head-side">
            <div className="cz-gr-faces" aria-hidden="true">
              {faceAvatars.map((r) => (
                <Face key={r.author} review={r} />
              ))}
            </div>
            <p>We create digital experiences that solve real business problems.</p>
          </div>
        </header>

        <div
          className="cz-gr-viewport"
          ref={viewportRef}
          onMouseEnter={() => setPaused(true)}
          onMouseLeave={() => setPaused(false)}
          onFocusCapture={() => setPaused(true)}
          onBlurCapture={(e) => {
            if (!e.currentTarget.contains(e.relatedTarget)) setPaused(false)
          }}
        >
          <div
            className="cz-gr-track"
            ref={trackRef}
            style={{
              transform: `translate3d(${offset}px, 0, 0)`,
              '--cz-gr-per': perView,
            }}
          >
            {reviews.map((review) => (
              <div key={review.author} className="cz-gr-slide">
                <ReviewCard review={review} />
              </div>
            ))}
          </div>
        </div>

        <div className="cz-gr-controls">
          <div className="cz-gr-arrows">
            <button type="button" className="cz-gr-arrow" onClick={prev} aria-label="Previous reviews">
              <ChevronLeft size={20} strokeWidth={2.4} />
            </button>
            <button type="button" className="cz-gr-arrow" onClick={next} aria-label="Next reviews">
              <ChevronRight size={20} strokeWidth={2.4} />
            </button>
          </div>
          <div className="cz-gr-dots" role="tablist" aria-label="Review pages">
            {Array.from({ length: pages }).map((_, i) => (
              <button
                key={i}
                type="button"
                role="tab"
                aria-selected={i === index}
                className={`cz-gr-dot${i === index ? ' is-active' : ''}`}
                onClick={() => setIndex(i)}
                aria-label={`Go to review set ${i + 1}`}
              />
            ))}
          </div>
          <a className="cz-gr-write" href={GOOGLE_PROFILE.writeReviewUrl} target="_blank" rel="noreferrer">
            Review us on Google
          </a>
        </div>
      </div>
    </section>
  )
}
