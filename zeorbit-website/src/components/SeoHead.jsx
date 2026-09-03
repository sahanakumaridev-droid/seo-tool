import { useEffect } from 'react'
import { PAGE_SEO, DEFAULT_OG_IMAGE } from '../data/pageSeo'
import { AREA_HUB, AREA_PAGES } from '../data/areas'
import {
  SITE_URL,
  buildFaqSchema,
  buildLocalBusinessSchema,
  buildOrganizationSchema,
} from '../data/localBusiness'

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

function absUrl(path) {
  const p = path || '/'
  if (p.startsWith('http')) return p
  return `${SITE_URL}${p === '/' ? '' : p}`
}

function absImage(image) {
  const img = image || DEFAULT_OG_IMAGE
  if (img.startsWith('http')) return img
  return `${SITE_URL}${img.startsWith('/') ? img : `/${img}`}`
}

/**
 * Page SEO: title, description, robots, canonical, Open Graph, Twitter, JSON-LD.
 * Canonical always uses zeorbit.com so previews on nip.io still share the live URL.
 */
export default function SeoHead({
  title,
  description,
  path = '/',
  image = DEFAULT_OG_IMAGE,
  type = 'website',
  robots = 'index,follow,max-image-preview:large',
  noindex = false,
  faqs = null,
  localBusiness = true,
}) {
  useEffect(() => {
    const url = absUrl(path)
    const absImg = absImage(image)
    const robotsVal = noindex ? 'noindex,nofollow' : robots

    document.title = title
    upsertMeta('name', 'description', description)
    upsertMeta('name', 'robots', robotsVal)
    upsertMeta('name', 'author', 'ZeOrbit')
    upsertMeta('name', 'theme-color', '#0a0a0a')
    upsertMeta('property', 'og:title', title)
    upsertMeta('property', 'og:description', description)
    upsertMeta('property', 'og:type', type)
    upsertMeta('property', 'og:url', url)
    upsertMeta('property', 'og:image', absImg)
    upsertMeta('property', 'og:image:alt', title)
    upsertMeta('property', 'og:site_name', 'ZeOrbit')
    upsertMeta('property', 'og:locale', 'en_US')
    upsertMeta('name', 'twitter:card', 'summary_large_image')
    upsertMeta('name', 'twitter:title', title)
    upsertMeta('name', 'twitter:description', description)
    upsertMeta('name', 'twitter:image', absImg)
    upsertLink('canonical', url)

    upsertJsonLd('zo-ld-org', buildOrganizationSchema())

    if (localBusiness) {
      upsertJsonLd('zo-ld-local', buildLocalBusinessSchema({ pageUrl: url, description }))
    } else {
      const stale = document.getElementById('zo-ld-local')
      if (stale) stale.remove()
    }

    upsertJsonLd('zo-ld-website', {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: 'ZeOrbit',
      url: SITE_URL,
      potentialAction: {
        '@type': 'SearchAction',
        target: `${SITE_URL}/blog?q={search_term_string}`,
        'query-input': 'required name=search_term_string',
      },
    })

    if (faqs?.length) {
      upsertJsonLd('zo-ld-faq', buildFaqSchema(faqs))
    } else {
      const stale = document.getElementById('zo-ld-faq')
      if (stale) stale.remove()
    }
  }, [title, description, path, image, type, robots, noindex, faqs, localBusiness])

  return null
}

/** Resolves static-route or area-page meta. Returns null for generated article slugs. */
export function seoForPath(pathname) {
  const path = (pathname || '/').replace(/\/+$/, '') || '/'
  if (PAGE_SEO[path]) return { path, ...PAGE_SEO[path] }
  if (path === '/areas') return { path, ...PAGE_SEO['/areas'] }
  if (path.startsWith('/areas/')) {
    const slug = path.slice('/areas/'.length)
    const page = AREA_PAGES[slug]
    if (page) {
      return {
        path,
        title: page.metaTitle || `${page.name} Web Design & Digital Agency — ZeOrbit`,
        description: page.metaDescription || AREA_HUB.metaDescription,
        image: DEFAULT_OG_IMAGE,
      }
    }
  }
  return null
}

export { PAGE_SEO, DEFAULT_OG_IMAGE, SITE_URL }
