import { useState, useEffect } from 'react'
import { MapPin, Send, CheckCircle2, AlertTriangle } from 'lucide-react'
import { getGbpStatus, createGbpPost } from '../api'

const CTA_TYPES = [
  { value: 'LEARN_MORE', label: 'Learn More' },
  { value: 'CALL', label: 'Call Now' },
  { value: 'BOOK', label: 'Book' },
  { value: 'ORDER', label: 'Order Online' },
  { value: 'SHOP', label: 'Shop' },
  { value: 'SIGN_UP', label: 'Sign Up' },
  { value: 'GET_OFFER', label: 'Get Offer' },
]
const MAX_LEN = 1500

export default function GoogleBusinessProfilePage() {
  const [configured, setConfigured] = useState(null)
  const [message, setMessage] = useState('')
  const [ctaType, setCtaType] = useState('LEARN_MORE')
  const [ctaUrl, setCtaUrl] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getGbpStatus().then(r => setConfigured(r.data.configured)).catch(() => setConfigured(false))
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await createGbpPost({
        message: message.trim(),
        cta_type: ctaType,
        cta_url: ctaUrl.trim() || null,
        image_url: imageUrl.trim() || null,
      })
      if (res.data.success) setResult(res.data)
      else setError(res.data.error || 'Post failed.')
    } catch {
      setError('Could not reach the server. Please try again.')
    }
    setLoading(false)
  }

  return (
    <div className="space-y-5 fade-in" style={{ maxWidth: 640 }}>
      <div>
        <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>Google Business Profile</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text-3)' }}>
          Post a free local update — it shows on your listing in Google Search and Maps. No ad spend, no campaign budget.
        </p>
      </div>

      {configured === false && (
        <div className="alert alert-warning">
          <AlertTriangle size={15} style={{ flexShrink: 0, marginTop: 1 }} />
          <div>
            <strong>Google Business Profile isn't connected yet.</strong> Set <code>GBP_ACCESS_TOKEN</code>, <code>GBP_ACCOUNT_ID</code>, and <code>GBP_LOCATION_ID</code> in the backend <code>.env</code> (from the Google Business Profile API), then restart the server. This is entirely free to use once connected — posting here never costs anything, unlike Google Ads.
          </div>
        </div>
      )}
      {configured === true && (
        <div className="alert alert-success"><CheckCircle2 size={15} /> Google Business Profile connected — posts are free to publish.</div>
      )}

      {result && (
        <div className="card p-5" style={{ borderColor: 'var(--green)' }}>
          <div className="flex items-center gap-2">
            <CheckCircle2 size={18} style={{ color: 'var(--green)' }} />
            <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-1)' }}>Posted to your Business Profile</h3>
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-3)', margin: '8px 0 0' }}>It'll appear on your listing in Google Search and Maps shortly.</p>
        </div>
      )}
      {error && <div className="alert alert-error">⚠ {error}</div>}

      <form onSubmit={handleSubmit} className="card p-5" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        <div>
          <div className="flex items-center justify-between" style={{ marginBottom: 6 }}>
            <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-2)' }}>Update message</label>
            <span style={{ fontSize: 11.5, color: 'var(--text-4)' }}>{message.length}/{MAX_LEN}</span>
          </div>
          <textarea value={message} maxLength={MAX_LEN} onChange={e => setMessage(e.target.value)}
            placeholder="We just wrapped up a new website for a San Diego client! Book your free consultation this week."
            rows={5} style={{ width: '100%', padding: '10px 12px', fontFamily: 'inherit', resize: 'vertical' }} />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Button</label>
            <select value={ctaType} onChange={e => setCtaType(e.target.value)} style={{ width: '100%', padding: '10px 12px' }}>
              {CTA_TYPES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Button link <span style={{ color: 'var(--text-4)', fontWeight: 400 }}>(optional)</span></label>
            <input type="text" value={ctaUrl} onChange={e => setCtaUrl(e.target.value)}
              placeholder="https://example.com or tel:+16195551234" style={{ width: '100%', padding: '10px 12px' }} />
          </div>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Photo URL <span style={{ color: 'var(--text-4)', fontWeight: 400 }}>(optional)</span></label>
          <input type="text" value={imageUrl} onChange={e => setImageUrl(e.target.value)}
            placeholder="https://example.com/photo.jpg" style={{ width: '100%', padding: '10px 12px' }} />
        </div>

        <button type="submit" disabled={loading || !message.trim()} className="btn btn-primary" style={{ padding: '12px 20px', fontSize: 14.5 }}>
          <Send size={15} /> {loading ? 'Posting…' : 'Post for Free'}
        </button>
      </form>

      <div className="card p-4 flex items-start gap-3">
        <MapPin size={16} style={{ color: 'var(--brand)', flexShrink: 0, marginTop: 2 }} />
        <p style={{ fontSize: 12.5, color: 'var(--text-3)', margin: 0, lineHeight: 1.6 }}>
          Google Business Profile posts are the closest free equivalent to a Google Ad for local visibility — they appear directly
          on your business listing when people search for you or businesses like you nearby. Combine this with the Site Audit and
          Keyword Research tools for a fully free growth path alongside (or instead of) paid Google Ads.
        </p>
      </div>
    </div>
  )
}
