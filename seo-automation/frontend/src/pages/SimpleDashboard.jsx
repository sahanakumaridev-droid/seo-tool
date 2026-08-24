import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, CheckCircle, Loader, ArrowRight, LogOut, Share2, Users } from 'lucide-react'
import { generateBulk, listPages } from '../api'

export default function SimpleDashboard() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1) // 1=input, 2=generating, 3=results
  const [form, setForm] = useState({
    businessType: 'Plumbing',
    locations: 'San Diego, La Jolla, Chula Vista',
    numPages: 10,
  })
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')
  const [expandedPage, setExpandedPage] = useState(null)
  const [showShareMenu, setShowShareMenu] = useState(false)
  const [sharePreview, setSharePreview] = useState(null) // For showing post preview

  const handleGenerate = async () => {
    setStep(2)
    setError('')
    
    try {
      // Step 1: Generate content
      const cities = form.locations.split(',').map(c => c.trim())
      await generateBulk({
        business_type: form.businessType,
        base_location: cities[0],
        cities: cities,
        num_cities: cities.length,
      })
      
      // Wait a moment then fetch the generated pages
      await new Promise(resolve => setTimeout(resolve, 2000))
      const pagesRes = await listPages(0, 100)
      const pages = pagesRes.data
      
      if (pages.length === 0) {
        throw new Error('No pages were generated. Please try again.')
      }
      
      // Extract SEO blocks from pages
      const seoBlocks = pages.slice(0, form.numPages).map(page => page.seo_block)
      
      setResults({
        pagesGenerated: seoBlocks.length,
        pages: pages.slice(0, form.numPages),
        seoBlocks: seoBlocks,
      })
      setStep(3)
      
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Generation failed')
      setStep(1)
    }
  }

  const handleReset = () => {
    setStep(1)
    setResults(null)
    setError('')
    setExpandedPage(null)
  }

  const handleLogout = () => {
    localStorage.removeItem('seo_auth')
    window.location.href = '/'  // Force full page reload to reset auth state
  }

  const handleShareToSocial = (platform, pageIndex = null) => {
    // ZeOrbit social media accounts
    const SOCIAL_ACCOUNTS = {
      facebook: 'https://www.facebook.com/zeorbit.web.designers.mobileapp.developers',
      facebookPage: 'https://www.facebook.com/zeorbit.web.designers.mobileapp.developers',
      twitter: 'https://twitter.com/orbit_ze',
      linkedin: 'https://www.linkedin.com/company/zeorbit/',
      instagram: 'https://www.instagram.com/zeorbit/',
      youtube: 'https://www.youtube.com/@ZeOrbit-Firm/',
      pinterest: 'https://www.pinterest.com/zeorbitsd/',
    }

    if (!results) return

    // Get the specific page or first page
    const block = pageIndex !== null ? results.seoBlocks[pageIndex] : results.seoBlocks[0]
    
    // Create share content
    const postTitle = `${block.business_type} in ${block.city}, ${block.state}`
    const postDescription = block.meta_description
    
    // For now, use ZeOrbit website. In production, this would be the actual published page URL
    const postUrl = `https://zeorbit.com/services/${block.slug}`

    // Platform-specific share URLs
    const shareUrls = {
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(postUrl)}&quote=${encodeURIComponent(postTitle + '\n\n' + postDescription)}`,
      twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(postTitle + '\n\n' + postDescription.substring(0, 200) + '...')}&url=${encodeURIComponent(postUrl)}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(postUrl)}`,
      pinterest: `https://pinterest.com/pin/create/button/?url=${encodeURIComponent(postUrl)}&description=${encodeURIComponent(postTitle)}&media=${encodeURIComponent(block.featured_image_url)}`,
    }

    // Open share dialog
    if (shareUrls[platform]) {
      window.open(shareUrls[platform], '_blank', 'width=600,height=400')
    } else {
      // For Instagram and YouTube, just open the account (they don't support URL sharing)
      window.open(SOCIAL_ACCOUNTS[platform], '_blank')
    }
    
    setShowShareMenu(false)
  }

  const handleCopyContent = (pageIndex) => {
    const block = results.seoBlocks[pageIndex]
    const content = `
${block.title}

${block.meta_description}

${block.intro}

${block.content}

FAQs:
${block.faqs.map(faq => `Q: ${faq.question}\nA: ${faq.answer}`).join('\n\n')}

Keywords: ${block.keywords.primary}, ${block.keywords.secondary.join(', ')}

Image: ${block.featured_image_url}
    `.trim()
    
    navigator.clipboard.writeText(content).then(() => {
      alert('✅ Content copied to clipboard! You can now paste it anywhere.')
    }).catch(() => {
      alert('❌ Failed to copy content')
    })
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0B0F1A',
    }}>
      {/* App Bar - Like Landing Page Navbar */}
      <div style={{
        background: '#0F172A',
        padding: '16px 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            background: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Zap size={22} color="white" />
          </div>
          <span style={{ fontSize: '20px', fontWeight: '700', color: 'white' }}>
            ZEORBIT
          </span>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Leads Button */}
          <button
            onClick={() => alert('Leads feature coming soon!')}
            style={{
              padding: '10px 20px',
              background: 'transparent',
              color: '#F1F5F9',
              border: '1px solid rgba(241, 245, 249, 0.2)',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s',
            }}
            onMouseEnter={e => {
              e.target.style.background = 'rgba(241, 245, 249, 0.1)'
              e.target.style.borderColor = 'rgba(241, 245, 249, 0.3)'
            }}
            onMouseLeave={e => {
              e.target.style.background = 'transparent'
              e.target.style.borderColor = 'rgba(241, 245, 249, 0.2)'
            }}
          >
            <Users size={16} />
            Leads
          </button>

          {/* Share Button with Dropdown */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowShareMenu(!showShareMenu)}
              disabled={!results}
              style={{
                padding: '10px 20px',
                background: results ? 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)' : '#4B5563',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: results ? 'pointer' : 'not-allowed',
                fontSize: '14px',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'all 0.2s',
                opacity: results ? 1 : 0.5,
              }}
              onMouseEnter={e => {
                if (results) e.target.style.transform = 'translateY(-1px)'
              }}
              onMouseLeave={e => {
                e.target.style.transform = 'translateY(0)'
              }}
            >
              <Share2 size={16} />
              Share
            </button>

            {/* Share Dropdown Menu */}
            {showShareMenu && results && (
              <div style={{
                position: 'absolute',
                top: '50px',
                right: 0,
                background: '#111827',
                border: '1px solid #1E2D42',
                borderRadius: '12px',
                boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
                padding: '8px',
                minWidth: '200px',
                zIndex: 1000,
              }}>
                <button onClick={() => handleShareToSocial('facebook')} style={{ width: '100%', padding: '10px 16px', background: 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', fontSize: '14px', color: '#F1F5F9', transition: 'background 0.2s' }} onMouseEnter={e => e.target.style.background = '#1A2235'} onMouseLeave={e => e.target.style.background = 'transparent'}>
                  Facebook Profile
                </button>
                <button onClick={() => handleShareToSocial('facebookPage')} style={{ width: '100%', padding: '10px 16px', background: 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', fontSize: '14px', color: '#F1F5F9', transition: 'background 0.2s' }} onMouseEnter={e => e.target.style.background = '#1A2235'} onMouseLeave={e => e.target.style.background = 'transparent'}>
                  Facebook Page
                </button>
                <button onClick={() => handleShareToSocial('twitter')} style={{ width: '100%', padding: '10px 16px', background: 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', fontSize: '14px', color: '#F1F5F9', transition: 'background 0.2s' }} onMouseEnter={e => e.target.style.background = '#1A2235'} onMouseLeave={e => e.target.style.background = 'transparent'}>
                  Twitter/X
                </button>
                <button onClick={() => handleShareToSocial('linkedin')} style={{ width: '100%', padding: '10px 16px', background: 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', fontSize: '14px', color: '#F1F5F9', transition: 'background 0.2s' }} onMouseEnter={e => e.target.style.background = '#1A2235'} onMouseLeave={e => e.target.style.background = 'transparent'}>
                  LinkedIn
                </button>
                <button onClick={() => handleShareToSocial('instagram')} style={{ width: '100%', padding: '10px 16px', background: 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', fontSize: '14px', color: '#F1F5F9', transition: 'background 0.2s' }} onMouseEnter={e => e.target.style.background = '#1A2235'} onMouseLeave={e => e.target.style.background = 'transparent'}>
                  Instagram
                </button>
                <button onClick={() => handleShareToSocial('pinterest')} style={{ width: '100%', padding: '10px 16px', background: 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', fontSize: '14px', color: '#F1F5F9', transition: 'background 0.2s' }} onMouseEnter={e => e.target.style.background = '#1A2235'} onMouseLeave={e => e.target.style.background = 'transparent'}>
                  Pinterest
                </button>
                <button onClick={() => handleShareToSocial('youtube')} style={{ width: '100%', padding: '10px 16px', background: 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', fontSize: '14px', color: '#F1F5F9', transition: 'background 0.2s' }} onMouseEnter={e => e.target.style.background = '#1A2235'} onMouseLeave={e => e.target.style.background = 'transparent'}>
                  YouTube
                </button>
              </div>
            )}
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            style={{
              padding: '10px 20px',
              background: 'transparent',
              color: '#F1F5F9',
              border: '1px solid rgba(241, 245, 249, 0.2)',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s',
            }}
            onMouseEnter={e => {
              e.target.style.background = 'rgba(241, 245, 249, 0.1)'
              e.target.style.borderColor = 'rgba(241, 245, 249, 0.3)'
            }}
            onMouseLeave={e => {
              e.target.style.background = 'transparent'
              e.target.style.borderColor = 'rgba(241, 245, 249, 0.2)'
            }}
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{
        width: '100%',
        maxWidth: '900px',
        margin: '0 auto',
        padding: '40px 20px',
      }}>
        {/* Header */}
        <div style={{
          background: 'transparent',
          padding: '32px 0',
          textAlign: 'center',
          marginBottom: '32px',
        }}>
          <h1 style={{
            fontSize: '36px',
            fontWeight: '900',
            color: '#F1F5F9',
            margin: '0 0 12px',
            letterSpacing: '-0.5px',
          }}>
            SEO Automation
          </h1>
          <p style={{
            fontSize: '18px',
            color: '#94A3B8',
            margin: 0,
          }}>
            Generate → Share → Get Leads
          </p>
        </div>

        {/* Content */}
        <div style={{
          background: '#111827',
          borderRadius: '16px',
          padding: '40px',
          boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
          border: '1px solid #1E2D42',
        }}>
          
          {/* STEP 1: INPUT FORM */}
          {step === 1 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div>
                <label style={{ 
                  display: 'block', 
                  fontSize: '14px', 
                  fontWeight: '600', 
                  color: '#CBD5E1',
                  marginBottom: '8px',
                }}>
                  🏢 Business Type
                </label>
                <input
                  type="text"
                  value={form.businessType}
                  onChange={e => setForm({ ...form, businessType: e.target.value })}
                  placeholder="e.g., Plumbing, Electrician, HVAC"
                  style={{
                    width: '100%',
                    padding: '14px 16px',
                    fontSize: '16px',
                    border: '2px solid #2A3B57',
                    background: '#1A2235',
                    color: '#F1F5F9',
                    borderRadius: '12px',
                    outline: 'none',
                    transition: 'border-color 0.2s',
                    boxSizing: 'border-box',
                  }}
                  onFocus={e => e.target.style.borderColor = '#2563EB'}
                  onBlur={e => e.target.style.borderColor = '#2A3B57'}
                />
              </div>

              <div>
                <label style={{ 
                  display: 'block', 
                  fontSize: '14px', 
                  fontWeight: '600', 
                  color: '#CBD5E1',
                  marginBottom: '8px',
                }}>
                  📍 Locations (comma-separated)
                </label>
                <textarea
                  value={form.locations}
                  onChange={e => setForm({ ...form, locations: e.target.value })}
                  placeholder="San Diego, La Jolla, Chula Vista, Oceanside..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '14px 16px',
                    fontSize: '16px',
                    border: '2px solid #2A3B57',
                    background: '#1A2235',
                    color: '#F1F5F9',
                    borderRadius: '12px',
                    outline: 'none',
                    transition: 'border-color 0.2s',
                    resize: 'vertical',
                    fontFamily: 'inherit',
                    boxSizing: 'border-box',
                  }}
                  onFocus={e => e.target.style.borderColor = '#2563EB'}
                  onBlur={e => e.target.style.borderColor = '#2A3B57'}
                />
              </div>

              <div>
                <label style={{ 
                  display: 'block', 
                  fontSize: '14px', 
                  fontWeight: '600', 
                  color: '#CBD5E1',
                  marginBottom: '8px',
                }}>
                  📄 Number of Pages
                </label>
                <input
                  type="number"
                  value={form.numPages}
                  onChange={e => setForm({ ...form, numPages: parseInt(e.target.value) || 1 })}
                  min="1"
                  max="100"
                  style={{
                    width: '100%',
                    padding: '14px 16px',
                    fontSize: '16px',
                    border: '2px solid #2A3B57',
                    background: '#1A2235',
                    color: '#F1F5F9',
                    borderRadius: '12px',
                    outline: 'none',
                    transition: 'border-color 0.2s',
                    boxSizing: 'border-box',
                  }}
                  onFocus={e => e.target.style.borderColor = '#2563EB'}
                  onBlur={e => e.target.style.borderColor = '#2A3B57'}
                />
              </div>

              {error && (
                <div style={{
                  padding: '12px 16px',
                  background: 'rgba(248,113,113,0.14)',
                  border: '1px solid rgba(248,113,113,0.30)',
                  borderRadius: '12px',
                  color: '#F87171',
                  fontSize: '14px',
                }}>
                  ⚠️ {error}
                </div>
              )}

              <button
                onClick={handleGenerate}
                style={{
                  width: '100%',
                  padding: '18px',
                  background: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
                  color: 'white',
                  fontSize: '18px',
                  fontWeight: '700',
                  border: 'none',
                  borderRadius: '12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '10px',
                  boxShadow: '0 4px 16px rgba(59, 130, 246, 0.4)',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                }}
                onMouseEnter={e => {
                  e.target.style.transform = 'translateY(-2px)'
                  e.target.style.boxShadow = '0 8px 24px rgba(59, 130, 246, 0.5)'
                }}
                onMouseLeave={e => {
                  e.target.style.transform = 'translateY(0)'
                  e.target.style.boxShadow = '0 4px 16px rgba(59, 130, 246, 0.4)'
                }}
              >
                <Zap size={22} />
                Generate SEO Content
                <ArrowRight size={22} />
              </button>

              <div style={{
                padding: '16px',
                background: 'rgba(59,130,246,0.10)',
                border: '1px solid rgba(59,130,246,0.25)',
                borderRadius: '12px',
                fontSize: '13px',
                color: '#93C5FD',
                lineHeight: '1.6',
              }}>
                <strong>✨ What happens next:</strong><br />
                1. AI generates SEO content for each location<br />
                2. Creates optimized meta tags and keywords<br />
                3. Generates images automatically<br />
                4. Saves all pages to the database
              </div>
            </div>
          )}

          {/* STEP 2: GENERATING */}
          {step === 2 && (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px 0',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '24px',
            }}>
              <Loader 
                size={64} 
                style={{ 
                  color: '#3B82F6',
                  animation: 'spin 1s linear infinite',
                }} 
              />
              <div>
                <h2 style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#F1F5F9',
                  margin: '0 0 8px',
                }}>
                  Generating Your Content...
                </h2>
                <p style={{
                  fontSize: '16px',
                  color: '#94A3B8',
                  margin: 0,
                }}>
                  This may take 1-2 minutes
                </p>
              </div>
              <div style={{
                width: '100%',
                maxWidth: '300px',
                height: '8px',
                background: '#1A2235',
                borderRadius: '4px',
                overflow: 'hidden',
              }}>
                <div style={{
                  height: '100%',
                  background: 'linear-gradient(90deg, #3B82F6, #2563EB)',
                  animation: 'progress 2s ease-in-out infinite',
                  width: '60%',
                }} />
              </div>
            </div>
          )}

          {/* STEP 3: RESULTS */}
          {step === 3 && results && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
              {/* Success Header */}
              <div style={{ textAlign: 'center', padding: '24px 0' }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'linear-gradient(135deg, #10b981, #059669)',
                  borderRadius: '50%',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px',
                }}>
                  <CheckCircle size={48} color="white" />
                </div>
                <h2 style={{
                  fontSize: '32px',
                  fontWeight: '800',
                  color: '#F1F5F9',
                  margin: '0 0 8px',
                }}>
                  Success! 🎉
                </h2>
                <p style={{
                  fontSize: '18px',
                  color: '#94A3B8',
                  margin: 0,
                }}>
                  {results.pagesGenerated} SEO pages generated with images and keywords
                </p>
              </div>

              {/* Generated Pages - Full Preview */}
              <div>
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: '700',
                  color: '#F1F5F9',
                  marginBottom: '24px',
                  paddingBottom: '12px',
                  borderBottom: '2px solid #1E2D42',
                }}>
                  📄 Generated Content
                </h3>

                {results.seoBlocks.map((block, i) => (
                  <div key={i} style={{
                    marginBottom: '48px',
                    background: '#111827',
                    borderRadius: '16px',
                    overflow: 'hidden',
                    boxShadow: '0 4px 16px rgba(0,0,0,0.4)',
                    border: '1px solid #1E2D42',
                  }}>
                    {/* Featured Image - Large */}
                    <div style={{ position: 'relative', width: '100%', height: '400px', overflow: 'hidden', background: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)' }}>
                      <img 
                        src={block.featured_image_url || ''}
                        alt={
                          block.in_content_images?.find((im) => im.is_featured)?.alt_text
                          || block.h1
                          || block.title
                          || 'Website design'
                        }
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover',
                          display: block.featured_image_url ? 'block' : 'none',
                        }}
                        onError={(e) => {
                          e.target.style.display = 'none'
                        }}
                        loading="lazy"
                      />
                      {/* Gradient Overlay */}
                      <div style={{
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: '120px',
                        background: 'linear-gradient(to top, rgba(0,0,0,0.7), transparent)',
                      }} />
                      {/* Page Number Badge */}
                      <div style={{
                        position: 'absolute',
                        top: '20px',
                        left: '20px',
                        padding: '8px 16px',
                        background: 'rgba(59, 130, 246, 0.95)',
                        color: 'white',
                        borderRadius: '8px',
                        fontSize: '14px',
                        fontWeight: '700',
                      }}>
                        Page {i + 1} of {results.pagesGenerated}
                      </div>
                    </div>

                    {/* Content Details */}
                    <div style={{ padding: '32px' }}>
                      {/* Title */}
                      <h2 style={{
                        fontSize: '28px',
                        fontWeight: '800',
                        color: '#F1F5F9',
                        margin: '0 0 8px',
                        lineHeight: '1.3',
                      }}>
                        {block.title}
                      </h2>

                      {/* Location */}
                      <div style={{ 
                        fontSize: '16px', 
                        color: '#94A3B8',
                        marginBottom: '24px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}>
                        <span style={{ fontSize: '18px' }}>📍</span>
                        <span>{block.city}, {block.state}</span>
                      </div>

                      {/* Meta Description */}
                      <div style={{ marginBottom: '24px' }}>
                        <div style={{ 
                          fontSize: '12px', 
                          fontWeight: '700', 
                          color: '#94A3B8',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          marginBottom: '8px',
                        }}>
                          Meta Description
                        </div>
                        <p style={{ 
                          fontSize: '16px', 
                          color: '#CBD5E1',
                          lineHeight: '1.7',
                          margin: 0,
                          padding: '16px',
                          background: '#1A2235',
                          borderRadius: '8px',
                          borderLeft: '4px solid #3B82F6',
                        }}>
                          {block.meta_description}
                        </p>
                      </div>

                      {/* Content Preview */}
                      <div style={{ marginBottom: '24px' }}>
                        <div style={{ 
                          fontSize: '12px', 
                          fontWeight: '700', 
                          color: '#94A3B8',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          marginBottom: '8px',
                        }}>
                          Content Preview
                        </div>
                        <div style={{ 
                          fontSize: '15px',
                          color: '#CBD5E1',
                          lineHeight: '1.8',
                          padding: '16px',
                          background: '#1A2235',
                          borderRadius: '8px',
                        }}>
                          {block.intro || block.content.substring(0, 400)}...
                        </div>
                      </div>

                      {/* Keywords */}
                      <div style={{ marginBottom: '24px' }}>
                        <div style={{ 
                          fontSize: '12px', 
                          fontWeight: '700', 
                          color: '#94A3B8',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          marginBottom: '12px',
                        }}>
                          SEO Keywords
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                          {/* Primary Keyword */}
                          <span style={{
                            padding: '8px 16px',
                            background: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
                            color: 'white',
                            fontSize: '13px',
                            borderRadius: '8px',
                            fontWeight: '600',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                          }}>
                            <span style={{ fontSize: '16px' }}>⭐</span>
                            {block.keywords.primary}
                          </span>
                          {/* Secondary Keywords */}
                          {block.keywords.secondary.slice(0, 5).map((kw, idx) => (
                            <span key={idx} style={{
                              padding: '8px 16px',
                              background: 'rgba(59,130,246,0.10)',
                              color: '#93C5FD',
                              fontSize: '13px',
                              borderRadius: '8px',
                              fontWeight: '500',
                              border: '1px solid rgba(59,130,246,0.25)',
                            }}>
                              {kw}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* FAQs Section */}
                      {block.faqs && block.faqs.length > 0 && (
                        <div style={{ marginBottom: '24px' }}>
                          <div style={{ 
                            fontSize: '12px', 
                            fontWeight: '700', 
                            color: '#94A3B8',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            marginBottom: '16px',
                          }}>
                            Frequently Asked Questions ({block.faqs.length})
                          </div>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {block.faqs.map((faq, faqIdx) => (
                              <div key={faqIdx} style={{
                                padding: '20px',
                                background: '#1A2235',
                                borderRadius: '12px',
                                border: '1px solid #1E2D42',
                              }}>
                                <div style={{
                                  fontSize: '16px',
                                  fontWeight: '700',
                                  color: '#F1F5F9',
                                  marginBottom: '12px',
                                }}>
                                  {faq.question}
                                </div>
                                <div style={{
                                  fontSize: '15px',
                                  color: '#CBD5E1',
                                  lineHeight: '1.7',
                                }}>
                                  {faq.answer}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Stats Row */}
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(3, 1fr)',
                        gap: '16px',
                        padding: '20px',
                        background: '#1A2235',
                        borderRadius: '12px',
                        marginBottom: '20px',
                      }}>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: '24px', fontWeight: '800', color: '#3B82F6', marginBottom: '4px' }}>
                            {block.readability_score || 85}
                          </div>
                          <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '600' }}>
                            SEO Score
                          </div>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: '24px', fontWeight: '800', color: '#10B981', marginBottom: '4px' }}>
                            {block.faqs?.length || 0}
                          </div>
                          <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '600' }}>
                            FAQs
                          </div>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: '24px', fontWeight: '800', color: '#F59E0B', marginBottom: '4px' }}>
                            {block.h2s?.length || 0}
                          </div>
                          <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '600' }}>
                            Headings
                          </div>
                        </div>
                      </div>

                      {/* Page Actions */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {/* Primary Actions */}
                        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                          <button
                            onClick={() => handleCopyContent(i)}
                            style={{
                              flex: 1,
                              minWidth: '150px',
                              padding: '12px 20px',
                              background: '#111827',
                              color: '#3B82F6',
                              fontSize: '14px',
                              fontWeight: '600',
                              border: '2px solid #3B82F6',
                              borderRadius: '10px',
                              cursor: 'pointer',
                              transition: 'all 0.2s',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              gap: '8px',
                            }}
                            onMouseEnter={e => {
                              e.target.style.background = '#3B82F6'
                              e.target.style.color = 'white'
                            }}
                            onMouseLeave={e => {
                              e.target.style.background = '#111827'
                              e.target.style.color = '#3B82F6'
                            }}
                          >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                            </svg>
                            Copy Content
                          </button>
                          
                          <button
                            onClick={() => {
                              // Copy Open Graph and Twitter Card meta tags
                              const pageUrl = `https://yourwebsite.com/${block.slug}`
                              const imageUrl = block.featured_image_url
                              const metaTags = `<!-- Open Graph Meta Tags (Facebook, WhatsApp, LinkedIn) -->
<meta property="og:type" content="website">
<meta property="og:url" content="${pageUrl}">
<meta property="og:title" content="${block.title}">
<meta property="og:description" content="${block.meta_description}">
<meta property="og:image" content="${imageUrl}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${block.business_type} in ${block.city}, ${block.state}">
<meta property="og:site_name" content="Your Business Name">

<!-- Twitter Card Meta Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:url" content="${pageUrl}">
<meta name="twitter:title" content="${block.title}">
<meta name="twitter:description" content="${block.meta_description}">
<meta name="twitter:image" content="${imageUrl}">
<meta name="twitter:image:alt" content="${block.business_type} in ${block.city}, ${block.state}">
<meta name="twitter:site" content="@yourtwitterhandle">`
                              
                              navigator.clipboard.writeText(metaTags).then(() => {
                                alert('✅ Social Media Meta Tags Copied!\n\n📋 Paste these tags in your page\'s <head> section.\n\nThese FREE tags will show your image and title when shared on:\n• WhatsApp\n• Facebook\n• Twitter/X\n• LinkedIn\n• Instagram\n\nNo API needed!')
                              }).catch(() => {
                                alert('❌ Failed to copy meta tags')
                              })
                            }}
                            style={{
                              flex: 1,
                              minWidth: '150px',
                              padding: '12px 20px',
                              background: '#111827',
                              color: '#2563EB',
                              fontSize: '14px',
                              fontWeight: '600',
                              border: '2px solid #2563EB',
                              borderRadius: '10px',
                              cursor: 'pointer',
                              transition: 'all 0.2s',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              gap: '8px',
                            }}
                            onMouseEnter={e => {
                              e.target.style.background = '#2563EB'
                              e.target.style.color = 'white'
                            }}
                            onMouseLeave={e => {
                              e.target.style.background = '#111827'
                              e.target.style.color = '#2563EB'
                            }}
                          >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                            </svg>
                            Copy Meta Tags
                          </button>
                          
                          <button
                            onClick={() => {
                              // Show preview modal
                              setSharePreview({
                                pageIndex: i,
                                block: block
                              })
                            }}
                            style={{
                              flex: 1,
                              minWidth: '150px',
                              padding: '12px 20px',
                              background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                              color: 'white',
                              fontSize: '14px',
                              fontWeight: '600',
                              border: 'none',
                              borderRadius: '10px',
                              cursor: 'pointer',
                              transition: 'all 0.2s',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              gap: '8px',
                            }}
                            onMouseEnter={e => {
                              e.target.style.transform = 'translateY(-2px)'
                              e.target.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.4)'
                            }}
                            onMouseLeave={e => {
                              e.target.style.transform = 'translateY(0)'
                              e.target.style.boxShadow = 'none'
                            }}
                          >
                            <Share2 size={16} />
                            Share on Social Media
                          </button>
                        </div>
                        
                        {/* Workflow Guide */}
                        <div style={{
                          padding: '12px 16px',
                          background: 'rgba(59,130,246,0.10)',
                          border: '1px solid rgba(59,130,246,0.25)',
                          borderRadius: '8px',
                          fontSize: '12px',
                          color: '#93C5FD',
                          lineHeight: '1.6',
                        }}>
                          <strong>📌 SEO Workflow:</strong> 1) Copy Meta Tags → 2) Add to your page's &lt;head&gt; → 3) Publish → 4) Share! (Image + title show automatically)
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', paddingTop: '24px', flexWrap: 'wrap' }}>
                <button
                  onClick={() => {
                    // Export as JSON
                    const dataStr = JSON.stringify(results.seoBlocks, null, 2)
                    const dataBlob = new Blob([dataStr], { type: 'application/json' })
                    const url = URL.createObjectURL(dataBlob)
                    const link = document.createElement('a')
                    link.href = url
                    link.download = `seo-content-${form.businessType.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}.json`
                    link.click()
                    URL.revokeObjectURL(url)
                  }}
                  style={{
                    padding: '16px 32px',
                    background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                    color: 'white',
                    fontSize: '16px',
                    fontWeight: '600',
                    border: 'none',
                    borderRadius: '12px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                  onMouseEnter={e => {
                    e.target.style.transform = 'translateY(-2px)'
                    e.target.style.boxShadow = '0 8px 24px rgba(16, 185, 129, 0.4)'
                  }}
                  onMouseLeave={e => {
                    e.target.style.transform = 'translateY(0)'
                    e.target.style.boxShadow = 'none'
                  }}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                  Download JSON
                </button>
                
                <button
                  onClick={handleReset}
                  style={{
                    padding: '16px 32px',
                    background: '#111827',
                    color: '#3B82F6',
                    fontSize: '16px',
                    fontWeight: '600',
                    border: '2px solid #3B82F6',
                    borderRadius: '12px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={e => {
                    e.target.style.background = '#3B82F6'
                    e.target.style.color = 'white'
                  }}
                  onMouseLeave={e => {
                    e.target.style.background = '#111827'
                    e.target.style.color = '#3B82F6'
                  }}
                >
                  Generate More Content
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Share Preview Modal */}
      {sharePreview && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px',
        }} onClick={() => setSharePreview(null)}>
          <div style={{
            background: '#111827',
            borderRadius: '16px',
            maxWidth: '600px',
            width: '100%',
            maxHeight: '90vh',
            overflow: 'auto',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          }} onClick={e => e.stopPropagation()}>
            {/* Modal Header */}
            <div style={{
              padding: '24px',
              borderBottom: '1px solid #1E2D42',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}>
              <h3 style={{ fontSize: '20px', fontWeight: '700', color: '#F1F5F9', margin: 0 }}>
                📱 Social Media Preview
              </h3>
              <button onClick={() => setSharePreview(null)} style={{
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                color: '#94A3B8',
                padding: '4px',
              }}>×</button>
            </div>

            {/* Post Preview */}
            <div style={{ padding: '24px' }}>
              {/* Preview Card - Looks like a social media post */}
              <div style={{
                border: '1px solid #1E2D42',
                borderRadius: '12px',
                overflow: 'hidden',
                marginBottom: '24px',
              }}>
                {/* Post Image */}
                <img 
                  src={sharePreview.block.featured_image_url}
                  alt={sharePreview.block.title}
                  style={{
                    width: '100%',
                    height: '300px',
                    objectFit: 'cover',
                  }}
                />
                
                {/* Post Content */}
                <div style={{ padding: '16px' }}>
                  <h4 style={{
                    fontSize: '18px',
                    fontWeight: '700',
                    color: '#F1F5F9',
                    margin: '0 0 8px',
                    lineHeight: '1.4',
                  }}>
                    {sharePreview.block.title}
                  </h4>
                  <p style={{
                    fontSize: '14px',
                    color: '#94A3B8',
                    lineHeight: '1.6',
                    margin: '0 0 12px',
                  }}>
                    {sharePreview.block.meta_description}
                  </p>
                  <div style={{
                    fontSize: '13px',
                    color: '#3B82F6',
                    fontWeight: '600',
                  }}>
                    yourwebsite.com/{sharePreview.block.slug}
                  </div>
                </div>
              </div>

              {/* Share Buttons */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '12px',
                marginBottom: '16px',
              }}>
                <button
                  onClick={() => {
                    const url = prompt('Enter your website URL:', `https://yourwebsite.com/${sharePreview.block.slug}`)
                    if (url) {
                      window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}&quote=${encodeURIComponent(sharePreview.block.title + '\n\n' + sharePreview.block.meta_description)}`, '_blank', 'width=600,height=400')
                    }
                  }}
                  style={{
                    padding: '12px',
                    background: '#1877F2',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                  }}
                >
                  📘 Share on Facebook
                </button>
                
                <button
                  onClick={() => {
                    const url = prompt('Enter your website URL:', `https://yourwebsite.com/${sharePreview.block.slug}`)
                    if (url) {
                      window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(sharePreview.block.title + '\n\n' + sharePreview.block.meta_description.substring(0, 200))}&url=${encodeURIComponent(url)}`, '_blank', 'width=600,height=400')
                    }
                  }}
                  style={{
                    padding: '12px',
                    background: '#000000',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                  }}
                >
                  𝕏 Share on Twitter/X
                </button>
                
                <button
                  onClick={() => {
                    const url = prompt('Enter your website URL:', `https://yourwebsite.com/${sharePreview.block.slug}`)
                    if (url) {
                      window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`, '_blank', 'width=600,height=400')
                    }
                  }}
                  style={{
                    padding: '12px',
                    background: '#0A66C2',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                  }}
                >
                  💼 Share on LinkedIn
                </button>
                
                <button
                  onClick={async () => {
                    // Check if auto-posting is configured
                    const statusCheck = confirm(
                      '📸 Instagram Auto-Post\n\n' +
                      'Do you want to automatically post to Instagram?\n\n' +
                      '✅ YES = Auto-post to your Instagram Business account\n' +
                      '❌ NO = Copy caption + download image (manual posting)\n\n' +
                      'Note: Auto-posting requires Instagram Business account setup.'
                    )
                    
                    if (statusCheck) {
                      // Try automatic posting
                      try {
                        const instagramCaption = `${sharePreview.block.title}\n\n📍 ${sharePreview.block.city}, ${sharePreview.block.state}\n\n🔗 Link in bio\n\n#${sharePreview.block.business_type.replace(/\s+/g, '')} #${sharePreview.block.city.replace(/\s+/g, '')} #LocalBusiness #SEO`
                        
                        const response = await fetch('http://localhost:8000/api/instagram/post', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({
                            image_url: sharePreview.block.featured_image_url,
                            caption: instagramCaption
                          })
                        })
                        
                        const result = await response.json()
                        
                        if (result.success) {
                          alert(`✅ Posted to Instagram!\n\n📸 Post ID: ${result.post_id}\n🔗 View: ${result.permalink}\n\nYour post is now live on Instagram!`)
                          setSharePreview(null) // Close modal
                        } else {
                          throw new Error(result.message || 'Auto-posting failed')
                        }
                      } catch (error) {
                        // Fallback to manual posting
                        const fallback = confirm(
                          '⚠️ Auto-posting not configured\n\n' +
                          'Instagram Business API is not set up yet.\n\n' +
                          'Would you like to:\n' +
                          '✅ YES = Copy caption + download image (manual posting)\n' +
                          '❌ NO = Cancel'
                        )
                        
                        if (fallback) {
                          // Manual posting fallback
                          const instagramCaption = `${sharePreview.block.title}\n\n📍 ${sharePreview.block.city}, ${sharePreview.block.state}\n\n🔗 Link in bio\n\n#${sharePreview.block.business_type.replace(/\s+/g, '')} #${sharePreview.block.city.replace(/\s+/g, '')} #LocalBusiness #SEO`
                          
                          try {
                            await navigator.clipboard.writeText(instagramCaption)
                            
                            // Download the image
                            const response = await fetch(sharePreview.block.featured_image_url)
                            const blob = await response.blob()
                            const url = URL.createObjectURL(blob)
                            const link = document.createElement('a')
                            link.href = url
                            link.download = `instagram-${sharePreview.block.business_type.toLowerCase().replace(/\s+/g, '-')}-${sharePreview.block.city.toLowerCase()}.jpg`
                            link.click()
                            URL.revokeObjectURL(url)
                            
                            alert('✅ Instagram Ready!\n\n📋 Caption copied to clipboard\n📸 Image downloaded\n\nNow:\n1. Open Instagram\n2. Create new post\n3. Upload the downloaded image\n4. Paste the caption (Ctrl+V / Cmd+V)\n5. Post!')
                          } catch (error) {
                            alert('✅ Caption copied!\n\n📋 Caption is in your clipboard\n📸 Right-click the image above and "Save Image As..."\n\nThen post to Instagram!')
                          }
                        }
                      }
                    } else {
                      // Manual posting (user chose NO)
                      const instagramCaption = `${sharePreview.block.title}\n\n📍 ${sharePreview.block.city}, ${sharePreview.block.state}\n\n🔗 Link in bio\n\n#${sharePreview.block.business_type.replace(/\s+/g, '')} #${sharePreview.block.city.replace(/\s+/g, '')} #LocalBusiness #SEO`
                      
                      try {
                        await navigator.clipboard.writeText(instagramCaption)
                        
                        // Download the image
                        const response = await fetch(sharePreview.block.featured_image_url)
                        const blob = await response.blob()
                        const url = URL.createObjectURL(blob)
                        const link = document.createElement('a')
                        link.href = url
                        link.download = `instagram-${sharePreview.block.business_type.toLowerCase().replace(/\s+/g, '-')}-${sharePreview.block.city.toLowerCase()}.jpg`
                        link.click()
                        URL.revokeObjectURL(url)
                        
                        alert('✅ Instagram Ready!\n\n📋 Caption copied to clipboard\n📸 Image downloaded\n\nNow:\n1. Open Instagram\n2. Create new post\n3. Upload the downloaded image\n4. Paste the caption (Ctrl+V / Cmd+V)\n5. Post!')
                      } catch (error) {
                        alert('✅ Caption copied!\n\n📋 Caption is in your clipboard\n📸 Right-click the image above and "Save Image As..."\n\nThen post to Instagram!')
                      }
                    }
                  }}
                  style={{
                    padding: '12px',
                    background: 'linear-gradient(45deg, #F58529, #DD2A7B, #8134AF)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                  }}
                >
                  📸 Post to Instagram
                </button>
              </div>

              {/* Instagram Caption Preview */}
              <div style={{
                padding: '16px',
                background: 'rgba(251,191,36,0.14)',
                border: '1px solid rgba(251,191,36,0.30)',
                borderRadius: '8px',
                marginBottom: '16px',
              }}>
                <div style={{ fontSize: '13px', fontWeight: '700', color: '#FBBF24', marginBottom: '8px' }}>
                  📸 Instagram Caption Preview:
                </div>
                <div style={{
                  fontSize: '13px',
                  color: '#FCD34D',
                  lineHeight: '1.6',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                }}>
                  {sharePreview.block.title}
                  {'\n\n'}📍 {sharePreview.block.city}, {sharePreview.block.state}
                  {'\n\n'}🔗 Link in bio
                  {'\n\n'}#{sharePreview.block.business_type.replace(/\s+/g, '')} #{sharePreview.block.city.replace(/\s+/g, '')} #LocalBusiness #SEO
                </div>
              </div>

              {/* Instructions */}
              <div style={{
                padding: '16px',
                background: 'rgba(59,130,246,0.10)',
                border: '1px solid rgba(59,130,246,0.25)',
                borderRadius: '8px',
                fontSize: '13px',
                color: '#93C5FD',
                lineHeight: '1.6',
              }}>
                <strong>💡 How to share:</strong><br />
                <strong>Instagram:</strong> Click "Instagram" button → Image downloads + caption copies → Open Instagram app → Create post → Upload image → Paste caption<br />
                <strong>Other platforms:</strong> Click button → Enter YOUR website URL → Share!
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @keyframes progress {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(400%); }
        }
      `}</style>
    </div>
  )
}
