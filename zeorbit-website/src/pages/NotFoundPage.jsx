import { Link, useLocation } from 'react-router-dom'
import SeoHead from '../components/SeoHead'

export default function NotFoundPage() {
  const { pathname } = useLocation()
  return (
    <main style={{ maxWidth: 640, margin: '4rem auto', padding: '0 1.25rem' }}>
      <SeoHead
        title="Page not found — ZeOrbit"
        description="This URL is not a published ZeOrbit page."
        path={pathname}
        noindex
        localBusiness={false}
      />
      <h1>Page not found</h1>
      <p>This URL is not a published ZeOrbit page.</p>
      <p>
        <Link to="/">Go to the homepage</Link>
      </p>
    </main>
  )
}
