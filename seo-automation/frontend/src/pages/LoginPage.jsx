import { useState } from 'react'
import { useNavigate, Link, Navigate } from 'react-router-dom'
import { Eye, EyeOff, ArrowRight } from 'lucide-react'
import AuthLayout from '../components/auth/AuthLayout'

export default function LoginPage({ onLogin }) {
  const navigate = useNavigate()
  // Snapshot once at mount — see RegisterPage.jsx for why this isn't reactive.
  const [alreadyAuthed] = useState(() => localStorage.getItem('seo_auth') === 'true')
  const [form, setForm] = useState({ email: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (alreadyAuthed) return <Navigate to="/content" replace />

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    await new Promise(r => setTimeout(r, 600))
    if (form.password.length >= 4) {
      onLogin()
      const hasProject = !!localStorage.getItem('seo_project')
      navigate(hasProject ? '/content' : '/onboarding')
    } else {
      setError('Invalid email or password.')
    }
    setLoading(false)
  }

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to your SEO dashboard"
      footer={
        <p style={{ fontSize: 13, color: 'var(--text-3)', textAlign: 'center' }}>
          New to ZeOrbit? <Link to="/register" style={{ color: 'var(--brand)', fontWeight: 600 }}>Start free</Link>
        </p>
      }
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Email</label>
          <input
            type="text" required value={form.email}
            onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
            placeholder="you@company.com" autoComplete="email"
            style={{ width: '100%', padding: '11px 14px' }}
          />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
            <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-2)' }}>Password</label>
            <Link to="/forgot-password" style={{ color: 'var(--brand)', fontSize: 12, fontWeight: 500 }}>Forgot password?</Link>
          </div>
          <div style={{ position: 'relative' }}>
            <input
              type={showPw ? 'text' : 'password'} required value={form.password}
              onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              placeholder="Enter your password" autoComplete="current-password"
              style={{ width: '100%', padding: '11px 42px 11px 14px' }}
            />
            <button type="button" onClick={() => setShowPw(s => !s)}
              style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-4)', padding: 0, display: 'flex' }}>
              {showPw ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </div>
        </div>

        {error && <div className="alert alert-error">⚠ {error}</div>}

        <button type="submit" disabled={loading || !form.email || !form.password} className="btn btn-primary"
          style={{ width: '100%', padding: '13px', fontSize: 15, marginTop: 4 }}>
          {loading ? 'Signing in…' : <>Sign In <ArrowRight size={16} /></>}
        </button>
      </form>

      {/* Demo access — this build has no real backend user accounts yet;
          any email/username + password (4+ chars) signs in. */}
      <div style={{ marginTop: 20, padding: '12px 14px', borderRadius: 10, background: 'var(--brand-soft)', border: '1px solid rgba(255,90,78,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10 }}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--brand-dark)' }}>Demo access</div>
          <div style={{ fontSize: 12.5, color: 'var(--text-2)' }}>
            <span style={{ fontFamily: 'monospace', background: '#fff', padding: '1px 6px', borderRadius: 4 }}>admin</span>
            {' / '}
            <span style={{ fontFamily: 'monospace', background: '#fff', padding: '1px 6px', borderRadius: 4 }}>admin</span>
          </div>
        </div>
        <button type="button" onClick={() => setForm({ email: 'admin', password: 'admin' })} className="btn btn-secondary" style={{ fontSize: 12, padding: '7px 12px' }}>
          Autofill
        </button>
      </div>
    </AuthLayout>
  )
}
