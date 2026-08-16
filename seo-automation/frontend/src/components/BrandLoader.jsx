/** Minimal branded loading lockup used while pages hydrate. */
import Logo from './Logo'

export default function BrandLoader({ label = 'Loading…' }) {
  return (
    <div
      style={{
        minHeight: '40vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 16,
        color: 'var(--text-3)',
      }}
    >
      <div style={{ animation: 'zoPulse 1.2s ease-in-out infinite' }}>
        <Logo size={36} />
      </div>
      <div style={{ fontSize: 13, fontWeight: 500 }}>{label}</div>
      <style>{`
        @keyframes zoPulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.55; transform: scale(0.96); }
        }
      `}</style>
    </div>
  )
}
