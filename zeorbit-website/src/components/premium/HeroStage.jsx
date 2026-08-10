import { useEffect, useRef, useState } from 'react'

/**
 * Cinematic product stage — demo-reel screen cycling + light cursor tilt.
 * Feels like a silent product video with a touch of interaction.
 */
export default function HeroStage({ desktopScreens = [], mobileScreens = [], className = '' }) {
  const stageRef = useRef(null)
  const rafRef = useRef(0)
  const targetRef = useRef({ x: 0, y: 0 })
  const currentRef = useRef({ x: 0, y: 0 })
  const [desktopIndex, setDesktopIndex] = useState(0)
  const [mobileIndex, setMobileIndex] = useState(0)
  const [reduceMotion, setReduceMotion] = useState(false)

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const sync = () => setReduceMotion(mq.matches)
    sync()
    mq.addEventListener('change', sync)
    return () => mq.removeEventListener('change', sync)
  }, [])

  useEffect(() => {
    if (reduceMotion || desktopScreens.length < 2) return undefined
    const id = window.setInterval(() => {
      setDesktopIndex((i) => (i + 1) % desktopScreens.length)
    }, 3800)
    return () => window.clearInterval(id)
  }, [desktopScreens.length, reduceMotion])

  useEffect(() => {
    if (reduceMotion || mobileScreens.length < 2) return undefined
    const id = window.setInterval(() => {
      setMobileIndex((i) => (i + 1) % mobileScreens.length)
    }, 4200)
    return () => window.clearInterval(id)
  }, [mobileScreens.length, reduceMotion])

  useEffect(() => {
    if (reduceMotion) return undefined
    const el = stageRef.current
    if (!el) return undefined

    const onMove = (e) => {
      const rect = el.getBoundingClientRect()
      const nx = ((e.clientX - rect.left) / rect.width - 0.5) * 2
      const ny = ((e.clientY - rect.top) / rect.height - 0.5) * 2
      targetRef.current = {
        x: Math.max(-1, Math.min(1, nx)),
        y: Math.max(-1, Math.min(1, ny)),
      }
    }

    const onLeave = () => {
      targetRef.current = { x: 0, y: 0 }
    }

    const tick = () => {
      const cur = currentRef.current
      const tgt = targetRef.current
      cur.x += (tgt.x - cur.x) * 0.08
      cur.y += (tgt.y - cur.y) * 0.08
      el.style.setProperty('--tilt-x', cur.x.toFixed(3))
      el.style.setProperty('--tilt-y', cur.y.toFixed(3))
      rafRef.current = requestAnimationFrame(tick)
    }

    el.addEventListener('pointermove', onMove)
    el.addEventListener('pointerleave', onLeave)
    rafRef.current = requestAnimationFrame(tick)

    return () => {
      el.removeEventListener('pointermove', onMove)
      el.removeEventListener('pointerleave', onLeave)
      cancelAnimationFrame(rafRef.current)
    }
  }, [reduceMotion])

  return (
    <div
      ref={stageRef}
      className={`cz-hero-stage ${reduceMotion ? 'is-static' : ''} ${className}`.trim()}
      aria-label="Interactive product demo"
    >
      <div className="cz-hero-stage-glow" aria-hidden="true" />
      <div className="cz-hero-stage-floor" aria-hidden="true" />

      <div className="cz-hero-stage-world" aria-hidden="true">
        <figure className="cz-hero-stage-mac">
          <div className="cz-hero-reel-host">
            {desktopScreens.map((s, i) => (
              <img
                key={s.src}
                src={s.src}
                alt=""
                className={i === desktopIndex ? 'is-active' : ''}
                loading={i === 0 ? 'eager' : 'lazy'}
                decoding="async"
              />
            ))}
          </div>
        </figure>

        <figure className="cz-hero-stage-phone">
          <div className="cz-hero-reel-host cz-hero-reel-host-phone">
            {mobileScreens.map((s, i) => (
              <img
                key={s.src}
                src={s.src}
                alt=""
                className={i === mobileIndex ? 'is-active' : ''}
                loading={i === 0 ? 'eager' : 'lazy'}
                decoding="async"
              />
            ))}
          </div>
        </figure>
      </div>
    </div>
  )
}
