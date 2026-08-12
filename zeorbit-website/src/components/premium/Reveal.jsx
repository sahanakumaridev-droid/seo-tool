import { useEffect, useRef, useState } from 'react'

function isPastOrInView(el, bottomMargin = 0.12) {
  if (!el || typeof window === 'undefined') return false
  const rect = el.getBoundingClientRect()
  const view = window.innerHeight || 1
  // Already on screen, or scrolled past (so fast jumps don't leave blank holes)
  return rect.top < view * (1 - bottomMargin)
}

/** Intersection reveal with optional eager / scrub styles */
export function useReveal(options = {}) {
  const ref = useRef(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return undefined

    if (options.eager) {
      el.classList.add('is-visible')
      return undefined
    }

    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduce) {
      el.classList.add('is-visible')
      return undefined
    }

    const show = () => {
      el.classList.add('is-visible')
    }

    // Catch elements already in / above the viewport (hash jumps, fast scroll)
    if (isPastOrInView(el)) {
      show()
      return undefined
    }

    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting || isPastOrInView(el)) {
          show()
          io.disconnect()
        }
      },
      {
        threshold: options.threshold ?? 0.01,
        rootMargin: options.rootMargin ?? '180px 0px 25% 0px',
      },
    )

    io.observe(el)

    // Fallback: if user skips past via hash / programmatic scroll, reveal leftovers
    const onScroll = () => {
      if (isPastOrInView(el)) {
        show()
        io.disconnect()
        window.removeEventListener('scroll', onScroll)
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true })

    return () => {
      io.disconnect()
      window.removeEventListener('scroll', onScroll)
    }
  }, [options.threshold, options.rootMargin, options.eager])

  return ref
}

export function Reveal({ as: Tag = 'div', className = '', eager = false, children, ...rest }) {
  const ref = useReveal({ eager })
  return (
    <Tag ref={ref} className={`cz-reveal ${eager ? 'is-visible' : ''} ${className}`.trim()} {...rest}>
      {children}
    </Tag>
  )
}

/** Maps scroll progress of an element (0–1) for cinematic transforms */
export function useScrollProgress() {
  const ref = useRef(null)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const el = ref.current
    if (!el) return undefined
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduce) return undefined

    let frame = 0
    const update = () => {
      frame = 0
      const rect = el.getBoundingClientRect()
      const view = window.innerHeight || 1
      const total = rect.height + view
      const raw = (view - rect.top) / total
      setProgress(Math.min(1, Math.max(0, raw)))
    }

    const onScroll = () => {
      if (frame) return
      frame = requestAnimationFrame(update)
    }

    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
      if (frame) cancelAnimationFrame(frame)
    }
  }, [])

  return [ref, progress]
}
