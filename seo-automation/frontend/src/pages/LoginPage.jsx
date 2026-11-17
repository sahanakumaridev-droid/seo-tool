import { useState } from 'react'
import { useNavigate, useLocation, Navigate } from 'react-router-dom'
import { Eye, EyeOff, ArrowRight } from 'lucide-react'
import AuthLayout from '../components/auth/AuthLayout'
import { loginUser } from '../api'

function nextPath(location, hasProject, role) {
  const from = location.state?.from?.pathname
  if (from && !['/login', '/register', '/forgot-password'].includes(from)) return from
  if (role === 'admin') return '/content'
  return hasProject ? '/' : '/onboarding'
}

export default function LoginPage({ onLogin }) {
  const navigate = useNavigate()
  const location = useLocation()
  const [alreadyAuthed] = useState(() => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('mp_token')
    return localStorage.getItem('seo_auth') === 'true' && !!token
  })
  const [form, setForm] = useState({ email: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState(() => (sessionStorage.getItem('seo_session_expired') === '1' ? 'Session expired. Sign in again.' : ''))
  const [loading, setLoading] = useState(false)

  if (alreadyAuthed) {
    let role = ''
    try { role = JSON.parse(localStorage.getItem('mp_user') || '{}').role || '' } catch { /* ignore */ }
    return <Navigate to={nextPath(location, !!localStorage.getItem('seo_project'), role)} replace />
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await loginUser(form.email.trim(), form.password)
      const role = res.data?.user?.role
      if (role === 'admin' && !localStorage.getItem('seo_project')) {
        localStorage.setItem('seo_project', JSON.stringify({
          business_name: 'ZeOrbit',
          website: 'https://zeorbit.com',
        }))
      }
      onLogin()
      sessionStorage.removeItem('seo_session_expired')
      const hasProject = !!localStorage.getItem('seo_project')
      navigate(nextPath(location, hasProject, role))
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Invalid email or password. Register first if you are new.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in with your ZeOrbit account"
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Username</label>
          <input
            type="text" required value={form.email}
            onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
            placeholder="Email" autoComplete="username"
            style={{ width: '100%', padding: '11px 14px' }}
          />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
            <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-2)' }}>Password</label>
          </div>
          <div style={{ position: 'relative' }}>
            <input
              type={showPw ? 'text' : 'password'} required value={form.password}
              onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              placeholder="Password" autoComplete="current-password"
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
    </AuthLayout>
  )
}
