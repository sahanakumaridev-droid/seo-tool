import { useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { ArrowLeft, RefreshCw, Save, CheckCircle, Upload, Globe, ExternalLink, Megaphone } from 'lucide-react'
import { generateSingle, savePage, publishToWordPress, publishToWeb, zeorbitBlogUrl, zeorbitArticleUrl } from '../api'

function ScoreRing({ value, color }) {
  const r = 20, c = 2 * Math.PI * r
  const dash = (value / 100) * c
  return (
    <svg width="52" height="52" viewBox="0 0 52 52">
      <circle cx="26" cy="26" r={r} fill="none" stroke="#2A3B57" strokeWidth="4" />
      <circle cx="26" cy="26" r={r} fill="none" stroke={color} strokeWidth="4"
        strokeDasharray={`${dash} ${c}`} strokeLinecap="round"
        transform="rotate(-90 26 26)" />
      <text x="26" y="31" textAnchor="middle" fontSize="11" fontWeight="700" fill={color}>{value}</text>
    </svg>
  )
}

function MetaRow({ label, value, multiline, onChange, hint }) {
  const fieldStyle = {
    width: '100%', background: 'transparent', border: 'none', outline: 'none', resize: 'vertical',
    fontSize: 14, lineHeight: 1.6, color: 'var(--text-primary)', fontFamily: 'inherit', padding: 0,
  }
  return (
    <div className="rounded-xl p-4" style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)' }}>
      <div className="flex items-center justify-between mb-2">
        <div className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>{label}</div>
        {hint && <div className="text-xs" style={{ color: 'var(--text-4)' }}>{hint}</div>}
      </div>
      {multiline ? (
        <textarea rows={label === 'Body Content' ? 12 : 3} value={value || ''} onChange={e => onChange(e.target.value)} style={fieldStyle} />
      ) : (
        <input type="text" value={value || ''} onChange={e => onChange(e.target.value)} style={fieldStyle} />
      )}
    </div>
  )
}

function EditableList({ label, items = [], color, onChange }) {
  const update = (i, val) => onChange(items.map((it, idx) => idx === i ? val : it))
  const remove = (i) => onChange(items.filter((_, idx) => idx !== i))
  const add = () => onChange([...items, ''])
  return (
    <div className="rounded-xl p-4" style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)' }}>
      <div className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: 'var(--text-muted)' }}>{label}</div>
      <div className="space-y-2">
        {items.map((h, i) => (
          <div key={i} className="flex items-center gap-2">
            <span className="text-xs font-bold flex-shrink-0" style={{ color }}>{label.startsWith('H2') ? 'H2' : 'H3'}</span>
            <input type="text" value={h} onChange={e => update(i, e.target.value)}
              className="flex-1 text-sm" style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 6, padding: '6px 8px', color: 'var(--text-primary)' }} />
            <button onClick={() => remove(i)} className="text-xs px-2 py-1 rounded" style={{ color: 'var(--red)' }}>Remove</button>
          </div>
        ))}
      </div>
      <button onClick={add} className="text-xs mt-2 font-semibold" style={{ color: 'var(--brand)' }}>+ Add heading</button>
    </div>
  )
}

function KwGroup({ label, kws = [], color }) {
  const colors = {
    cyan:   'bg-cyan-50 text-cyan-700 border-cyan-200',
    blue:   'bg-blue-50 text-blue-700 border-blue-200',
    emerald:'bg-emerald-50 text-emerald-700 border-emerald-200',
    violet: 'bg-violet-50 text-violet-700 border-violet-200',
  }
  return (
    <div>
      <div className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>{label}</div>
      <div className="flex flex-wrap gap-2">
        {kws.map((k, i) => (
          <span key={i} className={`text-xs px-2.5 py-1 rounded-lg border ${colors[color]}`}>{k}</span>
        ))}
      </div>
    </div>
  )
}

export default function PagePreviewPage() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const [block, setBlock] = useState(state?.block)
  const [tab, setTab] = useState('content')
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [publishResult, setPublishResult] = useState(null)
  const [webPublishing, setWebPublishing] = useState(false)
  const [webUrl, setWebUrl] = useState(null)
  const [webError, setWebError] = useState('')

  const businessType = state?.businessType || block?.business_type || ''
  const isPost = (state?.contentKind === 'post') || (block?.content_type === 'blog')
  const wpConfig = state?.wpConfig

  const handlePublishWeb = async () => {
    setWebPublishing(true); setWebError('')
    try {
      const res = await publishToWeb(block)
      const liveUrl = zeorbitArticleUrl(res.data.public_url || res.data.slug)
      setWebUrl(liveUrl)
      window.open(liveUrl, '_blank', 'noopener')
      window.open(zeorbitBlogUrl(), '_blank', 'noopener')
    } catch (e) {
      setWebError(e.response?.data?.detail || 'Publish failed. Is the backend running?')
    } finally { setWebPublishing(false) }
  }

  if (!block) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <p style={{ color: 'var(--text-muted)' }}>No page data found.</p>
        <button onClick={() => navigate('/content')} className="btn-primary px-4 py-2 rounded-lg text-white text-sm">
          Back to Content
        </button>
      </div>
    )
  }

  const score = Math.round(block.readability_score || 75)
  const scoreColor = score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444'

  const handleRegen = async () => {
    setLoading(true)
    try {
      const res = await generateSingle(businessType, block.city, block.state)
      setBlock(res.data)
    } finally { setLoading(false) }
  }

  const handleSave = async () => {
    await savePage(businessType, block.city, block.state)
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  const handlePublish = async () => {
    if (!wpConfig?.wp_url) return
    setPublishing(true)
    setPublishResult(null)
    try {
      const res = await publishToWordPress(block, wpConfig)
      setPublishResult(res.data)
    } catch (e) {
      setPublishResult({ success: false, error: e.response?.data?.detail || e.message })
    } finally { setPublishing(false) }
  }

  // All images to review: in-content assets + the featured image (deduped by url)
  const imageAssets = (() => {
    const list = [...(block.in_content_images || [])]
    const hasFeatured = list.some(im => im.is_featured || im.url === block.featured_image_url)
    if (block.featured_image_url && !hasFeatured) {
      list.unshift({ url: block.featured_image_url, is_featured: true, alt_text: block.h1 || block.title, caption: 'Featured image' })
    }
    return list.filter(im => im && im.url)
  })()

  const TABS = [
    { id: 'content', label: 'Content & Meta' },
    { id: 'images', label: `Images (${imageAssets.length})` },
    { id: 'intro', label: 'Intro' },
    { id: 'keywords', label: 'Keywords' },
    { id: 'questions', label: 'User Questions' },
    { id: 'faqs', label: `FAQs (${block.faqs?.length || 0})` },
    { id: 'schema', label: 'Schema' },
  ]

  return (
    <div className="space-y-5 fade-in">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)}
            className="p-2 rounded-lg transition-colors"
            style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
            <ArrowLeft size={15} />
          </button>
          <div>
            <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
              {isPost ? (block.h1 || block.title || 'Blog post') : `${block.city}${block.state ? `, ${block.state}` : ''}`}
            </h1>
            <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>
              {isPost ? 'Post · post-sitemap.xml' : 'Page · page-sitemap.xml'} · {block.slug}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-wrap justify-end">
          <button onClick={handleRegen} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
            style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Regenerate
          </button>
          <button onClick={handleSave}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-colors"
            style={saved
              ? { background: 'var(--green-soft)', border: '1px solid rgba(23,128,61,0.3)', color: 'var(--green)' }
              : { background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
            {saved ? <><CheckCircle size={13} /> Saved</> : <><Save size={13} /> Save</>}
          </button>
          {wpConfig?.wp_url && (
            <button onClick={handlePublish} disabled={publishing}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
              style={{ background: 'var(--bg-raised)', border: '1px solid var(--border-bright)', color: 'var(--text-1)' }}>
              <Upload size={13} className={publishing ? 'animate-pulse' : ''} />
              {publishing ? 'Publishing...' : publishResult?.success ? 'Published!' : 'Publish to WordPress'}
            </button>
          )}
          <button
            onClick={handlePublishWeb}
            disabled={webPublishing}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-semibold btn-primary disabled:opacity-50"
            title="Publish this page to the ZeOrbit website blog"
          >
            {webPublishing
              ? <svg className="animate-spin" width="15" height="15" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.3)" strokeWidth="3"/><path d="M12 2a10 10 0 0 1 10 10" stroke="#fff" strokeWidth="3" strokeLinecap="round"/></svg>
              : <Globe size={13} />}
            {webPublishing ? 'Publishing to ZeOrbit…' : webUrl ? 'Re-publish to ZeOrbit' : 'Publish to ZeOrbit'}
          </button>
          {webUrl ? (
            <>
              <button
                type="button"
                onClick={() => window.open(zeorbitBlogUrl(), '_blank', 'noopener')}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium"
                style={{ background: 'var(--green-soft)', border: '1px solid rgba(23,128,61,0.3)', color: 'var(--green)' }}
              >
                <ExternalLink size={13} /> View ZeOrbit Blog
              </button>
              <button
                type="button"
                onClick={() => navigate('/google-ads', {
                  state: {
                    finalUrl: webUrl,
                    public_url: webUrl,
                    category: businessType,
                    city: block.city || '',
                    businessName: businessType,
                    title: block.title || block.h1,
                    keywords: [
                      block.keywords?.primary,
                      ...(block.keywords?.secondary || []),
                    ].filter(Boolean),
                  },
                })}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-semibold"
                style={{ background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.35)', color: '#a5b4fc' }}
              >
                <Megaphone size={13} /> Create Google Ad
              </button>
            </>
          ) : null}
        </div>
      </div>

      {/* ZeOrbit blog publish banner */}
      {(webUrl || webError) && (
        <div className={`alert ${webError ? 'alert-error' : 'alert-success'}`}>
          {webError
            ? <span>✗ {webError}</span>
            : <span style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <CheckCircle size={15} />
                Published to ZeOrbit blog — it will appear under Blog on the marketing site.
                <a href={zeorbitBlogUrl()} target="_blank" rel="noreferrer" style={{ color: 'var(--brand-violet)', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                  Open ZeOrbit Blog <ExternalLink size={12} />
                </a>
                <a href={webUrl} target="_blank" rel="noreferrer" style={{ color: 'var(--brand-violet)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                  Live page <ExternalLink size={12} />
                </a>
              </span>}
        </div>
      )}

      {/* Publish result banner */}
      {publishResult && (
        <div className="rounded-xl px-4 py-3 text-sm flex items-center gap-2"
          style={{
            color: publishResult.success ? 'var(--green)' : 'var(--red)',
            background: publishResult.success ? 'var(--green-soft)' : 'var(--red-soft)',
            border: `1px solid ${publishResult.success ? 'rgba(23,128,61,0.25)' : 'rgba(220,38,38,0.25)'}`,
          }}>
          {publishResult.success
            ? <><CheckCircle size={14} /> Published — <a href={publishResult.post_url} target="_blank" rel="noreferrer" className="underline flex items-center gap-1">{publishResult.post_url} <ExternalLink size={11} /></a></>
            : <>✗ {publishResult.error}</>}
        </div>
      )}

      {/* Score cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: 'SEO Score', value: score, color: scoreColor },
          { label: 'Keyword Density', value: Math.round(block.keyword_density || 0), color: 'var(--brand)' },
          { label: 'Meta Complete', value: 100, color: '#10b981' },
        ].map(s => (
          <div key={s.label} className="card p-4 flex items-center gap-4">
            <ScoreRing value={s.value} color={s.color} />
            <div>
              <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{s.label}</div>
              <div className="text-lg font-bold mt-0.5" style={{ color: s.color }}>{s.value}%</div>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="flex border-b overflow-x-auto" style={{ borderColor: 'var(--border)' }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`px-5 py-3.5 text-sm font-medium whitespace-nowrap transition-colors ${tab === t.id ? 'tab-active' : 'tab-inactive'}`}>
              {t.label}
            </button>
          ))}
        </div>

        <div className="p-6 space-y-4">
          {tab === 'content' && (
            <>
              <MetaRow label="SEO Title" value={block.title} hint={`${(block.title || '').length}/60`}
                onChange={v => setBlock(prev => ({ ...prev, title: v }))} />
              <MetaRow label="Meta Description" value={block.meta_description} multiline hint={`${(block.meta_description || '').length}/160`}
                onChange={v => setBlock(prev => ({ ...prev, meta_description: v }))} />
              <MetaRow label="URL Slug" value={block.slug}
                onChange={v => setBlock(prev => ({ ...prev, slug: v.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') }))} />
              <MetaRow label="H1" value={block.h1}
                onChange={v => setBlock(prev => ({ ...prev, h1: v }))} />
              <EditableList label={isPost ? 'H2 Headings — Article sections' : 'H2 Headings — Question Based'} items={block.h2s || []} color="var(--brand)"
                onChange={v => setBlock(prev => ({ ...prev, h2s: v }))} />
              <EditableList label="H3 Headings" items={block.h3s || []} color="var(--brand-violet)"
                onChange={v => setBlock(prev => ({ ...prev, h3s: v }))} />
              <MetaRow label="Body Content" value={block.content} multiline
                onChange={v => setBlock(prev => ({ ...prev, content: v }))} />
              <MetaRow label="Call to Action" value={block.cta} multiline
                onChange={v => setBlock(prev => ({ ...prev, cta: v }))} />
            </>
          )}

          {tab === 'images' && (
            imageAssets.length === 0
              ? <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No images were attached to this page.</p>
              : (
                <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))' }}>
                  {imageAssets.map((img, i) => (
                    <div key={i} className="rounded-xl overflow-hidden" style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)' }}>
                      <div style={{ position: 'relative', aspectRatio: '16 / 10', background: 'var(--bg-overlay)' }}>
                        <img src={img.url} alt={img.alt_text || ''} loading="lazy"
                          style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                        {img.is_featured && (
                          <span style={{ position: 'absolute', top: 8, left: 8, fontSize: 10, fontWeight: 700, padding: '3px 8px', borderRadius: 999, background: 'var(--brand)', color: '#fff' }}>FEATURED</span>
                        )}
                      </div>
                      <div className="p-3">
                        {img.caption && <div className="text-xs font-semibold" style={{ color: 'var(--text-1)' }}>{img.caption}</div>}
                        {img.alt_text && <div className="text-xs mt-1" style={{ color: 'var(--text-3)' }}>alt: {img.alt_text}</div>}
                        <a href={img.url} target="_blank" rel="noreferrer" className="text-xs mt-1 inline-flex items-center gap-1" style={{ color: 'var(--brand-violet)' }}>
                          Open full size <ExternalLink size={10} />
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              )
          )}

          {tab === 'intro' && (
            <>
              <div className="rounded-xl p-4" style={{ background: 'rgba(6,182,212,0.06)', border: '1px solid rgba(6,182,212,0.2)' }}>
                <p className="text-xs font-semibold mb-1" style={{ color: 'var(--brand)' }}>AI Overview Optimized Intro</p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  First 2–3 lines answer directly with location + keyword — optimized for Google AI Overviews, Bing Copilot, and ChatGPT retrieval.
                </p>
              </div>
              <MetaRow label="Intro Paragraph" value={block.intro || block.content?.split('\n\n')[0]} multiline />
            </>
          )}

          {tab === 'keywords' && (
            <div className="space-y-5">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>Primary Keyword</div>
                <span className="inline-block px-3 py-1.5 rounded-lg text-sm font-medium"
                  style={{ background: 'var(--brand-soft)', color: 'var(--brand-dark)', border: '1px solid rgba(255,90,78,0.3)' }}>
                  {block.keywords?.primary}
                </span>
              </div>
              <KwGroup label="Short-tail / Main Keywords" kws={block.keywords?.secondary?.slice(0, 4)} color="cyan" />
              <KwGroup label="Long-tail Keywords" kws={block.keywords?.long_tail} color="blue" />
              <KwGroup label='"Near Me" Variations' kws={block.keywords?.near_me} color="emerald" />
            </div>
          )}

          {tab === 'questions' && (
            <div className="space-y-2">
              <div className="rounded-xl p-4 mb-2" style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)' }}>
                <p className="text-xs font-semibold mb-1" style={{ color: 'var(--amber)' }}>Real User Questions</p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Sourced from Google PAA & Suggest patterns. Used as H2s and FAQs for AI Overview optimization.
                </p>
              </div>
              {(block.keywords?.user_questions || []).map((q, i) => (
                <div key={i} className="flex items-start gap-3 rounded-xl p-3"
                  style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)' }}>
                  <span className="text-xs font-bold mt-0.5 flex-shrink-0" style={{ color: 'var(--amber)' }}>Q{i + 1}</span>
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{q}</span>
                </div>
              ))}
            </div>
          )}

          {tab === 'faqs' && (
            <div className="space-y-3">
              {block.faqs?.map((faq, i) => (
                <div key={i} className="rounded-xl p-4 space-y-2" style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)' }}>
                  <input type="text" value={faq.question}
                    onChange={e => setBlock(prev => ({ ...prev, faqs: prev.faqs.map((f, idx) => idx === i ? { ...f, question: e.target.value } : f) }))}
                    className="w-full text-sm font-semibold" style={{ background: 'transparent', border: 'none', outline: 'none', color: 'var(--brand)', fontFamily: 'inherit' }} />
                  <textarea rows={2} value={faq.answer}
                    onChange={e => setBlock(prev => ({ ...prev, faqs: prev.faqs.map((f, idx) => idx === i ? { ...f, answer: e.target.value } : f) }))}
                    className="w-full text-sm leading-relaxed" style={{ background: 'transparent', border: 'none', outline: 'none', resize: 'vertical', color: 'var(--text-secondary)', fontFamily: 'inherit' }} />
                </div>
              ))}
            </div>
          )}

          {tab === 'schema' && (
            <div className="space-y-4">
              {block.schema_markup && Object.entries(block.schema_markup).map(([key, val]) => (
                <div key={key}>
                  <div className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--brand)' }}>
                    {key.replace('_', ' ')}
                  </div>
                  <pre className="rounded-xl p-4 text-xs overflow-auto leading-relaxed"
                    style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)' }}>
                    {JSON.stringify(val, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
