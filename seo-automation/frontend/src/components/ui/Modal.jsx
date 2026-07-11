import { X } from 'lucide-react'

/**
 * Modal — centered dialog on a blurred dark backdrop.
 * Click backdrop or the × to close.
 */
export default function Modal({ open, onClose, title, children, maxWidth = 460, footer }) {
  if (!open) return null
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" style={{ maxWidth }} onClick={e => e.stopPropagation()}>
        {(title || onClose) && (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 20px', borderBottom: '1px solid var(--border)' }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-1)' }}>{title}</h3>
            {onClose && (
              <button onClick={onClose} aria-label="Close"
                style={{ width: 30, height: 30, borderRadius: 8, background: 'var(--bg-raised)', border: 'none', cursor: 'pointer', color: 'var(--text-3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <X size={16} />
              </button>
            )}
          </div>
        )}
        <div style={{ padding: 20 }}>{children}</div>
        {footer && <div style={{ padding: '14px 20px', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'flex-end', gap: 10 }}>{footer}</div>}
      </div>
    </div>
  )
}
