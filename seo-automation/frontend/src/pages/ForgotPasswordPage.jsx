import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, MailCheck } from 'lucide-react'
import AuthLayout from '../components/auth/AuthLayout'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    await new Promise(r => setTimeout(r, 600))
    setLoading(false)
    setSent(true)
  }

  if (sent) {
    return (
      <AuthLayout title="Check your email" subtitle={`We sent a password reset link to ${email}`}>
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <div style={{ width: 52, height: 52, borderRadius: 14, background: 'var(--green-soft)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16 }}>
            <MailCheck size={24} style={{ color: 'var(--green)' }} />
          </div>
          <p style={{ fontSize: 13.5, color: 'var(--text-3)', marginBottom: 20 }}>
            Didn't get it? Check your spam folder, or try again with a different address.
          </p>
          <Link to="/login" className="btn btn-secondary" style={{ display: 'inline-flex' }}>Back to login</Link>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout
      title="Forgot password"
      subtitle="Enter your email and we'll send you a reset link"
      footer={
        <p style={{ fontSize: 13, color: 'var(--text-3)', textAlign: 'center' }}>
          Remembered it? <Link to="/login" style={{ color: 'var(--brand)', fontWeight: 600 }}>Sign in</Link>
        </p>
      }
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Email</label>
          <input
            type="email" required value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="you@company.com" autoComplete="email"
            style={{ width: '100%', padding: '11px 14px' }}
          />
        </div>
        <button type="submit" disabled={loading || !email} className="btn btn-primary"
          style={{ width: '100%', padding: '13px', fontSize: 15, marginTop: 4 }}>
          {loading ? 'Sending…' : <>Send Reset Link <ArrowRight size={16} /></>}
        </button>
      </form>
    </AuthLayout>
  )
}
