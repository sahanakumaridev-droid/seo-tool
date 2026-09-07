import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

export default function VisitBeacon() {
  const location = useLocation()

  useEffect(() => {
    const apiBase = (import.meta.env.VITE_API_URL || '/api').trim().replace(/\/$/, '')
    const key = `zo-visit:${location.pathname}`
    try {
      if (sessionStorage.getItem(key)) return
      sessionStorage.setItem(key, '1')
    } catch { /* ignore */ }
    fetch(`${apiBase}/leads/visit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        path: location.pathname + (location.search || ''),
        referrer: typeof document !== 'undefined' ? document.referrer : '',
      }),
      keepalive: true,
    }).catch(() => {})
  }, [location.pathname, location.search])

  return null
}
