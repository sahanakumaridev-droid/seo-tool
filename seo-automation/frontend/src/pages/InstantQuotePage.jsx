import { useState } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle2, ArrowLeft, ArrowRight, Loader2 } from 'lucide-react'
import { createLead } from '../api'
import { QUOTE_STEPS } from '../data/leadEngine'
import Logo from '../components/Logo'

const inputCls =
  'w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50'
const optionCls = (active) =>
  `w-full text-left px-4 py-3 rounded-xl border text-sm transition-colors ${
    active
      ? 'bg-indigo-600/20 border-indigo-500/40 text-indigo-100'
      : 'bg-white/3 border-white/8 text-slate-300 hover:bg-white/5'
  }`

export default function InstantQuotePage() {
  const [step, setStep] = useState(0)
  const [service, setService] = useState('')
  const [budget, setBudget] = useState('')
  const [timeline, setTimeline] = useState('')
  const [contact, setContact] = useState({ name: '', email: '', phone: '', location: '' })
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState('')

  const steps = ['Service', 'Budget', 'Timeline', 'Contact']
  const canNext =
    (step === 0 && service) ||
    (step === 1 && budget) ||
    (step === 2 && timeline) ||
    (step === 3 && contact.name.trim() && (contact.email.trim() || contact.phone.trim()))

  const submit = async () => {
    if (!canNext) return
    setLoading(true)
    setError('')
    try {
      const serviceLabel = QUOTE_STEPS.services.find(s => s.id === service)?.label || service
      await createLead({
        source: 'instant-quote',
        name: contact.name.trim(),
        contact_name: contact.name.trim(),
        business_name: contact.name.trim(),
        email: contact.email.trim() || null,
        phone: contact.phone.trim() || null,
        location: contact.location.trim(),
        service: serviceLabel,
        budget,
        industry: 'Web / App',
        message: `Instant Quote · Timeline: ${timeline}`,
      })
      setDone(true)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Could not submit quote request')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)', color: 'var(--text-1)' }}>
      <div className="max-w-lg mx-auto px-4 py-10">
        <div className="flex items-center justify-between mb-8">
          <Logo size={28} />
          <Link to="/lead-engine" className="text-xs text-slate-500 hover:text-slate-300">
            Lead Engine
          </Link>
        </div>

        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">Get an Instant Quote</h1>
          <p className="text-sm text-slate-500 mt-1">
            Tell us what you need — we respond within 15 minutes during business hours.
          </p>
        </div>

        {/* Progress */}
        <div className="flex gap-1.5 mb-8">
          {steps.map((label, i) => (
            <div key={label} className="flex-1">
              <div className={`h-1 rounded-full ${i <= step ? 'bg-indigo-500' : 'bg-white/10'}`} />
              <div className={`text-[10px] mt-1.5 ${i === step ? 'text-indigo-300' : 'text-slate-600'}`}>{label}</div>
            </div>
          ))}
        </div>

        <div className="card p-5 sm:p-6">
          {done ? (
            <div className="text-center py-6 space-y-3">
              <CheckCircle2 size={40} className="mx-auto text-emerald-400" />
              <h2 className="text-lg font-semibold text-white">Request received</h2>
              <p className="text-sm text-slate-400">
                Our team will follow up shortly with next steps for your {QUOTE_STEPS.services.find(s => s.id === service)?.label || 'project'}.
              </p>
              <Link to="/" className="inline-block text-xs text-indigo-400 hover:underline mt-2">
                Back to ZeOrbit →
              </Link>
            </div>
          ) : (
            <>
              {step === 0 && (
                <div className="space-y-2">
                  <h2 className="text-sm font-semibold text-white mb-3">What do you need?</h2>
                  {QUOTE_STEPS.services.map(s => (
                    <button key={s.id} type="button" onClick={() => setService(s.id)} className={optionCls(service === s.id)}>
                      {s.label}
                    </button>
                  ))}
                </div>
              )}

              {step === 1 && (
                <div className="space-y-2">
                  <h2 className="text-sm font-semibold text-white mb-3">What's your approximate budget?</h2>
                  {QUOTE_STEPS.budgets.map(b => (
                    <button key={b} type="button" onClick={() => setBudget(b)} className={optionCls(budget === b)}>
                      {b}
                    </button>
                  ))}
                </div>
              )}

              {step === 2 && (
                <div className="space-y-2">
                  <h2 className="text-sm font-semibold text-white mb-3">When do you want to start?</h2>
                  {QUOTE_STEPS.timelines.map(t => (
                    <button key={t} type="button" onClick={() => setTimeline(t)} className={optionCls(timeline === t)}>
                      {t}
                    </button>
                  ))}
                </div>
              )}

              {step === 3 && (
                <div className="space-y-3">
                  <h2 className="text-sm font-semibold text-white mb-1">How can we reach you?</h2>
                  <p className="text-xs text-slate-500 mb-2">Name + email or phone required.</p>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Name</label>
                    <input className={inputCls} value={contact.name}
                      onChange={e => setContact(c => ({ ...c, name: e.target.value }))}
                      placeholder="Your name" autoComplete="name" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Email</label>
                    <input type="email" className={inputCls} value={contact.email}
                      onChange={e => setContact(c => ({ ...c, email: e.target.value }))}
                      placeholder="you@company.com" autoComplete="email" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Phone</label>
                    <input type="tel" className={inputCls} value={contact.phone}
                      onChange={e => setContact(c => ({ ...c, phone: e.target.value }))}
                      placeholder="+1 555-000-0000" autoComplete="tel" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Location</label>
                    <input className={inputCls} value={contact.location}
                      onChange={e => setContact(c => ({ ...c, location: e.target.value }))}
                      placeholder="San Diego, CA" autoComplete="address-level2" />
                  </div>
                </div>
              )}

              {error && <p className="text-xs text-red-400 mt-4">{error}</p>}

              <div className="flex gap-2 mt-6">
                {step > 0 && (
                  <button type="button" onClick={() => setStep(s => s - 1)}
                    className="flex-1 px-4 py-2.5 rounded-lg text-sm text-slate-400 border border-white/8 hover:bg-white/4 inline-flex items-center justify-center gap-1.5">
                    <ArrowLeft size={14} /> Back
                  </button>
                )}
                {step < 3 ? (
                  <button type="button" disabled={!canNext} onClick={() => setStep(s => s + 1)}
                    className="flex-1 btn-primary px-4 py-2.5 rounded-lg text-sm text-white font-semibold disabled:opacity-40 inline-flex items-center justify-center gap-1.5">
                    Next <ArrowRight size={14} />
                  </button>
                ) : (
                  <button type="button" disabled={!canNext || loading} onClick={submit}
                    className="flex-1 btn-primary px-4 py-2.5 rounded-lg text-sm text-white font-semibold disabled:opacity-40 inline-flex items-center justify-center gap-1.5">
                    {loading ? <Loader2 size={14} className="animate-spin" /> : null}
                    {loading ? 'Submitting…' : 'Get my quote'}
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
