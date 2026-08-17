import { useEffect } from 'react'

const SITE_URL = 'https://zeorbit.com'

function upsertMeta(attr, key, content) {
  if (!content) return
  let el = document.head.querySelector(`meta[${attr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function upsertLink(rel, href) {
  let el = document.head.querySelector(`link[rel="${rel}"]`)
  if (!el) {
    el = document.createElement('link')
    el.setAttribute('rel', rel)
    document.head.appendChild(el)
  }
  el.setAttribute('href', href)
}

function upsertJsonLd(id, data) {
  let el = document.getElementById(id)
  if (!el) {
    el = document.createElement('script')
    el.type = 'application/ld+json'
    el.id = id
    document.head.appendChild(el)
  }
  el.textContent = JSON.stringify(data)
}

/**
 * Lightweight page SEO without extra dependencies.
 */
export default function SeoHead({
  title = 'ZeOrbit — Build Smarter. Scale Faster. Lead with AI.',
  description = 'ZeOrbit is a U.S. AI, software, web, mobile, and digital growth technology partner—AI agents, custom software, web and mobile development, automation, ecommerce, data, and SEO/AEO/GEO.',
  path = '/',
  image = '/zeorbit-logo.png',
  type = 'website',
}) {
  useEffect(() => {
    const origin = window.location.origin
    const url = `${origin}${path === '/' ? '' : path}`
    const absImage = image.startsWith('http') ? image : `${origin}${image}`

    document.title = title
    upsertMeta('name', 'description', description)
    upsertMeta('name', 'robots', 'index,follow,max-image-preview:large')
    upsertMeta('property', 'og:title', title)
    upsertMeta('property', 'og:description', description)
    upsertMeta('property', 'og:type', type)
    upsertMeta('property', 'og:url', url)
    upsertMeta('property', 'og:image', absImage)
    upsertMeta('property', 'og:site_name', 'ZeOrbit')
    upsertMeta('property', 'og:locale', 'en_US')
    upsertMeta('name', 'twitter:card', 'summary_large_image')
    upsertMeta('name', 'twitter:title', title)
    upsertMeta('name', 'twitter:description', description)
    upsertMeta('name', 'twitter:image', absImage)
    upsertLink('canonical', url)

    upsertJsonLd('zo-ld-org', {
      '@context': 'https://schema.org',
      '@type': 'Organization',
      name: 'ZeOrbit',
      url: origin,
      logo: `${origin}/zeorbit-logo.png`,
      email: 'info@zeorbit.com',
      telephone: '+1-619-724-9517',
      areaServed: 'US',
      sameAs: [
        'https://www.facebook.com/zeorbit.web.designers.mobileapp.developers',
        'https://www.linkedin.com/company/zeorbit/',
        'https://maps.apple/p/VA-_LREgJ5PzDV',
        'https://maps.app.goo.gl/teVefHUc3yycwkcA7',
        'https://www.yelp.com/biz/zeorbit-san-diego-2',
        'https://zeorbit.com',
      ],
      address: {
        '@type': 'PostalAddress',
        streetAddress: '4231 Balboa Avenue, Suite 1340',
        addressLocality: 'San Diego',
        addressRegion: 'CA',
        postalCode: '92117',
        addressCountry: 'US',
      },
    })

    upsertJsonLd('zo-ld-website', {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: 'ZeOrbit',
      url: origin,
      potentialAction: {
        '@type': 'SearchAction',
        target: `${origin}/seo-ppc#blog`,
        'query-input': 'required name:search_term_string',
      },
    })
  }, [title, description, path, image, type])

  return null
}

export { SITE_URL }
