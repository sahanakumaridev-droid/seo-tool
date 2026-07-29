import { useMemo, useState } from 'react'
import { ArrowRight } from 'lucide-react'
import Logo from '../components/Logo'
import RevampHeader from '../components/revamp/RevampHeader'
import HeroOrbit from '../components/revamp/HeroOrbit'
import SectionHeading from '../components/revamp/SectionHeading'
import ContactForm from '../components/revamp/ContactForm'
import AIAssistant from '../components/revamp/AIAssistant'
import PathExplorer from '../components/revamp/PathExplorer'
import InsightsFeed from '../components/revamp/InsightsFeed'
import {
  AI_SOLUTIONS,
  INDUSTRIES,
  PROCESS_STEPS,
  SERVICES,
  TRUST_ITEMS,
} from '../data/revampContent'

const GOALS = [
  'I want more leads',
  'I want to automate operations',
  'I need a website',
  'I need an app',
  'I want better search visibility',
]

const GOAL_TO_RECOMMENDATIONS = {
  'I want more leads': ['Conversion-first web design', 'SEO / AEO / GEO strategy', 'Lead capture automation'],
  'I want to automate operations': ['Workflow automation', 'AI copilots', 'Custom software integration'],
  'I need a website': ['Website design & development', 'Content architecture', 'Performance optimization'],
  'I need an app': ['Mobile product strategy', 'Cross-platform engineering', 'Backend API architecture'],
  'I want better search visibility': ['Technical SEO audit', 'Search content engine', 'AI search optimization'],
}

export default function LandingPage() {
  const [selectedGoal, setSelectedGoal] = useState(GOALS[0])
  const [aiOpen, setAiOpen] = useState(false)
  const recommendations = useMemo(
    () => GOAL_TO_RECOMMENDATIONS[selectedGoal] || [],
    [selectedGoal],
  )

  function scrollToContact() {
    const el = document.getElementById('contact')
    if (!el) return
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="rv-page">
      <RevampHeader />

      <section className="rv-hero">
        <div className="rv-shell rv-hero-grid">
          <div>
            <p className="rv-eyebrow">AI • SOFTWARE • DIGITAL GROWTH</p>
            <h1>Build Smarter. Grow Faster. Powered by AI.</h1>
            <p className="rv-hero-copy">
              ZeOrbit designs and engineers intelligent websites, apps, AI systems,
              and growth operations for modern businesses that need measurable outcomes.
            </p>
            <div className="rv-hero-actions">
              <button type="button" className="btn btn-primary" onClick={scrollToContact}>
                Start a Project <ArrowRight size={16} />
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => document.getElementById('work')?.scrollIntoView({ behavior: 'smooth' })}>
                Explore Our Work
              </button>
              <button type="button" className="btn btn-ghost" onClick={() => setAiOpen(true)}>
                Talk to an AI Expert
              </button>
            </div>
          </div>
          <HeroOrbit />
        </div>
      </section>

      <section className="rv-trust">
        <div className="rv-shell rv-trust-list">
          {TRUST_ITEMS.map((item) => <span key={item}>{item}</span>)}
        </div>
      </section>

      <PathExplorer
        onExploreAI={() => document.getElementById('ai-solutions')?.scrollIntoView({ behavior: 'smooth' })}
        onStartProject={scrollToContact}
      />

      <section id="services" className="rv-section">
        <div className="rv-shell">
          <SectionHeading
            eyebrow="Core Services"
            title="Digital product, engineering, and growth under one roof."
            description="A premium delivery model across product strategy, engineering, AI integration, and search visibility."
          />
          <div className="rv-cards-grid">
            {SERVICES.map((service) => (
              <article key={service.title} className="rv-card">
                <img
                  src={service.image}
                  alt=""
                  width={480}
                  height={260}
                  loading="lazy"
                  decoding="async"
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

      <section id="ai-solutions" className="rv-section rv-section-dark">
        <div className="rv-shell">
          <SectionHeading
            eyebrow="AI That Works Inside Your Business"
            title="From strategy to production-grade AI systems."
            description="We build practical AI capabilities that integrate with your real business workflows."
          />
          <div className="rv-pills">
            {AI_SOLUTIONS.map((item) => <span key={item}>{item}</span>)}
          </div>
        </div>
      </section>

      <section id="work" className="rv-section">
        <div className="rv-shell">
          <SectionHeading
            eyebrow="Interactive AI Experience"
            title="See what AI can do for your business."
            description="This is currently a frontend decision engine. It is structured to connect to a Python AI endpoint later."
          />
          <div className="rv-ai-demo">
            <div className="rv-goals">
              {GOALS.map((goal) => (
                <button
                  key={goal}
                  type="button"
                  className={`rv-goal-btn${goal === selectedGoal ? ' active' : ''}`}
                  onClick={() => setSelectedGoal(goal)}
                >
                  {goal}
                </button>
              ))}
            </div>
            <div className="rv-recommendations">
              <p className="rv-recommendation-label">Recommended ZeOrbit Solution Stack</p>
              <ul>
                {recommendations.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="rv-section">
        <div className="rv-shell">
          <SectionHeading
            eyebrow="Process"
            title="A delivery flow built for momentum."
            description="Clear phases from discovery to optimization, aligned to technical quality and business outcomes."
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
            title="Built for teams where digital performance matters."
            description="Industry-specific execution with shared engineering and AI excellence."
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
            title="Latest published SEO content."
            description="Articles published live from the ZeOrbit SEO tool appear here automatically — open any card to read the live page."
          />
          <InsightsFeed limit={6} showViewAll />
        </div>
      </section>

      <section id="contact" className="rv-final-cta">
        <div className="rv-shell">
          <h2>Ready to build what&apos;s next?</h2>
          <p>Turn your next idea into an intelligent digital experience with ZeOrbit.</p>
          <div className="rv-contact-wrap">
            <ContactForm />
          </div>
        </div>
      </section>

      <footer id="about" className="rv-footer">
        <div className="rv-shell rv-footer-grid">
          <div>
            <Logo size={28} />
            <p>
              ZeOrbit is a U.S.-based digital product, software, AI, and growth partner
              for modern businesses.
            </p>
          </div>
          <div>
            <h4>Services</h4>
            <p>Websites · Apps · Custom Software · SEO/AEO/GEO</p>
          </div>
          <div>
            <h4>AI Solutions</h4>
            <p>Agents · Copilots · LLM Integration · Automation</p>
          </div>
          <div>
            <h4>Resources</h4>
            <p><a href="/blog" style={{ color: 'inherit' }}>Blog &amp; Insights</a></p>
            <p><a href="#insights" style={{ color: 'inherit' }}>Latest posts</a></p>
          </div>
          <div>
            <h4>Contact</h4>
            <p>info@zeorbit.com</p>
            <p>+1 (619) 724-9517</p>
          </div>
        </div>
      </footer>

      <AIAssistant open={aiOpen} onOpenChange={setAiOpen} />
    </div>
  )
}
