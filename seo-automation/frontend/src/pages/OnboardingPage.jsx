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
      <StepShell
        step={0} total={totalSteps}
        title="What's your website?" subtitle="We'll use this to run your first SEO analysis."
        onNext={() => setStep(1)} nextDisabled={!form.website.trim()}>
        <label className="ob-label" htmlFor="ob-website">Website URL</label>
        <div className="ob-field">
          <Globe2 size={16} className="ob-field-icon" />
          <input
            id="ob-website"
            className="ob-input-icon"
            type="text" value={form.website} onChange={e => set({ website: e.target.value })}
            placeholder="example.com" autoFocus
          />
        </div>
      </StepShell>
    )
  }

  if (step === 1) {
    return (
      <StepShell
        step={1} total={totalSteps}
        title="What's your business name?" subtitle="This appears on your reports and dashboard."
        onBack={() => setStep(0)} onSelectStep={setStep} onNext={() => setStep(2)} nextDisabled={!form.business_name.trim()}>
        <label className="ob-label" htmlFor="ob-business">Business name</label>
        <input
          id="ob-business"
          type="text" value={form.business_name} onChange={e => set({ business_name: e.target.value })}
          placeholder="Acme Plumbing Co." autoFocus
        />
      </StepShell>
    )
  }

  if (step === 2) {
    return (
      <StepShell
        step={2} total={totalSteps}
        title="Where's your business based?" subtitle="We'll use this to baseline local search data around you."
        onBack={() => setStep(1)} onSelectStep={setStep} onNext={() => setStep(3)} nextDisabled={!form.city.trim()}>
        <label className="ob-label" htmlFor="ob-city">City, State</label>
        <div className="ob-field">
          <input
            id="ob-city"
            type="text" value={form.city} onChange={e => set({ city: e.target.value })}
            placeholder="e.g. San Diego, CA" autoFocus
          />
        </div>
        <label className="ob-label" htmlFor="ob-country">Country</label>
        <select id="ob-country" value={form.country} onChange={e => set({ country: e.target.value })}>
          {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </StepShell>
    )
  }

  if (step === 3) {
    return (
      <StepShell
        step={3} total={totalSteps}
        title="What type of business is this?" subtitle="This helps us tailor recommendations."
        onBack={() => setStep(2)} onSelectStep={setStep} onNext={() => setStep(4)} nextDisabled={!form.business_type}>
        <p className="ob-label">Business type</p>
        <div className="ob-stack">
          {BUSINESS_TYPES.map(bt => (
            <button
              key={bt}
              type="button"
              onClick={() => set({ business_type: bt })}
              className={`btn ob-choice${form.business_type === bt ? ' is-selected' : ''}`}
            >
              {bt}
            </button>
          ))}
        </div>
      </StepShell>
    )
  }

  return (
    <StepShell
      step={4} total={totalSteps}
      title="What's your main SEO goal?" subtitle="We'll prioritize your dashboard around this."
      onBack={() => setStep(3)} onSelectStep={setStep} onNext={finish} nextDisabled={!form.goal} loading={analyzing}
      nextLabel="Run analysis">
      <div className="ob-choice-grid">
        {GOALS.map(g => (
          <button
            key={g.key}
            type="button"
            onClick={() => set({ goal: g.key })}
            className={`btn ob-choice${form.goal === g.key ? ' is-selected' : ''}`}
          >
            <g.icon size={18} />
            <span className="ob-choice-copy">{g.label}</span>
          </button>
        ))}
      </div>
    </StepShell>
  )
}
