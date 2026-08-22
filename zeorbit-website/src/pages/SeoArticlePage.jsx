import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import RevampHeader from '../components/revamp/RevampHeader'
import SiteFooter from '../components/SiteFooter'
import SeoHead from '../components/SeoHead'
import ContactForm from '../components/revamp/ContactForm'
import { getPublishedPage } from '../api'
import { SITE_CONTACT } from '../data/revampContent'

const LAYOUTS = ['qa', 'steps', 'story', 'cards', 'split', 'timeline']

function paragraphs(text) {
  return String(text || '')
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean)
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

function ArticleSections({ layout, h2s, h3s, body }) {
  const sections = h2s.map((heading, i) => ({
    heading,
    sub: h3s[i] || '',
    text: body[i] || '',
    bullets: bulletsFrom(body[i] || ''),
  }))
  const leftover = body.slice(h2s.length)

  if (layout === 'steps' || layout === 'timeline') {
    return (
      <ol className={`zo-article-flow is-${layout}`}>
        {sections.map((sec, i) => (
          <li key={`${sec.heading}-${i}`}>
            <h2>{sec.heading}</h2>
            {sec.sub ? <h3>{sec.sub}</h3> : null}
            {sec.bullets ? <ul>{sec.bullets.map((b) => <li key={b.slice(0, 40)}>{b}</li>)}</ul> : <p>{sec.text}</p>}
          </li>
        ))}
      </ol>
    )
  }

  if (layout === 'cards') {
    return (
      <div className="zo-article-cards">
        {sections.map((sec, i) => (
          <section key={`${sec.heading}-${i}`} className="zo-article-card">
            <h2>{sec.heading}</h2>
            {sec.sub ? <h3>{sec.sub}</h3> : null}
            <p>{sec.text}</p>
          </section>
        ))}
      </div>
    )
  }

  if (layout === 'split') {
    return (
      <div className="zo-article-split">
        {sections.map((sec, i) => (
          <section key={`${sec.heading}-${i}`} className={i % 2 === 0 ? 'is-problem' : 'is-solution'}>
            <h2>{sec.heading}</h2>
            {sec.sub ? <h3>{sec.sub}</h3> : null}
            {sec.bullets ? <ul>{sec.bullets.map((b) => <li key={b.slice(0, 40)}>{b}</li>)}</ul> : <p>{sec.text}</p>}
          </section>
        ))}
      </div>
    )
  }

  if (layout === 'story') {
    const [first, ...rest] = sections
    return (
      <div className="zo-article-story">
        {first ? (
          <>
            <h2>{first.heading}</h2>
            {first.text ? <blockquote>{first.text}</blockquote> : null}
          </>
        ) : null}
        {rest.map((sec, i) => (
          <section key={`${sec.heading}-${i}`}>
            <h2>{sec.heading}</h2>
            {sec.sub ? <h3>{sec.sub}</h3> : null}
            <p>{sec.text}</p>
          </section>
        ))}
      </div>
    )
  }

  return (
    <div className="zo-article-qa">
      {sections.map((sec, i) => (
        <details key={`${sec.heading}-${i}`} className="zo-article-qa-item" open={i < 2}>
          <summary>{sec.heading}</summary>
          {sec.sub ? <h3>{sec.sub}</h3> : null}
          {sec.bullets ? <ul>{sec.bullets.map((b) => <li key={b.slice(0, 40)}>{b}</li>)}</ul> : <p>{sec.text}</p>}
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
  const body = paragraphs(block.content)
  const hero = block.featured_image_url
  const layout = layoutFor(slug, block.layout_variant)
  const leftover = layout === 'qa' ? [] : body.slice(h2s.length)

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
              {desc ? <p className="zo-article-lead">{desc}</p> : null}
              {hero ? (
                <figure className="zo-article-hero">
                  <img src={hero} alt={h1} />
                </figure>
              ) : null}
              {block.intro ? paragraphs(block.intro).map((p) => <p key={p.slice(0, 40)}>{p}</p>) : null}
              <ArticleSections layout={layout} h2s={h2s} h3s={h3s} body={body} />
              {leftover.map((p) => <p key={p.slice(0, 48)}>{p}</p>)}
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
