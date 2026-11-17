import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { Copy, Download, RefreshCw, Save } from 'lucide-react'
import { generateKeywordBlog, getPage, publishToShopify, publishToWeb, publishToWordPress, repairKeywordBlog, saveKeywordBlog, zeorbitArticleUrl } from '../api'

const NONSENSE = [
  'the first decision',
  'what must work in',
  'what a later edit looks like',
  'the useful page names the job',
  'home page has to say',
  'separate page for each',
  'asks for the work',
]

function isNonsense(html) {
  const text = String(html || '').toLowerCase()
  return NONSENSE.filter((mark) => text.includes(mark)).length >= 2
}

function postTopic(item) {
  const keyword = String(item?.keyword || item?.primary_keyword || item?.entered_keyword || '').trim()
  const city = String(item?.city || '').trim()
  if (!city || keyword.toLowerCase().includes(city.toLowerCase())) return keyword
  const state = String(item?.state || '').trim()
  return `${keyword} in ${city}${state ? `, ${state}` : ''}`
}
import { stashPreview } from './KeywordBlogPage'

function plainText(html) {
  const box = document.createElement('div')
  box.innerHTML = (html || '').replace(/<style[\s\S]*?<\/style>/gi, '')
  box.querySelectorAll('h1,h2,h3,p,li').forEach((el) => {
    el.insertAdjacentText('afterend', '\n')
  })
  return (box.innerText || '').replace(/\n{3,}/g, '\n\n').trim()
}

function markBlocks(html) {
  const doc = new DOMParser().parseFromString(`<div id="root">${html || ''}</div>`, 'text/html')
  const root = doc.getElementById('root')
  const blocks = []
  let n = 0
  root.querySelectorAll('h1,h2,h3,h4,p,li').forEach((el) => {
    if (el.querySelector('h1,h2,h3,h4,p,li')) return
    const id = String(n++)
    el.setAttribute('data-ze', id)
    blocks.push({ id, tag: el.tagName.toLowerCase(), text: el.textContent || '' })
  })
  return { skeleton: root.innerHTML, blocks }
}

function htmlFromBlocks(skeleton, blocks) {
  const doc = new DOMParser().parseFromString(`<div id="root">${skeleton}</div>`, 'text/html')
  const root = doc.getElementById('root')
  blocks.forEach((block) => {
    const el = root.querySelector(`[data-ze="${block.id}"]`)
    if (el) el.textContent = block.text
  })
  root.querySelectorAll('[data-ze]').forEach((el) => el.removeAttribute('data-ze'))
  return root.innerHTML
}

const BLOCK_LABEL = { h1: 'Title', h2: 'Heading', h3: 'Heading', h4: 'Heading', p: 'Paragraph', li: 'List item' }

function readStash() {
  try {
    return JSON.parse(sessionStorage.getItem('zeorbit-write-preview') || 'null')
  } catch {
    return null
  }
}

export default function BlogPreviewPage() {
  const stored = readStash()
  const [blog, setBlog] = useState(stored?.blog || null)
  const [batch, setBatch] = useState(stored?.batch || null)
  const [editing, setEditing] = useState(false)
  const [blocks, setBlocks] = useState([])
  const [skeleton, setSkeleton] = useState('')
  const [openBlock, setOpenBlock] = useState('')
  const [busy, setBusy] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [sendTo, setSendTo] = useState('zeorbit')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const repaired = useRef('')

  useEffect(() => {
    if (!blog?.content_html || !isNonsense(blog.content_html)) return
    const key = blog.slug || postTopic(blog)
    if (!key || repaired.current === key) return
    repaired.current = key
    setBusy(true)
    setError('')
    repairKeywordBlog({
      slug: blog.slug || '',
      keyword: blog.keyword || blog.primary_keyword || blog.entered_keyword || '',
      city: blog.city || '',
      state: blog.state || '',
    }).then((res) => {
      remember({ ...blog, ...res.data, slug: blog.slug || res.data?.slug, city: blog.city || res.data?.city })
      setNotice('Rewrote this post so it stays on the service.')
    }).catch(() => {
      repaired.current = ''
      setError('This post still uses the old template. Click Regenerate.')
    }).finally(() => setBusy(false))
  }, [blog?.slug, blog?.content_html])

  useEffect(() => {
    if (blog?.content_html || !blog?.slug) return
    getPage(blog.slug).then((res) => {
      const block = res.data?.seo_block || {}
      setBlog({ ...block, slug: blog.slug, city: blog.city })
    }).catch(() => setError('That post could not be opened.'))
  }, [blog?.slug, blog?.content_html, blog?.city])

  function remember(nextBlog, nextBatch = batch) {
    setBlog(nextBlog)
    setBatch(nextBatch)
    stashPreview(nextBlog, nextBatch)
  }

  async function copy(text, label) {
    try {
      await navigator.clipboard.writeText(text)
      setNotice(`${label} copied.`)
    } catch {
      setNotice('Copy failed.')
    }
  }

  function download() {
    if (!blog) return
    const blob = new Blob([blog.content_html || ''], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${blog.slug || 'blog'}.html`
    a.click()
    URL.revokeObjectURL(url)
  }

  async function regenerate() {
    const value = (blog?.keyword || blog?.primary_keyword || '').trim()
    if (value.length < 2) return
    setBusy(true)
    setError('')
    try {
      const res = await generateKeywordBlog(value)
      remember(res.data, null)
      setEditing(false)
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'The article could not be generated.')
    } finally {
      setBusy(false)
    }
  }

  function publishBody(item) {
    return {
      title: item.seo_title || item.title,
      h1: item.title,
      slug: item.slug,
      meta_description: item.meta_description || item.title,
      intro: '',
      content: plainText(item.content_html),
      content_html: item.content_html,
      cta: 'Talk with ZeOrbit',
      h2s: ['Guide'],
      h3s: [],
      city: item.city || '',
      state: item.state || '',
      content_type: 'blog',
      business_type: item.detected_industry || 'ZeOrbit',
      focus_keyword: item.primary_keyword || item.keyword,
      keywords: {
        primary: item.keyword || item.primary_keyword || item.title,
        secondary: item.related_keywords || [],
        long_tail: [],
        near_me: [],
      },
      schema_markup: {},
      faqs: [],
      featured_image_url: '',
      quality_score: 92,
      readability_score: 92,
      keyword_density: 92,
      publishable: true,
    }
  }

  function destinationName() {
    if (sendTo === 'wordpress') return 'WordPress'
    if (sendTo === 'shopify') return 'Shopify'
    return 'ZeOrbit'
  }

  function publishError(err, fallback) {
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (detail?.message) return detail.message
    return err.message || fallback
  }

  async function sendOne(item) {
    const body = publishBody(item)
    if (sendTo === 'wordpress') {
      const res = await publishToWordPress(body, { status: 'publish' })
      if (!res.data?.success) throw new Error(res.data?.error || 'WordPress publish failed.')
      return res.data.post_url || 'WordPress'
    }
    if (sendTo === 'shopify') {
      const res = await publishToShopify(body)
      if (!res.data?.success) throw new Error(res.data?.error || 'Shopify publish failed.')
      return res.data.post_url || 'Shopify'
    }
    const res = await publishToWeb(body)
    return zeorbitArticleUrl(res.data?.public_url || res.data?.slug || item.slug)
  }

  async function publish() {
    if (!blog) return
    setPublishing(true)
    setError('')
    try {
      const url = await sendOne(blog)
      setNotice(`Published on ${destinationName()}: ${url}`)
    } catch (err) {
      setError(publishError(err, 'Publish failed.'))
    } finally {
      setPublishing(false)
    }
  }

  async function publishAll() {
    const items = batch?.created || []
    if (!items.length) return
    setPublishing(true)
    setError('')
    let done = 0
    try {
      for (const item of items) {
        let full = item
        if (!full.content_html && full.slug) {
          const res = await getPage(full.slug)
          full = { ...(res.data?.seo_block || {}), ...full, slug: full.slug }
        }
        await sendOne(full)
        done += 1
        setNotice(`Published ${done} of ${items.length} to ${destinationName()}.`)
      }
      setNotice(`Published ${done} posts to ${destinationName()}.`)
    } catch (err) {
      setError(publishError(err, `Stopped after ${done}. Publish failed.`))
    } finally {
      setPublishing(false)
    }
  }

  async function openCity(item) {
    setError('')
    if (item.content_html) {
      remember({ ...item, entered_keyword: item.entered_keyword || batch?.keyword || '' })
      setEditing(false)
      return
    }
    try {
      const res = await getPage(item.slug)
      const block = res.data?.seo_block || {}
      remember({ ...block, slug: item.slug, city: item.city, entered_keyword: block.entered_keyword || batch?.keyword || '' })
      setEditing(false)
    } catch {
      setError('That post could not be opened.')
    }
  }

  function withPlace(text, fromCity, toCity) {
    if (!text || !fromCity || fromCity === toCity) return text || ''
    return text.replace(new RegExp(fromCity.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), toCity)
  }

  async function applyEditToAll() {
    if (!blog || !batch?.created?.length) return
    const fromCity = blog.city || ''
    const next = batch.created.map((item) => ({
      ...item,
      seo_title: withPlace(blog.seo_title, fromCity, item.city),
      meta_description: withPlace(blog.meta_description, fromCity, item.city),
      content_html: withPlace(blog.content_html, fromCity, item.city),
      title: withPlace(blog.title, fromCity, item.city),
    }))
    const nextBatch = { ...batch, created: next }
    remember(blog, nextBatch)
    setNotice('Saving this edit on every city…')
    try {
      for (const item of next) await saveKeywordBlog(item)
      setNotice(`Updated ${next.length} posts.`)
    } catch {
      setError('The edit was applied on screen, but saving every post failed.')
    }
  }

  async function save() {
    if (!blog) return
    setNotice('')
    setError('')
    const nextBatch = batch?.created?.length
      ? { ...batch, created: batch.created.map((item) => item.slug === blog.slug ? { ...item, ...blog } : item) }
      : batch
    remember(blog, nextBatch)
    try {
      await saveKeywordBlog(blog)
      setNotice(`Saved ${blog.city || 'this post'} only.`)
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'The draft could not be saved.')
    }
  }

  if (!blog) {
    return (
      <div style={{ maxWidth: 860, margin: '0 auto', padding: '12px 0 48px' }}>
        <h1 style={{ fontSize: 28, margin: '0 0 8px' }}>Preview</h1>
        <p style={{ color: '#475569' }}>Generate a post first, then the preview opens here.</p>
        <Link to="/write" style={{ color: '#1d1d1f', fontWeight: 700 }}>Back to generate</Link>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 860, margin: '0 auto', padding: '12px 0 48px' }}>
      <Link to="/write" style={{ color: '#475569', fontSize: 14, textDecoration: 'none' }}>← Back to generate</Link>
      <h1 style={{ fontSize: 28, letterSpacing: '-0.03em', margin: '12px 0 16px' }}>Preview</h1>
      {batch?.created?.length > 1 ? (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 16 }}>
          {batch.created.map((item) => (
            <button key={item.slug} type="button" onClick={() => openCity(item)} style={{ border: blog?.slug === item.slug ? '1px solid #1d1d1f' : '1px solid #e6e6e8', background: '#fff', borderRadius: 999, padding: '6px 10px', fontSize: 12, cursor: 'pointer' }}>
              {item.city || item.slug}
            </button>
          ))}
        </div>
      ) : null}
      <article>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
          <button type="button" onClick={() => copy(blog.content_html, 'HTML')} style={btn}><Copy size={14} /> Copy HTML</button>
          <button type="button" onClick={() => copy(plainText(blog.content_html), 'Plain text')} style={btn}>Copy plain text</button>
          <button type="button" onClick={download} style={btn}><Download size={14} /> Download HTML</button>
          <button type="button" onClick={regenerate} disabled={busy} style={btn}><RefreshCw size={14} /> Regenerate</button>
          <label style={{ ...btn, cursor: 'default' }}>
            Send to
            <select value={sendTo} onChange={(e) => setSendTo(e.target.value)} aria-label="Send to" style={sendSelect}>
              <option value="zeorbit">ZeOrbit</option>
              <option value="wordpress">WordPress</option>
              <option value="shopify">Shopify</option>
            </select>
          </label>
          <button type="button" onClick={publish} disabled={publishing} style={{ ...btn, background: '#1d1d1f', color: '#fff', borderColor: '#1d1d1f' }}>
            {publishing ? 'Publishing…' : `Publish to ${destinationName()}`}
          </button>
          {batch?.created?.length > 1 ? (
            <button type="button" onClick={publishAll} disabled={publishing} style={{ ...btn, background: '#16a34a', color: '#fff', borderColor: '#16a34a' }}>
              {publishing ? 'Publishing…' : `Publish all ${batch.created.length}`}
            </button>
          ) : null}
          <button type="button" onClick={() => { setEditing(false); setOpenBlock('') }} style={{ ...btn, background: editing ? '#fff' : '#1d1d1f', color: editing ? '#1d1d1f' : '#fff' }}>Preview</button>
          <button type="button" onClick={() => {
            const marked = markBlocks(blog.content_html)
            setSkeleton(marked.skeleton)
            setBlocks(marked.blocks)
            setOpenBlock(marked.blocks[0]?.id || '')
            setEditing(true)
          }} style={{ ...btn, background: editing ? '#1d1d1f' : '#fff', color: editing ? '#fff' : '#1d1d1f' }}>Edit</button>
          {editing ? (
            <button type="button" onClick={save} style={btn}><Save size={14} /> Save this post</button>
          ) : null}
          {editing && batch?.created?.length > 1 ? (
            <button type="button" onClick={applyEditToAll} style={{ ...btn, background: '#1d1d1f', color: '#fff', borderColor: '#1d1d1f' }}>Apply to all cities</button>
          ) : null}
        </div>
        {error ? <p style={{ color: '#b42318' }}>{error}</p> : null}
        {notice ? <p style={{ color: '#067647' }}>{notice}</p> : null}
        <section style={card}>
          <div style={kicker}>SEO</div>
          {editing ? (
            <div style={{ display: 'grid', gap: 8, marginTop: 8 }}>
              <input value={blog.seo_title || ''} onChange={(e) => setBlog((prev) => prev ? { ...prev, seo_title: e.target.value } : prev)} aria-label="SEO title" style={field} />
              <textarea value={blog.meta_description || ''} onChange={(e) => setBlog((prev) => prev ? { ...prev, meta_description: e.target.value } : prev)} aria-label="Meta description" style={{ ...field, minHeight: 72 }} />
            </div>
          ) : (
            <>
              <p style={{ margin: '8px 0 4px', fontWeight: 750 }}>{blog.entered_keyword || blog.keyword || blog.primary_keyword}</p>
              {blog.seo_title && blog.seo_title !== (blog.keyword || blog.primary_keyword) ? (
                <p style={{ margin: '0 0 4px', color: '#1d1d1f' }}>{blog.seo_title}</p>
              ) : null}
              <p style={{ margin: 0, color: '#475569' }}>{blog.meta_description}</p>
            </>
          )}
          <p style={{ margin: '8px 0 0', fontSize: 13, color: '#64748b' }}>/{String(blog.slug || '').replace(/^\/?blog\/?/i, '')}</p>
          {blog.layout ? (
            <p style={{ margin: '8px 0 0', fontSize: 13, color: '#64748b' }}>
              Template {blog.layout} · {blog.pattern || 'layout'}
            </p>
          ) : null}
        </section>
        {editing ? (
          <div style={{ marginTop: 16, background: '#fff', border: '1px solid #d6d6d8', borderRadius: 12, overflow: 'hidden' }}>
            <div style={{ padding: '8px 12px', borderBottom: '1px solid #eceff2', fontSize: 13, color: '#64748b' }}>
              Edit a paragraph, then Save this post or Apply to all cities.
            </div>
            {blocks.map((block) => {
              const open = openBlock === block.id
              return (
                <div key={block.id} style={{ borderTop: '1px solid #f0f1f3', padding: '12px 14px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center', marginBottom: 6 }}>
                    <span style={{ fontSize: 11, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#8a9099', fontWeight: 700 }}>{BLOCK_LABEL[block.tag] || 'Paragraph'}</span>
                    <button type="button" onClick={() => setOpenBlock(open ? '' : block.id)} style={{ ...btn, padding: '4px 10px' }}>{open ? 'Done' : 'Edit'}</button>
                  </div>
                  {open ? (
                    <textarea
                      value={block.text}
                      aria-label={BLOCK_LABEL[block.tag] || 'Paragraph'}
                      onChange={(e) => {
                        const next = blocks.map((item) => item.id === block.id ? { ...item, text: e.target.value } : item)
                        setBlocks(next)
                        const content_html = htmlFromBlocks(skeleton, next)
                        setBlog((prev) => prev ? { ...prev, content_html } : prev)
                      }}
                      style={{ width: '100%', minHeight: block.tag === 'p' ? 96 : 56, border: '1px solid #d6d6d8', borderRadius: 8, padding: 10, font: '16px Georgia, serif', lineHeight: 1.55, boxSizing: 'border-box' }}
                    />
                  ) : (
                    <p style={{ margin: 0, fontFamily: 'Georgia, serif', fontSize: block.tag === 'h1' ? 28 : block.tag.startsWith('h') ? 20 : 16, fontWeight: block.tag.startsWith('h') ? 700 : 400, lineHeight: 1.5 }}>{block.text}</p>
                  )}
                </div>
              )
            })}
          </div>
        ) : isNonsense(blog.content_html) ? (
          <p style={{ marginTop: 20, color: '#475569' }}>Replacing the old template with an article about this service.</p>
        ) : (
          <div className="blog-html" style={{ marginTop: 20, fontSize: 17, lineHeight: 1.7 }} dangerouslySetInnerHTML={{ __html: (blog.content_html || '').replace(/(<p class="zo-vcard-title"[^>]*>)\s*Let['’]s Build:\s*/gi, '$1') }} />
        )}
        <style>{`
          .blog-html h1 { font-size: 32px; letter-spacing: -0.03em; line-height: 1.15; margin: 0 0 12px; }
          .blog-html h2 { font-size: 24px; letter-spacing: -0.02em; margin: 28px 0 8px; }
          .blog-html h3 { font-size: 18px; margin: 18px 0 6px; }
          .blog-html p { margin: 0 0 12px; }
          .blog-html img.blog-hero { width: 100%; height: 320px; object-fit: cover; border-radius: 16px; margin: 4px 0 18px; display: block; }
          .blog-html .blog-cta { display: inline-flex; align-items: center; background: #1d1d1f; color: #fff; text-decoration: none; border-radius: 999px; padding: 12px 18px; font-weight: 650; }
        `}</style>
      </article>
    </div>
  )
}

const field = { border: '1px solid #d6d6d8', borderRadius: 10, padding: '12px 14px', fontSize: 15, background: '#fff' }
const btn = {
  border: '1px solid #d6d6d8', background: '#fff', borderRadius: 8, padding: '8px 12px',
  display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 600, cursor: 'pointer',
}
const sendSelect = {
  border: 'none', background: 'transparent', fontSize: 13, fontWeight: 700, color: '#1d1d1f', cursor: 'pointer',
}
const card = { background: '#f6f6f7', borderRadius: 12, padding: 16 }
const kicker = { fontSize: 12, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#64748b', fontWeight: 700 }
