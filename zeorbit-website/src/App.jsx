import { BrowserRouter, Routes, Route } from 'react-router-dom'
import ScrollToTop from './components/ScrollToTop'
import LandingPage from './pages/LandingPage'
import BlogPage from './pages/BlogPage'
import ServicePage from './pages/ServicePage'

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/blog" element={<BlogPage />} />
        <Route path="/website-designing" element={<ServicePage slug="website-designing" />} />
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
