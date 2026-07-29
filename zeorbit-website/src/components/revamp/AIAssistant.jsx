import { useEffect, useRef, useState } from 'react'
import Modal from '../ui/Modal'
import { ArrowRight, Sparkles } from 'lucide-react'

const quickPrompts = [
  'I need AI agents for my business',
  'I need a website that converts',
  'I want to automate operations',
  'I need SEO / AEO / GEO',
]

function normalize(s) {
  return (s || '').toLowerCase().trim()
}

function routeAnswer(message) {
  const m = normalize(message)

  if (!m) {
    return {
      title: 'Ask ZeOrbit AI',
      body: 'Describe what you want to build—AI, software, website, app, automation, or growth—and we’ll map it to the right capability.',
      next: ['Start a Project', 'View Capabilities'],
    }
  }

  const picks = []
  if (m.includes('lead') || m.includes('sales') || m.includes('conversion')) picks.push('conversion-focused web development', 'lead capture automation')
  if (m.includes('website') || m.includes('web')) picks.push('website design & development', 'technical SEO + AEO readiness')
  if (m.includes('app') || m.includes('mobile') || m.includes('ios') || m.includes('android')) picks.push('mobile app development', 'API-backed product engineering')
  if (m.includes('seo') || m.includes('geo') || m.includes('aeo') || m.includes('search')) picks.push('SEO / AEO / GEO', 'paid search systems')
  if (m.includes('ai') || m.includes('agent') || m.includes('copilot') || m.includes('chatgpt') || m.includes('claude') || m.includes('gemini') || m.includes('rag')) picks.push('AI agents & custom AI applications', 'ChatGPT / Claude / Gemini integrations')
  if (m.includes('automation') || m.includes('workflow')) picks.push('business automation', 'workflow integrations')
  if (m.includes('data') || m.includes('pipeline') || m.includes('processing') || m.includes('analytics')) picks.push('data processing & analytics', 'decision-ready reporting')
  if (m.includes('software') || m.includes('crm') || m.includes('erp') || m.includes('dashboard')) picks.push('custom software development', 'systems integration')
  if (m.includes('ecommerce') || m.includes('shopify') || m.includes('store')) picks.push('ecommerce optimization', 'conversion-focused storefronts')

  const title = 'Recommended ZeOrbit capabilities'
  const body =
    picks.length > 0
      ? `Based on what you shared, start with: ${Array.from(new Set(picks)).slice(0, 4).join('; ')}.`
      : 'Add a bit more context (what you’re building + the outcome you need). We’ll map it to the right ZeOrbit stack.'

  const next = ['Start a Project', 'Go to Contact', 'Explore AI Solutions']
  return { title, body, next }
}

export default function AIAssistant({ open, onOpenChange }) {
  const [messages, setMessages] = useState([
    { id: 'm0', role: 'assistant', text: 'Hi — I’m ZeOrbit AI. Ask about AI agents, custom software, websites, mobile apps, automation, or SEO / AEO / GEO.' },
  ])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)

  const inputRef = useRef(null)
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 60)
    }
  }, [open])

  function scrollToBottom() {
    const el = document.getElementById('rv-ai-messages')
    if (el) el.scrollTop = el.scrollHeight
  }

  useEffect(() => {
    if (open) scrollToBottom()
  }, [open, messages.length])

  async function send(text) {
    const trimmed = (text || '').trim()
    if (!trimmed || sending) return

    setSending(true)
    setMessages((prev) => [...prev, { id: `u-${Date.now()}`, role: 'user', text: trimmed }])
    setInput('')

    // No live AI endpoint here — deterministic routing for now.
    await new Promise((r) => setTimeout(r, 350))

    const ans = routeAnswer(trimmed)
    setMessages((prev) => [
      ...prev,
      { id: `a-${Date.now()}`, role: 'assistant', text: `${ans.title}\n\n${ans.body}` },
    ])
    setSending(false)
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send(input)
    }
  }

  return (
    <>
      <button
        type="button"
        className="rv-ai-fab"
        onClick={() => onOpenChange(true)}
        aria-label="Ask ZeOrbit AI"
      >
        <Sparkles size={16} />
        Ask ZeOrbit AI
      </button>

      <Modal
        open={open}
        onClose={() => onOpenChange(false)}
        title="Ask ZeOrbit AI"
        maxWidth={520}
        footer={
          <button type="button" className="btn btn-ghost" onClick={() => onOpenChange(false)}>
            Close
          </button>
        }
      >
        <div className="rv-ai-modal">
          <div id="rv-ai-messages" className="rv-ai-messages" role="log" aria-live="polite">
            {messages.map((m) => (
              <div key={m.id} className={`rv-ai-msg ${m.role}`}>
                <div className="rv-ai-bubble">
                  {m.text.split('\n').map((line, i) => (
                    <p key={i} style={{ margin: 0 }}>{line}</p>
                  ))}
                </div>
              </div>
            ))}
            {sending ? <div className="rv-ai-msg assistant"><div className="rv-ai-bubble">Thinking…</div></div> : null}
          </div>

          <div className="rv-ai-suggestions" aria-label="Quick prompts">
            {quickPrompts.slice(0, 4).map((p) => (
              <button
                key={p}
                type="button"
                className="rv-ai-chip"
                onClick={() => send(p)}
              >
                {p}
              </button>
            ))}
          </div>

          <div className="rv-ai-composer">
            <textarea
              ref={inputRef}
              className="rv-ai-textarea"
              value={input}
              rows={2}
              placeholder="Ask anything about your project…"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
            />
            <button
              type="button"
              className="rv-ai-send"
              onClick={() => send(input)}
              disabled={!input.trim() || sending}
              aria-label="Send message"
            >
              <ArrowRight size={16} />
            </button>
          </div>

          <div className="rv-ai-footnote">
            This assistant is currently routing suggestions (no live AI endpoint connected yet).
          </div>
        </div>
      </Modal>
    </>
  )
}

