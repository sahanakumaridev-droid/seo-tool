import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Check } from 'lucide-react'
import Logo from '../components/Logo'
import RevampHeader from '../components/revamp/RevampHeader'
import HeroVisual from '../components/revamp/HeroVisual'
import SectionHeading from '../components/revamp/SectionHeading'
import ContactForm from '../components/revamp/ContactForm'
import FaqAccordion from '../components/revamp/FaqAccordion'
import {
  AWARD_BADGES,
  FAQS,
  FEATURE_BLOCKS,
  PRICING_TIERS,
  PROOF_STATS,
} from '../data/revampContent'

export default function LandingPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [emailError, setEmailError] = useState('')
  const [activeFeature, setActiveFeature] = useState(FEATURE_BLOCKS[0].id)
  const feature = FEATURE_BLOCKS.find((f) => f.id === activeFeature) || FEATURE_BLOCKS[0]

  function handleTrial(e) {
    e.preventDefault()
    const value = email.trim()
    if (!value || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
      setEmailError('Please enter your email address')
      return
    }
    setEmailError('')
    sessionStorage.setItem('seo_pending_email', value)
    navigate('/register')
  }

  return (
    <div className="rv-page">
      <div className="rv-apple">
        <RevampHeader />

        <section className="rv-hero">
          <div className="rv-shell rv-hero-center">
            <p className="rv-kicker">Local SEO, built to sell</p>
            <h1>
              The command center for
              <span className="rv-accent-text"> every search result</span>
            </h1>
            <p className="rv-hero-copy">
              Rank locally, publish at scale, and prove the win — for your business
              or white-label for clients.
            </p>

            <form className="rv-email-cta" onSubmit={handleTrial} noValidate>
              {emailError ? <p className="rv-email-error">{emailError}</p> : null}
              <div className={`rv-email-row${emailError ? ' has-error' : ''}`}>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    if (emailError) setEmailError('')
                  }}
                  placeholder="Work email"
                  aria-label="Work email"
                  autoComplete="email"
                />
                <button type="submit" className="btn btn-primary">
                  Start 7-day trial
                </button>
              </div>
            </form>

            <p className="rv-hero-note">No card required. Live in minutes. Keep every page you generate.</p>
            <HeroVisual />
          </div>
        </section>
      </div>

      <div className="rv-aurora" aria-hidden="true" />

      <section className="rv-social-proof-bar">
        <div className="rv-shell rv-trust-row">
          {PROOF_STATS.map((stat) => (
            <div key={stat.label} className="rv-trust-item">
              <strong>{stat.value}</strong>
              <span>{stat.label}</span>
            </div>
          ))}
        </div>
      </section>

      <section id="features" className="rv-section">
        <div className="rv-shell">
          <SectionHeading
            eyebrow="Platform"
            title="A full SEO product — not a pile of tools"
            description="Site health, keywords, AI visibility, local pages, and reporting in one workspace your clients can understand."
          />

          <div className="rv-feature-tabs" role="tablist" aria-label="Product features">
            {FEATURE_BLOCKS.map((block) => (
              <button
                key={block.id}
                type="button"
                role="tab"
                aria-selected={activeFeature === block.id}
                className={`rv-feature-tab${activeFeature === block.id ? ' active' : ''}`}
                onClick={() => setActiveFeature(block.id)}
              >
                {block.label}
              </button>
            ))}
          </div>

          <div className="rv-feature-panel" id="platform">
            <div>
              <p className="rv-eyebrow">{feature.label}</p>
              <h3>{feature.title}</h3>
              <ul className="rv-bullet-list">
                {feature.bullets.map((b) => (
                  <li key={b}><Check size={16} strokeWidth={2.5} />{b}</li>
                ))}
              </ul>
              <button type="button" className="btn btn-primary" onClick={() => navigate('/register')}>
                Try it free <ArrowRight size={16} />
              </button>
            </div>
            <div className="rv-feature-visual">
              <div className="rv-mini-dash">
                <div className="rv-mini-score">
                  <span>Site Health</span>
                  <strong>94</strong>
                </div>
                <div className="rv-mini-bars">
                  {[45, 60, 52, 72, 66, 84, 78, 92].map((h, i) => (
                    <span key={i} style={{ height: `${h}%` }} />
                  ))}
                </div>
                <div className="rv-mini-rows">
                  <div><span>AI Search Health</span><b>91</b></div>
                  <div><span>Issues to fix</span><b>18</b></div>
                  <div><span>AI Visibility Score</span><b>76</b></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="pricing" className="rv-section rv-section-light">
        <div className="rv-shell">
          <SectionHeading
            eyebrow="Pricing"
            title="Sell it. Run it. Scale it."
            description="Start with one market, then add seats and client workspaces as you grow."
          />
          <div className="rv-pricing-grid">
            {PRICING_TIERS.map((tier) => (
              <article key={tier.name} className={`rv-price-card${tier.highlighted ? ' highlighted' : ''}`}>
                {tier.highlighted ? <span className="rv-price-badge">Most popular</span> : null}
                <h3>{tier.name}</h3>
                <div className="rv-price-amount">
                  <span className="num">{tier.price}</span>
                  <span className="period">{tier.period}</span>
                </div>
                <p className="rv-price-tagline">{tier.tagline}</p>
                <ul className="rv-price-features">
                  {tier.features.map((f) => (
                    <li key={f}><Check size={15} strokeWidth={2.5} />{f}</li>
                  ))}
                </ul>
                <button
                  type="button"
                  className={tier.highlighted ? 'btn btn-primary' : 'btn btn-secondary'}
                  onClick={() => {
                    if (tier.name === 'Enterprise') {
                      document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
                      return
                    }
                    navigate('/register')
                  }}
                >
                  {tier.cta}
                </button>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="contact" className="rv-section">
        <div className="rv-shell rv-contact-layout">
          <div>
            <SectionHeading
              eyebrow="Sales"
              title="Want this as your agency product?"
              description="We’ll map a workspace for your brand, your clients, and the markets you sell into."
            />
          </div>
          <ContactForm />
        </div>
      </section>

      <section id="faq" className="rv-section rv-section-light">
        <div className="rv-shell">
          <SectionHeading eyebrow="FAQ" title="Questions, answered" />
          <FaqAccordion items={FAQS} />
        </div>
      </section>

      <section className="rv-final-cta">
        <div className="rv-shell rv-final-cta-inner">
          <h2>Own every search result</h2>
          <p>
            Visibility gaps now cost you AI consideration, not just rankings.
            Measure and grow search + AI from one premium platform.
          </p>
          <button type="button" className="btn btn-primary" onClick={() => navigate('/register')}>
            Start 7-day trial <ArrowRight size={16} />
          </button>
          <div className="rv-award-row">
            {AWARD_BADGES.map((badge) => (
              <span key={badge} className="rv-award-badge">{badge}</span>
            ))}
          </div>
        </div>
      </section>

      <footer className="rv-footer">
        <div className="rv-footer-bar">
          <div className="rv-footer-left">
            <Logo size={32} onDark />
            <span>© {new Date().getFullYear()} ZeOrbit. All rights reserved.</span>
          </div>
          <div className="rv-footer-legal">
            <a href="#contact">Legal</a>
            <a href="#contact">Privacy</a>
            <a href="#pricing">Pricing</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
