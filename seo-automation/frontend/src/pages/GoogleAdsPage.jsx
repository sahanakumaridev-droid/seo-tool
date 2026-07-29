import { useState, useEffect } from 'react'
import { Plus, X, Megaphone, CheckCircle2, ExternalLink, AlertTriangle, ArrowLeft, ArrowRight, Sparkles } from 'lucide-react'
import { getGoogleAdsStatus, createGoogleAdsCampaign } from '../api'

const STEPS = ['Business information', 'Create your ads', 'Set your budget']

// Google Ads hard-caps headlines at 30 chars and descriptions at 90 — every
// generated string is sliced to fit so a suggestion can never fail campaign
// creation even with a long business name/category.
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

export default function GoogleAdsPage() {
  const [configured, setConfigured] = useState(null)
  const [step, setStep] = useState(0)

  // Step 1 — business info
  const [biz, setBiz] = useState({ businessName: '', finalUrl: '', category: '', city: '' })

  // Step 2 — ads (auto-suggested from biz info, editable)
  const [headlines, setHeadlines] = useState(['', '', ''])
  const [descriptions, setDescriptions] = useState(['', ''])
  const [keywords, setKeywords] = useState('')
  const [suggested, setSuggested] = useState(false)

  // Step 3 — budget
  const [dailyBudget, setDailyBudget] = useState('25')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getGoogleAdsStatus().then(r => setConfigured(r.data.configured)).catch(() => setConfigured(false))
  }, [])

  const goToAdsStep = () => {
    if (!suggested) {
      const s = suggestAdCopy(biz)
      setHeadlines(s.headlines)
      setDescriptions(s.descriptions)
      setKeywords(s.keywords.join('\n'))
      setSuggested(true)
    }
    setStep(1)
  }

  const urlHasTld = /^[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$/i.test(
    biz.finalUrl.trim().replace(/^[a-z]+:\/\//i, '').split('/')[0]
  )
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
      })
      if (res.data.success) setResult(res.data)
      else setError(res.data.error || 'Campaign creation failed.')
    } catch {
      setError('Could not reach the server. Please try again.')
    }
    setLoading(false)
  }

  if (result) {
    return (
      <div className="space-y-5 fade-in" style={{ maxWidth: 640 }}>
        <div className="card p-6" style={{ borderColor: 'var(--green)' }}>
          <div className="flex items-center gap-2" style={{ marginBottom: 8 }}>
            <CheckCircle2 size={20} style={{ color: 'var(--green)' }} />
            <h3 style={{ fontSize: 17, fontWeight: 700, color: 'var(--text-1)' }}>Campaign created (paused)</h3>
          </div>
          <p style={{ fontSize: 13.5, color: 'var(--text-3)', margin: '0 0 16px' }}>
            Campaign ID: <span style={{ fontFamily: 'monospace' }}>{result.campaign_id}</span> — review it in Google Ads and unpause when you're ready to go live.
          </p>
          <div className="flex gap-3">
            {result.manage_url && (
              <a href={result.manage_url} target="_blank" rel="noreferrer" className="btn btn-primary">
                Manage in Google Ads <ExternalLink size={13} />
              </a>
            )}
            <button onClick={() => { setResult(null); setStep(0); setSuggested(false); setBiz({ businessName: '', finalUrl: '', category: '', city: '' }) }} className="btn btn-secondary">
              Create another campaign
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-5 fade-in" style={{ maxWidth: 640 }}>
      <div>
        <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>Google Ads</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text-3)' }}>Create your first campaign in a few simple steps.</p>
      </div>

      {configured === false && (
        <div className="alert alert-warning">
          <AlertTriangle size={15} style={{ flexShrink: 0, marginTop: 1 }} />
          <div>
            <strong>Google Ads isn't connected yet.</strong> A free <strong>Test account</strong> developer token works instantly (no review wait) for trying this end-to-end — upgrade to Basic/Standard access later to run it against a real account. Set the <code>GOOGLE_ADS_*</code> variables in the backend <code>.env</code> and restart the server. Campaigns are always created <strong>paused</strong>.
          </div>
        </div>
      )}
      {error && <div className="alert alert-error">⚠ {error}</div>}

      <div className="card p-6">
        <StepDots step={step} />
        <div className="section-label" style={{ marginBottom: 4 }}>Step {step + 1} of {STEPS.length}</div>
        <h2 style={{ fontSize: 19, fontWeight: 700, color: 'var(--text-1)', margin: '0 0 20px' }}>{STEPS[step]}</h2>

        {step === 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Business name</label>
              <input type="text" value={biz.businessName} onChange={e => setBiz(b => ({ ...b, businessName: e.target.value }))}
                placeholder="Acme Plumbing Co." style={{ width: '100%', padding: '10px 12px' }} />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Website (where ads should link to)</label>
              <input type="text" value={biz.finalUrl} onChange={e => setBiz(b => ({ ...b, finalUrl: e.target.value }))}
                placeholder="https://example.com" style={{ width: '100%', padding: '10px 12px' }} />
              {biz.finalUrl.trim() && !urlHasTld && (
                <div style={{ fontSize: 12, color: 'var(--red, #d92d20)', marginTop: 6 }}>
                  Enter a real public domain (e.g. example.com) — Google Ads can't target localhost, IP addresses, or bare names.
                </div>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>What do you do?</label>
                <input type="text" value={biz.category} onChange={e => setBiz(b => ({ ...b, category: e.target.value }))}
                  placeholder="Plumbing services" style={{ width: '100%', padding: '10px 12px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>City <span style={{ color: 'var(--text-4)', fontWeight: 400 }}>(optional)</span></label>
                <input type="text" value={biz.city} onChange={e => setBiz(b => ({ ...b, city: e.target.value }))}
                  placeholder="Austin" style={{ width: '100%', padding: '10px 12px' }} />
              </div>
            </div>
          </div>
        )}

        {step === 1 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div className="alert alert-info" style={{ margin: 0 }}>
              <Sparkles size={14} style={{ flexShrink: 0, marginTop: 1 }} />
              <span>Ad copy suggested from your business info — edit anything before continuing.</span>
            </div>
            <ListField label="Headlines" hint="3-15, max 30 characters each" values={headlines} setValues={setHeadlines}
              min={3} max={15} maxLength={30} placeholder="Best Plumber in Austin" />
            <ListField label="Descriptions" hint="2-4, max 90 characters each" values={descriptions} setValues={setDescriptions}
              min={2} max={4} maxLength={90} placeholder="Licensed, insured, and available 24/7." />
            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Keywords</label>
              <textarea value={keywords} onChange={e => setKeywords(e.target.value)} rows={4}
                style={{ width: '100%', padding: '10px 12px', fontFamily: 'inherit', resize: 'vertical' }} />
              <p style={{ fontSize: 11.5, color: 'var(--text-4)', margin: '4px 0 0' }}>One per line. Added as broad match.</p>
            </div>
          </div>
        )}

        {step === 2 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6 }}>Daily budget (USD)</label>
              <input type="number" min="1" step="0.5" value={dailyBudget} onChange={e => setDailyBudget(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', maxWidth: 200 }} />
              <p style={{ fontSize: 11.5, color: 'var(--text-4)', margin: '4px 0 0' }}>You can change this any time in Google Ads. Real spend only starts once you unpause the campaign there.</p>
            </div>
            <div style={{ border: '1px solid var(--border)', borderRadius: 10, padding: 16 }}>
              <div className="section-label" style={{ marginBottom: 10 }}>Review</div>
              <div style={{ fontSize: 13.5, color: 'var(--text-2)', display: 'flex', flexDirection: 'column', gap: 6 }}>
                <div><strong>{biz.businessName || 'Your Business'}</strong> · {biz.category || '—'}{biz.city ? ` · ${biz.city}` : ''}</div>
                <div>{headlines.filter(Boolean).length} headlines · {descriptions.filter(Boolean).length} descriptions · {keywords.split(/[\n,]/).filter(k => k.trim()).length} keywords</div>
                <div style={{ color: 'var(--text-4)' }}>Links to {biz.finalUrl || '—'}</div>
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
              disabled={step === 0 ? !bizValid : !adsValid}
              className="btn btn-primary"
            >
              Continue <ArrowRight size={15} />
            </button>
          ) : (
            <button onClick={handleCreate} disabled={loading || !dailyBudget || Number(dailyBudget) <= 0} className="btn btn-primary">
              <Megaphone size={15} /> {loading ? 'Creating campaign…' : 'Create Campaign'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
