import { useEffect, useMemo, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { RefreshCw } from 'lucide-react'
import AiPlatformLinks from '../AiPlatformLinks'

const SERVICE_OPTIONS = [
  { value: 'Website Design & Development', label: 'Website (WordPress / Shopify / Wix / Squarespace)' },
  { value: 'Mobile App Development', label: 'Mobile App (iOS / Android)' },
  { value: 'UX & UI Design', label: 'UX & UI Design' },
  { value: 'SEO / AEO / GEO', label: 'SEO / GEO / PPC / Google Ads' },
  { value: 'Ecommerce Optimization', label: 'Ecommerce' },
  { value: 'Custom Software Development', label: 'Custom Software' },
  { value: 'AI Solutions & AI Agents', label: 'AI (when needed)' },
  { value: 'Business Automation', label: 'Automation' },
]

const CONTACT_PAGE_SERVICES = [
  { value: '', label: 'Service Need' },
  { value: 'Master Care', label: 'Master Care' },
  { value: 'Web Designing', label: 'Web Designing' },
  { value: 'Digital Advertising', label: 'Digital Advertising' },
  { value: 'SEO', label: 'SEO' },
  { value: 'Logo Designs', label: 'Logo Designs' },
  { value: 'Content Marketing', label: 'Content Marketing' },
  { value: 'Mobile App Development', label: 'Mobile Apps' },
  { value: 'Custom Software Development', label: 'Custom Software' },
]

const BUDGET_OPTIONS = [
  { value: '', label: 'Select budget (optional)' },
  { value: '<$2k', label: 'Under $2k' },
  { value: '$2k-$5k', label: '$2k–$5k' },
  { value: '$5k-$15k', label: '$5k–$15k' },
  { value: '$15k+', label: '$15k+' },
]

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())
}

function digitsOnly(value) {
  return String(value || '').replace(/\D/g, '')
}

function isValidUsPhone(value) {
  let digits = digitsOnly(value)
  if (digits.length === 11 && digits.startsWith('1')) digits = digits.slice(1)
  if (digits.length !== 10) return false
  if ('01'.includes(digits[0]) || '01'.includes(digits[3])) return false
  if (/^(\d)\1{9}$/.test(digits)) return false
  return true
}

function formSourceFromPath(pathname) {
  const path = (pathname || '/').replace(/\/+$/, '') || '/'
  if (path === '/') return 'home'
  return path.replace(/^\//, '').slice(0, 40) || 'home'
}

export default function ContactForm({
  hideIntro = false,
  submitLabel = 'Send request',
  variant = 'default',
}) {
  const isContactPage = variant === 'contactPage'
  const serviceOptions = isContactPage ? CONTACT_PAGE_SERVICES : SERVICE_OPTIONS
  const location = useLocation()

  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    budget: '',
    service: isContactPage ? '' : (SERVICE_OPTIONS[0]?.value ?? ''),
    message: '',
    website_url: '',
    captcha_answer: '',
  })

  const [captcha, setCaptcha] = useState({ id: '', image: '' })
  const [startedAt] = useState(() => Date.now())
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState({ type: 'idle', message: '' })
  const [touched, setTouched] = useState({})

  useEffect(() => {
    const wanted = new URLSearchParams(location.search).get('service')
    if (!wanted) return
    const options = isContactPage ? CONTACT_PAGE_SERVICES : SERVICE_OPTIONS
    const match = options.find(
      (opt) => opt.value && opt.value.toLowerCase() === wanted.trim().toLowerCase(),
    )
    if (match) setForm((prev) => ({ ...prev, service: match.value }))
  }, [location.search, isContactPage])

  const payload = useMemo(() => {
    const trimmed = {
      name: form.name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      business_name: form.company.trim(),
      service: form.service || 'Web Designing',
      budget: form.budget,
      message: form.message.trim(),
    }

    return {
      source: formSourceFromPath(location.pathname),
      page_url: typeof window !== 'undefined' ? window.location.href : '',
      contact_name: trimmed.name,
      captcha_id: captcha.id,
      captcha_answer: form.captcha_answer.trim(),
      website_url: form.website_url,
      started_at: startedAt,
      ...trimmed,
    }
  }, [form, location.pathname, captcha.id, startedAt])

  const errors = useMemo(() => {
    const next = {}
    if (touched.name && !payload.name) next.name = 'Name is required'
    if (touched.email) {
      if (!payload.email) next.email = 'Email is required'
      else if (!isValidEmail(payload.email)) next.email = 'Enter a valid email'
    }
    if (touched.phone) {
      if (!payload.phone) next.phone = 'U.S. phone number is required'
      else if (!isValidUsPhone(payload.phone)) next.phone = 'Enter a valid U.S. phone number'
    }
    if (touched.message && !payload.message) next.message = 'Tell us a bit about the project'
    if (touched.captcha_answer && !payload.captcha_answer) next.captcha_answer = 'Enter the code from the image'
    return next
  }, [payload, touched])

  const canSubmit = useMemo(() => {
    if (!payload.name) return false
    if (!payload.email || !isValidEmail(payload.email)) return false
    if (!payload.phone || !isValidUsPhone(payload.phone)) return false
    if (!payload.message) return false
    if (!payload.captcha_id || !payload.captcha_answer) return false
    return true
  }, [payload])

  function markTouched(field) {
    setTouched((p) => ({ ...p, [field]: true }))
  }

  async function loadCaptcha() {
    const apiBase = (import.meta.env.VITE_API_URL || '/api').trim().replace(/\/$/, '')
    try {
      const res = await fetch(`${apiBase}/leads/captcha`)
      if (!res.ok) throw new Error('captcha')
      const data = await res.json()
      setCaptcha({ id: data.id || '', image: data.image || '' })
      setForm((p) => ({ ...p, captcha_answer: '' }))
    } catch {
      setCaptcha({ id: '', image: '' })
    }
  }

  useEffect(() => {
    loadCaptcha()
  }, [])

  async function onSubmit(e) {
    e.preventDefault()
    setTouched({ name: true, email: true, phone: true, message: true, captcha_answer: true })
    if (!canSubmit || loading) return

    setLoading(true)
    setStatus({ type: 'idle', message: '' })
    try {
      // VITE_API_URL is the API root (`/api` in production). Do not append `/api` again.
      const apiBase = (import.meta.env.VITE_API_URL || '/api').trim().replace(/\/$/, '')
      const endpoint = `${apiBase}/leads/`

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        let detail = `Request failed (${res.status})`
        try {
          const data = await res.json()
          if (typeof data?.detail === 'string') detail = data.detail
        } catch {
          const text = await res.text().catch(() => '')
          if (text) detail = text
        }
        throw new Error(detail)
      }

      await res.json().catch(() => ({}))
      setStatus({ type: 'success', message: "Thanks — we'll reach out within one business day." })
      setTouched({})
      setForm({
        name: '',
        email: '',
        phone: '',
        company: '',
        budget: '',
        service: isContactPage ? '' : (SERVICE_OPTIONS[0]?.value ?? ''),
        message: '',
        website_url: '',
        captcha_answer: '',
      })
      loadCaptcha()
    } catch (err) {
      setStatus({
        type: 'error',
        message: err?.message ? `Could not submit: ${err.message}` : 'Could not submit. Please try again.',
      })
      loadCaptcha()
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="zo-ai-above-form">
        <AiPlatformLinks />
      </div>
    <div
      className={`rv-contact-card${isContactPage ? ' is-contact-page' : ''}`}
      role="region"
      aria-label="Contact ZeOrbit"
    >
      {hideIntro ? null : (
        <div className="rv-contact-head">
          <p className="rv-contact-eyebrow">Talk to ZeOrbit</p>
          <h3>Tell us what you need</h3>
          <p className="rv-contact-sub">
            Website, mobile app, UX/UI, SEO, ads, or software — we&apos;ll route your request to the right team.
          </p>
        </div>
      )}

      <form className="rv-contact-form" onSubmit={onSubmit} noValidate>
        <div className={`rv-form-grid${isContactPage ? ' is-contact-page' : ''}`}>
          <label className="rv-label">
            <span className="rv-label-row">
              {isContactPage ? 'Full Name' : 'Name'} <em className="rv-req">*</em>
            </span>
            <input
              className={`rv-input${errors.name ? ' is-invalid' : ''}`}
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              onBlur={() => markTouched('name')}
              autoComplete="name"
              placeholder={isContactPage ? 'Full Name' : 'Your full name'}
              required
              aria-invalid={Boolean(errors.name)}
            />
            {errors.name ? <span className="rv-field-error">{errors.name}</span> : null}
          </label>

          <label className="rv-label">
            <span className="rv-label-row">
              {isContactPage ? 'Your Email' : 'Email'} <em className="rv-req">*</em>
            </span>
            <input
              className={`rv-input${errors.email ? ' is-invalid' : ''}`}
              value={form.email}
              onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
              onBlur={() => markTouched('email')}
              autoComplete="email"
              type="email"
              placeholder={isContactPage ? 'Your Email' : 'you@company.com'}
              required
              aria-invalid={Boolean(errors.email)}
            />
            {errors.email ? <span className="rv-field-error">{errors.email}</span> : null}
          </label>

          <label className="rv-label">
            <span className="rv-label-row">
              {isContactPage ? 'Your Number' : 'Phone'} <em className="rv-req">*</em>
            </span>
            <input
              className={`rv-input${errors.phone ? ' is-invalid' : ''}`}
              value={form.phone}
              onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))}
              onBlur={() => markTouched('phone')}
              autoComplete="tel"
              inputMode="tel"
              placeholder={isContactPage ? 'Your Number' : '(619) 555-0100'}
              required
              aria-invalid={Boolean(errors.phone)}
            />
            {errors.phone ? <span className="rv-field-error">{errors.phone}</span> : null}
          </label>

          {isContactPage ? (
            <label className="rv-label">
              <span className="rv-label-row">Service Need</span>
              <div className="rv-select-wrap">
                <select
                  className="rv-input rv-select"
                  value={form.service}
                  onChange={(e) => setForm((p) => ({ ...p, service: e.target.value }))}
                >
                  {serviceOptions.map((o) => (
                    <option key={o.value || 'empty'} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>
            </label>
          ) : (
            <>
              <label className="rv-label">
                <span className="rv-label-row">
                  Company <span className="rv-opt">optional</span>
                </span>
                <input
                  className="rv-input"
                  value={form.company}
                  onChange={(e) => setForm((p) => ({ ...p, company: e.target.value }))}
                  autoComplete="organization"
                  placeholder="Company or brand name"
                />
              </label>

              <label className="rv-label">
                <span className="rv-label-row">
                  Budget range <span className="rv-opt">optional</span>
                </span>
                <div className="rv-select-wrap">
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
                </div>
              </label>

              <label className="rv-label">
                <span className="rv-label-row">What do you need?</span>
                <div className="rv-select-wrap">
                  <select
                    className="rv-input rv-select"
                    value={form.service}
                    onChange={(e) => setForm((p) => ({ ...p, service: e.target.value }))}
                  >
                    {serviceOptions.map((o) => (
                      <option key={o.value} value={o.value}>
                        {o.label}
                      </option>
                    ))}
                  </select>
                </div>
              </label>
            </>
          )}
        </div>

        <label className="rv-label rv-label-full">
          <span className="rv-label-row">
            {isContactPage ? 'Additional Message' : 'Project description'} <em className="rv-req">*</em>
          </span>
          <textarea
            className={`rv-textarea${errors.message ? ' is-invalid' : ''}`}
            value={form.message}
            onChange={(e) => setForm((p) => ({ ...p, message: e.target.value }))}
            onBlur={() => markTouched('message')}
            required
            rows={isContactPage ? 4 : 5}
            placeholder={
              isContactPage
                ? 'Additional Message'
                : 'Goals, timeline, current site/app, and anything else we should know…'
            }
            aria-invalid={Boolean(errors.message)}
          />
          {errors.message ? <span className="rv-field-error">{errors.message}</span> : null}
        </label>

        <div className="rv-hp" aria-hidden="true">
          <label>
            Website
            <input
              tabIndex={-1}
              autoComplete="off"
              value={form.website_url}
              onChange={(e) => setForm((p) => ({ ...p, website_url: e.target.value }))}
            />
          </label>
        </div>

        <div className="rv-captcha">
          <div className="rv-captcha-image">
            {captcha.image ? (
              <img src={captcha.image} alt="Captcha code" width={188} height={58} />
            ) : (
              <span>Loading code…</span>
            )}
            <button type="button" className="rv-captcha-refresh" onClick={loadCaptcha} aria-label="Refresh captcha">
              <RefreshCw size={16} strokeWidth={2.3} />
            </button>
          </div>
          <label className="rv-label rv-captcha-field">
            <span className="rv-label-row">
              Type the code <em className="rv-req">*</em>
            </span>
            <input
              className={`rv-input${errors.captcha_answer ? ' is-invalid' : ''}`}
              value={form.captcha_answer}
              onChange={(e) => setForm((p) => ({ ...p, captcha_answer: e.target.value.toUpperCase() }))}
              onBlur={() => markTouched('captcha_answer')}
              autoComplete="off"
              autoCapitalize="characters"
              spellCheck={false}
              inputMode="text"
              maxLength={8}
              placeholder="5-character code"
              required
              aria-invalid={Boolean(errors.captcha_answer)}
            />
            {errors.captcha_answer ? <span className="rv-field-error">{errors.captcha_answer}</span> : null}
          </label>
        </div>

        {status.type !== 'idle' ? (
          <div
            className={`rv-status ${status.type === 'success' ? 'success' : 'error'}`}
            role={status.type === 'success' ? 'status' : 'alert'}
          >
            {status.message}
          </div>
        ) : null}

        <div className="rv-contact-actions">
          <button type="submit" className="rv-submit-btn" disabled={!canSubmit || loading}>
            {loading ? 'Sending…' : submitLabel}
          </button>
          <p className="rv-contact-privacy">
            By submitting, you agree to be contacted about this request. No spam.
          </p>
        </div>
      </form>
    </div>
    </>
  )
}
