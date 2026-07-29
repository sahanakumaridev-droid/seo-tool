import { ExternalLink, Star } from 'lucide-react'
import { SITE_CONTACT } from '../data/revampContent'
import { GOOGLE_REVIEWS } from '../data/googleReviews'

function Stars({ count = 5 }) {
  return (
    <span className="zo-reviews-stars" aria-label={`${count} out of 5 stars`}>
      {Array.from({ length: count }).map((_, i) => (
        <Star key={i} size={14} fill="currentColor" aria-hidden />
      ))}
    </span>
  )
}

export default function GoogleReviews() {
  const g = SITE_CONTACT.google

  return (
    <section id="reviews" className="zo-reviews-section" aria-labelledby="zo-reviews-title">
      <div className="rv-shell">
        <header className="zo-reviews-head">
          <p className="zo-reviews-eyebrow">What Clients Are Saying</p>
          <h2 id="zo-reviews-title">Trusted by businesses we build for.</h2>
          <p className="zo-reviews-sub">Recent notes from clients on Google.</p>
        </header>

        <div className="zo-reviews-summary">
          <div>
            <a
              className="zo-reviews-business"
              href={g.reviewsUrl}
              target="_blank"
              rel="noreferrer"
            >
              {g.businessName}
            </a>
            <div className="zo-reviews-score">
              <strong>{g.rating}</strong>
              <Stars />
              <span>Based on {g.reviewCount} reviews</span>
            </div>
            <p className="zo-reviews-powered">powered by Google</p>
          </div>
          <div className="zo-reviews-actions">
            <a className="btn zo-outline-btn" href={g.reviewsUrl} target="_blank" rel="noreferrer">
              Read all reviews <ExternalLink size={14} />
            </a>
            <a className="btn zo-gradient-btn" href={g.writeReviewUrl} target="_blank" rel="noreferrer">
              Review us on Google
            </a>
          </div>
        </div>

        <div className="zo-reviews-grid">
          {GOOGLE_REVIEWS.map((review) => (
            <article key={review.author} className="zo-review-card">
              <div className="zo-review-card-top">
                <div className="zo-review-avatar" aria-hidden>
                  {review.author.slice(0, 1)}
                </div>
                <div>
                  <h3>{review.author}</h3>
                  <p>{review.when}</p>
                </div>
              </div>
              <Stars count={review.rating} />
              <p className="zo-review-text">{review.text}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
