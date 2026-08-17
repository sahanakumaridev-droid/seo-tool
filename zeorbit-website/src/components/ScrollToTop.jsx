import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

/** Reset scroll on every route change so tab navigation always opens at the top. */
export default function ScrollToTop() {
  const { pathname, hash } = useLocation()

  useEffect(() => {
    if (hash) return
    window.scrollTo(0, 0)
  }, [pathname, hash])

  return null
}
