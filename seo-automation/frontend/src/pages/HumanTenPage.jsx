import { useEffect, useState } from 'react'
import { ExternalLink, CheckCircle2, Copy } from 'lucide-react'
import { getHumanTen, markHumanRequested, markHumanBing } from '../api'

export default function HumanTenPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState('')

  const load = async () => {
    setError('')
    try {
      const res = await getHumanTen()
      setData(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Could not load today’s queue.')
    }
  }

  useEffect(() => { load() }, [])

  const copy = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(text)
      setTimeout(() => setCopied(''), 1500)
    } catch {
      setCopied('')
    }
  }

  const queue = data?.gsc_queue || []
  const bing = data?.bing || {}

  return (
    <div className="space-y-6 fade-in">
      <div>
        <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>
          Daily 10%
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text-3)', maxWidth: 640 }}>
          {data?.split || '90% machine / 10% human'}. The timer already submits sitemaps, IndexNow,
          and crawl/inspect. You only do what Google will not let an API do — about{' '}
          <strong>{data?.minutes_today ?? 10} minutes</strong> today.
        </p>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12 }}>
        <div className="card p-4">
          <div style={{ fontSize: 11, color: 'var(--text-4)', fontWeight: 600 }}>Today</div>
          <div style={{ fontSize: 18, fontWeight: 700, marginTop: 6 }}>{data?.today || '—'}</div>
        </div>
        <div className="card p-4">
          <div style={{ fontSize: 11, color: 'var(--text-4)', fontWeight: 600 }}>GSC requests used</div>
          <div style={{ fontSize: 18, fontWeight: 700, marginTop: 6 }}>
            {data?.requested_today || 0}/{data?.quota || 10}
          </div>
        </div>
        <div className="card p-4">
          <div style={{ fontSize: 11, color: 'var(--text-4)', fontWeight: 600 }}>Left in quota</div>
          <div style={{ fontSize: 18, fontWeight: 700, marginTop: 6 }}>{data?.remaining_quota ?? 10}</div>
        </div>
      </div>

      <div className="card p-5">
        <h2 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 8px', color: 'var(--text-1)' }}>
          1. Request indexing (required today)
        </h2>
        <p style={{ fontSize: 13, color: 'var(--text-3)', margin: '0 0 10px' }}>
          Open each link, then click <strong>Request indexing</strong> in Google Search Console.
          Come back and mark it done so tomorrow’s queue skips it. Cap is about 10 per day.
        </p>
        <p style={{ fontSize: 13, color: 'var(--text-3)', margin: '0 0 14px', lineHeight: 1.5 }}>
          Google must be signed in as an owner of <strong>{data?.gsc_property || 'https://zeorbit.com/'}</strong>.
          If you see “you don’t have access to this property,” switch Google accounts, or ask the owner to add this Gmail under Search Console → Settings → Users.
          The SEO tool API already uses a service account — your browser login is separate.
        </p>
        {queue.length === 0 ? (
          <p style={{ fontSize: 13, color: 'var(--green)' }}>No GSC clicks left in today’s quota — or hubs already marked.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {queue.map((row, i) => (
              <div key={row.url} style={{
                display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12,
                padding: '10px 12px', border: '1px solid var(--border)', borderRadius: 8,
              }}>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 12, color: 'var(--text-4)' }}>{i + 1}. {row.gsc_status}</div>
                  <div style={{ fontSize: 13, wordBreak: 'break-all', marginTop: 2 }}>{row.url}</div>
                </div>
                <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                  <a className="btn btn-primary" href={row.inspect_link} target="_blank" rel="noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
                    Open GSC <ExternalLink size={12} />
                  </a>
                  <button type="button" className="btn btn-secondary" style={{ fontSize: 12 }} onClick={() => copy(row.url)}>
                    {copied === row.url ? 'Copied' : 'Copy URL'}
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ fontSize: 12 }}
                    onClick={async () => {
                      const res = await markHumanRequested(row.url)
                      setData(res.data)
                    }}
                  >
                    Mark done
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card p-5">
        <h2 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 8px', color: 'var(--text-1)' }}>
          2. Bing Webmaster (once)
        </h2>
        <p style={{ fontSize: 13, color: 'var(--text-3)', margin: '0 0 12px' }}>{bing.detail}</p>
        {bing.done ? (
          <div style={{ color: 'var(--green)', display: 'flex', alignItems: 'center', gap: 6, fontSize: 13 }}>
            <CheckCircle2 size={15} /> Already marked done {bing.done_at ? `· ${bing.done_at}` : ''}
          </div>
        ) : (
          <div className="flex gap-2 flex-wrap">
            <a className="btn btn-primary" href={bing.url} target="_blank" rel="noreferrer">Open Bing Webmaster</a>
            <button type="button" className="btn btn-secondary" onClick={async () => {
              const res = await markHumanBing(true)
              setData(res.data)
            }}>I added the sitemap</button>
          </div>
        )}
        {bing.sitemap && (
          <p style={{ fontSize: 12, color: 'var(--text-4)', marginTop: 10, wordBreak: 'break-all' }}>
            Sitemap: {bing.sitemap}
          </p>
        )}
      </div>

      <div className="card p-5">
        <h2 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 8px', color: 'var(--text-1)' }}>
          3. AI search check (weekly, ~3 minutes)
        </h2>
        <p style={{ fontSize: 13, color: 'var(--text-3)', margin: '0 0 12px' }}>
          ChatGPT and Gemini will not take an API “cite us” command. Paste these with browsing/search on.
          Ranking and citations stay human-reviewed on purpose.
        </p>
        {(data?.citation_prompts || []).map((p) => (
          <div key={p} style={{
            display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'flex-start',
            padding: '10px 0', borderTop: '1px solid var(--border)', fontSize: 13,
          }}>
            <span>{p}</span>
            <button type="button" className="btn btn-secondary" style={{ flexShrink: 0 }} onClick={() => copy(p)}>
              <Copy size={12} /> {copied === p ? 'Copied' : 'Copy'}
            </button>
          </div>
        ))}
      </div>

      <div className="card p-5">
        <h2 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 8px', color: 'var(--text-1)' }}>
          4. Google Business Profile (optional weekly)
        </h2>
        <p style={{ fontSize: 13, color: 'var(--text-3)' }}>
          Reviews cannot be auto-generated. One real GBP post per week is the human 10% for Maps.
          Use Social in the sidebar, or ask a customer for a Google review.
        </p>
      </div>
    </div>
  )
}
