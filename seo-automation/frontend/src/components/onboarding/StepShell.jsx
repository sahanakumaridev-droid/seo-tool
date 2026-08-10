import { ArrowLeft, ArrowRight } from 'lucide-react'
import Logo from '../Logo'

export default function StepShell({ title, subtitle, onBack, onNext, nextLabel = 'Continue', nextDisabled, loading, children }) {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)', display: 'flex', flexDirection: 'column', alignItems: 'center', fontFamily: 'var(--font-sans)' }}>
      <div style={{ width: '100%', maxWidth: 560, padding: '40px 24px' }}>
        <div style={{ marginBottom: 36, display: 'flex', justifyContent: 'center' }}>
          <Logo size={30} />
        </div>

        <div className="card fade-in" style={{ padding: '36px 32px' }}>
          <div style={{ marginBottom: 26 }}>
            <h1 style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)', margin: '0 0 6px', letterSpacing: '-0.3px' }}>{title}</h1>
            {subtitle && <p style={{ fontSize: 13.5, color: 'var(--text-3)', margin: 0 }}>{subtitle}</p>}
          </div>

          {children}

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 30 }}>
            {onBack ? (
              <button onClick={onBack} className="btn btn-ghost"><ArrowLeft size={15} /> Back</button>
            ) : <span />}
            <button onClick={onNext} disabled={nextDisabled || loading} className="btn btn-primary">
              {loading ? 'Working…' : <>{nextLabel} <ArrowRight size={15} /></>}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
