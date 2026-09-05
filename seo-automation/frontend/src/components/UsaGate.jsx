import { useEffect, useState } from 'react'
import BrandLoader from './BrandLoader'

const CACHE_KEY = 'zo_geo_cc'
const US_ONLY_PATH = '/us-only.html'

async function lookupCountry() {
  const cached = sessionStorage.getItem(CACHE_KEY)
  if (cached) return cached

  const controllers = []
  const fetchJson = async (url) => {
    const ctrl = new AbortController()
    controllers.push(ctrl)
    const t = setTimeout(() => ctrl.abort(), 5000)
    try {
      const res = await fetch(url, { signal: ctrl.signal })
      if (!res.ok) throw new Error('geo lookup failed')
      return await res.json()
    } finally {
      clearTimeout(t)
    }
  }

  try {
    for (const url of ['https://ipwho.is/?fields=success,country_code', 'https://ipapi.co/json/']) {
      try {
        const data = await fetchJson(url)
        const code = String(data.country_code || data.country || '').toUpperCase()
        if (code.length === 2) {
          sessionStorage.setItem(CACHE_KEY, code)
          return code
        }
      } catch {
        /* try next provider */
      }
    }
    return ''
  } finally {
    controllers.forEach((c) => c.abort())
  }
}

/**
 * Same visitor rule as zeorbit.com nginx GeoIP: United States only.
 * Local Vite has no GeoIP, so the browser checks the public IP.
 */
export default function UsaGate({ children }) {
  const skip = import.meta.env.VITE_SKIP_US_GATE === 'true'
    || ['localhost', '127.0.0.1'].includes(window.location.hostname)
  const [allowed, setAllowed] = useState(skip)

  useEffect(() => {
    if (skip) return undefined
    if (window.location.pathname === US_ONLY_PATH) {
      setAllowed(true)
      return undefined
    }

    let cancelled = false
    lookupCountry().then((code) => {
      if (cancelled) return
      if (code === 'US') {
        setAllowed(true)
        return
      }
      window.location.replace(US_ONLY_PATH)
    })
    return () => { cancelled = true }
  }, [skip])

  if (!allowed) {
    return (
      <div style={{ minHeight: '100vh', background: '#fafaf8' }}>
        <BrandLoader label="Checking location…" />
      </div>
    )
  }

  return children
}
