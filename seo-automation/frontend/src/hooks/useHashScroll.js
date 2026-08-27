import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

export function scrollToHashId(id) {
  if (!id) return false
  const el = document.getElementById(id)
  if (!el) return false
  el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  if (el.querySelector('form')) {
    window.setTimeout(() => {
      el.querySelector('input:not([type="hidden"]), textarea, select')?.focus({ preventScroll: true })
    }, 400)
  }
  return true
}

export function useHashScroll() {
  const { hash, pathname } = useLocation()

  useEffect(() => {
    if (!hash) return undefined
    const id = decodeURIComponent(hash.replace('#', ''))
    let tries = 0
    let timer = 0
    const go = () => {
      if (scrollToHashId(id)) return
      tries += 1
      if (tries < 24) timer = window.setTimeout(go, 40)
    }
    timer = window.setTimeout(go, 40)
    return () => window.clearTimeout(timer)
  }, [hash, pathname])
}
