import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import RevampHeader from '../components/revamp/RevampHeader'
import SiteFooter from '../components/SiteFooter'
import SeoHead from '../components/SeoHead'
import ContactForm from '../components/revamp/ContactForm'
import { getPublishedPage } from '../api'
import { SITE_CONTACT } from '../data/revampContent'

const LAYOUTS = ['qa', 'steps', 'story', 'cards', 'split', 'timeline']

const INSTRUCTION_MARKERS = [
  'focus each page on the specific',
  'make every page feel unique',
  'custom content requirements',
  'honor every point',
  'avoid generic or repetitive',
  'keep the content simple, credible',
  'show how zeorbit can help with seo-',
  'these should be treated only as ai',
]

function looksLikeInstruction(text) {
  const t = String(text || '').toLowerCase()
  return INSTRUCTION_MARKERS.some((m) => t.includes(m))
}

/** Force glued `## Heading Next sentence` into real markdown sections. */
function normalizeMarkdownBody(raw, h2s = []) {
  let text = String(raw || '').replace(/\r\n/g, '\n').trim()
  if (!text) return ''

  // Any ## not already at line start → own block
  text = text.replace(/([^\n])\s*(##\s+)/g, '$1\n\n$2')

  const heads = (h2s || []).map((h) => String(h || '').trim()).filter(Boolean)
    .sort((a, b) => b.length - a.length)

  for (const h of heads) {
    const esc = h.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    // ## Exact H2 immediately followed by body text on the same line
    text = text.replace(new RegExp(`(##\\s*${esc})(?=\\s*\\S)`, 'ig'), '$1\n\n')
  }

  // Generic: ## TitleCase words… then a new sentence starting with A-Z after the heading phrase
  text = text.replace(/(##\s+[^\n]+?)(\s+)(?=[A-Z][a-z])/g, (full, head, sp) => {
    // If heading line already ends cleanly, leave it; otherwise break before new sentence
    if (/\n\n$/.test(head)) return full
    // Don't break inside the heading itself when h2 list already handled it
    const line = head.replace(/^##\s*/, '')
    if (heads.some((h) => h.toLowerCase() === line.trim().toLowerCase())) {
      return `${head}\n\n`
    }
    return full
  })

  text = text.replace(/\n{3,}/g, '\n\n')
  return text.trim()
}

/** Split walls of text into short, readable paragraphs (2–3 sentences). */
function readableParagraphs(text) {
  const chunks = String(text || '')
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter((p) => p && !looksLikeInstruction(p) && !/^#{1,6}\s/.test(p))

  const out = []
  for (const chunk of chunks) {
    // Strip leftover inline ## Title fragments that slipped through
    const cleaned = chunk.replace(/\s*##\s+[A-Z][^.!?\n]{0,80}/g, '').trim()
    if (!cleaned) continue
    if (cleaned.length < 280) {
      out.push(cleaned)
      continue
    }
    const sentences = cleaned.match(/[^.!?]+[.!?]+(?:\s|$)|[^.!?]+$/g) || [cleaned]
    let buf = ''
    let count = 0
    for (const s of sentences) {
      const piece = s.trim()
      if (!piece) continue
      buf = buf ? `${buf} ${piece}` : piece
      count += 1
      if (count >= 2 || buf.length >= 220) {
        out.push(buf.trim())
        buf = ''
        count = 0
      }
    }
    if (buf.trim()) out.push(buf.trim())
  }
  return out
}

function paragraphs(text) {
  return readableParagraphs(text)
}

function layoutFor(slug, explicit) {
  if (explicit && LAYOUTS.includes(explicit)) return explicit
  let h = 0
  const s = String(slug || '')
  for (let i = 0; i < s.length; i += 1) h = (h * 33 + s.charCodeAt(i)) >>> 0
  return LAYOUTS[h % LAYOUTS.length]
}

function bulletsFrom(text) {
  const lines = String(text || '')
    .split(/\n+/)
    .map((l) => l.trim())
    .filter(Boolean)
  const items = lines
    .filter((l) => /^[-•*]|\d+[.)]/.test(l))
    .map((l) => l.replace(/^[-•*]\s*/, '').replace(/^\d+[.)]\s*/, ''))
  if (items.length >= 2) return items
  const parts = String(text || '').split(/•/).map((p) => p.trim()).filter((p) => p.length > 12)
  return parts.length >= 2 ? parts : null
}

function fallbackSection(heading) {
  return (
    `${heading || 'This section'} matters when someone lands on your site and needs a clear answer. `
    + 'ZeOrbit builds WordPress pages that explain the offer in plain language, show proof, '
    + 'and make the next step obvious — contact, call, or book.'
  )
}

function parseMarkdownSections(raw, h2s, h3s) {
  const text = normalizeMarkdownBody(raw, h2s)
  if (!/^##\s/m.test(text)) return null
  const startsWithH2 = /^##\s/.test(text)
  const parts = text.split(/^##\s+/m).filter(Boolean)
  const chunks = startsWithH2 ? parts : parts.slice(1)
  if (!chunks.length) return null
  return chunks.map((chunk, i) => {
    const nl = chunk.indexOf('\n')
    let heading = (nl === -1 ? chunk : chunk.slice(0, nl)).trim()
    let rest = (nl === -1 ? '' : chunk.slice(nl)).trim()
    // If heading still has body glued on (no newline case), peel using known h2s
    if (!rest && h2s?.length) {
      for (const h of [...h2s].sort((a, b) => b.length - a.length)) {
        if (heading.toLowerCase().startsWith(h.toLowerCase()) && heading.length > h.length) {
          rest = heading.slice(h.length).trim()
          heading = h
          break
        }
      }
    }
    rest = readableParagraphs(rest).join('\n\n')
    if (!rest || rest.split(/\s+/).length < 20) {
      rest = fallbackSection(heading)
    }
    return { heading, sub: h3s[i] || '', text: rest, bullets: bulletsFrom(rest) }
  })
}

function SectionCopy({ sec }) {
  if (sec.bullets) {
    return <ul className="zo-article-list">{sec.bullets.map((b) => <li key={b.slice(0, 40)}>{b}</li>)}</ul>
  }
  return readableParagraphs(sec.text).map((p) => <p key={p.slice(0, 48)}>{p}</p>)
}

function allocateSections(h2s, h3s, paras) {
  const n = h2s.length
  if (!n) return { sections: [], leftover: paras }
  let idx = 0
  const sections = h2s.map((heading, i) => {
    const remainingH = n - i
    const remainingP = paras.length - idx
    const takeCount = i === n - 1
      ? remainingP
      : remainingP >= remainingH
        ? Math.max(1, Math.floor(remainingP / remainingH))
        : remainingP > 0
          ? 1
          : 0
    const take = paras.slice(idx, idx + takeCount)
    idx += take.length
    let text = take.join('\n\n')
    if (!text || text.split(/\s+/).length < 20) {
      text = fallbackSection(heading)
    }
    return { heading, sub: h3s[i] || '', text, bullets: bulletsFrom(text) }
  })
  return { sections, leftover: paras.slice(idx) }
}

function ArticleSections({ layout, h2s, h3s, body, rawContent, images }) {
  const parsed = parseMarkdownSections(rawContent, h2s, h3s)
  const allocated = parsed
    ? { sections: parsed, leftover: [] }
    : allocateSections(h2s, h3s, body)
  const { sections, leftover } = allocated
  const bodyImages = (images || []).filter((img) => img?.url && !img.is_featured)

  const withImage = (sec, i) => {
    const img = bodyImages[i]
    return (
      <>
        {img ? (
          <figure className="zo-article-inline">
            <img
              src={img.url}
              alt={img.alt_text || sec.heading}
              title={img.title || sec.heading}
              loading="lazy"
              onError={(e) => {
                const fig = e.currentTarget.closest('figure')
                if (fig) fig.style.display = 'none'
              }}
            />
            {img.caption ? <figcaption>{img.caption}</figcaption> : null}
          </figure>
        ) : null}
        <SectionCopy sec={sec} />
      </>
    )
  }

  // Always render a clean vertical article — cards/split become stacked sections
  // so long SEO copy stays readable (no wall-of-text columns).
  const useStack = layout === 'cards' || layout === 'split' || layout === 'story' || !layout

  if (layout === 'steps' || layout === 'timeline') {
    return (
      <ol className={`zo-article-flow is-${layout}`}>
        {sections.map((sec, i) => (
          <li key={`${sec.heading}-${i}`}>
            <h2>{sec.heading}</h2>
            {sec.sub ? <h3>{sec.sub}</h3> : null}
            {withImage(sec, i)}
          </li>
        ))}
      </ol>
    )
  }

  if (useStack) {
    return (
      <div className="zo-article-stack">
        {sections.map((sec, i) => (
          <section key={`${sec.heading}-${i}`} className="zo-article-block">
            <h2>{sec.heading}</h2>
            {sec.sub ? <h3>{sec.sub}</h3> : null}
            {withImage(sec, i)}
          </section>
        ))}
        {leftover.map((p) => <p key={p.slice(0, 48)}>{p}</p>)}
      </div>
    )
  }

  return (
    <div className="zo-article-qa">
      {sections.map((sec, i) => (
        <details key={`${sec.heading}-${i}`} className="zo-article-qa-item" open={i < 2}>
          <summary>{sec.heading}</summary>
          {sec.sub ? <h3>{sec.sub}</h3> : null}
          {withImage(sec, i)}
        </details>
      ))}
      {leftover.map((p) => <p key={p.slice(0, 48)}>{p}</p>)}
    </div>
  )
}

export default function SeoArticlePage() {
  const { slug } = useParams()
  const [row, setRow] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    setRow(null)
    ;(async () => {
      try {
        const { data } = await getPublishedPage(slug)
        if (!cancelled) setRow(data)
      } catch {
        if (!cancelled) setError('notfound')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => { cancelled = true }
  }, [slug])

  const block = row?.seo_block || {}
  const title = block.title || block.h1 || 'ZeOrbit'
  const h1 = block.h1 || block.title || ''
  const desc = block.meta_description || block.intro || ''
  const location = [row?.city, row?.state].filter(Boolean).join(', ')
  const faqs = Array.isArray(block.faqs) ? block.faqs : []
  const h2s = Array.isArray(block.h2s) ? block.h2s : []
  const h3s = Array.isArray(block.h3s) ? block.h3s : []
  const normalized = normalizeMarkdownBody(block.content || '', h2s)
  const body = paragraphs(normalized.replace(/^##\s+.+$/gm, '').replace(/\n{3,}/g, '\n\n'))
  const layout = layoutFor(slug, block.layout_variant)
  const images = Array.isArray(block.in_content_images) ? block.in_content_images : []
  const hero = block.featured_image_url || images.find((im) => im?.is_featured)?.url || images[0]?.url || ''
  const heroKey = (hero || '').split('?')[0]
  const distinctBody = images.find((im) => im?.url && im.url.split('?')[0] !== heroKey)
  const footerImg = (
    (block.footer_image_url && block.footer_image_url.split('?')[0] !== heroKey)
      ? block.footer_image_url
      : (distinctBody?.url || '')
  )
  const featuredMeta = images.find(
    (im) => im?.is_featured || (im?.url && hero && im.url.split('?')[0] === hero.split('?')[0]),
  )
  const footerMeta = images.find(
    (im) => im?.url && footerImg && im.url.split('?')[0] === footerImg.split('?')[0],
  )
  const heroAlt = featuredMeta?.alt_text || h1
  const footerAlt = footerMeta?.alt_text || 'Related website design example'

  return (
    <div className={`rv-page zo-blog-page zo-seo-article is-layout-${layout}`}>
      <SeoHead
        title={title}
        description={desc}
        path={`/${slug || ''}`}
        image={hero || '/zeorbit-logo.png'}
        type="article"
      />
      <RevampHeader />

      <main className="zo-article">
        <div className="rv-shell zo-article-inner">
          {loading ? (
            <p className="zo-blog-empty">Loading…</p>
          ) : error || !row ? (
            <div className="zo-article-missing">
              <p className="zo-blog-eyebrow">Not published yet</p>
              <h1>This page is not live</h1>
              <p>Generate it in the SEO tool, then click Publish to ZeOrbit.</p>
              <Link className="zo-article-back" to="/blog">Back to blog</Link>
            </div>
          ) : (
            <article>
              {location ? <p className="zo-blog-eyebrow">{location}</p> : null}
              <h1>{h1}</h1>
              {hero ? (
                <figure className="zo-article-hero">
                  <img src={hero} alt={heroAlt} />
                </figure>
              ) : null}
              {block.intro ? paragraphs(block.intro).map((p) => <p key={p.slice(0, 40)}>{p}</p>) : null}
              <ArticleSections
                layout={layout}
                h2s={h2s}
                h3s={h3s}
                body={body}
                rawContent={normalized}
                images={block.in_content_images || []}
              />
              {footerImg && footerImg.split('?')[0] !== (hero || '').split('?')[0] ? (
                <figure className="zo-article-footer-image">
                  <img src={footerImg} alt={footerAlt} />
                </figure>
              ) : null}
              {block.cta ? <p className="zo-article-cta">{block.cta}</p> : null}
              <p>
                <a className="zo-article-call" href={`tel:${SITE_CONTACT.phoneTel}`}>
                  CALL NOW : {SITE_CONTACT.phone}
                </a>
              </p>
              {faqs.length > 0 ? (
                <div className="zo-article-faqs">
                  <h2>Frequently Asked Questions</h2>
                  {faqs.map((faq, i) => (
                    <div key={i} className="zo-article-faq">
                      <h3>{faq.question || faq.q}</h3>
                      <p>{faq.answer || faq.a}</p>
                    </div>
                  ))}
                </div>
              ) : null}
            </article>
          )}
        </div>
      </main>

      {!error && row ? (
        <section className="zo-article-contact" id="contact">
          <div className="rv-shell">
            <ContactForm />
          </div>
        </section>
      ) : null}

      <SiteFooter />
    </div>
  )
}
