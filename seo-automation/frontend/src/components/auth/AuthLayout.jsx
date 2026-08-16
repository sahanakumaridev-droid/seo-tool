import { useNavigate } from 'react-router-dom'
import { CheckCircle2 } from 'lucide-react'
import Logo from '../Logo'

const HIGHLIGHTS = [
  'Full site audit in under 2 minutes',
  'Real keyword volume, difficulty & CPC data',
  'Daily rank tracking across the U.S.',
  'AI search visibility across Google AI, ChatGPT & Perplexity',
]

/** Shared two-column shell for Login / Register / Forgot / Reset. */
export default function AuthLayout({ title, subtitle, children, footer }) {
  const navigate = useNavigate()
  return (
    <div style={{ display: 'flex', minHeight: '100dvh', height: '100dvh', background: 'var(--bg-base)', fontFamily: 'var(--font-sans)', overflow: 'hidden' }}>
      {/* Left — brand panel */}
      <div className="hide-mobile" style={{
        flex: '0 0 min(420px, 40%)', background: 'var(--text-1)', color: '#fff',
        display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
        padding: '32px 36px', position: 'relative', overflow: 'auto', minHeight: 0,
      }}>
        <div style={{ position: 'absolute', top: -100, right: -100, width: 340, height: 340, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,90,78,0.25) 0%, transparent 70%)', filter: 'blur(40px)' }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          <button onClick={() => navigate('/')} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
            <Logo size={40} onDark />
          </button>
        </div>

        <div style={{ position: 'relative', zIndex: 1 }}>
          <h2 style={{ fontSize: 30, fontWeight: 800, lineHeight: 1.2, margin: '0 0 16px', letterSpacing: '-0.5px' }}>
            Grow your search visibility. Turn rankings into revenue.
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 28 }}>
            {HIGHLIGHTS.map(h => (
              <div key={h} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <CheckCircle2 size={16} color="#FF6B54" style={{ flexShrink: 0 }} />
                <span style={{ fontSize: 13.5, color: 'rgba(255,255,255,0.8)' }}>{h}</span>
              </div>
            ))}
          </div>
        </div>

        <div style={{ position: 'relative', zIndex: 1, fontSize: 12, color: 'rgba(255,255,255,0.35)' }}>
          © 2026 ZeOrbit · zeorbit.com
        </div>
      </div>

      {/* Right — form panel */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '32px 24px', overflow: 'auto', minHeight: 0 }}>
        <div style={{ width: '100%', maxWidth: 380 }}>
          <div className="mobile-only" style={{ marginBottom: 28 }}>
            <Logo size={36} />
          </div>
          <div style={{ marginBottom: 30 }}>
            <h1 style={{ fontSize: 26, fontWeight: 800, color: 'var(--text-1)', margin: '0 0 8px', letterSpacing: '-0.5px' }}>{title}</h1>
            {subtitle && <p style={{ fontSize: 14, color: 'var(--text-3)', margin: 0 }}>{subtitle}</p>}
          </div>
          {children}
          {footer && <div style={{ marginTop: 24 }}>{footer}</div>}
        </div>
      </div>
    </div>
  )
}
