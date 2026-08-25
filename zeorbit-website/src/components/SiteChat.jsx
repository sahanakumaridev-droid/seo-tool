import { useEffect, useId, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { MessageCircle, Send, X } from 'lucide-react'
import { SITE_CONTACT } from '../data/revampContent'
import { OPEN_CHAT_EVENT } from '../utils/openSiteChat'

const TOPICS = [
  {
    id: 'website',
    label: 'I need a new website',
    match: (m) => m.includes('website') || m.includes('web design') || m.includes('wordpress') || m.includes('shopify'),
    reply:
      'Great — we build conversion-focused websites on WordPress, Shopify, Wix, and custom stacks. Tell me your timeline or industry and we’ll point you to the right next step.',
    followUps: [
      { id: 'web-timeline', label: 'I need it in 2–4 weeks', reply: 'Got it — a focused launch window works best with a clear brief. Share your goals on a free quote and we’ll confirm what’s realistic.' },
      { id: 'web-platform', label: 'Which platform fits me?', reply: 'WordPress for content-heavy sites, Shopify for ecommerce, Wix/Squarespace for faster brochure sites, custom when you need unique product UX. A short call usually settles this in minutes.' },
      { id: 'quote', label: 'Get a free quote', kind: 'quote' },
    ],
  },
  {
    id: 'app',
    label: 'I need a mobile app',
    match: (m) => m.includes('app') || m.includes('mobile') || m.includes('ios') || m.includes('android'),
    reply:
      'We design and ship iOS/Android apps with clean UX and solid backends. Are you starting from an idea, a prototype, or an existing product?',
    followUps: [
      { id: 'app-idea', label: 'Starting from an idea', reply: 'Perfect — we’ll map MVP scope, screens, and a build path so you don’t overbuild. Send a short brief and we’ll outline phase one.' },
      { id: 'app-existing', label: 'I already have an app', reply: 'We can audit UX, performance, and the roadmap — then improve or rebuild where it pays off. Share the store link or a screen recording if you have one.' },
      { id: 'quote', label: 'Get a free quote', kind: 'quote' },
    ],
  },
  {
    id: 'seo',
    label: 'I need SEO & ads help',
    match: (m) => m.includes('seo') || m.includes('ads') || m.includes('ppc') || m.includes('google ads') || m.includes('marketing'),
    reply:
      'We help with technical SEO, local visibility, content, and paid campaigns. Which matters most right now — organic search, local maps, or paid ads?',
    followUps: [
      { id: 'seo-organic', label: 'Organic / SEO', reply: 'We’ll start with a technical + content pass: crawl issues, page intent, and local signals. Share your site URL on a quote request and we’ll prioritize fixes.' },
      { id: 'seo-ads', label: 'Paid ads', reply: 'We set up Google Ads and social campaigns around clear offers and tracking — not vanity clicks. Tell us your monthly budget range when you request a quote.' },
      { id: 'quote', label: 'Get a free quote', kind: 'quote' },
    ],
  },
  {
    id: 'care',
    label: 'Tell me about Master Care',
    match: (m) => m.includes('master care') || m.includes('maintenance') || (m.includes('care') && !m.includes('medicare')),
    reply:
      'Master Care keeps your site updated, secure, backed up, and supported after launch — so you’re not chasing plugins and downtime alone. Want what’s included, or ready to start?',
    followUps: [
      { id: 'care-included', label: 'What’s included?', reply: 'Typical Master Care covers updates, security monitoring, backups, uptime checks, and a support lane for fixes. Exact scope depends on your stack — WordPress, Shopify, or custom.' },
      { id: 'care-start', label: 'Start Master Care', kind: 'link', href: '/website-designing#care', linkLabel: 'Open Master Care' },
      { id: 'quote', label: 'Get a free quote', kind: 'quote' },
    ],
  },
  {
    id: 'project',
    label: 'I want to start a project',
    match: (m) => m.includes('project') || m.includes('start') || m.includes('quote') || m.includes('brief'),
    reply:
      'Perfect. Share a short brief — goals, timeline, and budget range — and we’ll map the next step. You can type here or jump to a free quote form.',
    followUps: [
      { id: 'quote', label: 'Open free quote form', kind: 'quote' },
      { id: 'call', label: 'Prefer a call', kind: 'tel' },
      { id: 'email', label: 'Email us instead', kind: 'email' },
    ],
  },
]

const WELCOME = {
  id: 'welcome',
  role: 'assistant',
  text: 'Hi — how can ZeOrbit help today? Pick a quick option below, or type your own message.',
}

function findTopic(message) {
  const m = (message || '').toLowerCase()
  return TOPICS.find((t) => t.match(m)) || null
}

function defaultReply() {
  return 'Thanks — tell us a bit more about what you need, or pick a quick option if you’re not sure where to start.'
}

export default function SiteChat() {
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [messages, setMessages] = useState([WELCOME])
  const [chips, setChips] = useState(() => TOPICS.map((t) => ({ id: t.id, label: t.label, kind: 'topic' })))
  const titleId = useId()
  const listRef = useRef(null)
  const inputRef = useRef(null)
  const sendingRef = useRef(false)

  useEffect(() => {
    const onOpen = (event) => {
      setOpen(true)
      const prefill = event?.detail?.prefill
      if (typeof prefill === 'string' && prefill.trim()) {
        window.setTimeout(() => {
          void handleSend(prefill.trim())
        }, 160)
      }
    }
    window.addEventListener(OPEN_CHAT_EVENT, onOpen)
    return () => window.removeEventListener(OPEN_CHAT_EVENT, onOpen)
  }, [])

  useEffect(() => {
    if (!open) return undefined
    const t = window.setTimeout(() => inputRef.current?.focus(), 80)
    return () => window.clearTimeout(t)
  }, [open])

  useEffect(() => {
    if (!open) return
    const el = listRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [open, messages.length, sending, chips])

  useEffect(() => {
    if (!open) return undefined
    const onKey = (e) => {
      if (e.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open])

  function chipsForTopic(topic) {
    if (!topic?.followUps?.length) return []
    return topic.followUps.map((f) => ({
      id: f.id,
      label: f.label,
      kind: f.kind || 'reply',
      reply: f.reply,
      href: f.href,
    }))
  }

  async function handleSend(text, options = {}) {
    const trimmed = (text || '').trim()
    if (!trimmed || sendingRef.current) return
    sendingRef.current = true
    setSending(true)
    setChips([])
    setInput('')
    setMessages((prev) => [...prev, { id: `u-${Date.now()}`, role: 'user', text: trimmed }])

    await new Promise((r) => window.setTimeout(r, 320))

    const topic = options.topic || findTopic(trimmed)
    const replyText = options.replyText || topic?.reply || defaultReply()
    setMessages((prev) => [...prev, { id: `a-${Date.now()}`, role: 'assistant', text: replyText }])

    if (options.nextChips) {
      setChips(options.nextChips)
    } else if (topic) {
      setChips(chipsForTopic(topic))
    } else {
      setChips(TOPICS.map((t) => ({ id: t.id, label: t.label, kind: 'topic' })))
    }

    sendingRef.current = false
    setSending(false)
  }

  function onChipClick(chip) {
    if (sendingRef.current) return

    if (chip.kind === 'topic') {
      const topic = TOPICS.find((t) => t.id === chip.id)
      if (!topic) return
      void handleSend(topic.label, { topic, replyText: topic.reply, nextChips: chipsForTopic(topic) })
      return
    }

    if (chip.kind === 'quote') {
      setChips([])
      setMessages((prev) => [
        ...prev,
        { id: `u-${Date.now()}`, role: 'user', text: chip.label },
        {
          id: `a-${Date.now() + 1}`,
          role: 'assistant',
          text: 'Opening the free quote form — share a short brief and we’ll reply with next steps.',
          cta: { to: '/contact#contact', label: 'Go to free quote' },
        },
      ])
      return
    }

    if (chip.kind === 'link' && chip.href) {
      setChips([])
      setMessages((prev) => [
        ...prev,
        { id: `u-${Date.now()}`, role: 'user', text: chip.label },
        {
          id: `a-${Date.now() + 1}`,
          role: 'assistant',
          text: 'Here’s Master Care — hosting, updates, security, and support after launch.',
          cta: { to: chip.href, label: 'View Master Care' },
        },
      ])
      return
    }

    if (chip.kind === 'tel') {
      setChips([])
      setMessages((prev) => [
        ...prev,
        { id: `u-${Date.now()}`, role: 'user', text: chip.label },
        {
          id: `a-${Date.now() + 1}`,
          role: 'assistant',
          text: `Call us at ${SITE_CONTACT.phone} — or leave a message here and we’ll follow up.`,
          ctaTel: SITE_CONTACT.phoneTel,
        },
      ])
      return
    }

    if (chip.kind === 'email') {
      setChips([])
      setMessages((prev) => [
        ...prev,
        { id: `u-${Date.now()}`, role: 'user', text: chip.label },
        {
          id: `a-${Date.now() + 1}`,
          role: 'assistant',
          text: `Email ${SITE_CONTACT.email} anytime — or keep chatting here.`,
          ctaMail: SITE_CONTACT.email,
        },
      ])
      return
    }

    if (chip.kind === 'reply' && chip.reply) {
      void handleSend(chip.label, { replyText: chip.reply, nextChips: [] })
    }
  }

  const mailHref = `mailto:${SITE_CONTACT.email}?subject=${encodeURIComponent('Chat with ZeOrbit')}&body=${encodeURIComponent("Hi ZeOrbit — I'd like help with my website / app project. Here's what I need:\n\n")}`

  return (
    <>
      <button
        type="button"
        className={`zo-chat-fab${open ? ' is-open' : ''}`}
        aria-label={open ? 'Close chat' : 'Open chat'}
        aria-expanded={open}
        title="Chat"
        onClick={() => setOpen((v) => !v)}
      >
        {open ? <X size={20} strokeWidth={2.2} aria-hidden /> : <MessageCircle size={20} strokeWidth={2.2} aria-hidden />}
      </button>

      {open ? (
        <div className="zo-site-chat" role="dialog" aria-modal="true" aria-labelledby={titleId}>
          <div className="zo-site-chat-panel">
            <header className="zo-site-chat-head">
              <div className="zo-site-chat-brand">
                <span className="zo-site-chat-icon" aria-hidden>
                  <MessageCircle size={18} strokeWidth={2.2} />
                </span>
                <div>
                  <h2 id={titleId}>Chat with ZeOrbit</h2>
                  <p>Usually replies in a few minutes</p>
                </div>
              </div>
              <button type="button" className="zo-site-chat-close" aria-label="Close chat" onClick={() => setOpen(false)}>
                <X size={18} strokeWidth={2.2} />
              </button>
            </header>

            <div ref={listRef} className="zo-site-chat-messages" role="log" aria-live="polite">
              {messages.map((m) => (
                <div key={m.id} className={`zo-site-chat-msg is-${m.role}`}>
                  <div className="zo-site-chat-bubble">
                    <p>{m.text}</p>
                    {m.cta ? (
                      <Link className="zo-site-chat-inline-cta" to={m.cta.to} onClick={() => setOpen(false)}>
                        {m.cta.label}
                      </Link>
                    ) : null}
                    {m.ctaTel ? (
                      <a className="zo-site-chat-inline-cta" href={`tel:${m.ctaTel}`}>
                        Call now
                      </a>
                    ) : null}
                    {m.ctaMail ? (
                      <a className="zo-site-chat-inline-cta" href={`mailto:${m.ctaMail}`}>
                        Send email
                      </a>
                    ) : null}
                  </div>
                </div>
              ))}
              {sending ? (
                <div className="zo-site-chat-msg is-assistant">
                  <div className="zo-site-chat-bubble">
                    <p>Typing…</p>
                  </div>
                </div>
              ) : null}
            </div>

            {chips.length > 0 && !sending ? (
              <div className="zo-site-chat-prefills" aria-label="Quick replies">
                {chips.map((chip) => (
                  <button
                    key={chip.id}
                    type="button"
                    className="zo-site-chat-chip"
                    onClick={() => onChipClick(chip)}
                  >
                    {chip.label}
                  </button>
                ))}
              </div>
            ) : null}

            <form
              className="zo-site-chat-composer"
              onSubmit={(e) => {
                e.preventDefault()
                void handleSend(input)
              }}
            >
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message…"
                autoComplete="off"
              />
              <button type="submit" aria-label="Send" disabled={!input.trim() || sending}>
                <Send size={16} strokeWidth={2.2} />
              </button>
            </form>

            <footer className="zo-site-chat-footer">
              <a href={mailHref}>Email us</a>
              <a href={`tel:${SITE_CONTACT.phoneTel}`}>Call {SITE_CONTACT.phone}</a>
              <Link to="/contact#contact" onClick={() => setOpen(false)}>
                Free quote
              </Link>
            </footer>
          </div>
        </div>
      ) : null}
    </>
  )
}
