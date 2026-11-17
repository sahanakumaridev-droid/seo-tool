import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Globe2, TrendingUp, Users, MapPin, Search as SearchIcon, Wrench, Sparkles,
} from 'lucide-react'
import StepShell from '../components/onboarding/StepShell'
import { runSiteAudit } from '../api'

const COUNTRIES = ['United States']

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

const INTRO = [
  {
    kicker: 'United States',
    title: 'Built for businesses across the U.S.',
    body: 'Cities, counties, and local areas stay tied to the place you actually serve.',
    scene: 'map',
  },
  {
    kicker: 'Search',
    title: 'Show up where customers look.',
    body: 'Pages, local results, and the next step are planned before anything is published.',
    scene: 'search',
  },
  {
    kicker: 'Launch',
    title: 'A short brief becomes a live page.',
    body: 'Tell us the goal. The layout, the copy, and the call to action follow.',
    scene: 'page',
  },
]

function IntroFlow({ onDone, onSkip }) {
  const [index, setIndex] = useState(0)
  const slide = INTRO[index]
  const last = index === INTRO.length - 1
  return (
    <div className="ob-intro">
      <div className={`ob-scene ob-scene-${slide.scene}`} key={slide.scene} aria-hidden="true">
        {slide.scene === 'map' ? (
          <>
            <span className="ob-pin ob-pin-a">San Diego</span>
            <span className="ob-pin ob-pin-b">Los Angeles</span>
            <span className="ob-pin ob-pin-c">Austin</span>
          </>
        ) : null}
        {slide.scene === 'search' ? (
          <div className="ob-search">
            <span />
            <i /><i /><i />
          </div>
        ) : null}
        {slide.scene === 'page' ? (
          <div className="ob-page">
            <b />
            <em /><em /><em />
          </div>
        ) : null}
      </div>
      <div className="ob-intro-copy">
        <p>{slide.kicker}</p>
        <h1>{slide.title}</h1>
        <span>{slide.body}</span>
        <div className="ob-intro-dots" role="tablist" aria-label="Intro">
          {INTRO.map((item, i) => (
            <button key={item.kicker} type="button" aria-label={item.kicker} className={i === index ? 'is-on' : ''} onClick={() => setIndex(i)} />
          ))}
        </div>
        <div className="ob-intro-actions">
          <button type="button" className="ob-intro-next" onClick={() => (last ? onDone() : setIndex(index + 1))}>
            {last ? 'Set up my account' : 'Continue'}
          </button>
          <button type="button" className="ob-intro-skip" onClick={onSkip}>Skip</button>
        </div>
      </div>
      <style>{`
        .ob-intro { min-height: 100vh; display: grid; grid-template-columns: 1.1fr 0.9fr; background: #f6f7f9; color: #142033; }
        .ob-scene { position: relative; margin: 28px; border-radius: 28px; background: #1c305c; overflow: hidden; }
        .ob-pin, .ob-search, .ob-page { position: absolute; }
        .ob-pin { color: #fff; font-size: 13px; font-weight: 700; padding: 8px 12px; border-radius: 999px; background: rgba(255,255,255,.14); }
        .ob-pin::before { content: ''; display: inline-block; width: 8px; height: 8px; margin-right: 8px; border-radius: 50%; background: #fff; }
        .ob-pin-a { top: 28%; left: 18%; animation: ob-in .6s ease-out both; }
        .ob-pin-b { top: 46%; left: 42%; animation: ob-in .6s ease-out .15s both; }
        .ob-pin-c { top: 62%; left: 64%; animation: ob-in .6s ease-out .3s both; }
        .ob-search { inset: 22% 16%; display: grid; gap: 14px; align-content: start; }
        .ob-search span { height: 46px; border-radius: 14px; background: rgba(255,255,255,.16); animation: ob-in .5s ease-out both; }
        .ob-search i { display: block; height: 18px; border-radius: 8px; background: rgba(255,255,255,.28); transform-origin: left; animation: ob-bar .7s ease-out both; }
        .ob-search i:nth-child(2) { width: 86%; animation-delay: .1s; }
        .ob-search i:nth-child(3) { width: 70%; animation-delay: .2s; }
        .ob-search i:nth-child(4) { width: 54%; animation-delay: .3s; }
        .ob-page { inset: 18% 18% 18% 22%; background: #fff; border-radius: 18px; padding: 22px; display: grid; gap: 12px; align-content: start; animation: ob-in .5s ease-out both; }
        .ob-page b { height: 22px; width: 58%; border-radius: 8px; background: #1c305c; }
        .ob-page em { display: block; height: 12px; border-radius: 6px; background: #e6e8ee; }
        .ob-page em:nth-of-type(1) { width: 92%; animation: ob-bar .6s ease-out .1s both; }
        .ob-page em:nth-of-type(2) { width: 80%; animation: ob-bar .6s ease-out .2s both; }
        .ob-page em:nth-of-type(3) { width: 66%; animation: ob-bar .6s ease-out .3s both; }
        .ob-intro-copy { display: flex; flex-direction: column; justify-content: center; padding: 48px 56px 48px 12px; }
        .ob-intro-copy p { margin: 0; letter-spacing: .14em; text-transform: uppercase; font-size: 12px; font-weight: 700; color: #8a6a62; }
        .ob-intro-copy h1 { margin: 10px 0 0; font-size: 40px; line-height: 1.08; letter-spacing: -0.03em; }
        .ob-intro-copy > span { margin-top: 12px; max-width: 36ch; color: #4b5568; font-size: 17px; line-height: 1.5; }
        .ob-intro-dots { display: flex; gap: 8px; margin-top: 28px; }
        .ob-intro-dots button { width: 8px; height: 8px; border: 0; border-radius: 99px; background: #d4d4d8; padding: 0; cursor: pointer; }
        .ob-intro-dots .is-on { width: 22px; background: #1c305c; }
        .ob-intro-actions { display: flex; gap: 12px; align-items: center; margin-top: 22px; }
        .ob-intro-next { border: 0; border-radius: 999px; background: #1c305c; color: #fff; padding: 12px 18px; font-weight: 700; cursor: pointer; }
        .ob-intro-next:active { transform: scale(.98); }
        .ob-intro-skip { border: 0; background: transparent; color: #4b5568; font-weight: 650; cursor: pointer; }
        @keyframes ob-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
        @keyframes ob-bar { from { transform: scaleX(.2); opacity: .4; } to { transform: none; opacity: 1; } }
        @media (max-width: 800px) {
          .ob-intro { grid-template-columns: 1fr; }
          .ob-scene { min-height: 280px; margin: 16px 16px 0; }
          .ob-intro-copy { padding: 24px 20px 32px; }
          .ob-intro-copy h1 { font-size: 32px; }
        }
        @media (prefers-reduced-motion: reduce) {
          .ob-pin, .ob-search span, .ob-search i, .ob-page, .ob-page em { animation: none; }
        }
      `}</style>
    </div>
  )
}

export default function OnboardingPage() {
  const navigate = useNavigate()
  const [intro, setIntro] = useState(true)
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

  const skip = () => {
    localStorage.setItem('seo_project', JSON.stringify({
      business_name: 'ZeOrbit',
      website: 'https://zeorbit.com',
    }))
    window.dispatchEvent(new Event('seo_project_updated'))
    navigate('/content')
  }

  if (intro) return <IntroFlow onDone={() => setIntro(false)} onSkip={skip} />

  if (step === 0) {
    return (
      <StepShell
        step={0} total={totalSteps}
        title="What's your website?" subtitle="We'll use this to run your first SEO analysis."
        onNext={() => setStep(1)} nextDisabled={!form.website.trim()}
        onSkip={skip}>
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
