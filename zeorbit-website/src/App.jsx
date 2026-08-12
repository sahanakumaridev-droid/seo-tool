import { BrowserRouter, Navigate, Routes, Route } from 'react-router-dom'
import ScrollToTop from './components/ScrollToTop'
import SiteDock from './components/SiteDock'
import LandingPage from './pages/LandingPage'
import ServicePage from './pages/ServicePage'
import WebsiteDesignPage from './pages/WebsiteDesignPage'

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <SiteDock />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/blog" element={<Navigate to="/seo-ppc#blog" replace />} />
        <Route path="/website-designing" element={<WebsiteDesignPage />} />
        <Route path="/mobile-apps" element={<ServicePage slug="mobile-apps" />} />
        <Route path="/custom-software" element={<ServicePage slug="custom-software" />} />
        <Route path="/seo-ppc" element={<ServicePage slug="seo-ppc" />} />
        <Route path="/contact" element={<ServicePage slug="contact" />} />
        <Route path="/revamp-preview" element={<LandingPage />} />
        <Route path="*" element={<LandingPage />} />
      </Routes>
    </BrowserRouter>
  )
}
