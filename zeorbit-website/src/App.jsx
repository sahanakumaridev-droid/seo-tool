import { lazy, Suspense, useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import ScrollToTop from './components/ScrollToTop'
import PageJump from './components/PageJump'
import RouteMeta from './components/RouteMeta'
import LandingPage from './pages/LandingPage'

const SiteDock = lazy(() => import('./components/SiteDock'))
const SiteChat = lazy(() => import('./components/SiteChat'))
const ServicePage = lazy(() => import('./pages/ServicePage'))
const WebsiteDesignPage = lazy(() => import('./pages/WebsiteDesignPage'))
const PortfolioPage = lazy(() => import('./pages/PortfolioPage'))
const BlogPage = lazy(() => import('./pages/BlogPage'))
const SeoArticlePage = lazy(() => import('./pages/SeoArticlePage'))
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicyPage'))
const AreasPage = lazy(() => import('./pages/AreasPage'))

function DelayedChrome() {
  const [ready, setReady] = useState(false)
  useEffect(() => {
    const id = window.setTimeout(() => setReady(true), 800)
    return () => window.clearTimeout(id)
  }, [])
  if (!ready) return null
  return (
    <Suspense fallback={null}>
      <SiteDock />
      <SiteChat />
    </Suspense>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <PageJump />
      <RouteMeta />
      <DelayedChrome />
      <Suspense fallback={null}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/blog" element={<BlogPage />} />
          <Route path="/website-designing" element={<WebsiteDesignPage />} />
          <Route path="/mobile-apps" element={<ServicePage slug="mobile-apps" />} />
          <Route path="/custom-software" element={<ServicePage slug="custom-software" />} />
          <Route path="/seo-ppc" element={<ServicePage slug="seo-ppc" />} />
          <Route path="/contact" element={<ServicePage slug="contact" />} />
          <Route path="/areas" element={<AreasPage />} />
          <Route path="/areas/:slug" element={<AreasPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
          <Route path="/privacy" element={<PrivacyPolicyPage />} />
          <Route path="/revamp-preview" element={<LandingPage />} />
          <Route path="/:slug" element={<SeoArticlePage />} />
          <Route path="*" element={<LandingPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
