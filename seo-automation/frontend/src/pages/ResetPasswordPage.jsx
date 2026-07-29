import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, CheckCircle2 } from 'lucide-react'
import AuthLayout from '../components/auth/AuthLayout'

export default function ResetPasswordPage() {
  const [form, setForm] = useState({ password: '', confirm: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm) {
      setError("Passwords don't match.")
      return
    }
    setLoading(true)
    await new Promise(r => setTimeout(r, 600))
    setLoading(false)
    setDone(true)
  }

  if (done) {
    return (
      <AuthLayout title="Password updated" subtitle="You can now sign in with your new password">
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <div style={{ width: 52, height: 52, borderRadius: 14, background: 'var(--green-soft)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16 }}>
            <CheckCircle2 size={24} style={{ color: 'var(--green)' }} />
          </div>
          <Link to="/login" className="btn btn-primary" style={{ display: 'inline-flex' }}>Go to login</Link>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Set a new password" subtitle="Choose a strong password you haven't used before">
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>New password</label>
          <input
            type="password" required minLength={6} value={form.password}
            onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
            placeholder="At least 6 characters" autoComplete="new-password"
            style={{ width: '100%', padding: '11px 14px' }}
          />
        </div>
        <div>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Confirm password</label>
          <input
            type="password" required value={form.confirm}
            onChange={e => setForm(f => ({ ...f, confirm: e.target.value }))}
            placeholder="Re-enter your password" autoComplete="new-password"
            style={{ width: '100%', padding: '11px 14px' }}
          />
        </div>

        {error && <div className="alert alert-error">⚠ {error}</div>}

        <button type="submit" disabled={loading || !form.password || !form.confirm} className="btn btn-primary"
          style={{ width: '100%', padding: '13px', fontSize: 15, marginTop: 4 }}>
          {loading ? 'Updating…' : <>Update Password <ArrowRight size={16} /></>}
        </button>
      </form>
    </AuthLayout>
  )
}
