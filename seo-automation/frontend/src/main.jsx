import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import UsaGate from './components/UsaGate.jsx'

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
