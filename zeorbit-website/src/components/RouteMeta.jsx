import { useLocation } from 'react-router-dom'
import SeoHead, { seoForPath } from './SeoHead'
import { NEAR_ME_FAQS } from '../data/localBusiness'

/**
 * Applies title/description/OG/canonical on every known marketing route.
 * Generated articles keep their own SeoHead after content loads.
 */
export default function RouteMeta() {
  const { pathname } = useLocation()
  const rec = seoForPath(pathname)
  if (!rec) return null
  const faqs = rec.path === '/web-designer-near-me' ? NEAR_ME_FAQS : null
  return (
    <SeoHead
      title={rec.title}
      description={rec.description}
      path={rec.path}
      image={rec.image}
      robots={rec.robots}
      faqs={faqs}
    />
  )
}
