import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Globe2, TrendingUp, Users, MapPin, Search as SearchIcon, Wrench, Sparkles,
} from 'lucide-react'
import StepShell from '../components/onboarding/StepShell'
import { runSiteAudit } from '../api'

const COUNTRIES = ['United States', 'Canada', 'United Kingdom', 'Australia']

const BUSINESS_TYPES = [
  'Local Service Business', 'E-commerce', 'SaaS / Software', 'Marketing Agency',
  'Franchise / Multi-location', 'Other',
]

const GOALS = [
  { key: 'traffic',     label: 'Increase Google traffic',      icon: TrendingUp },
  { key: 'leads',        label: 'Generate leads',                icon: Users },
  { key: 'local',        label: 'Improve local rankings',        icon: MapPin },
  { key: 'competitors',  label: 'Track competitors',             icon: SearchIcon },
  { key: 'technical',    label: 'Improve technical SEO',          icon: Wrench },
  { key: 'ai',           label: 'Improve AI visibility',          icon: Sparkles },
]

function FieldLabel({ children }) {
  return <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 8 }}>{children}</label>
}

export default function OnboardingPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [analyzing, setAnalyzing] = useState(false)
  const [form, setForm] = useState({
    website: '', business_name: '', country: 'United States', city: '', business_type: '', goal: '',
  })

  const totalSteps = 5
  const set = (patch) => setForm(f => ({ ...f, ...patch }))

  const finish = async () => {
    setAnalyzing(true)
    let audit = null
    try {
      const res = await runSiteAudit(form.website)
      audit = res.data
    } catch {
      audit = null
    }

    const saved = JSON.parse(localStorage.getItem('seo_project') || '{}')
    const next = {
      ...saved,
      website: form.website,
      business_name: form.business_name,
      country: form.country,
      business_type: form.business_type,
      base_location: form.city,
      goal: form.goal,
      audit,
    }
    localStorage.setItem('seo_project', JSON.stringify(next))
    window.dispatchEvent(new Event('seo_project_updated'))
    navigate('/content')
  }

  if (step === 0) {
    return (
      <StepShell step={0} total={totalSteps} title="What's your website?" subtitle="We'll use this to run your first SEO analysis."
        onNext={() => setStep(1)} nextDisabled={!form.website.trim()}>
        <FieldLabel>Website URL</FieldLabel>
        <div style={{ position: 'relative' }}>
          <Globe2 size={16} style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-4)' }} />
          <input
            type="text" value={form.website} onChange={e => set({ website: e.target.value })}
            placeholder="example.com" autoFocus
            style={{ width: '100%', padding: '11px 14px 11px 38px' }}
          />
        </div>
      </StepShell>
    )
  }

  if (step === 1) {
    return (
      <StepShell step={1} total={totalSteps} title="What's your business name?" subtitle="This appears on your reports and dashboard."
        onBack={() => setStep(0)} onNext={() => setStep(2)} nextDisabled={!form.business_name.trim()}>
        <FieldLabel>Business name</FieldLabel>
        <input
          type="text" value={form.business_name} onChange={e => set({ business_name: e.target.value })}
          placeholder="Acme Plumbing Co." autoFocus
          style={{ width: '100%', padding: '11px 14px' }}
        />
      </StepShell>
    )
  }

  if (step === 2) {
    return (
      <StepShell step={2} total={totalSteps} title="Where's your business based?" subtitle="Enter your city and state so we can accurately baseline local search data and nearby locations."
        onBack={() => setStep(1)} onNext={() => setStep(3)} nextDisabled={!form.city.trim()}>
        <FieldLabel>City, State</FieldLabel>
        <input
          type="text" value={form.city} onChange={e => set({ city: e.target.value })}
          placeholder="e.g. San Diego, CA" autoFocus
          style={{ width: '100%', padding: '11px 14px', marginBottom: 16 }}
        />
        <FieldLabel>Country</FieldLabel>
        <select value={form.country} onChange={e => set({ country: e.target.value })} style={{ width: '100%', padding: '11px 14px' }}>
          {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </StepShell>
    )
  }

  if (step === 3) {
    return (
      <StepShell step={3} total={totalSteps} title="What type of business is this?" subtitle="This helps us tailor recommendations."
        onBack={() => setStep(2)} onNext={() => setStep(4)} nextDisabled={!form.business_type}>
        <FieldLabel>Business type</FieldLabel>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {BUSINESS_TYPES.map(bt => (
            <button key={bt} type="button" onClick={() => set({ business_type: bt })}
              className="btn"
              style={{
                justifyContent: 'flex-start', width: '100%', padding: '11px 14px',
                background: form.business_type === bt ? 'var(--brand-soft)' : 'var(--bg-raised)',
                border: `1px solid ${form.business_type === bt ? 'var(--brand)' : 'var(--border-bright)'}`,
                color: form.business_type === bt ? 'var(--brand-dark)' : 'var(--text-2)',
              }}>
              {bt}
            </button>
          ))}
        </div>
      </StepShell>
    )
  }

  // Step 4 — goal + run analysis
  return (
    <StepShell step={4} total={totalSteps} title="What's your main SEO goal?" subtitle="We'll prioritize your dashboard around this."
      onBack={() => setStep(3)} onNext={finish} nextDisabled={!form.goal} loading={analyzing}
      nextLabel="Run Initial SEO Analysis">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        {GOALS.map(g => (
          <button key={g.key} type="button" onClick={() => set({ goal: g.key })}
            className="btn"
            style={{
              flexDirection: 'column', alignItems: 'flex-start', gap: 8, height: 'auto', padding: '14px',
              background: form.goal === g.key ? 'var(--brand-soft)' : 'var(--bg-raised)',
              border: `1px solid ${form.goal === g.key ? 'var(--brand)' : 'var(--border-bright)'}`,
            }}>
            <g.icon size={18} style={{ color: form.goal === g.key ? 'var(--brand)' : 'var(--text-3)' }} />
            <span style={{ fontSize: 12.5, fontWeight: 600, color: form.goal === g.key ? 'var(--brand-dark)' : 'var(--text-2)', textAlign: 'left' }}>{g.label}</span>
          </button>
        ))}
      </div>
    </StepShell>
  )
}
