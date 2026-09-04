import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

/** Directories under public/ that would otherwise shadow the React app. */
export const SPA_SHELL_ROUTES = [
  'blog',
  'contact',
  'portfolio',
  'mobile-apps',
  'custom-software',
  'seo-ppc',
  'website-designing',
  'web-designer-near-me',
  'privacy-policy',
  'areas',
  'areas/san-diego',
  'areas/el-cajon',
  'areas/los-angeles',
  'areas/orange-county',
  'areas/new-york',
]

const SITE = 'https://zeorbit.com'

const ROUTE_SEO = {
  blog: {
    title: 'Insights — Website, App & SEO Guides | ZeOrbit',
    description:
      'Practical guides on websites, WordPress, Shopify, mobile apps, SEO, and digital growth from the ZeOrbit team.',
    canonical: `${SITE}/blog`,
  },
  contact: {
    title: 'Contact ZeOrbit — Websites, Apps & Growth',
    description:
      'Talk with ZeOrbit about a website, mobile app, SEO, or custom software project. Call +1 (619) 724-9517 or email info@zeorbit.com. San Diego, CA 92117.',
    canonical: `${SITE}/contact`,
  },
  portfolio: {
    title: 'Our Work — ZeOrbit Web, App & Brand Portfolio',
    description:
      'Selected websites, mobile apps, flyers, and logos designed and built by ZeOrbit for businesses across California and beyond.',
    canonical: `${SITE}/portfolio`,
  },
  'mobile-apps': {
    title: 'Mobile App Development — iOS & Android | ZeOrbit',
    description:
      'ZeOrbit designs and builds iOS and Android apps — native and cross-platform — from prototype to App Store and Google Play launch.',
    canonical: `${SITE}/mobile-apps`,
  },
  'custom-software': {
    title: 'Custom Software & Internal Tools | ZeOrbit',
    description:
      'Custom software, dashboards, automation, and portals built around how your U.S. business actually runs. Architecture, build, and ongoing support.',
    canonical: `${SITE}/custom-software`,
  },
  'seo-ppc': {
    title: 'SEO, GEO, PPC & Google Ads | ZeOrbit',
    description:
      'Technical SEO, local SEO, content, GEO, PPC, and Google Ads so U.S. businesses get found and chosen. Strategy, execution, and reporting from ZeOrbit.',
    canonical: `${SITE}/seo-ppc`,
  },
  'website-designing': {
    title: 'Website Design — WordPress, Shopify, Wix & Squarespace | ZeOrbit',
    description:
      'Custom website design and development for U.S. businesses. WordPress, Shopify, Wix, Squarespace, redesigns, and Master Care from ZeOrbit in San Diego.',
    canonical: `${SITE}/website-designing`,
  },
  'web-designer-near-me': {
    title: 'Best Web Designer Near Me in San Diego | ZeOrbit',
    description:
      'Looking for the best web designer near you in San Diego? ZeOrbit has a 5.0 Google rating, 20+ years experience, and builds WordPress, Shopify & custom websites. Call 619-724-9517.',
    canonical: `${SITE}/web-designer-near-me`,
  },
  'privacy-policy': {
    title: 'Privacy Policy — ZeOrbit',
    description: 'How ZeOrbit collects, uses, and protects personal information on zeorbit.com.',
    canonical: `${SITE}/privacy-policy`,
  },
  areas: {
    title: 'Areas We Serve — ZeOrbit',
    description:
      'ZeOrbit serves San Diego, El Cajon, Los Angeles, Orange County, and clients nationwide with websites, apps, SEO, and custom software.',
    canonical: `${SITE}/areas`,
  },
}

function applyRouteSeo(html, route) {
  const seo = ROUTE_SEO[route]
  if (!seo) return html
  let out = html
  out = out.replace(/<title>[^<]*<\/title>/, `<title>${seo.title}</title>`)
  out = out.replace(
    /<meta name="description" content="[^"]*" \/>/,
    `<meta name="description" content="${seo.description}" />`,
  )
  out = out.replace(
    /<link rel="canonical" href="[^"]*" \/>/,
    `<link rel="canonical" href="${seo.canonical}" />`,
  )
  out = out.replace(/<meta property="og:url" content="[^"]*" \/>/, `<meta property="og:url" content="${seo.canonical}" />`)
  out = out.replace(/<meta property="og:title" content="[^"]*" \/>/, `<meta property="og:title" content="${seo.title}" />`)
  out = out.replace(
    /<meta property="og:description" content="[^"]*" \/>/,
    `<meta property="og:description" content="${seo.description}" />`,
  )
  return out
}

function isSpaPath(urlPath) {
  const clean = (urlPath || '').split('?')[0].replace(/\/+$/, '') || '/'
  return SPA_SHELL_ROUTES.some((route) => clean === `/${route}`)
}

/** Serve the Vite app instead of crawler-only public/{route}/index.html. */
export function spaPublicShells() {
  return {
    name: 'spa-public-shells',
    configureServer(server) {
      server.middlewares.use((req, _res, next) => {
        if (req.method && req.method !== 'GET' && req.method !== 'HEAD') {
          next()
          return
        }
        if (isSpaPath(req.url)) {
          req.url = '/index.html'
        }
        next()
      })
    },
    closeBundle() {
      const dist = path.resolve(__dirname, 'dist')
      const indexPath = path.join(dist, 'index.html')
      if (!fs.existsSync(indexPath)) return
      const index = fs.readFileSync(indexPath, 'utf8')
      for (const route of SPA_SHELL_ROUTES) {
        const destDir = path.join(dist, route)
        fs.mkdirSync(destDir, { recursive: true })
        fs.writeFileSync(path.join(destDir, 'index.html'), applyRouteSeo(index, route))
      }
    },
  }
}
