import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  CheckCircle2, XCircle, AlertTriangle, RefreshCw, Plug, ExternalLink,
} from 'lucide-react'
import { getGoogleLiveStatus, getSocialPlatforms } from '../api'

function StatusPill({ ok, label }) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      fontSize: 11.5, fontWeight: 700, padding: '3px 9px', borderRadius: 6,
      color: ok ? 'var(--green)' : 'var(--amber)',
      background: ok ? 'var(--green-soft)' : 'var(--amber-soft)',
    }}>
      {ok ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
      {label}
    </span>
  )
}

function ModuleCard({ title, to, live, detail, blocking = [], docs, formCmd }) {
  return (
    <div className="card p-5" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div className="flex items-center justify-between gap-3">
        <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-1)', margin: 0 }}>{title}</h3>
        <StatusPill ok={!!live} label={live ? 'LIVE' : 'NOT LIVE'} />
      </div>
      {detail && (
        <p style={{ fontSize: 12.5, color: 'var(--text-3)', margin: 0, lineHeight: 1.5 }}>{detail}</p>
      )}
      {blocking?.length > 0 && (
        <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12.5, color: 'var(--text-2)', lineHeight: 1.55 }}>
          {blocking.map((b, i) => <li key={i}>{b}</li>)}
        </ul>
      )}
      {formCmd && (
        <code style={{
          display: 'block', fontSize: 11.5, padding: '8px 10px', borderRadius: 8,
          background: 'var(--bg-raised)', color: 'var(--text-2)', overflowX: 'auto',
        }}>
          {formCmd}
        </code>
      )}
      <div className="flex gap-2" style={{ marginTop: 'auto' }}>
        {to && <Link to={to} className="btn btn-secondary" style={{ fontSize: 12.5 }}>Open module</Link>}
        {docs && (
          <a href={docs} target="_blank" rel="noreferrer" className="btn btn-ghost" style={{ fontSize: 12.5 }}>
            Docs <ExternalLink size={12} />
          </a>
        )}
      </div>
    </div>
  )
}

export default function IntegrationsPage() {
  const [data, setData] = useState(null)
  const [social, setSocial] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [live, platforms] = await Promise.all([
        getGoogleLiveStatus().catch(() => null),
        getSocialPlatforms().catch(() => ({ data: null })),
      ])
      if (!live?.data) {
        setError('Could not load Google integration status. Is the API running?')
      } else {
        setData(live.data)
      }
      setSocial(platforms.data)
    } catch (e) {
      setError('Could not load integration status. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const mods = data?.modules || {}
  const ads = mods.google_ads || {}
  const idx = mods.google_indexing || {}
  const ai = data?.free_ai || {}

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>
            API Integrations
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-3)' }}>
            Live Google automation status — no mock data when DEMO_MODE is off.
          </p>
        </div>
        <button onClick={load} disabled={loading} className="btn btn-primary flex items-center gap-2">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {error && <div className="alert alert-error">⚠ {error}</div>}

      {data && (
        <div className="alert" style={{
          background: data.all_google_live ? 'var(--green-soft)' : 'var(--amber-soft)',
          borderColor: data.all_google_live ? 'var(--green)' : 'var(--amber)',
        }}>
          {data.all_google_live
            ? <><CheckCircle2 size={15} /> All Google modules are LIVE.</>
            : <><AlertTriangle size={15} /> Google automation is incomplete — finish blockers below. DEMO_MODE={String(data.demo_mode)}</>}
        </div>
      )}

      {loading && !data ? (
        <div className="card p-8 text-center" style={{ color: 'var(--text-4)' }}>Loading…</div>
      ) : (
        <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))' }}>
          <ModuleCard
            title="Google Ads"
            to="/google-ads"
            live={ads.live}
            detail={ads.detail}
            blocking={ads.blocking}
            docs={ads.docs}
            formCmd={ads.fix_cmd}
          />
          <ModuleCard
            title="Google Indexing (Search Console)"
            to="/indexing"
            live={idx.live}
            detail={idx.crawl_fallback ? 'Crawl checks work free; live “Indexed by Google” needs Search Console.' : undefined}
            blocking={idx.blocking}
            docs={idx.docs}
          />
          <ModuleCard
            title="Free AI (Groq / Gemini)"
            live={ai.ready}
            detail={ai.provider ? `Active provider: ${ai.provider}` : 'Used for content and Ads copy'}
            blocking={ai.blocking}
          />
        </div>
      )}

      {social && (
        <div className="card p-5">
          <div className="flex items-center gap-2" style={{ marginBottom: 12 }}>
            <Plug size={16} style={{ color: 'var(--brand)' }} />
            <h3 style={{ fontSize: 15, fontWeight: 700, margin: 0, color: 'var(--text-1)' }}>Social platforms</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(social).map(([name, ok]) => (
              <span key={name} style={{
                fontSize: 12, padding: '5px 10px', borderRadius: 8,
                border: '1px solid var(--border)', color: 'var(--text-2)',
                display: 'inline-flex', alignItems: 'center', gap: 6,
                textTransform: 'capitalize',
              }}>
                {ok ? <CheckCircle2 size={12} style={{ color: 'var(--green)' }} /> : <XCircle size={12} style={{ color: 'var(--text-4)' }} />}
                {name}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="card p-5" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-1)', margin: 0 }}>Reddit presence for ZeOrbit</h3>
        <p style={{ fontSize: 12.5, color: 'var(--text-3)', margin: 0, lineHeight: 1.55 }}>
          Reddit threads often rank in Google. Do not spam or use unofficial automation — Reddit bans that.
          Build mentions by being useful in communities that already talk about websites, WordPress, Shopify, and local business.
        </p>
        <ol style={{ margin: 0, paddingLeft: 18, fontSize: 12.5, color: 'var(--text-2)', lineHeight: 1.6 }}>
          <li>Create a company account that names ZeOrbit, with a short bio, website, and what you actually build (WordPress / Shopify / redesigns).</li>
          <li>Start in relevant subs: r/webdev, r/WordPress, r/shopify, r/smallbusiness, r/Entrepreneur, and city subs for your target markets. Read rules first; many ban self-promo.</li>
          <li>Spend 2–4 weeks answering questions with specifics (process, pricing ranges, mobile/SEO pitfalls). Mention ZeOrbit only when it is a natural next step.</li>
          <li>Publish one genuine case or how-to as a text post when the sub allows it. Link zeorbit.com in comments, not as the entire post.</li>
          <li>Search Reddit + Google for “website designer [city]”, “WordPress agency”, “Shopify help” and reply to existing threads with a real answer — those URLs are what Google surfaces.</li>
          <li>Track branded + service queries in Search Console. A useful Reddit thread that names ZeOrbit is more durable than a directory listing.</li>
        </ol>
        <a href="https://www.reddit.com/search/?q=website%20design%20small%20business" target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ fontSize: 12.5, width: 'fit-content' }}>
          Search Reddit discussions <ExternalLink size={12} />
        </a>
      </div>

      <div className="card p-5" style={{ fontSize: 12.5, color: 'var(--text-3)', lineHeight: 1.6 }}>
        <strong style={{ color: 'var(--text-1)' }}>Credentials stay in backend/.env only.</strong>
        {' '}Never paste passwords or API keys into chat. After updating .env, restart the API and click Refresh.
        Verify from terminal: <code>python3 scripts/verify_google_live.py</code>
      </div>
    </div>
  )
}
