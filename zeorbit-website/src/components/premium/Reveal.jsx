import { useEffect, useRef, useState } from 'react'

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

    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.classList.add('is-visible')
          io.disconnect()
        }
      },
      { threshold: options.threshold ?? 0.08, rootMargin: options.rootMargin ?? '80px 0px 20% 0px' },
    )

    io.observe(el)
    return () => io.disconnect()
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
