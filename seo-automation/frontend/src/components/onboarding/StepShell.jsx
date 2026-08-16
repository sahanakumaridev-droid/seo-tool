import { ArrowLeft, ArrowRight, Check } from 'lucide-react'
import Logo from '../Logo'

const STEPS = [
  { label: 'Website' },
  { label: 'Business' },
  { label: 'Location' },
  { label: 'Type' },
  { label: 'Goal' },
]

export default function StepShell({
  step = 0,
  total = STEPS.length,
  title,
  subtitle,
  onBack,
  onNext,
  onSelectStep,
  nextLabel = 'Continue',
  nextDisabled,
  loading,
  children,
}) {
  const steps = STEPS.slice(0, total)
  const progress = ((step + 1) / total) * 100

  const submit = (e) => {
    e.preventDefault()
    if (!nextDisabled && !loading) onNext?.()
  }

  return (
    <div className="ob-shell">
      <header className="ob-top">
        <a href="/" className="ob-logo" aria-label="ZeOrbit home">
          <Logo size={32} />
        </a>
        <div
          className="ob-progress"
          role="progressbar"
          aria-valuemin={1}
          aria-valuenow={step + 1}
          aria-valuemax={total}
          aria-label={`Step ${step + 1} of ${total}`}
        >
          <span className="ob-progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </header>

      <div className="ob-shell-inner">
        <ol className="ob-stepper" aria-label="Onboarding steps">
          {steps.map((item, i) => {
            const state = i < step ? 'done' : i === step ? 'current' : 'upcoming'
            const clickable = Boolean(onSelectStep) && i < step
            return (
              <li key={item.label} className={`ob-step ob-step-${state}`}>
                <button
                  type="button"
                  className="ob-step-btn"
                  disabled={!clickable}
                  onClick={clickable ? () => onSelectStep(i) : undefined}
                  aria-current={state === 'current' ? 'step' : undefined}
                  aria-label={`${item.label}, step ${i + 1} of ${total}${state === 'done' ? ', completed' : ''}`}
                >
                  <span className="ob-step-dot">
                    {state === 'done' ? <Check size={10} strokeWidth={3} /> : null}
                  </span>
                  <span className="ob-step-label">{item.label}</span>
                </button>
              </li>
            )
          })}
        </ol>

        <form className="ob-panel" onSubmit={submit}>
          <p className="ob-kicker">{steps[step]?.label}</p>
          <h1>{title}</h1>
          {subtitle ? <p className="ob-card-sub">{subtitle}</p> : null}

          <div className="ob-body">{children}</div>

          <div className="ob-card-actions">
            {onBack ? (
              <button type="button" onClick={onBack} className="btn btn-ghost">
                <ArrowLeft size={16} /> Back
              </button>
            ) : null}
            <button type="submit" disabled={nextDisabled || loading} className="btn btn-primary">
              {loading ? 'Working…' : <>{nextLabel} <ArrowRight size={16} /></>}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
