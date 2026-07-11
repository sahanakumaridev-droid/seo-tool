import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Zap, TrendingUp, Globe, Share2, Users, BarChart2, ArrowRight, CheckCircle } from 'lucide-react'

const FEATURES = [
  { icon: TrendingUp, label: 'AI Bulk Content',    desc: 'Generate 50+ city pages in seconds' },
  { icon: Globe,      label: 'WordPress Publish',  desc: 'Auto-publish with images & SEO meta' },
  { icon: Share2,     label: 'Social Automation',  desc: 'Share to all platforms instantly' },
  { icon: Users,      label: 'Lead Capture',       desc: 'Bark, Thumbtack & website leads' },
  { icon: BarChart2,  label: 'SEO Analytics',      desc: 'Rankings, traffic & competitor gaps' },
]

const STATS = [
  { value: '50+', label: 'Cities' },
  { value: 'GPT-4', label: 'AI Engine' },
  { value: '6', label: 'Platforms' },
  { value: '100%', label: 'SEO Ready' },
]

export default function LoginPage({ onLogin }) {
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
      localStorage.setItem('seo_auth', 'true')
      onLogin()
      navigate('/')
    } else {
      setError('Invalid username or password.')
    }
    setLoading(false)
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', fontFamily: "'Inter', system-ui, sans-serif" }}>

      {/* ── LEFT PANEL — Design / Branding ── */}
      <div style={{
        flex: '0 0 55%',
        background: 'linear-gradient(135deg, #080C14 0%, #0D1628 40%, #0A1020 100%)',
        position: 'relative',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '48px 56px',
      }}>
        {/* Animated background orbs */}
        <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: '-80px', left: '-80px', width: 400, height: 400, borderRadius: '50%', background: 'radial-gradient(circle, rgba(6,182,212,0.18) 0%, transparent 70%)', filter: 'blur(40px)' }} />
          <div style={{ position: 'absolute', bottom: '10%', right: '-60px', width: 350, height: 350, borderRadius: '50%', background: 'radial-gradient(circle, rgba(99,102,241,0.2) 0%, transparent 70%)', filter: 'blur(40px)' }} />
          <div style={{ position: 'absolute', top: '45%', left: '30%', width: 250, height: 250, borderRadius: '50%', background: 'radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%)', filter: 'blur(50px)' }} />
          {/* Grid lines */}
          <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0.04 }} xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>

        {/* Logo */}
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 44, height: 44, borderRadius: 14, background: 'linear-gradient(135deg,#06B6D4,#3B82F6)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 24px rgba(6,182,212,0.5)' }}>
              <Zap size={22} color="white" />
            </div>
            <div>
              <div style={{ color: 'white', fontWeight: 900, fontSize: 22, letterSpacing: '-0.5px', lineHeight: 1 }}>ZEORBIT</div>
              <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 11, marginTop: 2 }}>SEO Intelligence Platform</div>
            </div>
          </div>
        </div>

        {/* Hero text */}
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '5px 12px', borderRadius: 20, background: 'rgba(6,182,212,0.1)', border: '1px solid rgba(6,182,212,0.25)', marginBottom: 20 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#06B6D4', display: 'inline-block', boxShadow: '0 0 6px #06B6D4' }} />
            <span style={{ color: '#67E8F9', fontSize: 12, fontWeight: 600 }}>AI-Powered Local SEO</span>
          </div>

          <h1 style={{ color: 'white', fontSize: 42, fontWeight: 900, lineHeight: 1.15, margin: '0 0 16px', letterSpacing: '-1px' }}>
            Dominate Local Search<br />
            <span style={{ background: 'linear-gradient(135deg,#06B6D4,#1D4ED8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              in Every City
            </span>
          </h1>

          <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: 15, lineHeight: 1.7, margin: '0 0 36px', maxWidth: 420 }}>
            Generate 50+ SEO-optimized pages, auto-publish to WordPress with AI images, and share to all social platforms — from one dashboard.
          </p>

          {/* Stats row */}
          <div style={{ display: 'flex', gap: 20, marginBottom: 40 }}>
            {STATS.map(s => (
              <div key={s.label} style={{ textAlign: 'center' }}>
                <div style={{ color: 'white', fontWeight: 800, fontSize: 22, lineHeight: 1 }}>{s.value}</div>
                <div style={{ color: 'rgba(255,255,255,0.35)', fontSize: 11, marginTop: 4 }}>{s.label}</div>
              </div>
            ))}
          </div>

          {/* Feature list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {FEATURES.map(f => (
              <div key={f.label} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '12px 16px', borderRadius: 12, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(8px)' }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg,rgba(6,182,212,0.2),rgba(99,102,241,0.2))', border: '1px solid rgba(6,182,212,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <f.icon size={16} color="#67E8F9" />
                </div>
                <div>
                  <div style={{ color: 'white', fontWeight: 600, fontSize: 13 }}>{f.label}</div>
                  <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 11, marginTop: 1 }}>{f.desc}</div>
                </div>
                <CheckCircle size={14} color="rgba(16,185,129,0.7)" style={{ marginLeft: 'auto', flexShrink: 0 }} />
              </div>
            ))}
          </div>
        </div>

        {/* Bottom tagline */}
        <div style={{ position: 'relative', zIndex: 1 }}>
          <p style={{ color: 'rgba(255,255,255,0.2)', fontSize: 12, margin: 0 }}>
            © 2026 ZeOrbit · zeorbit.com
          </p>
        </div>
      </div>

      {/* ── RIGHT PANEL — Login Form ── */}
      <div style={{
        flex: '0 0 45%',
        background: '#ffffff',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px 56px',
        position: 'relative',
      }}>
        {/* Top right link */}
        <div style={{ position: 'absolute', top: 28, right: 36, display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ color: '#9ca3af', fontSize: 13 }}>New to ZeOrbit?</span>
          <button onClick={() => navigate('/home')} style={{ color: '#1877f2', fontSize: 13, fontWeight: 600, background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
            Learn more →
          </button>
        </div>

        <div style={{ width: '100%', maxWidth: 380 }}>
          {/* Form header */}
          <div style={{ marginBottom: 36 }}>
            <h2 style={{ color: '#111827', fontWeight: 800, fontSize: 28, margin: '0 0 8px', letterSpacing: '-0.5px' }}>
              Welcome back 👋
            </h2>
            <p style={{ color: '#6b7280', fontSize: 14, margin: 0 }}>
              Sign in to your SEO dashboard
            </p>
          </div>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Username */}
            <div>
              <label style={{ display: 'block', color: '#374151', fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
                Username
              </label>
              <input
                type="text"
                value={form.username}
                onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                placeholder="Enter your username"
                autoComplete="username"
                style={{ width: '100%', border: '1.5px solid #e5e7eb', borderRadius: 10, fontSize: 14, padding: '12px 14px', outline: 'none', color: '#111827', background: '#f9fafb', boxSizing: 'border-box', transition: 'border-color 0.15s, box-shadow 0.15s' }}
                onFocus={e => { e.target.style.borderColor = '#1877f2'; e.target.style.boxShadow = '0 0 0 3px rgba(24,119,242,0.1)'; e.target.style.background = '#fff' }}
                onBlur={e => { e.target.style.borderColor = '#e5e7eb'; e.target.style.boxShadow = 'none'; e.target.style.background = '#f9fafb' }}
              />
            </div>

            {/* Password */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <label style={{ color: '#374151', fontSize: 13, fontWeight: 600 }}>Password</label>
                <a href="#" style={{ color: '#1877f2', fontSize: 12, textDecoration: 'none', fontWeight: 500 }}>Forgot password?</a>
              </div>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPw ? 'text' : 'password'}
                  value={form.password}
                  onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  style={{ width: '100%', border: '1.5px solid #e5e7eb', borderRadius: 10, fontSize: 14, padding: '12px 44px 12px 14px', outline: 'none', color: '#111827', background: '#f9fafb', boxSizing: 'border-box', transition: 'border-color 0.15s, box-shadow 0.15s' }}
                  onFocus={e => { e.target.style.borderColor = '#1877f2'; e.target.style.boxShadow = '0 0 0 3px rgba(24,119,242,0.1)'; e.target.style.background = '#fff' }}
                  onBlur={e => { e.target.style.borderColor = '#e5e7eb'; e.target.style.boxShadow = 'none'; e.target.style.background = '#f9fafb' }}
                />
                <button type="button" onClick={() => setShowPw(s => !s)}
                  style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', padding: 0, display: 'flex' }}>
                  {showPw ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div style={{ padding: '10px 14px', borderRadius: 8, background: '#fef2f2', border: '1px solid #fecaca', color: '#dc2626', fontSize: 13, display: 'flex', alignItems: 'center', gap: 8 }}>
                <span>⚠</span> {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading || !form.username || !form.password}
              style={{
                width: '100%', padding: '13px 16px', borderRadius: 10, border: 'none',
                background: loading ? '#93c5fd' : 'linear-gradient(135deg,#1877f2,#1d4ed8)',
                color: 'white', fontSize: 15, fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer',
                opacity: (!form.username || !form.password) ? 0.6 : 1,
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                boxShadow: '0 4px 14px rgba(24,119,242,0.35)',
                transition: 'opacity 0.15s, transform 0.1s',
                marginTop: 4,
              }}
              onMouseEnter={e => { if (!loading && form.username && form.password) e.currentTarget.style.transform = 'translateY(-1px)' }}
              onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
            >
              {loading ? (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ animation: 'spin 0.8s linear infinite' }}>
                    <circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.3)" strokeWidth="3"/>
                    <path d="M12 2a10 10 0 0 1 10 10" stroke="white" strokeWidth="3" strokeLinecap="round"/>
                  </svg>
                  Signing in...
                </>
              ) : (
                <>Sign In <ArrowRight size={16} /></>
              )}
            </button>
          </form>

          {/* Divider */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '24px 0' }}>
            <div style={{ flex: 1, height: 1, background: '#e5e7eb' }} />
            <span style={{ color: '#9ca3af', fontSize: 12 }}>Demo credentials</span>
            <div style={{ flex: 1, height: 1, background: '#e5e7eb' }} />
          </div>

          {/* Demo hint */}
          <div style={{ padding: '14px 16px', borderRadius: 10, background: '#eff6ff', border: '1px solid #bfdbfe', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ color: '#1e40af', fontSize: 12, fontWeight: 700, marginBottom: 4 }}>Quick Demo Access</div>
              <div style={{ color: '#3b82f6', fontSize: 13 }}>
                <span style={{ fontFamily: 'monospace', background: '#dbeafe', padding: '1px 6px', borderRadius: 4 }}>admin</span>
                {' / '}
                <span style={{ fontFamily: 'monospace', background: '#dbeafe', padding: '1px 6px', borderRadius: 4 }}>admin</span>
              </div>
            </div>
            <button
              onClick={() => { setForm({ username: 'admin', password: 'admin' }) }}
              style={{ padding: '7px 14px', borderRadius: 8, background: '#1877f2', color: 'white', border: 'none', fontSize: 12, fontWeight: 700, cursor: 'pointer' }}>
              Auto-fill
            </button>
          </div>

          {/* Footer */}
          <p style={{ color: '#9ca3af', fontSize: 12, textAlign: 'center', marginTop: 28 }}>
            By signing in, you agree to our{' '}
            <a href="#" style={{ color: '#6b7280', textDecoration: 'underline' }}>Terms</a>
            {' & '}
            <a href="#" style={{ color: '#6b7280', textDecoration: 'underline' }}>Privacy Policy</a>
          </p>
        </div>

        {/* Spin animation */}
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    </div>
  )
}
