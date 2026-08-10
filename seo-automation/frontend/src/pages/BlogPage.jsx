import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import RevampHeader from '../components/revamp/RevampHeader'
import SectionHeading from '../components/revamp/SectionHeading'
import InsightsFeed from '../components/revamp/InsightsFeed'

export default function BlogPage() {
  return (
    <div className="rv-page">
      <RevampHeader />

      <main className="rv-section" style={{ paddingTop: 80 }}>
        <div className="rv-shell">
          <p style={{ marginBottom: 28 }}>
            <Link to="/" className="rv-link-button" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <ArrowLeft size={16} /> Back to home
            </Link>
          </p>

          <SectionHeading
            eyebrow="Blog · Insights"
            title="Published SEO intelligence."
            description="Live articles from the ZeOrbit SEO tool — every page published to the web (and tracked WordPress posts) appears here automatically."
          />

          <InsightsFeed limit={48} showViewAll={false} emptyUseFallback={false} />
        </div>
      </main>
    </div>
  )
}
