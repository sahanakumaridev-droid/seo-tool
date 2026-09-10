import { useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'

function visitorSessionId() {
  try {
    let id = localStorage.getItem('zo_vid')
    if (!id) {
      id = (crypto.randomUUID && crypto.randomUUID()) || `v-${Date.now()}`
      localStorage.setItem('zo_vid', id)
    }
    return id
  } catch {
    return ''
  }
}

export default function VisitBeacon() {
  const location = useLocation()
  const lastRef = useRef('')

  useEffect(() => {
    const apiBase = (import.meta.env.VITE_API_URL || '/api').trim().replace(/\/$/, '')
    const path = location.pathname + (location.search || '')
    const stamp = `${path}:${Math.floor(Date.now() / 4000)}`
    if (lastRef.current === stamp) return
    lastRef.current = stamp
    const params = new URLSearchParams(location.search || '')
    fetch(`${apiBase}/leads/visit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        path,
        referrer: typeof document !== 'undefined' ? document.referrer : '',
        session_id: visitorSessionId(),
        language: typeof navigator !== 'undefined' ? navigator.language : '',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || '',
        screen: typeof window !== 'undefined' ? `${window.screen?.width || 0}x${window.screen?.height || 0}` : '',
        title: typeof document !== 'undefined' ? document.title : '',
        utm_source: params.get('utm_source') || '',
      }),
      keepalive: true,
    }).catch(() => {})
  }, [location.pathname, location.search])

  return null
}
