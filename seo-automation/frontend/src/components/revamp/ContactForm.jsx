import { useMemo, useState } from 'react'
import { CheckCircle2, Loader2 } from 'lucide-react'

const SERVICE_OPTIONS = [
  { value: 'Site Performance', label: 'Site Performance' },
  { value: 'Keyword Research', label: 'Keyword Research' },
  { value: 'AI Visibility', label: 'AI Visibility' },
  { value: 'Competitive Analysis', label: 'Competitive Analysis' },
  { value: 'Content', label: 'Content' },
  { value: 'Link Building', label: 'Link Building' },
  { value: 'Local', label: 'Local' },
  { value: 'Reports', label: 'Reports' },
  { value: 'Enterprise', label: 'Enterprise / Custom' },
]

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())
}

function normalizeWebsite(value) {
  const v = value.trim()
  if (!v) return ''
  if (/^https?:\/\//i.test(v)) return v
  return `https://${v}`
}

export default function ContactForm() {
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    website: '',
    service: SERVICE_OPTIONS[0]?.value ?? '',
    message: '',
  })

  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState({ type: 'idle', message: '' })

  const payload = useMemo(() => ({
    source: 'landing_page',
    name: form.name.trim(),
    email: form.email.trim(),
    phone: form.phone.trim(),
    business_name: form.company.trim(),
    website: normalizeWebsite(form.website),
    service: form.service,
    message: form.message.trim(),
  }), [form])

  const canSubmit = Boolean(
    payload.name
    && payload.email
    && isValidEmail(payload.email)
    && payload.business_name
    && payload.message
  )

  async function onSubmit(e) {
    e.preventDefault()
    if (!canSubmit || loading) return

    setLoading(true)
    setStatus({ type: 'idle', message: '' })
    try {
      const endpoint = '/api/leads/'

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        let detail = `Request failed (${res.status})`
        try {
          const data = await res.json()
          if (data?.detail) detail = typeof data.detail === 'string' ? data.detail : detail
        } catch {
          /* ignore */
        }
        throw new Error(detail)
      }

      setStatus({
        type: 'success',
        message: 'Request received. Our team will email you within one business day.',
      })
      setForm({
        name: '',
        email: '',
        phone: '',
        company: '',
        website: '',
        service: SERVICE_OPTIONS[0]?.value ?? '',
        message: '',
      })
    } catch (err) {
      setStatus({
        type: 'error',
        message: err?.message
          ? `Could not send: ${err.message}. Email info@zeorbit.com if this keeps happening.`
          : 'Could not send. Please try again or email info@zeorbit.com.',
      })
    } finally {
      setLoading(false)
    }
  }

  if (status.type === 'success') {
    return (
      <div className="rv-contact-card rv-contact-success" role="status">
        <CheckCircle2 size={36} />
        <h3>You’re on the list</h3>
        <p>{status.message}</p>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => setStatus({ type: 'idle', message: '' })}
        >
          Send another request
        </button>
      </div>
    )
  }

  return (
    <div className="rv-contact-card" role="region" aria-label="Contact ZeOrbit">
      <div className="rv-contact-head">
        <p className="rv-contact-eyebrow">Talk to sales</p>
        <h3>Tell us about your SEO goals</h3>
        <p className="rv-contact-sub">
          Submit here — we keep you on this page and reply by email within one business day.
        </p>
      </div>

      <form className="rv-contact-form" onSubmit={onSubmit} noValidate>
        <div className="rv-form-grid">
          <label className="rv-label">
            Name *
            <input
              className="rv-input"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              autoComplete="name"
              required
            />
          </label>

          <label className="rv-label">
            Work email *
            <input
              className="rv-input"
              value={form.email}
              onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
              autoComplete="email"
              type="email"
              required
            />
          </label>

          <label className="rv-label">
            Company *
            <input
              className="rv-input"
              value={form.company}
              onChange={(e) => setForm((p) => ({ ...p, company: e.target.value }))}
              autoComplete="organization"
              required
            />
          </label>

          <label className="rv-label">
            Website
            <input
              className="rv-input"
              value={form.website}
              onChange={(e) => setForm((p) => ({ ...p, website: e.target.value }))}
              autoComplete="url"
              placeholder="yourbusiness.com"
            />
          </label>

          <label className="rv-label">
            Phone
            <input
              className="rv-input"
              value={form.phone}
              onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))}
              autoComplete="tel"
              inputMode="tel"
            />
          </label>

          <label className="rv-label">
            What do you need?
            <select
              className="rv-input rv-select"
              value={form.service}
              onChange={(e) => setForm((p) => ({ ...p, service: e.target.value }))}
            >
              {SERVICE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </label>
        </div>

        <label className="rv-label">
          Project details *
          <textarea
            className="rv-textarea"
            value={form.message}
            onChange={(e) => setForm((p) => ({ ...p, message: e.target.value }))}
            required
            rows={4}
            placeholder="Cities you serve, competitors, current rankings, WordPress URL…"
          />
        </label>

        {status.type === 'error' ? (
          <div className="rv-status error" role="alert">{status.message}</div>
        ) : null}

        <div className="rv-contact-actions">
          <button type="submit" className="btn btn-primary" disabled={!canSubmit || loading}>
            {loading ? (
              <>
                <Loader2 size={16} className="rv-spin-icon" /> Sending…
              </>
            ) : (
              'Send request'
            )}
          </button>
          <p className="rv-contact-privacy">
            Stays on this page. We’ll only use your details to reply about ZeOrbit.
          </p>
        </div>
      </form>
    </div>
  )
}
