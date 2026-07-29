/** Circular score indicator (0-100), color-coded green/amber/red by band. Reused by the Overview and Site Audit pages. */
export default function ScoreRing({ score, size = 108, label = '/ 100' }) {
  const color = score >= 80 ? 'var(--green)' : score >= 60 ? 'var(--amber)' : 'var(--red)'
  const r = size / 2 - 12
  const circumference = 2 * Math.PI * r
  const offset = circumference * (1 - score / 100)
  const c = size / 2
  return (
    <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={c} cy={c} r={r} fill="none" stroke="var(--border)" strokeWidth="9" />
        <circle cx={c} cy={c} r={r} fill="none" stroke={color} strokeWidth="9" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          transform={`rotate(-90 ${c} ${c})`} style={{ transition: 'stroke-dashoffset .6s ease' }} />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <span className="font-display" style={{ fontSize: size * 0.24, fontWeight: 800, color: 'var(--text-1)' }}>{score}</span>
        <span style={{ fontSize: 10, color: 'var(--text-4)' }}>{label}</span>
      </div>
    </div>
  )
}
