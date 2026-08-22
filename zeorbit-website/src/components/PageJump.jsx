import { useEffect, useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

export default function PageJump() {
  const [show, setShow] = useState(false)

  useEffect(() => {
    const onScroll = () => {
      const y = window.scrollY || document.documentElement.scrollTop
      const max = document.documentElement.scrollHeight - window.innerHeight
      setShow(y > 240 && max > 480)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
    }
  }, [])

  const jump = (edge) => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const top = edge === 'top' ? 0 : document.documentElement.scrollHeight
    window.scrollTo({ top, left: 0, behavior: reduce ? 'auto' : 'smooth' })
  }

  if (!show) return null

  return (
    <div className="zo-page-jump" role="group" aria-label="Page scroll">
      <button type="button" className="zo-page-jump-btn" aria-label="Back to top" title="Top" onClick={() => jump('top')}>
        <ChevronUp size={18} strokeWidth={2.2} />
      </button>
      <button type="button" className="zo-page-jump-btn" aria-label="Jump to bottom" title="Bottom" onClick={() => jump('bottom')}>
        <ChevronDown size={18} strokeWidth={2.2} />
      </button>
    </div>
  )
}
