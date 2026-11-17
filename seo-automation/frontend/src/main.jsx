import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import UsaGate from './components/UsaGate.jsx'

const SEO_UI_BUILD = '2026-09-10-content-v6'

try {
  const prev = sessionStorage.getItem('seo_ui_build')
  if (prev && prev !== SEO_UI_BUILD) {
    sessionStorage.setItem('seo_ui_build', SEO_UI_BUILD)
    window.location.reload()
  } else if (!prev) {
    sessionStorage.setItem('seo_ui_build', SEO_UI_BUILD)
  }
} catch { /* ignore */ }

window.addEventListener('pageshow', (e) => {
  if (e.persisted) window.location.reload()
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <UsaGate>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </UsaGate>
    </ErrorBoundary>
  </StrictMode>,
)
