import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { X } from 'lucide-react'

const STORAGE_KEY = 'zo_lead_captured'

export function hasStoredLead() {
  try {
    return Boolean(localStorage.getItem(STORAGE_KEY))
  } catch {
    return false
  }
}

function isIntentLink(anchor) {
  if (!anchor || anchor.tagName !== 'A') return false
  const href = (anchor.getAttribute('href') || '').toLowerCase()
  const text = (anchor.textContent || '').toLowerCase()
  if (anchor.target === '_blank' && (href.startsWith('http') && !href.includes('127.0.0.1') && !href.includes('zeorbit'))) {
    return false
  }
  if (href.startsWith('tel:') || href.startsWith('mailto:')) return false
  return (
    href.includes('/contact') ||
    href.includes('#contact') ||
    text.includes('free quote') ||
    text.includes("let's talk") ||
    text.includes('lets talk') ||
    text.includes('start with master')
  )
}

async function postIntentLead(fields) {
  const apiBase = (import.meta.env.VITE_API_URL || '/api').trim().replace(/\/$/, '')
  const res = await fetch(`${apiBase}/leads/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source: 'intent',
      name: fields.name.trim(),
      contact_name: fields.name.trim(),
      email: fields.email.trim(),
      phone: fields.phone.trim(),
      service: 'Site click',
      message: `Clicked from ${typeof window !== 'undefined' ? window.location.pathname : ''}`,
      page_url: typeof window !== 'undefined' ? window.location.href : '',
      website_url: '',
    }),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(typeof data.detail === 'string' ? data.detail : 'Could not save your details')
  }
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      name: fields.name.trim(),
      email: fields.email.trim(),
      phone: fields.phone.trim(),
      at: Date.now(),
    }))
  } catch { /* ignore */ }
  return data
}

export default function IdentifyGate() {
  const location = useLocation()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [nextHref, setNextHref] = useState('')
  const [form, setForm] = useState({ name: '', email: '', phone: '' })
  const [status, setStatus] = useState('')
  const [saving, setSaving] = useState(false)
  const [stripeOn, setStripeOn] = useState(false)

  useEffect(() => {
    const apiBase = (import.meta.env.VITE_API_URL || '/api').trim().replace(/\/$/, '')
    fetch(`${apiBase}/leads/stripe-status`).then((r) => r.json()).then((d) => setStripeOn(Boolean(d.configured))).catch(() => {})
    const onClick = (event) => {
      if (hasStoredLead()) return
      const anchor = event.target?.closest?.('a')
      if (!isIntentLink(anchor)) return
      event.preventDefault()
      event.stopPropagation()
      setNextHref(anchor.getAttribute('href') || '/contact#contact')
      setOpen(true)
    }
    document.addEventListener('click', onClick, true)
    return () => document.removeEventListener('click', onClick, true)
  }, [])

  function goNext(href) {
    setOpen(false)
    const target = href || nextHref || '/contact#contact'
    if (target.startsWith('http')) {
      window.location.href = target
      return
    }
    navigate(target)
  }

  async function onSubmit(e) {
    e.preventDefault()
    setStatus('')
    setSaving(true)
    try {
      await postIntentLead(form)
      goNext(nextHref)
    } catch (err) {
      setStatus(err.message || 'Could not save')
    } finally {
      setSaving(false)
    }
  }

  if (!open) return null

  return (
    <div className="zo-identify-overlay" role="dialog" aria-modal="true" aria-labelledby="zo-identify-title">
      <div className="zo-identify-card">
        <button type="button" className="zo-identify-close" aria-label="Close" onClick={() => setOpen(false)}>
          <X size={18} />
        </button>
        <p className="zo-identify-kicker">{location.pathname === '/' ? 'Home' : location.pathname}</p>
        <h2 id="zo-identify-title">How can we reach you?</h2>
        <p>
          A page visit does not include your email or phone. Leave <strong>one</strong> of these so we can follow up on this click.
        </p>
        <form onSubmit={onSubmit}>
          <input
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            placeholder="Name"
            autoComplete="name"
          />
          <input
            type="email"
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
            placeholder="Email"
            autoComplete="email"
          />
          <input
            type="tel"
            value={form.phone}
            onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
            placeholder="U.S. phone"
            autoComplete="tel"
          />
          {status ? <p className="zo-identify-status">{status}</p> : null}
          <button type="submit" disabled={saving}>{saving ? 'Saving…' : 'Continue'}</button>
          {stripeOn ? (
            <button
              type="button"
              className="zo-identify-stripe"
              disabled={saving}
              onClick={async () => {
                setSaving(true)
                setStatus('')
                try {
                  const apiBase = (import.meta.env.VITE_API_URL || '/api').trim().replace(/\/$/, '')
                  const res = await fetch(`${apiBase}/leads/stripe/checkout`, { method: 'POST' })
                  const data = await res.json().catch(() => ({}))
                  if (!res.ok || !data.url) throw new Error(data.detail || 'Stripe is not ready')
                  window.location.href = data.url
                } catch (err) {
                  setStatus(err.message || 'Stripe checkout failed')
                  setSaving(false)
                }
              }}
            >
              Continue with Stripe
            </button>
          ) : (
            <p className="zo-identify-hint">
              Stripe only captures email after they type it on Stripe Checkout — same as this form. It does not read Gmail from a site visit.
            </p>
          )}
        </form>
      </div>
    </div>
  )
}
