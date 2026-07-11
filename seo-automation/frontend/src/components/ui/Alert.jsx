import { Info, CheckCircle, AlertTriangle, XCircle } from 'lucide-react'

/**
 * Alert — inline message banner. variant: info | success | warning | error
 */
const ICONS = { info: Info, success: CheckCircle, warning: AlertTriangle, error: XCircle }

export default function Alert({ children, variant = 'info', icon = true, className = '' }) {
  const Icon = ICONS[variant] || Info
  return (
    <div className={`alert alert-${variant} ${className}`.trim()}>
      {icon && <Icon size={16} style={{ flexShrink: 0, marginTop: 1 }} />}
      <div>{children}</div>
    </div>
  )
}
