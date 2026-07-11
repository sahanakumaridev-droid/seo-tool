/**
 * Badge — small status pill. tone: brand | success | warning | danger | neutral
 */
const TONES = {
  brand:   { color: 'var(--brand-violet)', background: 'var(--brand-soft)' },
  success: { color: 'var(--green)', background: 'var(--green-soft)' },
  warning: { color: 'var(--amber)', background: 'var(--amber-soft)' },
  danger:  { color: 'var(--red)', background: 'var(--red-soft)' },
  neutral: { color: 'var(--text-3)', background: 'var(--bg-raised)' },
}

export default function Badge({ children, tone = 'neutral', className = '', style = {} }) {
  return (
    <span
      className={`badge ${className}`.trim()}
      style={{ ...TONES[tone] || TONES.neutral, ...style }}
    >
      {children}
    </span>
  )
}
