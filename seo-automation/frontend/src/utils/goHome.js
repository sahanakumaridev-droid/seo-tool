/** Always land on the homepage at the top — even if already on `/`. */
export function goToHomepageTop(navigate, pathname) {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const toTop = () => window.scrollTo({ top: 0, left: 0, behavior: reduce ? 'auto' : 'smooth' })
  if (pathname === '/') {
    if (window.location.hash) {
      window.history.replaceState(null, '', '/')
    }
    toTop()
    return
  }
  navigate('/')
  window.setTimeout(toTop, 0)
}
