import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, FileText, Globe, Image, Share2, Users, BarChart2, ArrowRight, CheckCircle, Star, Eye, EyeOff, X } from 'lucide-react'

const C = {
  bg: '#0B0F1A', surface: '#111827', raised: '#1A2235', border: '#1E2D42',
  brand: '#3B82F6', violet: '#60A5FA', green: '#34D399', amber: '#FBBF24',
  t1: '#F1F5F9', t2: '#94A3B8', t3: '#64748B',
  grad: 'linear-gradient(135deg,#3B82F6,#1D4ED8)',
}

const FEATURES = [
  { Icon: FileText,  accent: '#3B82F6', title: 'AI Bulk Content',      desc: 'Generate 50+ SEO-optimized pages in seconds using GPT-4.' },
  { Icon: Globe,     accent: '#2563EB', title: 'WordPress Publishing', desc: 'Auto-publish with RankMath, Yoast, or AIOSEO. Images, categories, and tags included.' },
  { Icon: Image,     accent: '#60A5FA', title: 'AI Image Generation',  desc: 'Auto-generate and attach relevant images using DALL·E 3, Unsplash, or Pexels.' },
  { Icon: Share2,    accent: '#1D4ED8', title: 'Social Automation',    desc: 'Share to Facebook, X, LinkedIn, and Instagram with captions and hashtags.' },
  { Icon: Users,     accent: '#059669', title: 'Lead Capture',         desc: 'Capture and manage leads from Angi, Thumbtack, and your own website.' },
  { Icon: BarChart2, accent: '#2563EB', title: 'SEO Analytics',        desc: 'Track keyword rankings, organic traffic, and competitor gaps.' },
]

const STEPS = [
  { n: '01', title: 'Set Your Business',     desc: 'Enter your business type, service area, and target keywords. Pick your cities and industry.', accent: '#3B82F6' },
  { n: '02', title: 'AI Generates Content',  desc: 'GPT-4 creates unique, SEO-optimized pages for every city — titles, meta, FAQs, and schema.', accent: '#2563EB' },
  { n: '03', title: 'Auto-Publish & Share',  desc: 'Pages publish to WordPress automatically. Social posts go out to every platform instantly.', accent: '#059669' },
]

const TESTIMONIALS = [
  { name: 'Marcus T.', role: 'Plumbing Owner · San Diego, CA', text: 'Generated 50 city pages in under 2 minutes. Our organic traffic doubled in 60 days.' },
  { name: 'Sarah K.',  role: 'Marketing Agency · Austin, TX',  text: 'We use this for all our local SEO clients. The WordPress auto-publish saves us 10+ hours a week.' },
  { name: 'James R.',  role: 'HVAC Contractor · Phoenix, AZ',  text: 'The lead capture from Angi and Thumbtack is a game changer. Everything in one place.' },
]

const STATS = [
  { v: '50+',    l: 'Cities / campaign' },
  { v: 'GPT-4',  l: 'AI Engine' },
  { v: '6',      l: 'Social platforms' },
  { v: '100%',   l: 'SEO optimized' },
]

function Btn({ children, onClick, primary, large }) {
  const [hov, setHov] = useState(false)
  return (
    <button onClick={onClick} onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)}
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 8,
        padding: large ? '14px 32px' : '10px 22px', borderRadius: 12, border: 'none', cursor: 'pointer',
        fontSize: large ? 16 : 14, fontWeight: 700, transition: 'all 0.15s',
        transform: hov ? 'translateY(-2px)' : 'none',
        ...(primary ? {
          background: C.grad, color: '#fff',
          boxShadow: hov ? '0 8px 28px rgba(59,130,246,0.4)' : '0 4px 16px rgba(59,130,246,0.25)',
        } : {
          background: hov ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.04)',
          color: C.t1, border: `1px solid ${hov ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.1)'}`,
        }),
      }}
    >
      {children}
    </button>
  )
}

function FeatureCard({ f }) {
  const [hov, setHov] = useState(false)
  return (
    <div onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)}
      style={{
        padding: 24, borderRadius: 16, background: hov ? '#1A2235' : C.surface,
        border: `1px solid ${C.border}`, boxShadow: hov ? '0 8px 24px rgba(0,0,0,0.3)' : 'none',
        transition: 'all 0.18s', transform: hov ? 'translateY(-2px)' : 'none',
      }}>
      <div style={{ width: 42, height: 42, borderRadius: 12, background: `${f.accent}18`, border: `1px solid ${f.accent}30`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16 }}>
        <f.Icon size={19} color={f.accent} />
      </div>
      <h3 style={{ fontSize: 15, fontWeight: 700, color: C.t1, margin: '0 0 8px' }}>{f.title}</h3>
      <p style={{ fontSize: 13, color: C.t2, lineHeight: 1.65, margin: 0 }}>{f.desc}</p>
    </div>
  )
}

function LoginDialog({ onClose, onLogin }) {
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    await new Promise(r => setTimeout(r, 700))
    if (form.username === 'admin' && form.password === 'admin') {
      onLogin()
      navigate('/dashboard')
    } else {
      setError('Invalid username or password.')
    }
    setLoading(false)
  }

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }} onClick={onClose}>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)' }} />
      <div style={{ position: 'relative', width: '100%', maxWidth: 420, background: '#111827', border: '1px solid #2A3B57', borderRadius: 20, boxShadow: '0 25px 60px rgba(0,0,0,0.6)', overflow: 'hidden' }} onClick={e => e.stopPropagation()}>
        <button onClick={onClose} style={{ position: 'absolute', top: 16, right: 16, width: 32, height: 32, borderRadius: 8, background: 'rgba(255,255,255,0.06)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94A3B8', transition: 'all 0.15s' }}
          onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.12)'; e.currentTarget.style.color = '#F1F5F9' }}
          onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.06)'; e.currentTarget.style.color = '#94A3B8' }}>
          <X size={16} />
        </button>

        <div style={{ padding: '40px 36px 36px' }}>
          <div style={{ textAlign: 'center', marginBottom: 28 }}>
            <div style={{ width: 52, height: 52, borderRadius: 14, background: C.grad, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14, boxShadow: '0 8px 24px rgba(59,130,246,0.3)' }}>
              <Zap size={26} color="white" />
            </div>
            <h2 style={{ fontSize: 24, fontWeight: 800, color: '#F1F5F9', margin: '0 0 6px', letterSpacing: '-0.5px' }}>Welcome to ZEORBIT</h2>
            <p style={{ fontSize: 14, color: '#94A3B8', margin: 0 }}>Sign in to your SEO dashboard</p>
          </div>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#CBD5E1', marginBottom: 6 }}>Username</label>
              <input type="text" value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} placeholder="admin" autoComplete="username"
                style={{ width: '100%', padding: '11px 14px', fontSize: 14, borderRadius: 10, border: '1.5px solid #2A3B57', background: '#1A2235', color: '#F1F5F9', outline: 'none', boxSizing: 'border-box', transition: 'all 0.15s' }}
                onFocus={e => { e.target.style.borderColor = '#3B82F6'; e.target.style.boxShadow = '0 0 0 3px rgba(59,130,246,0.18)'; e.target.style.background = '#1A2235' }}
                onBlur={e => { e.target.style.borderColor = '#2A3B57'; e.target.style.boxShadow = 'none'; e.target.style.background = '#1A2235' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#CBD5E1', marginBottom: 6 }}>Password</label>
              <div style={{ position: 'relative' }}>
                <input type={showPw ? 'text' : 'password'} value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} placeholder="••••••••" autoComplete="current-password"
                  style={{ width: '100%', padding: '11px 42px 11px 14px', fontSize: 14, borderRadius: 10, border: '1.5px solid #2A3B57', background: '#1A2235', color: '#F1F5F9', outline: 'none', boxSizing: 'border-box', transition: 'all 0.15s' }}
                  onFocus={e => { e.target.style.borderColor = '#3B82F6'; e.target.style.boxShadow = '0 0 0 3px rgba(59,130,246,0.18)'; e.target.style.background = '#1A2235' }}
                  onBlur={e => { e.target.style.borderColor = '#2A3B57'; e.target.style.boxShadow = 'none'; e.target.style.background = '#1A2235' }}
                />
                <button type="button" onClick={() => setShowPw(s => !s)}
                  style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#94A3B8', padding: 0, display: 'flex' }}>
                  {showPw ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </div>
            </div>

            {error && (
              <div style={{ padding: '10px 14px', borderRadius: 8, background: 'rgba(248,113,113,0.14)', border: '1px solid rgba(248,113,113,0.30)', color: '#F87171', fontSize: 13 }}>⚠ {error}</div>
            )}

            <button type="submit" disabled={loading || !form.username || !form.password}
              style={{
                width: '100%', padding: '13px', borderRadius: 10, border: 'none',
                background: loading ? '#93c5fd' : C.grad, color: 'white', fontSize: 15, fontWeight: 700,
                cursor: loading ? 'not-allowed' : 'pointer', opacity: (!form.username || !form.password) ? 0.6 : 1,
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                boxShadow: '0 4px 14px rgba(59,130,246,0.35)', transition: 'all 0.15s', marginTop: 4,
              }}>
              {loading ? 'Signing in...' : <>Sign In <ArrowRight size={16} /></>}
            </button>
          </form>

          <div style={{ marginTop: 20, paddingTop: 20, borderTop: '1px solid #1E2D42', textAlign: 'center' }}>
            <p style={{ fontSize: 12, color: '#94A3B8', margin: 0 }}>
              Demo: <span style={{ fontFamily: 'monospace', background: '#1A2235', padding: '2px 6px', borderRadius: 4, color: '#F1F5F9', fontWeight: 600 }}>admin / admin</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function LandingPage({ onLogin }) {
  const navigate = useNavigate()
  const [showLogin, setShowLogin] = useState(false)

  return (
    <div className="landing-dark" style={{ minHeight: '100vh', background: C.bg, color: C.t1, fontFamily: "'Inter',-apple-system,sans-serif", overflowX: 'hidden' }}>

      {/* ── Navbar ── */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 40px', height: 64,
        background: 'rgba(11,15,26,0.9)', backdropFilter: 'blur(16px)',
        borderBottom: `1px solid ${C.border}`,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: C.grad, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 20px rgba(59,130,246,0.4)' }}>
            <Zap size={18} color="white" />
          </div>
          <span style={{ fontWeight: 900, fontSize: 18, letterSpacing: '-0.5px' }}>ZEORBIT</span>
          <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 20, background: 'rgba(59,130,246,0.1)', color: C.brand, border: `1px solid rgba(59,130,246,0.2)`, marginLeft: 4 }}>SEO AI</span>
        </div>

        <div style={{ display: 'flex', gap: 32, fontSize: 14, color: C.t2 }}>
          {['Features', 'How it works', 'Reviews'].map(l => (
            <a key={l} href={`#${l.toLowerCase().replace(/ /g, '-')}`}
              style={{ color: C.t2, textDecoration: 'none', transition: 'color 0.15s' }}
              onMouseEnter={e => e.target.style.color = C.t1}
              onMouseLeave={e => e.target.style.color = C.t2}>{l}</a>
          ))}
        </div>

        <div style={{ display: 'flex', gap: 10 }}>
          <Btn onClick={() => setShowLogin(true)}>Sign In</Btn>
          <Btn onClick={() => setShowLogin(true)} primary>Get Started Free</Btn>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section style={{ paddingTop: 140, paddingBottom: 100, textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: 0, left: '50%', transform: 'translateX(-50%)', width: 700, height: 400, borderRadius: '50%', background: 'radial-gradient(ellipse,rgba(59,130,246,0.15) 0%,rgba(37,99,235,0.08) 50%,transparent 70%)', filter: 'blur(60px)', pointerEvents: 'none' }} />

        <div style={{ position: 'relative', maxWidth: 800, margin: '0 auto', padding: '0 24px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 20, background: 'rgba(59,130,246,0.08)', border: `1px solid rgba(59,130,246,0.2)`, color: C.brand, fontSize: 13, fontWeight: 600, marginBottom: 24 }}>
            <Zap size={13} /> AI-Powered Local SEO for U.S. Businesses
          </div>

          <h1 style={{ fontSize: 58, fontWeight: 900, lineHeight: 1.1, margin: '0 0 20px', letterSpacing: '-2px' }}>
            Dominate Local Search<br />
            <span style={{ background: C.grad, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>in Every U.S. City</span>
          </h1>

          <p style={{ fontSize: 18, color: C.t2, maxWidth: 560, margin: '0 auto 40px', lineHeight: 1.7 }}>
            Generate 50+ SEO-optimized pages, auto-publish to WordPress, share to social media, and capture leads — all from one AI-powered platform built for American local businesses.
          </p>

          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap', marginBottom: 64 }}>
            <Btn onClick={() => setShowLogin(true)} primary large>Start Free Today <ArrowRight size={18} /></Btn>
            <Btn onClick={() => setShowLogin(true)} large>View Dashboard</Btn>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, maxWidth: 560, margin: '0 auto' }}>
            {STATS.map(s => (
              <div key={s.l} style={{ padding: '16px 12px', borderRadius: 12, background: 'rgba(255,255,255,0.03)', border: `1px solid ${C.border}`, textAlign: 'center' }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: C.t1, lineHeight: 1 }}>{s.v}</div>
                <div style={{ fontSize: 11, color: C.t3, marginTop: 5 }}>{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section id="how-it-works" style={{ padding: '80px 24px' }}>
        <div style={{ maxWidth: 960, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 56 }}>
            <h2 style={{ fontSize: 34, fontWeight: 800, margin: '0 0 10px', letterSpacing: '-0.5px' }}>How It Works</h2>
            <p style={{ color: C.t2, fontSize: 15 }}>Three steps to dominate local SEO in any U.S. city</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 20 }}>
            {STEPS.map(s => (
              <div key={s.n} style={{ position: 'relative', padding: '28px 24px', borderRadius: 16, background: C.surface, border: `1px solid ${C.border}`, boxShadow: '0 2px 8px rgba(0,0,0,0.3)' }}>
                <div style={{ fontSize: 52, fontWeight: 900, color: s.accent, opacity: 0.12, lineHeight: 1, marginBottom: 12 }}>{s.n}</div>
                <h3 style={{ fontSize: 17, fontWeight: 700, color: C.t1, margin: '0 0 8px' }}>{s.title}</h3>
                <p style={{ fontSize: 13, color: C.t2, lineHeight: 1.65, margin: 0 }}>{s.desc}</p>
                <div style={{ position: 'absolute', top: 24, right: 24, width: 8, height: 8, borderRadius: '50%', background: s.accent, boxShadow: `0 0 10px ${s.accent}` }} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" style={{ padding: '80px 24px', background: 'rgba(17,24,39,0.6)' }}>
        <div style={{ maxWidth: 960, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 56 }}>
            <h2 style={{ fontSize: 34, fontWeight: 800, margin: '0 0 10px', letterSpacing: '-0.5px' }}>Everything You Need</h2>
            <p style={{ color: C.t2, fontSize: 15 }}>A complete AI-powered SEO and lead generation platform</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
            {FEATURES.map(f => <FeatureCard key={f.title} f={f} />)}
          </div>
        </div>
      </section>

      {/* ── Testimonials ── */}
      <section id="reviews" style={{ padding: '80px 24px' }}>
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 56 }}>
            <h2 style={{ fontSize: 34, fontWeight: 800, margin: '0 0 10px', letterSpacing: '-0.5px' }}>Trusted by U.S. Local Businesses</h2>
            <p style={{ color: C.t2, fontSize: 15 }}>See what business owners across America are saying</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
            {TESTIMONIALS.map(t => (
              <div key={t.name} style={{ padding: 24, borderRadius: 16, background: C.surface, border: `1px solid ${C.border}` }}>
                <div style={{ display: 'flex', gap: 3, marginBottom: 14 }}>
                  {[...Array(5)].map((_, i) => <Star key={i} size={13} fill={C.amber} color={C.amber} />)}
                </div>
                <p style={{ fontSize: 13, color: C.t2, lineHeight: 1.7, margin: '0 0 16px' }}>"{t.text}"</p>
                <div style={{ fontSize: 13, fontWeight: 600, color: C.t1 }}>{t.name}</div>
                <div style={{ fontSize: 11, color: C.t3, marginTop: 2 }}>{t.role}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section style={{ padding: '100px 24px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at center,rgba(37,99,235,0.1) 0%,transparent 65%)', pointerEvents: 'none' }} />
        <div style={{ position: 'relative', maxWidth: 560, margin: '0 auto' }}>
          <h2 style={{ fontSize: 40, fontWeight: 900, margin: '0 0 16px', letterSpacing: '-1px' }}>Ready to Dominate Local SEO?</h2>
          <p style={{ color: C.t2, fontSize: 16, margin: '0 0 36px', lineHeight: 1.6 }}>Start generating AI-powered content for every city in your U.S. market today.</p>
          <Btn onClick={() => setShowLogin(true)} primary large>Get Started Free <ArrowRight size={20} /></Btn>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 28, marginTop: 24, flexWrap: 'wrap' }}>
            {['No credit card required', 'Free forever plan', 'Cancel anytime'].map(t => (
              <span key={t} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: C.t3 }}>
                <CheckCircle size={12} color={C.green} /> {t}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer style={{ padding: '28px 40px', borderTop: `1px solid ${C.border}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 26, height: 26, borderRadius: 7, background: C.grad, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Zap size={13} color="white" />
          </div>
          <span style={{ fontWeight: 700, fontSize: 13, color: C.t1 }}>ZEORBIT</span>
          <span style={{ color: C.t3, fontSize: 12 }}>© 2026 SEO Intelligence Platform</span>
        </div>
        <div style={{ display: 'flex', gap: 20 }}>
          {['zeorbit.com', 'instagram.com/zeorbit', 'twitter.com/orbit_ze'].map(l => (
            <a key={l} href={`https://${l}`} target="_blank" rel="noreferrer"
              style={{ color: C.t3, fontSize: 12, textDecoration: 'none', transition: 'color 0.15s' }}
              onMouseEnter={e => e.target.style.color = C.t1}
              onMouseLeave={e => e.target.style.color = C.t3}>{l}</a>
          ))}
        </div>
      </footer>

      {/* ── Login Dialog ── */}
      {showLogin && <LoginDialog onClose={() => setShowLogin(false)} onLogin={onLogin} />}
    </div>
  )
}
