import { useMemo, useState } from 'react'

const SERVICE_OPTIONS = [
  { value: 'Website Design & Development', label: 'Website' },
  { value: 'Mobile App Development', label: 'Mobile App' },
  { value: 'SEO / AEO / GEO', label: 'SEO / AEO / GEO' },
  { value: 'Generative AI Integration', label: 'AI Integration' },
  { value: 'Custom Software Development', label: 'Custom Software' },
  { value: 'Workflow Automation', label: 'Automation' },
  { value: 'Web Data Processing', label: 'Data Processing' },
  { value: 'Ecommerce Optimization', label: 'Ecommerce' },
]

const BUDGET_OPTIONS = [
  { value: '', label: 'Select budget (optional)' },
  { value: '<$5k', label: 'Under $5k' },
  { value: '$5k-$15k', label: '$5k-$15k' },
  { value: '$15k-$50k', label: '$15k-$50k' },
  { value: '$50k+', label: '$50k+' },
]

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())
}

export default function ContactForm() {
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    budget: '',
    service: SERVICE_OPTIONS[0]?.value ?? '',
    message: '',
  })

  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState({ type: 'idle', message: '' })

  const payload = useMemo(() => {
    const trimmed = {
      name: form.name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      business_name: form.company.trim(),
      service: form.service,
      budget: form.budget,
      message: form.message.trim(),
    }

    return {
      source: 'landing_page',
      ...trimmed,
    }
  }, [form])

  const canSubmit = useMemo(() => {
    if (!payload.name) return false
    if (!payload.email || !isValidEmail(payload.email)) return false
    if (!payload.business_name) return false
    if (!payload.message) return false
    return true
  }, [payload])

  async function onSubmit(e) {
    e.preventDefault()
    if (!canSubmit || loading) return

    setLoading(true)
    setStatus({ type: 'idle', message: '' })
    try {
      const apiBase = (import.meta.env.VITE_API_URL || '').trim()
      const endpoint = apiBase ? `${apiBase.replace(/\/$/, '')}/api/leads/` : '/api/leads/'

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        const text = await res.text().catch(() => '')
        throw new Error(text || `Request failed with ${res.status}`)
      }

      await res.json().catch(() => ({}))
      setStatus({ type: 'success', message: "Thanks — we’ll reach out shortly." })
      setForm({
        name: '',
        email: '',
        phone: '',
        company: '',
        budget: '',
        service: SERVICE_OPTIONS[0]?.value ?? '',
        message: '',
      })
    } catch (err) {
      setStatus({
        type: 'error',
        message: err?.message ? `Could not submit: ${err.message}` : 'Could not submit. Please try again.',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rv-contact-card" role="region" aria-label="Contact ZeOrbit">
      <div className="rv-contact-head">
        <p className="rv-contact-eyebrow">Talk to ZeOrbit</p>
        <h3>Tell us what you need</h3>
        <p className="rv-contact-sub">
          We’ll route your request to the right team and follow up with next steps.
        </p>
      </div>

      <form className="rv-contact-form" onSubmit={onSubmit}>
        <div className="rv-form-grid">
          <label className="rv-label">
            Name
            <input
              className="rv-input"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              autoComplete="name"
              required
            />
          </label>

          <label className="rv-label">
            Email
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
            Phone (optional)
            <input
              className="rv-input"
              value={form.phone}
              onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))}
              autoComplete="tel"
              inputMode="tel"
            />
          </label>

          <label className="rv-label">
            Company
            <input
              className="rv-input"
              value={form.company}
              onChange={(e) => setForm((p) => ({ ...p, company: e.target.value }))}
              autoComplete="organization"
              required
            />
          </label>

          <label className="rv-label">
            Budget range (optional)
            <select
              className="rv-input rv-select"
              value={form.budget}
              onChange={(e) => setForm((p) => ({ ...p, budget: e.target.value }))}
            >
              {BUDGET_OPTIONS.map((o) => (
                <option key={o.value || 'empty'} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>

          <label className="rv-label">
            What do you need?
            <select
              className="rv-input rv-select"
              value={form.service}
              onChange={(e) => setForm((p) => ({ ...p, service: e.target.value }))}
            >
              {SERVICE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <label className="rv-label">
          Project description
          <textarea
            className="rv-textarea"
            value={form.message}
            onChange={(e) => setForm((p) => ({ ...p, message: e.target.value }))}
            required
            rows={5}
          />
        </label>

        {status.type !== 'idle' ? (
          <div
            className={`rv-status ${status.type === 'success' ? 'success' : 'error'}`}
            role={status.type === 'success' ? 'status' : 'alert'}
          >
            {status.message}
          </div>
        ) : null}

        <div className="rv-contact-actions">
          <button type="submit" className="btn btn-primary" disabled={!canSubmit || loading}>
            {loading ? 'Sending…' : 'Send Request'}
          </button>
          <p className="rv-contact-privacy">
            By submitting, you agree to be contacted about your request. No spam.
          </p>
        </div>
      </form>
    </div>
  )
}

