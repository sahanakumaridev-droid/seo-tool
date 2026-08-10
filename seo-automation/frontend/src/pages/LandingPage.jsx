import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Check } from 'lucide-react'
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
      <RevampHeader />

      <section className="rv-hero">
        <div className="rv-shell rv-hero-center">
          <h1>Be found everywhere search happens</h1>
          <p className="rv-hero-copy">
            Capture visibility across Google and AI — all with one platform built for today’s search.
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
                placeholder="Enter your work email"
                aria-label="Work email"
                autoComplete="email"
              />
              <button type="submit" className="btn btn-primary">
                Try free for 7 days
              </button>
            </div>
          </form>

          <p className="rv-hero-note">
            Unlimited access to the ZeOrbit tools that fit your goals
          </p>

          <HeroVisual />
        </div>
      </section>

      <section className="rv-social-proof-bar">
        <div className="rv-shell">
          <p><strong>28M</strong> marketers already use ZeOrbit</p>
        </div>
      </section>

      <section id="features" className="rv-section">
        <div className="rv-shell">
          <SectionHeading
            title="More than SEO tools — a complete visibility management platform"
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
                Try free for 7 days
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

      <section className="rv-section rv-proof">
        <div className="rv-shell">
          <SectionHeading title="Most trusted AI + SEO tools" />
          <div className="rv-proof-grid rv-proof-grid-3">
            {PROOF_STATS.map((stat) => (
              <div key={stat.label} className="rv-proof-item">
                <strong>{stat.value}</strong>
                <span>{stat.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="contact" className="rv-section">
        <div className="rv-shell rv-contact-layout">
          <div>
            <SectionHeading
              title="Talk to sales"
              description="Need a custom plan for your team? Tell us about your goals — we reply on this page."
            />
          </div>
          <ContactForm />
        </div>
      </section>

      <section id="faq" className="rv-section rv-section-light">
        <div className="rv-shell">
          <SectionHeading title="Frequently asked questions" />
          <FaqAccordion items={FAQS} />
        </div>
      </section>

      {/* Semrush-style closing footer block */}
      <section className="rv-final-cta">
        <div className="rv-shell rv-final-cta-inner">
          <h2>OWN EVERY SEARCH RESULT</h2>
          <p>
            Visibility gaps now cost you AI consideration, not just rankings.
            Measure and grow your visibility across search and AI from one platform.
          </p>
          <button type="button" className="btn btn-primary" onClick={() => navigate('/register')}>
            Try free for 7 days
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
            <Logo size={26} />
            <span>© {new Date().getFullYear()} ZeOrbit. All rights reserved.</span>
          </div>
          <div className="rv-footer-legal">
            <a href="#contact">Legal Info</a>
            <a href="#contact">Privacy Policy</a>
            <a href="#contact">Do not sell my personal info</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
