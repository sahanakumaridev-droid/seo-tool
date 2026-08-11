import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Plus, X, Megaphone, CheckCircle2, ExternalLink, AlertTriangle, ArrowLeft, ArrowRight, Sparkles, Globe, FileText } from 'lucide-react'
import { getGoogleAdsStatus, createGoogleAdsCampaign, suggestGoogleAdsCopy, listLandingPagesForAds, listGoogleAdsCampaigns, setGoogleAdsCampaignStatus } from '../api'

const STEPS = ['Landing page & business', 'Create your ads', 'Set your budget']

const HEADLINE_MAX = 30
const DESCRIPTION_MAX = 90

function suggestAdCopy({ businessName, category, city }) {
  const cat = category.trim() || 'services'
  const catLower = cat.toLowerCase()
  const place = city.trim()
  const name = businessName.trim() || 'Your Business'

  const headlines = [
    place ? `${cat} in ${place}` : cat,
    `${cat} Experts`,
    `Get a Free Quote`,
    `Call ${name}`,
    place ? `Top-Rated Near ${place}` : `Top-Rated ${cat}`,
  ].map(h => h.slice(0, HEADLINE_MAX))

  const descriptions = [
    `${name} provides reliable ${catLower}. Free quotes available.`,
    place ? `Serving ${place}. Fast, affordable, book online.` : `Fast, affordable service. Book online in minutes.`,
  ].map(d => d.slice(0, DESCRIPTION_MAX))

  const keywords = [
    catLower,
    `${catLower} near me`,
    place ? `${catLower} in ${place}` : `best ${catLower}`,
    `affordable ${catLower}`,
  ]
  return { headlines, descriptions, keywords }
}

function isAdsReadyUrl(url) {
  try {
    const host = new URL(url.includes('://') ? url : `https://${url}`).hostname
    if (!host || host === 'localhost' || /^\d+\.\d+\.\d+\.\d+$/.test(host)) return false
    if (/^(127\.|10\.|192\.168\.|0\.)/.test(host)) return false
    return /^[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$/i.test(host)
  } catch {
    return false
  }
}

function ListField({ label, hint, values, setValues, min, max, maxLength, placeholder }) {
  const update = (i, v) => setValues(vs => vs.map((x, idx) => idx === i ? v : x))
  const add = () => values.length < max && setValues(vs => [...vs, ''])
  const remove = (i) => values.length > min && setValues(vs => vs.filter((_, idx) => idx !== i))

  return (
    <div>
      <div className="flex items-center justify-between" style={{ marginBottom: 6 }}>
        <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-2)' }}>{label}</label>
        <span style={{ fontSize: 11.5, color: 'var(--text-4)' }}>{hint}</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {values.map((v, i) => (
          <div key={i} style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <input
              type="text" value={v} maxLength={maxLength}
              onChange={e => update(i, e.target.value)}
              placeholder={placeholder}
              style={{ flex: 1, padding: '9px 12px', fontSize: 13.5 }}
            />
            <span style={{ fontSize: 10.5, color: 'var(--text-4)', width: 32, textAlign: 'right', flexShrink: 0 }}>{v.length}/{maxLength}</span>
            <button type="button" onClick={() => remove(i)} disabled={values.length <= min}
              className="btn btn-ghost" style={{ padding: 8 }}>
              <X size={13} />
            </button>
          </div>
        ))}
      </div>
      {values.length < max && (
        <button type="button" onClick={add} className="btn btn-ghost" style={{ marginTop: 8, fontSize: 12.5, padding: '6px 10px' }}>
          <Plus size={13} /> Add {label.toLowerCase().replace(/s$/, '')}
        </button>
      )}
    </div>
  )
}

function StepDots({ step }) {
  return (
    <div style={{ display: 'flex', gap: 6, marginBottom: 6 }}>
      {STEPS.map((_, i) => (
        <span key={i} style={{
          height: 5, width: i === step ? 26 : 14, borderRadius: 999,
          background: i <= step ? 'var(--brand)' : 'var(--border-bright)', transition: 'all .2s',
        }} />
      ))}
    </div>
  )
}

function applyIncomingPrefill(incoming) {
  if (!incoming) return null
  return {
    businessName: incoming.businessName || incoming.business_name || '',
    finalUrl: incoming.finalUrl || incoming.final_url || incoming.public_url || '',
    category: incoming.category || incoming.business_type || '',
    city: incoming.city || '',
    keywords: Array.isArray(incoming.keywords) ? incoming.keywords : [],
    title: incoming.title || '',
  }
}

export default function GoogleAdsPage() {
  const location = useLocation()
  const [mode, setMode] = useState('setup')
  const [llmProvider, setLlmProvider] = useState(null)
  const [statusDetail, setStatusDetail] = useState('')
  const [adsAccount, setAdsAccount] = useState({
    customer_id: '',
    login_customer_id: '',
    open_hint: '',
    campaigns_url: '',
    auto_create_on_publish: false,
    auto_enable: false,
  })
  const [step, setStep] = useState(0)

  const [biz, setBiz] = useState({ businessName: '', finalUrl: '', category: '', city: '' })
  const [selectedPageId, setSelectedPageId] = useState('')

  const [landingPages, setLandingPages] = useState([])
  const [landingMeta, setLandingMeta] = useState({ total: 0, ads_ready_count: 0, public_base_url: '' })
  const [landingLoading, setLandingLoading] = useState(true)
  const [landingError, setLandingError] = useState('')

  const [headlines, setHeadlines] = useState(['', '', ''])
  const [descriptions, setDescriptions] = useState(['', ''])
  const [keywords, setKeywords] = useState('')
  const [suggested, setSuggested] = useState(false)

  const [dailyBudget, setDailyBudget] = useState('25')
  const [loading, setLoading] = useState(false)
  const [suggesting, setSuggesting] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [goLiveOnCreate, setGoLiveOnCreate] = useState(true)
  const [campaigns, setCampaigns] = useState([])
  const [campaignsLoading, setCampaignsLoading] = useState(false)
  const [campaignActionId, setCampaignActionId] = useState('')
  const [campaignNote, setCampaignNote] = useState('')
  const [resultLive, setResultLive] = useState(false)

  const loadCampaigns = () => {
    setCampaignsLoading(true)
    listGoogleAdsCampaigns(30)
      .then(r => {
        setCampaigns(r.data.campaigns || [])
        if (!r.data.ok && r.data.error) setCampaignNote(r.data.error)
      })
      .catch(() => setCampaignNote('Could not load campaigns.'))
      .finally(() => setCampaignsLoading(false))
  }

  const toggleCampaign = async (id, enable) => {
    setCampaignActionId(id)
    setCampaignNote('')
    try {
      const r = await setGoogleAdsCampaignStatus(id, enable)
      if (r.data.ok) {
        setCampaignNote(r.data.note || (enable ? 'Approved & live from this tool.' : 'Paused.'))
        if (result?.campaign_id === id) setResultLive(!!enable)
        loadCampaigns()
      } else {
        setCampaignNote(r.data.error || 'Status update failed.')
      }
    } catch {
      setCampaignNote('Could not update campaign status.')
    }
    setCampaignActionId('')
  }

  useEffect(() => {
    getGoogleAdsStatus()
      .then(r => {
        setMode(r.data.mode || (r.data.demo ? 'demo' : r.data.live ? 'live' : 'setup'))
        setLlmProvider(r.data.llm_provider || null)
        setStatusDetail(r.data.detail || '')
        setAdsAccount({
          customer_id: r.data.customer_id || '',
          login_customer_id: r.data.login_customer_id || '',
          open_hint: r.data.open_hint || '',
          campaigns_url: r.data.campaigns_url || '',
          auto_create_on_publish: !!r.data.auto_create_on_publish,
          auto_enable: !!r.data.auto_enable,
        })
        if (r.data.live) {
          // load after status confirms live
          listGoogleAdsCampaigns(30)
            .then(res => setCampaigns(res.data.campaigns || []))
            .catch(() => {})
        }
      })
      .catch(() => { setMode('setup') })
  }, [])

  useEffect(() => {
    setLandingLoading(true)
    listLandingPagesForAds(0, 50)
      .then(r => {
        setLandingPages(r.data.pages || [])
        setLandingMeta({
          total: r.data.total || 0,
          ads_ready_count: r.data.ads_ready_count || 0,
          public_base_url: r.data.public_base_url || '',
        })
        setLandingError('')
      })
      .catch(() => {
        setLandingPages([])
        setLandingError('Could not load published SEO pages.')
      })
      .finally(() => setLandingLoading(false))
  }, [])

  // Prefill from Content / Preview navigation state or query string
  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const fromQuery = {
      finalUrl: params.get('finalUrl') || '',
      businessName: params.get('businessName') || '',
      category: params.get('category') || '',
      city: params.get('city') || '',
    }
    const prefill = applyIncomingPrefill(location.state) || (fromQuery.finalUrl ? fromQuery : null)
    if (!prefill) return
    setBiz(b => ({
      businessName: prefill.businessName || b.businessName,
      finalUrl: prefill.finalUrl || b.finalUrl,
      category: prefill.category || b.category,
      city: prefill.city || b.city,
    }))
    if (prefill.keywords?.length) {
      setKeywords(prefill.keywords.join('\n'))
      setSuggested(true)
    }
  }, [location.state, location.search])

  const selectLandingPage = (page) => {
    if (!page) {
      setSelectedPageId('')
      return
    }
    setSelectedPageId(page.id)
    const titleBit = String(page.title || '').split(/[-|–]/)[0] || ''
    setBiz(b => ({
      ...b,
      finalUrl: page.public_url,
      category: b.category || page.business_type || '',
      city: b.city || page.city || '',
      businessName: b.businessName || titleBit,
    }))
    if (page.keywords?.length) {
      setKeywords(page.keywords.join('\n'))
    }
    setSuggested(false)
  }

  const goToAdsStep = async () => {
    if (!suggested) {
      setSuggesting(true)
      try {
        const res = await suggestGoogleAdsCopy({
          business_name: biz.businessName,
          category: biz.category,
          city: biz.city,
        })
        if (res.data?.headlines?.length) {
          setHeadlines(res.data.headlines.slice(0, 15))
          setDescriptions(res.data.descriptions?.slice(0, 4) || ['', ''])
          if (!keywords.trim()) setKeywords((res.data.keywords || []).join('\n'))
        } else {
          const s = suggestAdCopy(biz)
          setHeadlines(s.headlines)
          setDescriptions(s.descriptions)
          if (!keywords.trim()) setKeywords(s.keywords.join('\n'))
        }
      } catch {
        const s = suggestAdCopy(biz)
        setHeadlines(s.headlines)
        setDescriptions(s.descriptions)
        if (!keywords.trim()) setKeywords(s.keywords.join('\n'))
      }
      setSuggested(true)
      setSuggesting(false)
    }
    setStep(1)
  }

  const urlHasTld = isAdsReadyUrl(biz.finalUrl.trim())
  const bizValid = biz.businessName.trim() && biz.finalUrl.trim() && urlHasTld && biz.category.trim()
  const adsValid = headlines.every(h => h.trim()) && descriptions.every(d => d.trim()) && keywords.trim()

  const handleCreate = async () => {
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await createGoogleAdsCampaign({
        campaign_name: `${biz.businessName.trim()} - ${biz.category.trim()}`,
        daily_budget: Number(dailyBudget),
        final_url: biz.finalUrl.trim(),
        keywords: keywords.split(/[\n,]/).map(k => k.trim()).filter(Boolean),
        headlines: headlines.map(h => h.trim()).filter(Boolean),
        descriptions: descriptions.map(d => d.trim()).filter(Boolean),
        enable: true, // always approve/go-live from ZeOrbit — never send users to Google Ads UI
      })
      if (res.data.success) {
        setResult(res.data)
        setResultLive(true)
        // Belt-and-suspenders: if API still returned a paused campaign, enable it here.
        if (res.data.campaign_id) {
          try {
            const en = await setGoogleAdsCampaignStatus(res.data.campaign_id, true)
            if (en.data?.ok) setCampaignNote(en.data.note || 'Approved & live from ZeOrbit.')
            else if (en.data?.error) setCampaignNote(en.data.error)
          } catch {
            /* create already succeeded */
          }
        }
        loadCampaigns()
      } else setError(res.data.error || 'Campaign creation failed.')
    } catch {
      setError('Could not reach the server. Please try again.')
    }
    setLoading(false)
  }

  if (result) {
    const live = resultLive || goLiveOnCreate
    return (
      <div className="space-y-5 fade-in" style={{ maxWidth: 720 }}>
        <div className="card p-6" style={{ borderColor: 'var(--green)' }}>
          <div className="flex items-center gap-2" style={{ marginBottom: 8 }}>
            <CheckCircle2 size={20} style={{ color: 'var(--green)' }} />
            <h3 style={{ fontSize: 17, fontWeight: 700, color: 'var(--text-1)' }}>
              {live ? 'Campaign approved in ZeOrbit' : 'Campaign ready — approve here'}
            </h3>
          </div>
          <p style={{ fontSize: 13.5, color: 'var(--text-3)', margin: '0 0 16px' }}>
            Campaign ID: <span style={{ fontFamily: 'monospace' }}>{result.campaign_id}</span>
            {result.demo
              ? ' — demo simulation.'
              : live
                ? ' — enabled from this tool. Google may briefly show Under review (automatic).'
                : ' — still paused. Click Approve below to go live without opening Google Ads.'}
          </p>
          <p style={{ fontSize: 12.5, color: 'var(--text-4)', margin: '0 0 16px' }}>
            Landing page: <a href={biz.finalUrl} target="_blank" rel="noreferrer" style={{ color: 'var(--brand)' }}>{biz.finalUrl}</a>
          </p>
          <div className="flex gap-3 flex-wrap">
            {!live && result.campaign_id && (
              <button
                className="btn btn-primary"
                disabled={campaignActionId === result.campaign_id}
                onClick={() => toggleCampaign(result.campaign_id, true)}
              >
                {campaignActionId === result.campaign_id ? 'Approving…' : 'Approve & go live here'}
              </button>
            )}
            {live && (
              <button
                className="btn btn-secondary"
                disabled={campaignActionId === result.campaign_id}
                onClick={() => toggleCampaign(result.campaign_id, false)}
              >
                Pause campaign
              </button>
            )}
            <button onClick={() => { setResult(null); setResultLive(false); setStep(0); setSuggested(false); setSelectedPageId(''); setBiz({ businessName: '', finalUrl: '', category: '', city: '' }) }} className="btn btn-secondary">
              Create another campaign
            </button>
          </div>
          {campaignNote && <p style={{ marginTop: 12, fontSize: 13, color: 'var(--text-3)' }}>{campaignNote}</p>}
        </div>

        {mode === 'live' && (
          <div className="card p-5">
            <div className="flex items-center justify-between gap-3" style={{ marginBottom: 12 }}>
              <div>
                <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-1)', margin: 0 }}>Your campaigns</h2>
                <p style={{ fontSize: 12.5, color: 'var(--text-3)', margin: '4px 0 0' }}>
                  Approve, enable, or pause here — stay in ZeOrbit.
                </p>
              </div>
              <button type="button" className="btn btn-secondary" onClick={loadCampaigns} disabled={campaignsLoading}>
                {campaignsLoading ? 'Loading…' : 'Refresh'}
              </button>
            </div>
            {campaigns.length === 0 ? (
              <p style={{ fontSize: 13, color: 'var(--text-4)', margin: 0 }}>
                {campaignsLoading ? 'Loading campaigns…' : 'No campaigns listed yet. Click Refresh.'}
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {campaigns.slice(0, 12).map(c => (
                  <div key={c.id} style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12,
                    padding: '10px 12px', borderRadius: 8, border: '1px solid var(--border)',
                  }}>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-1)' }} className="truncate">{c.name}</div>
                      <div style={{ fontSize: 11.5, color: 'var(--text-4)', marginTop: 2 }}>
                        #{c.id} · {c.status} · ${Number(c.daily_budget || 0).toFixed(2)}/day
                      </div>
                    </div>
                    <div className="flex gap-2 flex-shrink-0">
                      {c.status !== 'ENABLED' ? (
                        <button
                          type="button"
                          className="btn btn-primary"
                          disabled={campaignActionId === String(c.id)}
                          onClick={() => toggleCampaign(c.id, true)}
                        >
                          {campaignActionId === String(c.id) ? 'Approving…' : 'Approve'}
                        </button>
                      ) : (
                        <button
                          type="button"
                          className="btn btn-secondary"
                          disabled={campaignActionId === String(c.id)}
                          onClick={() => toggleCampaign(c.id, false)}
                        >
                          Pause
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-5 fade-in" style={{ maxWidth: 720 }}>
      <div>
        <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>Google Ads</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text-3)' }}>
          Pick a published SEO page URL, then publish a paused Search campaign that links to it.
        </p>
      </div>

      {mode === 'live' && (
        <div className="alert alert-success">
          <CheckCircle2 size={15} />
          <div>
            <strong>Live Google Ads API — automated.</strong>{' '}
            Publishing an SEO page auto-creates a Search campaign
            {adsAccount.auto_enable ? ' and enables it from ZeOrbit (can spend).' : ' — approve it here to go live.'}
            {llmProvider ? ` Free AI copy via ${llmProvider}.` : ''}
            <div style={{ marginTop: 8, fontSize: 12.5, lineHeight: 1.5 }}>
              Connected Ads account: <strong>{adsAccount.customer_id || '—'}</strong>
              {adsAccount.login_customer_id ? <> (manager <strong>{adsAccount.login_customer_id}</strong>)</> : null}
              . Use <strong>Approve</strong> below to go live from this tool, or{' '}
              <a href={adsAccount.campaigns_url || 'https://ads.google.com/aw/campaigns'} target="_blank" rel="noreferrer"
                style={{ color: 'inherit', fontWeight: 700, textDecoration: 'underline' }}>
                open the Google Ads dashboard
              </a>
              {adsAccount.open_hint ? <> — {adsAccount.open_hint}</> : null}
            </div>
          </div>
        </div>
      )}
      {mode === 'ai' && (
        <div className="alert alert-success">
          <CheckCircle2 size={15} />
          <div><strong>Free AI ad copy{llmProvider ? ` (${llmProvider})` : ''}.</strong> Connect Ads credentials to create paused live campaigns.</div>
        </div>
      )}
      {mode === 'demo' && (
        <div className="alert alert-warning">
          <AlertTriangle size={15} />
          <div><strong>Demo simulation.</strong> Set Ads credentials for live paused campaigns, or a free Groq/Gemini key for AI copy.</div>
        </div>
      )}
      {mode === 'setup' && (
        <div className="alert alert-warning">
          <AlertTriangle size={15} style={{ flexShrink: 0, marginTop: 1 }} />
          <div>
            <strong>Google Ads not live.</strong>{' '}
            {statusDetail || 'Connect Ads credentials. API is free; campaigns are created paused.'}
            {' '}<Link to="/integrations" style={{ color: 'inherit', fontWeight: 700 }}>See Integrations</Link>
          </div>
        </div>
      )}
      {error && <div className="alert alert-error">⚠ {error}</div>}
      {campaignNote && mode === 'live' && !result && (
        <div className="alert alert-success"><CheckCircle2 size={15} /> {campaignNote}</div>
      )}

      {mode === 'live' && (
        <div className="card p-5">
          <div className="flex items-center justify-between gap-3" style={{ marginBottom: 12 }}>
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-1)', margin: 0 }}>Your campaigns</h2>
              <p style={{ fontSize: 12.5, color: 'var(--text-3)', margin: '4px 0 0' }}>
                Enable or pause here — no Google Ads “approve” click needed for pause/unpause.
              </p>
            </div>
            <button type="button" className="btn btn-secondary" onClick={loadCampaigns} disabled={campaignsLoading}>
              {campaignsLoading ? 'Loading…' : 'Refresh'}
            </button>
          </div>
          {campaigns.length === 0 ? (
            <p style={{ fontSize: 13, color: 'var(--text-4)', margin: 0 }}>No campaigns yet. Create one below.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {campaigns.slice(0, 12).map(c => (
                <div key={c.id} style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12,
                  padding: '10px 12px', borderRadius: 8, border: '1px solid var(--border)',
                }}>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-1)' }} className="truncate">{c.name}</div>
                    <div style={{ fontSize: 11.5, color: 'var(--text-4)', marginTop: 2 }}>
                      #{c.id} · {c.status} · ${Number(c.daily_budget || 0).toFixed(2)}/day
                    </div>
                  </div>
                  <div className="flex gap-2 flex-shrink-0">
                    {c.status !== 'ENABLED' ? (
                      <button
                        type="button"
                        className="btn btn-primary"
                        style={{ padding: '6px 10px', fontSize: 12 }}
                        disabled={campaignActionId === c.id}
                        onClick={() => toggleCampaign(c.id, true)}
                      >
                        {campaignActionId === c.id ? '…' : 'Enable'}
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="btn btn-secondary"
                        style={{ padding: '6px 10px', fontSize: 12 }}
                        disabled={campaignActionId === c.id}
                        onClick={() => toggleCampaign(c.id, false)}
                      >
                        {campaignActionId === c.id ? '…' : 'Pause'}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
          <p style={{ fontSize: 11.5, color: 'var(--text-4)', margin: '12px 0 0' }}>
            Note: Google’s own “Under review” policy check still happens automatically after enable — no tool can skip that.
          </p>
        </div>
      )}

      <div className="card p-6">
        <StepDots step={step} />
        <div className="section-label" style={{ marginBottom: 4 }}>Step {step + 1} of {STEPS.length}</div>
        <h2 style={{ fontSize: 19, fontWeight: 700, color: 'var(--text-1)', margin: '0 0 20px' }}>{STEPS[step]}</h2>

        {step === 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
                <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-2)', display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Globe size={14} /> SEO landing page
                </label>
                <Link to="/content" style={{ fontSize: 12, color: 'var(--brand)' }}>Generate & publish pages →</Link>
              </div>

              {landingLoading ? (
                <p style={{ fontSize: 13, color: 'var(--text-4)' }}>Loading published pages…</p>
              ) : landingError ? (
                <p style={{ fontSize: 13, color: 'var(--red, #d92d20)' }}>{landingError}</p>
              ) : landingPages.length === 0 ? (
                <div className="alert alert-info" style={{ margin: 0 }}>
                  <FileText size={14} />
                  <div>
                    No published SEO pages yet. Go to <Link to="/content" style={{ fontWeight: 700, color: 'inherit' }}>SEO Content</Link>,
                    generate pages, click <strong>Publish All to ZeOrbit</strong>, then return here.
                  </div>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 240, overflowY: 'auto' }}>
                  {landingPages.map(page => {
                    const active = selectedPageId === page.id || biz.finalUrl === page.public_url
                    return (
                      <button
                        key={page.id}
                        type="button"
                        onClick={() => selectLandingPage(page)}
                        style={{
                          textAlign: 'left', padding: '10px 12px', borderRadius: 10, cursor: 'pointer',
                          border: active ? '1px solid var(--brand)' : '1px solid var(--border)',
                          background: active ? 'color-mix(in srgb, var(--brand) 12%, transparent)' : 'var(--bg-raised)',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8, alignItems: 'flex-start' }}>
                          <div style={{ minWidth: 0 }}>
                            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-1)' }} className="truncate">{page.title}</div>
                            <div style={{ fontSize: 11.5, color: 'var(--text-4)', marginTop: 2 }} className="truncate">{page.public_url}</div>
                            <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 4 }}>
                              {page.business_type || page.source}
                              {page.city ? ` · ${page.city}${page.state ? `, ${page.state}` : ''}` : ''}
                            </div>
                          </div>
                          <span style={{
                            fontSize: 10, fontWeight: 700, flexShrink: 0, padding: '2px 6px', borderRadius: 999,
                            color: page.ads_ready ? 'var(--green)' : 'var(--amber, #f59e0b)',
                            border: `1px solid ${page.ads_ready ? 'var(--green)' : 'var(--amber, #f59e0b)'}`,
                          }}>
                            {page.ads_ready ? 'Ads ready' : 'Local URL'}
                          </span>
                        </div>
                      </button>
                    )
                  })}
                </div>
              )}

              {landingMeta.ads_ready_count === 0 && landingPages.length > 0 && (
                <div className="alert alert-warning" style={{ marginTop: 10, marginBottom: 0 }}>
                  <AlertTriangle size={14} />
                  <div>
                    These pages use a local host ({landingMeta.public_base_url || 'localhost'}). Google Ads needs a public domain.
                    Set <code>PUBLIC_BASE_URL</code> in backend <code>.env</code> to your live SEO host, republish, then refresh this list.
                  </div>
                </div>
              )}
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>
                Final URL (ads link here)
              </label>
              <input type="text" value={biz.finalUrl} onChange={e => { setBiz(b => ({ ...b, finalUrl: e.target.value })); setSelectedPageId('') }}
                placeholder="https://yoursite.com/p/web-design-san-diego" style={{ width: '100%', padding: '10px 12px' }} />
              {biz.finalUrl.trim() && !urlHasTld && (
                <div style={{ fontSize: 12, color: 'var(--red, #d92d20)', marginTop: 6 }}>
                  Enter a real public domain (e.g. https://example.com/p/slug) — Google Ads can't target localhost or IPs.
                </div>
              )}
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Business name</label>
              <input type="text" value={biz.businessName} onChange={e => setBiz(b => ({ ...b, businessName: e.target.value }))}
                placeholder="ZeOrbit" style={{ width: '100%', padding: '10px 12px' }} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>What do you do?</label>
                <input type="text" value={biz.category} onChange={e => setBiz(b => ({ ...b, category: e.target.value }))}
                  placeholder="Website design" style={{ width: '100%', padding: '10px 12px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>City <span style={{ color: 'var(--text-4)', fontWeight: 400 }}>(optional)</span></label>
                <input type="text" value={biz.city} onChange={e => setBiz(b => ({ ...b, city: e.target.value }))}
                  placeholder="San Diego" style={{ width: '100%', padding: '10px 12px' }} />
              </div>
            </div>
          </div>
        )}

        {step === 1 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div className="alert alert-info" style={{ margin: 0 }}>
              <Sparkles size={14} style={{ flexShrink: 0, marginTop: 1 }} />
              <span>{suggesting ? 'Generating free AI ad copy…' : 'Ad copy from free AI / SEO keywords — edit anything before continuing.'}</span>
            </div>
            <ListField label="Headlines" hint="3-15, max 30 characters each" values={headlines} setValues={setHeadlines}
              min={3} max={15} maxLength={30} placeholder="Best Plumber in Austin" />
            <ListField label="Descriptions" hint="2-4, max 90 characters each" values={descriptions} setValues={setDescriptions}
              min={2} max={4} maxLength={90} placeholder="Licensed, insured, and available 24/7." />
            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Keywords</label>
              <textarea value={keywords} onChange={e => setKeywords(e.target.value)} rows={4}
                style={{ width: '100%', padding: '10px 12px', fontFamily: 'inherit', resize: 'vertical' }} />
              <p style={{ fontSize: 11.5, color: 'var(--text-4)', margin: '4px 0 0' }}>One per line. Added as broad match. Prefills from the SEO page when available.</p>
            </div>
          </div>
        )}

        {step === 2 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Daily budget (USD)</label>
              <input type="number" min="1" step="0.5" value={dailyBudget} onChange={e => setDailyBudget(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', maxWidth: 200 }} />
              <p style={{ fontSize: 11.5, color: 'var(--text-4)', margin: '4px 0 0' }}>
                {goLiveOnCreate
                  ? 'Campaign will be created ENABLED and can start spending after Google review.'
                  : 'Campaign is created paused ($0). Enable it later from Your campaigns above.'}
              </p>
            </div>
            <label style={{ display: 'flex', alignItems: 'flex-start', gap: 10, cursor: 'pointer' }}>
              <input type="checkbox" checked={goLiveOnCreate} onChange={e => setGoLiveOnCreate(e.target.checked)} style={{ marginTop: 3 }} />
              <span style={{ fontSize: 13, color: 'var(--text-2)', lineHeight: 1.45 }}>
                <strong>Approve & go live here</strong> (default on). No need to open Google Ads to unpause. Google’s automatic “Under review” can still take a short time.
              </span>
            </label>
            <div style={{ border: '1px solid var(--border)', borderRadius: 10, padding: 16 }}>
              <div className="section-label" style={{ marginBottom: 10 }}>Review</div>
              <div style={{ fontSize: 13.5, color: 'var(--text-2)', display: 'flex', flexDirection: 'column', gap: 6 }}>
                <div><strong>{biz.businessName || 'Your Business'}</strong> · {biz.category || '—'}{biz.city ? ` · ${biz.city}` : ''}</div>
                <div>{headlines.filter(Boolean).length} headlines · {descriptions.filter(Boolean).length} descriptions · {keywords.split(/[\n,]/).filter(k => k.trim()).length} keywords</div>
                <div style={{ color: 'var(--text-4)', wordBreak: 'break-all' }}>Links to {biz.finalUrl || '—'}</div>
              </div>
            </div>
          </div>
        )}

        <div className="flex items-center justify-between" style={{ marginTop: 28 }}>
          {step > 0 ? (
            <button onClick={() => setStep(s => s - 1)} className="btn btn-ghost"><ArrowLeft size={15} /> Back</button>
          ) : <span />}
          {step < 2 ? (
            <button
              onClick={() => step === 0 ? goToAdsStep() : setStep(2)}
              disabled={step === 0 ? (!bizValid || suggesting) : !adsValid}
              className="btn btn-primary"
            >
              {step === 0 && suggesting ? 'Drafting ads…' : <>Continue <ArrowRight size={15} /></>}
            </button>
          ) : (
            <button onClick={handleCreate} disabled={loading || !dailyBudget || Number(dailyBudget) <= 0} className="btn btn-primary">
              <Megaphone size={15} /> {loading ? 'Creating campaign…' : 'Publish to Google Ads'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
