import RevampHeader from '../components/revamp/RevampHeader'
import InsightsFeed from '../components/revamp/InsightsFeed'
import SiteFooter from '../components/SiteFooter'
import GoogleReviews from '../components/GoogleReviews'

export default function BlogPage() {
  return (
    <div className="rv-page zo-service-page">
      <RevampHeader />

      <section className="zo-svc-hero" style={{ paddingBottom: 24 }}>
        <div className="rv-shell">
          <p className="zo-svc-eyebrow" style={{ color: '#ff5a4e' }}>Insights · Blog</p>
          <h1 className="rv-blog-title">AI, search, and digital growth insights</h1>
          <p className="rv-blog-lead">
            Live articles from the ZeOrbit SEO tool—practical guidance on SEO, AEO, GEO, AI search, and product growth for U.S. businesses.
          </p>
        </div>
      </section>

      <main className="rv-section" style={{ paddingTop: 12, background: '#f7f8fa' }}>
        <div className="rv-shell">
          <InsightsFeed limit={48} showViewAll={false} emptyUseFallback={false} />
        </div>
      </main>

      <GoogleReviews />
      <SiteFooter />
    </div>
  )
}
