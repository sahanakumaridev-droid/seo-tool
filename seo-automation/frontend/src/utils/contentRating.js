const STOP = new Set([
  'about', 'after', 'also', 'and', 'are', 'between', 'difference', 'from', 'have',
  'into', 'that', 'the', 'their', 'them', 'this', 'what', 'when', 'with', 'your',
  'website', 'mobile', 'design',
])

function words(value) {
  const all = String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(Boolean)
  const long = all.filter((w) => w.length > 3 && !STOP.has(w))
  if (long.length) return long
  const small = new Set(['the', 'and', 'for', 'are', 'what', 'how', 'with', 'your', 'that', 'this', 'from', 'into'])
  return all.filter((w) => w.length >= 3 && !small.has(w))
}

function hasAny(text, tokens) {
  const blob = ` ${String(text || '').toLowerCase()} `
  return tokens.some((t) => blob.includes(t))
}

/** Accuracy of this draft against the topic, industry, image keyword, and location. */
export function rateContent(block) {
  const topic = words(block?.keywords?.primary || block?.focus_keyword || block?.title)
  const industry = words(block?.industry)
  const image = words(block?.image_keyword || block?.image_concept)
  const body = `${block?.intro || ''}\n${block?.content || ''}`
  const city = String(block?.city || '').trim()
  const notes = []
  let score = 0

  if (!topic.length) {
    return { score: 0, notes: ['No topic was saved on this draft, so accuracy cannot be checked.'] }
  }

  if (hasAny(block?.title, topic) && hasAny(block?.h1, topic)) {
    score += 2
  } else {
    notes.push('Title does not match the topic.')
  }

  const bodyHits = topic.filter((t) => body.toLowerCase().includes(t)).length
  if (bodyHits >= Math.min(2, topic.length)) {
    score += 2
  } else {
    notes.push('Body does not stay on the topic.')
  }

  if (hasAny(block?.slug, topic)) {
    score += 2
  } else {
    notes.push('Slug does not match the topic.')
  }

  if (hasAny(block?.meta_description, topic)) {
    score += 1
  } else {
    notes.push('Meta description does not describe the topic.')
  }

  const industryOk = !industry.length || industry.some((t) => topic.includes(t) || body.toLowerCase().includes(t))
  if (industryOk) score += 1
  else notes.push('Industry does not match the post.')

  const imageOk = !image.length || image.some((t) => topic.includes(t) || body.toLowerCase().includes(t))
  if (imageOk) score += 1
  else notes.push('Image keyword does not match the post.')

  const inventedPlace = !city && /\b(county|in [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b/.test(body)
  const missingPlace = city && !body.toLowerCase().includes(city.toLowerCase())
  if (!inventedPlace && !missingPlace) score += 1
  else if (inventedPlace) notes.push('A city or county appears even though no location was selected.')
  else notes.push('The selected location is missing from the post.')

  return { score, notes }
}
