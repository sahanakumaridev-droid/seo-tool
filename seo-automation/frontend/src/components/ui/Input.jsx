/**
 * Form primitives — Field (label wrapper), Input, Textarea, Select.
 * All inherit the global dark field styling from index.css.
 */
export function Field({ label, hint, children, style = {} }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, ...style }}>
      {label && (
        <label style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-3)' }}>
          {label}
        </label>
      )}
      {children}
      {hint && <span style={{ fontSize: 11, color: 'var(--text-4)' }}>{hint}</span>}
    </div>
  )
}

const base = { width: '100%', padding: '10px 12px', fontSize: 14 }

export function Input({ className = '', style = {}, ...rest }) {
  return <input className={className} style={{ ...base, ...style }} {...rest} />
}

export function Textarea({ className = '', style = {}, rows = 4, ...rest }) {
  return <textarea rows={rows} className={className} style={{ ...base, resize: 'vertical', ...style }} {...rest} />
}

export function Select({ children, className = '', style = {}, ...rest }) {
  return <select className={className} style={{ ...base, ...style }} {...rest}>{children}</select>
}
