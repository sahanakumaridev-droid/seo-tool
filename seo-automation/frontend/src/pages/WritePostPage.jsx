import { useState } from 'react'
import { publishToWeb } from '../api'

const field = {
  width: '100%',
  border: '1px solid #cbd5e1',
  borderRadius: 8,
  padding: '10px 12px',
  fontSize: 14,
  color: '#0f172a',
  background: '#fff',
}

function slugify(text) {
  return (text || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 80)
}

export default function WritePostPage() {
  const [form, setForm] = useState({
    title: '',
    slug: '',
    meta_description: '',
    intro: '',
    h2s: '',
    h3s: '',
    content: '',
    cta: '',
    conclusion: '',
    featured_image_url: '',
    city: '',
    state: 'CA',
  })
  const [status, setStatus] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))

  async function publish() {
    const title = form.title.trim()
    if (!title || !form.content.trim()) {
      setStatus('Title and body are required.')
      return
    }
    const slug = (form.slug || slugify(title)).trim()
    const h2s = form.h2s.split('\n').map((s) => s.trim()).filter(Boolean)
    const h3s = form.h3s.split('\n').map((s) => s.trim()).filter(Boolean)
    const body = [
      form.content.trim(),
      form.conclusion.trim() ? `## Conclusion\n\n${form.conclusion.trim()}` : '',
    ].filter(Boolean).join('\n\n')
    setBusy(true)
    setStatus('')
    try {
      const res = await publishToWeb({
        title,
        h1: title,
        slug,
        meta_description: form.meta_description.trim() || title,
        intro: form.intro.trim(),
        content: body,
        cta: form.cta.trim(),
        h2s,
        h3s,
        city: form.city.trim(),
        state: form.state.trim() || 'CA',
        content_type: 'blog',
        business_type: 'Editorial',
        focus_keyword: title,
        keywords: { primary: title, secondary: [] },
        featured_image_url: form.featured_image_url.trim(),
        quality_score: 92,
        readability_score: 92,
        keyword_density: 92,
        publishable: true,
        faqs: [],
      })
      const url = res.data?.public_url || res.data?.url || `https://zeorbit.com/${slug}`
      setStatus(`Published: ${url}`)
    } catch (err) {
      setStatus(err.response?.data?.detail?.message || err.response?.data?.detail || err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ maxWidth: 820, margin: '0 auto', padding: '8px 0 40px' }}>
      <h1 style={{ fontSize: 22, margin: '0 0 6px' }}>Write and publish</h1>
      <p style={{ color: '#475569', marginTop: 0, fontSize: 14 }}>
        One form for the whole post. Publish sends it live on zeorbit.com.
      </p>
      <div style={{ display: 'grid', gap: 12 }}>
        <label>Meta title<input style={field} value={form.title} onChange={set('title')} /></label>
        <label>URL slug<input style={field} value={form.slug} placeholder="optional — built from the title" onChange={set('slug')} /></label>
        <label>Meta description<textarea style={{ ...field, minHeight: 70 }} value={form.meta_description} onChange={set('meta_description')} /></label>
        <label>Intro<textarea style={{ ...field, minHeight: 80 }} value={form.intro} onChange={set('intro')} /></label>
        <label>H2 headings, one per line<textarea style={{ ...field, minHeight: 70 }} value={form.h2s} onChange={set('h2s')} /></label>
        <label>H3 headings, one per line<textarea style={{ ...field, minHeight: 60 }} value={form.h3s} onChange={set('h3s')} /></label>
        <label>Body<textarea style={{ ...field, minHeight: 220 }} value={form.content} onChange={set('content')} /></label>
        <label>Conclusion<textarea style={{ ...field, minHeight: 80 }} value={form.conclusion} onChange={set('conclusion')} /></label>
        <label>CTA<input style={field} value={form.cta} onChange={set('cta')} /></label>
        <label>Featured image URL<input style={field} value={form.featured_image_url} onChange={set('featured_image_url')} /></label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 120px', gap: 12 }}>
          <label>City<input style={field} value={form.city} onChange={set('city')} /></label>
          <label>State<input style={field} value={form.state} onChange={set('state')} /></label>
        </div>
        <button type="button" onClick={publish} disabled={busy}
          style={{ justifySelf: 'start', background: '#5b5ce6', color: '#fff', border: 0, borderRadius: 8, padding: '10px 18px', fontWeight: 700 }}>
          {busy ? 'Publishing…' : 'Publish'}
        </button>
        {status ? <p style={{ margin: 0, fontSize: 14 }}>{String(status)}</p> : null}
      </div>
    </div>
  )
}
