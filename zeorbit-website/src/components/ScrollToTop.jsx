import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

/** Reset scroll on every route change so tab navigation always opens at the top. */
export default function ScrollToTop() {
  const { pathname, hash } = useLocation()

  useEffect(() => {
    if (hash) {
      const id = decodeURIComponent(hash.replace('#', ''))
      // Wait a tick so the new page can mount before scrolling to an anchor.
      requestAnimationFrame(() => {
        const el = document.getElementById(id)
        if (el) {
          el.scrollIntoView({ block: 'start' })
          return
        }
        window.scrollTo(0, 0)
      })
      return
    }

    window.scrollTo(0, 0)
  }, [pathname, hash])

  return null
}
