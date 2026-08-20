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
