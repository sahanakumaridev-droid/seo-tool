/** Keep blog article clicks on the live ZeOrbit site, not the SEO-tool host. */

function articlePath(path) {
  const clean = (path || '/').replace(/\/$/, '') || '/'
  if (clean.startsWith('/p/')) return `/${clean.slice(3)}`
  return clean
}

export function toSiteBlogHref(item) {
  const raw = (item?.url || item?.public_url || '').trim()
  if (!raw) return '/blog'
  if (raw.startsWith('/p/')) return articlePath(raw.split('?')[0])
  if (raw.startsWith('/') && !raw.startsWith('//')) return articlePath(raw)

  try {
    const u = new URL(raw)
    const host = (u.hostname || '').toLowerCase()
    const path = articlePath(u.pathname || '/')
    if (host.includes('nip.io') || host.startsWith('seo.') || host.endsWith('zeorbit.com')) {
      if (path === '/' || path === '/blog') return '/blog'
      return path
    }
  } catch {
    return '/blog'
  }
  return '/blog'
}

export function isOffsiteBlogHref(href) {
  if (!href || href.startsWith('/')) return false
  try {
    const host = new URL(href).hostname.replace(/^www\./, '').toLowerCase()
    return host !== 'zeorbit.com'
  } catch {
    return false
  }
}

/** Force a real document load so nginx serves the published article, not the SPA contact shell. */
export function blogArticleClickProps(item) {
  const href = toSiteBlogHref(item)
  if (isOffsiteBlogHref(href)) {
    return { href, target: '_blank', rel: 'noopener noreferrer' }
  }
  const go = (event) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return
    event.preventDefault()
    event.stopPropagation()
    const path = href.startsWith('/') ? href : `/${href}`
    const here = window.location.pathname.replace(/\/$/, '') || '/'
    const there = path.replace(/\/$/, '') || '/'
    if (here === there) {
      window.location.reload()
      return
    }
    window.location.href = `${window.location.origin}${path}`
  }
  return {
    href,
    onClickCapture: go,
    onClick: go,
  }
}
