import { useState, useEffect } from 'react'

/** Reads the current project (business_type, base_location, website, ...)
 * from localStorage, kept in sync with the `seo_project_updated` event
 * fired whenever Onboarding/ContentPage save changes. */
export default function useProjectInfo() {
  const read = () => {
    try { return JSON.parse(localStorage.getItem('seo_project') || '{}') } catch { return {} }
  }
  const [info, setInfo] = useState(read)
  useEffect(() => {
    const handler = () => setInfo(read())
    window.addEventListener('seo_project_updated', handler)
    return () => window.removeEventListener('seo_project_updated', handler)
  }, [])
  return info
}
