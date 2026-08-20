import { useState, useEffect } from 'react'
import { Share2, Globe, MessageCircle, Briefcase, Camera, CheckCircle, XCircle,
         Send, RefreshCw, ExternalLink, Sparkles, Copy, ArrowRight } from 'lucide-react'
import { shareToSocial, getSocialPlatforms, listPages } from '../api'
import axios from 'axios'
import useProjectInfo from '../hooks/useProjectInfo'

/** Prefer live WP URL, then published /p/ URL, then profile website — never example.com. */
function isUsableUrl(url) {
  if (!url || typeof url !== 'string') return false
  const u = url.trim().toLowerCase()
  if (!u) return false
  if (u.includes('example.com') || u.includes('example.org') || u.includes('placeholder')) return false
  return true
}

function resolvePostUrl(block, projectWebsite, pagePublicUrl) {
  const liveHost = 'https://zeorbit.com'
  const toLive = (url) => {
    if (!url) return url
    try {
      const u = new URL(url)
      if (u.hostname.includes('nip.io') || u.hostname.startsWith('seo.')) {
        const path = u.pathname.replace(/\/$/, '')
        if (path.startsWith('/p/')) return `${liveHost}/${path.slice(3)}`
        if (path && path !== '/' && path !== '/blog') return `${liveHost}${path}`
        return `${liveHost}/blog`
      }
    } catch { /* relative or invalid */ }
    return url
  }
  if (isUsableUrl(pagePublicUrl)) return toLive(pagePublicUrl)
  if (!block) return ''
  if (isUsableUrl(block.wp_post_url)) return toLive(block.wp_post_url)
  if (isUsableUrl(block.public_url)) return toLive(block.public_url)
  if (block.slug) {
    return `${liveHost}/${block.slug}`
  }
  const site = (projectWebsite || '').trim().replace(/\/$/, '')
  if (site && isUsableUrl(site.startsWith('http') ? site : `https://${site}`)) {
    const base = site.startsWith('http') ? site : `https://${site}`
    return block.slug ? `${base}/${block.slug}` : base
  }
  return ''
}

/* ── ZeOrbit's real social accounts ─────────────────────────── */
const PLATFORMS = {
  facebook: {
    label: 'Facebook',
    profileUrl: 'https://www.facebook.com/zeorbit.web.designers.mobileapp.developers',
    pageUrl: 'https://www.facebook.com/zeorbit.web.designers.mobileapp.developers',
    shareUrl: (u, t) => `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(u)}&quote=${encodeURIComponent(t)}`,
    bg: '#1877f2',
    color: '#1877f2',
    tagline: 'ZeOrbit on Facebook',
    handle: '@zeorbit.web.designers.mobileapp.developers',
    logo: (
      <svg viewBox="0 0 24 24" width="28" height="28" fill="white">
        <path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.236 2.686.236v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.267h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/>
      </svg>
    ),
  },
  instagram: {
    label: 'Instagram',
    profileUrl: 'https://www.instagram.com/zeorbit/',
    shareUrl: () => 'https://www.instagram.com/zeorbit/',
    bg: 'linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888)',
    color: '#e1306c',
    tagline: 'ZeOrbit on Instagram',
    handle: '@zeorbit',
    logo: (
      <svg viewBox="0 0 24 24" width="28" height="28" fill="white">
        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
      </svg>
    ),
  },
  twitter: {
    label: 'Twitter / X',
    profileUrl: 'https://twitter.com/orbit_ze',
    shareUrl: (u, t) => `https://twitter.com/intent/tweet?url=${encodeURIComponent(u)}&text=${encodeURIComponent(t)}`,
    bg: '#000000',
    color: '#1d9bf0',
    tagline: 'ZeOrbit on Twitter/X',
    handle: '@orbit_ze',
    logo: (
      <svg viewBox="0 0 24 24" width="26" height="26" fill="white">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.737-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
      </svg>
    ),
  },
  linkedin: {
    label: 'LinkedIn',
    profileUrl: 'https://www.linkedin.com/company/zeorbit/',
    shareUrl: (u, t) => `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(u)}&summary=${encodeURIComponent(t)}`,
    bg: '#0a66c2',
    color: '#0a66c2',
    tagline: 'ZeOrbit on LinkedIn',
    handle: 'zeorbit',
    logo: (
      <svg viewBox="0 0 24 24" width="28" height="28" fill="white">
        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
      </svg>
    ),
  },
  youtube: {
    label: 'YouTube',
    profileUrl: 'https://www.youtube.com/@ZeOrbit-Firm/',
    shareUrl: (u, t) => `https://www.youtube.com/results?search_query=${encodeURIComponent(t)}`,
    bg: '#ff0000',
    color: '#ff0000',
    tagline: 'ZeOrbit on YouTube',
    handle: '@ZeOrbit-Firm',
    logo: (
      <svg viewBox="0 0 24 24" width="30" height="30" fill="white">
        <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
      </svg>
    ),
  },
  pinterest: {
    label: 'Pinterest',
    profileUrl: 'https://www.pinterest.com/zeorbitsd/',
    shareUrl: (u, t) => `https://pinterest.com/pin/create/button/?url=${encodeURIComponent(u)}&description=${encodeURIComponent(t)}`,
    bg: '#e60023',
    color: '#e60023',
    tagline: 'ZeOrbit on Pinterest',
    handle: 'zeorbitsd',
    logo: (
      <svg viewBox="0 0 24 24" width="28" height="28" fill="white">
        <path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 01.083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/>
      </svg>
    ),
  },
  threads: {
    label: 'Threads',
    profileUrl: 'https://www.threads.net/',
    shareUrl: (u, t) => `https://www.threads.net/intent/post?text=${encodeURIComponent(t + ' ' + u)}`,
    bg: '#000000',
    color: '#2563EB',
    tagline: 'ZeOrbit on Threads',
    handle: '@zeorbit',
    logo: (
      <svg viewBox="0 0 192 192" width="26" height="26" fill="white">
        <path d="M141.5 88.2c-.6-.3-1.3-.6-1.9-.9-1.1-20.7-12.4-32.5-31.4-32.6h-.3c-11.4 0-20.8 4.8-26.6 13.6l10.5 7.2c4.3-6.5 11.1-7.9 16.2-7.9h.2c6.3 0 11.1 1.9 14.2 5.5 2.2 2.6 3.7 6.3 4.4 10.9-5.5-.9-11.5-1.2-17.8-.8-17.9 1-29.4 11.5-28.6 26 .4 7.4 4.1 13.7 10.4 17.8 5.3 3.5 12.2 5.2 19.3 4.8 9.5-.5 16.9-4.1 22.1-10.7 3.9-5 6.4-11.5 7.5-19.7 4.5 2.7 7.8 6.3 9.7 10.6 3.1 7.3 3.3 19.3-6.5 29.1-8.6 8.6-18.9 12.3-34.5 12.4-17.3-.1-30.4-5.7-38.9-16.5-8-10.1-12.1-24.8-12.3-43.5.2-18.7 4.3-33.4 12.3-43.5 8.5-10.8 21.6-16.4 38.9-16.5 17.4.1 30.7 5.7 39.5 16.6 4.3 5.3 7.5 12 9.7 19.8l12.3-3.3c-2.6-9.6-6.7-17.9-12.2-24.7C154.9 11.9 138.3 4.2 116.5 4h-.1c-21.8.2-38.2 7.9-48.9 23-9.5 13.4-14.4 32.1-14.6 55.5v.1c.2 23.4 5.1 42.1 14.6 55.5 10.7 15.1 27.1 22.8 48.9 23h.1c19.4-.1 33-5.2 44.3-16.4 14.8-14.8 14.3-33.3 9.4-44.7-3.5-8.1-10-14.7-18.9-19.1zM115 124.6c-7.8.4-15.9-3.1-16.3-10.6-.3-5.6 4-11.8 16.8-12.5 1.5-.1 2.9-.1 4.3-.1 4.6 0 9 .4 12.9 1.3-1.5 18.1-10 21.5-17.7 21.9z"/>
      </svg>
    ),
  },
}
function buildCaption(block, platform, projectWebsite, pagePublicUrl) {
  if (!block) return ''
  const kws = block?.keywords?.secondary?.slice(0, 4) || []
  const hashtags = kws.map(k => '#' + k.replace(/\s+/g, '')).join(' ')
  const postUrl = resolvePostUrl(block, projectWebsite, pagePublicUrl)
  const base = `${block?.title}\n\n${block?.meta_description}`
  if (platform === 'twitter') {
    return postUrl
      ? `${base.slice(0, 180)}\n\n${postUrl}\n\n${hashtags}`.slice(0, 280)
      : `${base.slice(0, 220)}\n\n${hashtags}`.slice(0, 280)
  }
  return postUrl
    ? `${base}\n\n🔗 ${postUrl}\n\n${hashtags} #LocalSEO #SmallBusiness`
    : `${base}\n\n${hashtags} #LocalSEO #SmallBusiness`
}

/* ── Platform Card ───────────────────────────────────────────── */
function PlatformCard({ id, platform, onShare, hasPage }) {
  const [hovered, setHovered] = useState(false)
  const isGradient = typeof platform.bg === 'string' && platform.bg.startsWith('linear')

  return (
    <div
      style={{
        borderRadius: 16, overflow: 'hidden',
        border: '1px solid var(--border)',
        background: 'var(--bg-surface)',
        transition: 'transform 0.2s, box-shadow 0.2s',
        transform: hovered ? 'translateY(-3px)' : 'none',
        boxShadow: hovered ? 'var(--shadow-lg)' : 'var(--shadow-sm)',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Brand header */}
      <div style={{ background: platform.bg, padding: '18px 18px 14px', display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{ width: 48, height: 48, borderRadius: 12, background: 'rgba(255,255,255,0.18)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          {platform.logo}
        </div>
        <div>
          <div style={{ color: 'white', fontWeight: 800, fontSize: 16, lineHeight: 1.2 }}>{platform.label}</div>
          <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: 11, marginTop: 2 }}>{platform.handle}</div>
        </div>
      </div>

      {/* Buttons */}
      <div style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 7 }}>
        {/* Visit profile */}
        <button onClick={() => window.open(platform.profileUrl, '_blank', 'noopener')}
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '9px 12px', borderRadius: 9, background: platform.bg, color: 'white', border: 'none', cursor: 'pointer', fontSize: 12, fontWeight: 700 }}
          onMouseEnter={e => e.currentTarget.style.opacity = '0.85'}
          onMouseLeave={e => e.currentTarget.style.opacity = '1'}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><ExternalLink size={12} /> View Profile</span>
          <ArrowRight size={12} />
        </button>

        {/* FB has a separate page link */}
        {id === 'facebook' && platform.pageUrl && (
          <button onClick={() => window.open(platform.pageUrl, '_blank', 'noopener')}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '9px 12px', borderRadius: 9, background: 'rgba(24,119,242,0.2)', color: '#60a5fa', border: '1px solid rgba(24,119,242,0.3)', cursor: 'pointer', fontSize: 12, fontWeight: 600 }}
            onMouseEnter={e => e.currentTarget.style.background = 'rgba(24,119,242,0.3)'}
            onMouseLeave={e => e.currentTarget.style.background = 'rgba(24,119,242,0.2)'}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><ExternalLink size={12} /> Business Page</span>
            <ArrowRight size={12} />
          </button>
        )}

        {/* Share post */}
        <button onClick={() => onShare(id)} disabled={!hasPage}
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, padding: '9px 12px', borderRadius: 9, background: 'var(--bg-raised)', color: hasPage ? 'var(--text-1)' : 'var(--text-4)', border: '1px solid var(--border-bright)', cursor: hasPage ? 'pointer' : 'not-allowed', fontSize: 12, fontWeight: 600 }}
          onMouseEnter={e => { if (hasPage) e.currentTarget.style.background = 'var(--bg-overlay)' }}
          onMouseLeave={e => e.currentTarget.style.background = 'var(--bg-raised)'}>
          <Share2 size={12} /> Share SEO Post
        </button>
      </div>
    </div>
  )
}

/* ── Main Component ──────────────────────────────────────────── */
export default function SocialPage() {
  const project = useProjectInfo()
  const [apiStatus, setApiStatus] = useState({ facebook: false, twitter: false, linkedin: false, instagram: false, pinterest: false, threads: false })
  const [pages, setPages] = useState([])
  const [selected, setSelected] = useState(null)
  const [imageUrl, setImageUrl] = useState('')
  const [generatingImage, setGeneratingImage] = useState(false)
  const [copied, setCopied] = useState('')
  const [shareResult, setShareResult] = useState(null)
  const [apiLoading, setApiLoading] = useState(false)
  const [selectedPlatforms, setSelectedPlatforms] = useState(['facebook', 'twitter', 'linkedin'])
  const [error, setError] = useState('')

  useEffect(() => {
    getSocialPlatforms().then(r => setApiStatus(r.data)).catch(() => {})
    listPages(0, 50).then(r => setPages(r.data)).catch(() => {})
  }, [])

  /* Open native share dialog for that platform */
  const handleShare = (platformId) => {
    if (!selected) { setError('Select a page first to share'); return }
    const block = selected.seo_block
    const postUrl = resolvePostUrl(block, project.website, selected.public_url)
    if (!postUrl) {
      setError('Publish this page to the web (or set your website in Onboarding) before sharing.')
      return
    }
    const caption = buildCaption(block, platformId, project.website, selected.public_url)
    const shareLink = PLATFORMS[platformId].shareUrl(postUrl, caption)
    window.open(shareLink, '_blank', 'width=640,height=520,noopener')
  }

  /* Copy caption */
  const handleCopy = (platformId) => {
    if (!selected) return
    navigator.clipboard.writeText(buildCaption(selected.seo_block, platformId, project.website, selected.public_url))
    setCopied(platformId)
    setTimeout(() => setCopied(''), 2000)
  }

  /* AI image generation */
  const handleGenerateImage = async () => {
    if (!selected) { setError('Select a page first'); return }
    setGeneratingImage(true)
    setError('')
    try {
      const block = selected.seo_block
      const res = await axios.post('/api/images/generate', {
        business_type: block.business_type,
        city: block.city,
        prompt: `${block.business_type} professional service in ${block.city}, modern, clean, no text`,
      })
      setImageUrl(res.data.image_url)
    } catch (e) {
      setError(e.response?.data?.detail || 'Image generation failed — add UNSPLASH_ACCESS_KEY or OPENAI_API_KEY to .env')
    } finally { setGeneratingImage(false) }
  }

  /* API auto-share */
  const handleApiShare = async () => {
    if (!selected) { setError('Select a page first'); return }
    setApiLoading(true)
    setError('')
    setShareResult(null)
    try {
      const block = selected.seo_block
      const postUrl = resolvePostUrl(block, project.website, selected.public_url)
      if (!postUrl) {
        setError('Publish this page first, or add your website URL in Onboarding.')
        setApiLoading(false)
        return
      }
      const res = await shareToSocial({
        post_url: postUrl,
        title: block.title,
        meta_description: block.meta_description,
        city: block.city,
        business_type: block.business_type,
        keywords: block.keywords?.secondary?.slice(0, 5) || [],
        platforms: selectedPlatforms,
        image_url: imageUrl || null,
      })
      setShareResult(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally { setApiLoading(false) }
  }

  const selectedBlock = selected?.seo_block
  const selectedPostUrl = resolvePostUrl(selectedBlock, project.website, selected?.public_url)

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Social Media</h1>
          <p className="text-sm text-slate-500 mt-0.5">Visit platforms, share posts, and auto-publish with AI-generated content</p>
        </div>
        {/* Page selector */}
        <select
          value={selected ? selected.slug : ''}
          onChange={e => { setSelected(pages.find(p => p.slug === e.target.value) || null); setError('') }}
          className="bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500/50 max-w-xs"
        >
          <option value="">— Select a page to share —</option>
          {pages.map(p => (
            <option key={p.slug} value={p.slug}>{p.seo_block?.city} — {p.business_type}</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-sm flex items-center gap-2">
          <span>⚠️</span> {error}
        </div>
      )}

      {/* ── Platform Cards Grid ── */}
      <div>
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Platforms — click to visit or share</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Object.entries(PLATFORMS).map(([id, platform]) => (
            <PlatformCard
              key={id}
              id={id}
              platform={platform}
              onShare={handleShare}
              hasPage={!!selected}
            />
          ))}
        </div>
      </div>

      {/* ── Bottom row: AI image + post preview + API share ── */}
      <div className="grid lg:grid-cols-3 gap-5">

        {/* AI Image */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles size={14} className="text-violet-400" />
            <span className="text-sm font-semibold text-white">AI Image</span>
          </div>
          <div className="flex gap-2 mb-3">
            <input
              type="url"
              value={imageUrl}
              onChange={e => setImageUrl(e.target.value)}
              placeholder="Paste URL or generate →"
              className="flex-1 min-w-0 bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-violet-500/50"
            />
            <button
              onClick={handleGenerateImage}
              disabled={generatingImage || !selected}
              className="flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-semibold text-white disabled:opacity-40 flex-shrink-0"
              style={{ background: 'linear-gradient(135deg,#2563EB,#1D4ED8)' }}
            >
              {generatingImage ? <RefreshCw size={11} className="animate-spin" /> : <Sparkles size={11} />}
              {generatingImage ? '...' : 'Generate'}
            </button>
          </div>
          {imageUrl ? (
            <img src={imageUrl} alt="AI" className="w-full h-40 object-cover rounded-xl border border-white/8" />
          ) : (
            <div className="w-full h-40 rounded-xl border border-dashed border-white/10 flex items-center justify-center text-slate-600 text-xs">
              No image yet
            </div>
          )}
          <p className="text-[10px] text-slate-600 mt-2">DALL-E 3 → Unsplash → Pexels</p>
        </div>

        {/* Post preview */}
        <div className="card p-5">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Post Preview</div>
          {selectedBlock ? (
            <>
              {imageUrl && <img src={imageUrl} alt="" className="w-full h-28 object-cover rounded-lg mb-3 border border-white/8" />}
              <div className="text-sm font-semibold text-white mb-1 line-clamp-2">{selectedBlock.title}</div>
              <div className="text-xs text-slate-400 leading-relaxed mb-2 line-clamp-3">{selectedBlock.meta_description}</div>
              <div className="text-xs text-indigo-400 truncate mb-3">
                🔗 {selectedPostUrl || 'Publish or set website URL to share'}
              </div>
              <div className="flex flex-wrap gap-1">
                {selectedBlock.keywords?.secondary?.slice(0, 4).map(kw => (
                  <span key={kw} className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    #{kw.replace(/\s+/g, '')}
                  </span>
                ))}
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-40 text-slate-600 text-xs text-center">
              <Share2 size={28} className="mb-2 opacity-30" />
              Select a page above to preview your post
            </div>
          )}
        </div>

        {/* API auto-share + captions */}
        <div className="card p-5 flex flex-col gap-4">
          <div>
            <div className="text-sm font-semibold text-white mb-1">API Auto-Share</div>
            <p className="text-xs text-slate-500 mb-3">Posts automatically using stored API tokens</p>
            <div className="grid grid-cols-2 gap-1.5 mb-3">
              {['facebook','twitter','linkedin','instagram','pinterest','threads'].map(id => {
                const p = PLATFORMS[id]
                const active = selectedPlatforms.includes(id)
                return (
                  <button key={id}
                    onClick={() => setSelectedPlatforms(prev => active ? prev.filter(x => x !== id) : [...prev, id])}
                    className="flex items-center gap-2 px-2.5 py-2 rounded-lg text-xs border transition-colors"
                    style={{
                      background: active ? 'var(--brand-soft)' : 'var(--bg-surface)',
                      borderColor: active ? 'var(--brand)' : 'var(--border-bright)',
                      color: active ? 'var(--brand)' : 'var(--text-3)',
                    }}>
                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: active ? p.color : 'var(--border-bright)', flexShrink: 0 }} />
                    {p.label}
                    {apiStatus[id] && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-400" />}
                  </button>
                )
              })}
            </div>
            <button onClick={handleApiShare} disabled={apiLoading || !selected}
              className="btn-primary w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-white text-sm font-semibold disabled:opacity-40">
              {apiLoading ? <RefreshCw size={13} className="animate-spin" /> : <Send size={13} />}
              {apiLoading ? 'Sharing...' : 'Auto-Share via API'}
            </button>
          </div>

          {/* Copy captions */}
          {selectedBlock && (
            <div>
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Copy Captions</div>
              <div className="space-y-1.5">
                {Object.keys(PLATFORMS).map(id => (
                  <button key={id} onClick={() => handleCopy(id)}
                    className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs border border-white/6 hover:border-white/12 hover:bg-white/4 transition-colors text-slate-400 hover:text-slate-200">
                    <span className="flex items-center gap-2">
                      <span style={{ width: 7, height: 7, borderRadius: '50%', background: PLATFORMS[id].color, display: 'inline-block' }} />
                      {PLATFORMS[id].label}
                    </span>
                    {copied === id
                      ? <span className="flex items-center gap-1 text-emerald-400"><CheckCircle size={10} /> Copied!</span>
                      : <span className="flex items-center gap-1"><Copy size={10} /> Copy</span>}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* API share results */}
          {shareResult && (
            <div className="space-y-1.5">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Results</div>
              {shareResult.map((r, i) => (
                <div key={i} className="flex items-center justify-between px-3 py-2 rounded-lg bg-white/3 border border-white/6 text-xs">
                  <span className="text-slate-300">{PLATFORMS[r.platform]?.label || r.platform}</span>
                  {r.success
                    ? <span className="flex items-center gap-1 text-emerald-400"><CheckCircle size={10} /> Done</span>
                    : <span className="flex items-center gap-1 text-red-400"><XCircle size={10} /> {r.error?.slice(0, 30)}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
