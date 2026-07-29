import './App.css'
import { useEffect, useState } from 'react'

function App() {
  const [apiStatus, setApiStatus] = useState('Checking backend...')

  useEffect(() => {
    const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

    fetch(`${backendUrl}/api/health`)
      .then((response) => response.json())
      .then((data) => setApiStatus(data.message || 'Backend connected'))
      .catch(() => setApiStatus('Backend not reachable yet'))
  }, [])

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">ZEO<span>RBIT</span></div>
        <nav>
          <a href="#services">Services</a>
          <a href="#why">Why Us</a>
          <a href="#contact">Contact</a>
        </nav>
        <button type="button" className="btn-outline">Book a Demo</button>
      </header>

      <main>
        <section className="hero">
          <p className="tag">AI-Powered Growth Platform</p>
          <h1>Scale Your Digital Visibility With Zeorbit</h1>
          <p className="subtitle">
            We combine SEO automation, performance marketing, and real-time
            analytics to help your business get found and convert faster.
          </p>
          <div className="cta-row">
            <button type="button" className="btn-primary">Start Free Audit</button>
            <button type="button" className="btn-secondary">See Platform Tour</button>
          </div>
          <p className="api-pill">Backend status: {apiStatus}</p>
        </section>

        <section id="services" className="grid-section">
          <article className="card">
            <h3>Technical SEO</h3>
            <p>Automated site health checks, indexing diagnostics, and error prioritization.</p>
          </article>
          <article className="card">
            <h3>Content Intelligence</h3>
            <p>Keyword-backed briefs, AI-assisted content workflows, and SERP opportunity discovery.</p>
          </article>
          <article className="card">
            <h3>Ads & Conversion</h3>
            <p>Campaign optimization with clear attribution across paid, organic, and local channels.</p>
          </article>
        </section>

        <section id="why" className="split-section">
          <div>
            <h2>Built for growth teams that need speed</h2>
            <p>
              Zeorbit centralizes your SEO stack and marketing data in one place.
              Move from manual reporting to actionable insights in minutes.
            </p>
          </div>
          <ul>
            <li>Unified dashboard for SEO, content, and ads</li>
            <li>Actionable recommendations, not noisy reports</li>
            <li>Designed for agencies, startups, and local businesses</li>
          </ul>
        </section>

        <section id="contact" className="contact-cta">
          <h2>Ready to revamp your growth engine?</h2>
          <p>We can help you launch smarter campaigns with measurable ROI.</p>
          <button type="button" className="btn-primary">Talk to Zeorbit</button>
        </section>
      </main>

      <footer className="footer">
        <p>© {new Date().getFullYear()} Zeorbit. All rights reserved.</p>
      </footer>
    </div>
  )
}

export default App
