import { ArrowRight, Briefcase, ChartNoAxesCombined, Clock3, Flag, Play, Smartphone, Sparkles, Trophy, Users } from 'lucide-react'
import RevampHeader from '../components/revamp/RevampHeader'
import HeroOrbit from '../components/revamp/HeroOrbit'
import GrowthStack from '../components/revamp/GrowthStack'
import SectionHeading from '../components/revamp/SectionHeading'
import ContactForm from '../components/revamp/ContactForm'
import PathExplorer from '../components/revamp/PathExplorer'
import InsightsFeed from '../components/revamp/InsightsFeed'
import AIAssistant from '../components/revamp/AIAssistant'
import GoogleReviews from '../components/GoogleReviews'
import SiteFooter from '../components/SiteFooter'
import { useState } from 'react'
import {
  INDUSTRIES,
  PROCESS_STEPS,
  SERVICES,
  STATS,
  TRUST_ITEMS,
} from '../data/revampContent'

const TRUST_ICONS = [Flag, Smartphone, ChartNoAxesCombined, Users]
const STAT_ICONS = [Briefcase, ChartNoAxesCombined, Clock3, Trophy]

export default function LandingPage() {
  const [aiOpen, setAiOpen] = useState(false)

  function scrollToContact() {
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="rv-page zo-mock">
      <RevampHeader />

      <section className="rv-hero zo-hero">
        <div className="rv-shell rv-hero-grid">
          <div>
            <p className="zo-hero-pill">
              <Sparkles size={12} /> AI • SOFTWARE • DIGITAL GROWTH
            </p>
            <h1>
              Build Smarter. Scale Faster.{' '}
              <span className="zo-gradient-text">Lead with AI.</span>
            </h1>
            <p className="rv-hero-copy">
              AI, software, web, mobile and search solutions built to help businesses automate, scale and grow.
            </p>
            <div className="rv-hero-actions">
              <button type="button" className="btn zo-gradient-btn" onClick={scrollToContact}>
                Start a Project <ArrowRight size={16} />
              </button>
              <button
                type="button"
                className="btn btn-secondary zo-outline-btn"
                onClick={() => document.getElementById('services')?.scrollIntoView({ behavior: 'smooth' })}
              >
                <Play size={14} /> View Capabilities
              </button>
              <button type="button" className="zo-text-link" onClick={() => setAiOpen(true)}>
                Ask ZeOrbit AI <Sparkles size={14} />
              </button>
            </div>
          </div>
          <HeroOrbit />
        </div>
      </section>

      <section className="rv-trust zo-trust">
        <div className="rv-shell rv-trust-grid">
          {TRUST_ITEMS.map((item, i) => {
            const Icon = TRUST_ICONS[i] || Flag
            return (
              <article key={item.title} className="rv-trust-item">
                <Icon size={18} className="zo-trust-icon" />
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.copy}</p>
                </div>
              </article>
            )
          })}
        </div>
      </section>

      <GrowthStack onSeePlan={scrollToContact} />

      <section className="zo-stats-bar">
        <div className="rv-shell rv-stats-grid">
          {STATS.map((stat, i) => {
            const Icon = STAT_ICONS[i] || Briefcase
            return (
              <article key={stat.label} className="rv-stat-card">
                <Icon size={18} className="zo-stat-icon" />
                <p className="rv-stat-value">{stat.value}</p>
                <p className="rv-stat-label">{stat.label}</p>
              </article>
            )
          })}
        </div>
      </section>

      <PathExplorer onStartProject={scrollToContact} />

      <section id="services" className="rv-section">
        <div className="rv-shell">
          <SectionHeading
            eyebrow="Core Services"
            title="Technology Built Around Your Business"
            description="AI solutions, custom software, web and mobile development, automation, ecommerce, data, and SEO/AEO/GEO—engineered as one stack for U.S. companies."
          />
          <div className="rv-cards-grid">
            {SERVICES.map((service) => (
              <article key={service.title} className="rv-card">
                <img
                  src={service.image}
                  alt={service.title}
                  width={480}
                  height={260}
                  loading="lazy"
                  decoding="async"
                  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 360px"
                  className="rv-card-image rv-card-image-svg"
                />
                <h3>{service.title}</h3>
                <p>{service.description}</p>
                <div className="rv-tags">
                  {service.tags.map((tag) => <span key={tag}>{tag}</span>)}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="rv-section">
        <div className="rv-shell">
          <SectionHeading
            eyebrow="Why ZeOrbit"
            title="One Technology Partner. From Idea to Scale."
            description="AI-first development, custom-built systems, scalable engineering, web and mobile expertise, search and AI visibility, automation, and long-term support—without juggling separate vendors."
          />
          <div className="rv-process-grid">
            {PROCESS_STEPS.map((step) => (
              <article key={step.id} className="rv-process-step">
                <p>{step.id}</p>
                <h3>{step.title}</h3>
                <span>{step.copy}</span>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="industries" className="rv-section rv-section-muted">
        <div className="rv-shell">
          <SectionHeading
            eyebrow="Industries"
            title="Built for U.S. businesses where technology drives growth."
            description="Healthcare, legal, home services, real estate, ecommerce, and professional services—delivered with the same engineering standards."
          />
          <div className="rv-industries">
            {INDUSTRIES.map((item) => <article key={item}>{item}</article>)}
          </div>
        </div>
      </section>

      <section id="insights" className="rv-section">
        <div className="rv-shell">
          <SectionHeading
            eyebrow="Insights · Blog"
            title="Practical notes on AI, search, and digital growth."
            description="Articles from the ZeOrbit SEO tool appear here automatically—clear writing for SEO, AEO, GEO, and product teams."
          />
          <InsightsFeed limit={6} showViewAll />
        </div>
      </section>

      <GoogleReviews />

      <section id="contact" className="rv-final-cta">
        <div className="rv-shell">
          <h2>Ready to build what&apos;s next?</h2>
          <p>Tell us about your AI, software, website, app, automation, or growth goals—we&apos;ll map a clear next step.</p>
          <div className="rv-contact-wrap">
            <ContactForm />
          </div>
        </div>
      </section>

      <SiteFooter />

      <AIAssistant open={aiOpen} onOpenChange={setAiOpen} />
    </div>
  )
}
