import { useEffect, useRef, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

function cardStep(track) {
  const card = track.querySelector('.wds-work-card')
  if (!card) return track.clientWidth
  const styles = getComputedStyle(track)
  const gap = Number.parseFloat(styles.columnGap || styles.gap) || 18
  return card.getBoundingClientRect().width + gap
}

export default function WorkCarousel({ items }) {
  const trackRef = useRef(null)
  const hoverRef = useRef(false)
  const [canPrev, setCanPrev] = useState(false)
  const [canNext, setCanNext] = useState(true)
  const [page, setPage] = useState(0)
  const [pages, setPages] = useState(items.length)

  const sync = () => {
    const track = trackRef.current
    if (!track) return
    const max = Math.max(0, track.scrollWidth - track.clientWidth)
    const step = cardStep(track)
    const nextPage = step ? Math.round(track.scrollLeft / step) : 0
    setPage(nextPage)
    setPages(step ? Math.max(1, Math.round(max / step) + 1) : 1)
    setCanPrev(track.scrollLeft > 12)
    setCanNext(track.scrollLeft < max - 12)
  }

  const go = (dir) => {
    const track = trackRef.current
    if (!track) return
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    track.scrollBy({
      left: dir * cardStep(track),
      behavior: reduce ? 'auto' : 'smooth',
    })
  }

  const goTo = (index) => {
    const track = trackRef.current
    if (!track) return
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    track.scrollTo({
      left: index * cardStep(track),
      behavior: reduce ? 'auto' : 'smooth',
    })
  }

  useEffect(() => {
    const track = trackRef.current
    if (!track) return undefined
    sync()
    const onScroll = () => sync()
    track.addEventListener('scroll', onScroll, { passive: true })
    const ro = new ResizeObserver(sync)
    ro.observe(track)
    return () => {
      track.removeEventListener('scroll', onScroll)
      ro.disconnect()
    }
  }, [items])

  useEffect(() => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduce || items.length < 3) return undefined
    const onVis = () => {
      hoverRef.current = document.hidden
    }
    document.addEventListener('visibilitychange', onVis)
    const id = window.setInterval(() => {
      if (hoverRef.current || document.hidden) return
      const track = trackRef.current
      if (!track) return
      const max = track.scrollWidth - track.clientWidth
      if (track.scrollLeft >= max - 12) {
        track.scrollTo({ left: 0, behavior: 'smooth' })
      } else {
        go(1)
      }
    }, 4800)
    return () => {
      window.clearInterval(id)
      document.removeEventListener('visibilitychange', onVis)
    }
  }, [items.length])

  return (
    <div
      className="wds-work-carousel"
      onMouseEnter={() => {
        hoverRef.current = true
      }}
      onMouseLeave={() => {
        hoverRef.current = false
      }}
      onFocus={() => {
        hoverRef.current = true
      }}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) hoverRef.current = false
      }}
    >
      <div className="wds-work-stage">
        <button
          type="button"
          className="wds-work-arrow is-prev"
          aria-label="Previous work"
          disabled={!canPrev}
          onClick={() => go(-1)}
        >
          <ChevronLeft size={20} strokeWidth={2.4} />
        </button>

        <div
          ref={trackRef}
          className="wds-work-track"
          tabIndex={0}
          aria-label="Our work carousel"
          onKeyDown={(event) => {
            if (event.key === 'ArrowRight') {
              event.preventDefault()
              go(1)
            }
            if (event.key === 'ArrowLeft') {
              event.preventDefault()
              go(-1)
            }
          }}
        >
          {items.map((item) => {
            const media = (
              <>
                <div className="wds-work-media">
                  <img
                    src={item.image}
                    alt={item.alt || item.title || ''}
                    loading="lazy"
                    decoding="async"
                  />
                </div>
                <div className="wds-work-meta">
                  <h3>{item.title}</h3>
                  <p>{item.meta}</p>
                </div>
              </>
            )

            return (
              <article key={item.title} className="wds-work-card">
                {item.href ? (
                  <a
                    className="wds-work-link"
                    href={item.href}
                    target="_blank"
                    rel="noreferrer"
                    aria-label={`${item.title} — visit live site`}
                  >
                    {media}
                  </a>
                ) : (
                  media
                )}
              </article>
            )
          })}
        </div>

        <button
          type="button"
          className="wds-work-arrow is-next"
          aria-label="Next work"
          disabled={!canNext}
          onClick={() => go(1)}
        >
          <ChevronRight size={20} strokeWidth={2.4} />
        </button>
      </div>

      <div className="wds-work-dots" role="tablist" aria-label="Work slides">
        {Array.from({ length: pages }, (_, i) => (
          <button
            key={i}
            type="button"
            role="tab"
            aria-selected={i === page}
            className={`wds-work-dot${i === page ? ' is-active' : ''}`}
            onClick={() => goTo(i)}
          >
            <span className="sr-only">Slide {i + 1}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
