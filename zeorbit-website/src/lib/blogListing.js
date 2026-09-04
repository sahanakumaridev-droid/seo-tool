/** Marketing / area pages that must never appear in the blog listing. */
const HIDDEN_SLUGS = new Set([
  'blog',
  'contact',
  'portfolio',
  'mobile-apps',
  'custom-software',
  'seo-ppc',
  'website-designing',
  'web-designer-near-me',
  'privacy-policy',
  'privacy',
  'areas',
  'revamp-preview',
  'us-only',
  'business-directories',
  'restaurants-website-redesign-downtown',
  'restaurants-custom-website-design-san-diego',
])

function listingKey(item) {
  const slug = String(item?.slug || '').replace(/^\/+|\/+$/g, '').toLowerCase()
  if (slug) return slug
  const raw = String(item?.url || item?.public_url || '')
  try {
    const path = raw.includes('://') ? new URL(raw).pathname : raw
    return path.replace(/^\/+|\/+$/g, '').toLowerCase()
  } catch {
    return raw.replace(/^\/+|\/+$/g, '').toLowerCase()
  }
}

export function isHiddenBlogItem(item) {
  const key = listingKey(item)
  const title = String(item?.title || '').trim().toLowerCase()
  if (HIDDEN_SLUGS.has(key) || HIDDEN_SLUGS.has(title)) return true
  if (key === 'areas' || key.startsWith('areas/')) return true
  if (title === 'areas' || title.startsWith('areas/')) return true
  return false
}

export function visibleBlogPosts(items) {
  return (Array.isArray(items) ? items : []).filter((item) => !isHiddenBlogItem(item))
}
