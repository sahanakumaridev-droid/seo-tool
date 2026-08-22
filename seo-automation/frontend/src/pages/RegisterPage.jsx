import { useState } from 'react'
import { useNavigate, Link, Navigate } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import AuthLayout from '../components/auth/AuthLayout'
import { registerUser } from '../api'

export default function RegisterPage({ onLogin }) {
  const navigate = useNavigate()
  const [alreadyAuthed] = useState(() => localStorage.getItem('seo_auth') === 'true')
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (alreadyAuthed) return <Navigate to="/" replace />

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await registerUser({
        name: form.name.trim(),
        email: form.email.trim(),
        password: form.password,
        role: 'client',
      })
      onLogin()
      navigate('/onboarding')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Registration failed. Try a different email.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Start with a free SEO audit — no credit card required"
      footer={
        <p style={{ fontSize: 13, color: 'var(--text-3)', textAlign: 'center' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--brand)', fontWeight: 600 }}>Sign in</Link>
        </p>
      }
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Full name</label>
          <input
            type="text" required value={form.name}
            onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            placeholder="Jane Cooper" autoComplete="name"
            style={{ width: '100%', padding: '11px 14px' }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Work email</label>
          <input
            type="email" required value={form.email}
            onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
            placeholder="you@company.com" autoComplete="email"
            style={{ width: '100%', padding: '11px 14px' }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Password</label>
          <input
            type="password" required minLength={6} value={form.password}
            onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
            placeholder="At least 6 characters" autoComplete="new-password"
            style={{ width: '100%', padding: '11px 14px' }}
          />
        </div>

        {error && <div className="alert alert-error">⚠ {error}</div>}

        <button type="submit" disabled={loading || !form.name || !form.email || form.password.length < 6}
          className="btn btn-primary" style={{ width: '100%', padding: '13px', fontSize: 15, marginTop: 4 }}>
          {loading ? 'Creating account…' : <>Create account <ArrowRight size={16} /></>}
        </button>
      </form>
    </AuthLayout>
  )
}
