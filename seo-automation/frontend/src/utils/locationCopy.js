function escapeRe(s) {
  return String(s || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function swapPlace(text, src, dest, keepZip) {
  if (!text) return text
  let out = String(text)
  const srcCity = (src.city || '').trim()
  const destCity = (dest.city || '').trim()
  const srcState = (src.state || '').trim()
  const destState = (dest.state || '').trim()
  const srcZip = String(src.zip || '').replace(/\D/g, '').slice(0, 5)
  const destZip = String(dest.zip || '').replace(/\D/g, '').slice(0, 5)
  if (srcCity && destCity && srcCity.toLowerCase() !== destCity.toLowerCase()) {
    out = out.replace(new RegExp(escapeRe(srcCity), 'gi'), destCity)
  }
  if (srcState && destState && srcState.toUpperCase() !== destState.toUpperCase()) {
    out = out.replace(new RegExp(`\\b${escapeRe(srcState)}\\b`, 'g'), destState)
  }
  if (keepZip && srcZip && destZip && srcZip !== destZip) {
    out = out.split(srcZip).join(destZip)
  }
  if (!keepZip) {
    out = out.replace(/\[\d{5}\]\([^)]*\)/g, '')
    out = out.replace(/\b\d{5}(?:-\d{4})?\b/g, '')
    out = out.replace(/\s+,/g, ',').replace(/[ \t]{2,}/g, ' ').trim()
  }
  return out
}

/** Copy master edit onto another location, swapping city/state; ZIP only in FAQ answers. */
export function relocalizeBlock(src, dest) {
  const next = { ...dest }
  const fields = ['title', 'h1', 'intro', 'content', 'meta_description', 'cta']
  for (const field of fields) {
    if (src[field]) next[field] = swapPlace(src[field], src, dest, false)
  }
  if (Array.isArray(src.h2s)) next.h2s = src.h2s.map((h) => swapPlace(h, src, dest, false))
  if (Array.isArray(src.h3s)) next.h3s = src.h3s.map((h) => swapPlace(h, src, dest, false))
  if (Array.isArray(src.faqs)) {
    next.faqs = src.faqs.map((faq) => ({
      ...faq,
      question: swapPlace(faq.question || faq.q || '', src, dest, false),
      answer: swapPlace(faq.answer || faq.a || '', src, dest, true),
    }))
  }
  next.city = dest.city
  next.state = dest.state
  next.zip = dest.zip || next.zip
  next.slug = dest.slug
  return next
}
