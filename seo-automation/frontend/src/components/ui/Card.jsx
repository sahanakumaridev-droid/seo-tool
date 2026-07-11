/**
 * Card — surface container. `hover` adds lift-on-hover, `pad` sets padding (px).
 */
export default function Card({ children, hover = false, pad = 20, className = '', style = {}, ...rest }) {
  return (
    <div
      className={`card${hover ? ' card-hover' : ''} ${className}`.trim()}
      style={{ padding: pad, ...style }}
      {...rest}
    >
      {children}
    </div>
  )
}

export function CardHeader({ title, subtitle, icon: Icon, action }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {Icon && <Icon size={16} style={{ color: 'var(--brand-violet)' }} />}
        <div>
          <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-1)' }}>{title}</h3>
          {subtitle && <p style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2 }}>{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  )
}
