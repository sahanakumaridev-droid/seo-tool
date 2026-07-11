/**
 * Button — the single button primitive for the whole app.
 * Variants: primary | secondary | ghost | danger
 * Sizes:    sm | md | lg
 * Renders <a> when `href` is passed, otherwise <button>.
 */
const SIZES = {
  sm: { padding: '6px 12px', fontSize: 12 },
  md: { padding: '9px 16px', fontSize: 13 },
  lg: { padding: '12px 22px', fontSize: 15 },
}

export default function Button({
  children, variant = 'primary', size = 'md', icon: Icon, iconRight: IconRight,
  loading = false, disabled = false, href, className = '', style = {}, ...rest
}) {
  const cls = `btn btn-${variant} ${className}`.trim()
  const s = { ...SIZES[size] || SIZES.md, ...style }
  const content = (
    <>
      {loading
        ? <span className="animate-spin" style={{ width: 14, height: 14, border: '2px solid rgba(255,255,255,0.35)', borderTopColor: '#fff', borderRadius: '50%', display: 'inline-block' }} />
        : Icon && <Icon size={size === 'lg' ? 18 : 15} />}
      {children}
      {IconRight && <IconRight size={size === 'lg' ? 18 : 15} />}
    </>
  )
  if (href) {
    return <a href={href} className={cls} style={s} {...rest}>{content}</a>
  }
  return <button className={cls} style={s} disabled={disabled || loading} {...rest}>{content}</button>
}
