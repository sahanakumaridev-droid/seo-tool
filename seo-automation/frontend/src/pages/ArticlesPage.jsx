import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, MapPin, Globe, Eye, CheckCircle, X, Search, Link2, FileText, Image as ImageIcon,
         Upload, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import { analyzeWebsite, generateArticles, publishToWordPress, publishBulkToWordPress, publishToWeb, zeorbitBlogUrl } from '../api'

const SEO_PLUGINS = [
  { value: 'rankmath', label: 'RankMath' },
  { value: 'aioseo', label: 'All in One SEO' },
  { value: 'yoast', label: 'Yoast SEO' },
]

function WordPressPanel({ wpConfig, setWpConfig }) {
  const [open, setOpen] = useState(false)
  const connected = !!wpConfig.wp_url
  const inp = "w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50"
  const lbl = "block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5"
  return (
    <div className="card border-violet-500/20">
      <button onClick={() => setOpen(o => !o)} className="w-full flex items-center justify-between px-5 py-4">
        <div className="flex items-center gap-2">
          <Globe size={15} className="text-violet-400" />
          <span className="text-sm font-semibold text-white">WordPress Auto-Publish</span>
          {connected && <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">Configured</span>}
        </div>
        {open ? <ChevronUp size={14} className="text-slate-500" /> : <ChevronDown size={14} className="text-slate-500" />}
      </button>
      {open && (
        <div className="px-5 pb-5 space-y-3 border-t border-white/5 pt-4">
          <p className="text-xs text-slate-500">
            Use an <a href="https://wordpress.org/documentation/article/application-passwords/" target="_blank" rel="noreferrer" className="text-indigo-400 underline">Application Password</a> (not your login password). Posts publish live with their featured image.
          </p>
          <div className="grid grid-cols-2 gap-3">
            <div><label className={lbl}>WordPress URL</label>
              <input type="url" value={wpConfig.wp_url} onChange={e => setWpConfig(c => ({ ...c, wp_url: e.target.value }))} placeholder="https://yoursite.com" className={inp} /></div>
            <div><label className={lbl}>Username</label>
              <input type="text" value={wpConfig.wp_username} onChange={e => setWpConfig(c => ({ ...c, wp_username: e.target.value }))} placeholder="your_wp_username" className={inp} /></div>
            <div><label className={lbl}>Application Password</label>
              <input type="password" value={wpConfig.wp_app_password} onChange={e => setWpConfig(c => ({ ...c, wp_app_password: e.target.value }))} placeholder="Connected on server — leave blank" className={inp} /></div>
            <div><label className={lbl}>SEO Plugin</label>
              <select value={wpConfig.seo_plugin} onChange={e => setWpConfig(c => ({ ...c, seo_plugin: e.target.value }))} className={inp}>
                {SEO_PLUGINS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select></div>
          </div>
          <div className="flex items-center gap-3">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Publish Status</label>
            <div className="flex gap-2">
              {['draft', 'publish'].map(s => (
                <button key={s} type="button" onClick={() => setWpConfig(c => ({ ...c, status: s }))}
                  className={`px-3 py-1 rounded-md text-xs font-medium capitalize transition-colors ${wpConfig.status === s ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-600/30' : 'bg-white/4 text-slate-400 border border-white/6 hover:border-white/15'}`}>{s}</button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Website Profile Card ───────────────────────────────────────
function ProfileCard({ profile }) {
  if (!profile) return null
  return (
    <div className="card p-5 border-emerald-500/20">
      <div className="flex items-center gap-2 mb-3">
        <Globe size={15} className="text-emerald-400" />
        <span className="text-sm font-semibold text-white">Website Analysis</span>
        {profile.analyzed
          ? <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">Analyzed</span>
          : <span className="text-xs px-2 py-0.5 rounded-full bg-amber-400/10 text-amber-400 border border-amber-400/20">Limited (site unreachable / no AI key)</span>}
      </div>
      {profile.business_name && <div className="text-sm text-slate-200 font-semibold mb-1">{profile.business_name}</div>}
      {profile.summary && <p className="text-xs text-slate-400 mb-3 leading-relaxed">{profile.summary}</p>}
      <div className="grid sm:grid-cols-2 gap-3">
        <ChipGroup label="Services" items={profile.services} color="indigo" />
        <ChipGroup label="Products" items={profile.products} color="violet" />
        <ChipGroup label="Blog Topics" items={profile.existing_blog_topics} color="sky" />
        <div>
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Brand Tone / Audience</div>
          <p className="text-xs text-slate-400">{profile.brand_tone || '—'}</p>
          <p className="text-xs text-slate-500 mt-1">{profile.target_audience}</p>
        </div>
      </div>
      <div className="flex items-center gap-2 mt-3 text-xs text-slate-500">
        <Link2 size={12} className="text-slate-500" />
        {profile.page_inventory?.length || 0} pages found for internal linking
      </div>
    </div>
  )
}

function ChipGroup({ label, items, color }) {
  const colors = {
    indigo: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/25',
    violet: 'bg-violet-500/15 text-violet-300 border-violet-500/25',
    sky: 'bg-sky-500/15 text-sky-300 border-sky-500/25',
  }
  if (!items?.length) return (
    <div>
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{label}</div>
      <p className="text-xs text-slate-600">—</p>
    </div>
  )
  return (
    <div>
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{label}</div>
      <div className="flex flex-wrap gap-1.5">
        {items.slice(0, 8).map((it, i) => (
          <span key={i} className={`text-xs px-2 py-0.5 rounded-lg border ${colors[color]}`}>{it}</span>
        ))}
      </div>
    </div>
  )
}

// ── Main Page ──────────────────────────────────────────────────
export default function ArticlesPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    primary_keyword: '',
    location: 'Austin, TX',
    website_url: '',
    num_cities: 5,
    num_articles: 1,
    industry: '',
  })
  const [analyzing, setAnalyzing] = useState(false)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [articles, setArticles] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('seo_articles') || '[]') } catch { return [] }
  })
  useEffect(() => { sessionStorage.setItem('seo_articles', JSON.stringify(articles)) }, [articles])
  const [toast, setToast] = useState(null)
  const resultsRef = useRef(null)
  const [wpConfig, setWpConfig] = useState({ wp_url: 'https://zeorbit.com', wp_username: 'zeor@admnir', wp_app_password: '', seo_plugin: 'aioseo', status: 'publish' })
  const [publishResults, setPublishResults] = useState({})
  const [publishingAll, setPublishingAll] = useState(false)
  const [webResults, setWebResults] = useState({})

  const handlePublishWebOne = async (block, i) => {
    setWebResults(r => ({ ...r, [i]: 'loading' }))
    try {
      const res = await publishToWeb(block)
      setWebResults(r => ({ ...r, [i]: { url: res.data.public_url } }))
      window.open(res.data.public_url, '_blank', 'noopener')
      window.open(zeorbitBlogUrl(), '_blank', 'noopener')
    } catch (e) {
      setWebResults(r => ({ ...r, [i]: { error: e.response?.data?.detail || 'Failed' } }))
    }
  }

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 4000)
  }
  const update = (patch) => setForm(f => ({ ...f, ...patch }))

  const handleAnalyze = async () => {
    if (!form.website_url) { setError('Enter a website URL to analyze.'); return }
    setAnalyzing(true); setError('')
    try {
      const res = await analyzeWebsite(form.website_url)
      setProfile(res.data)
      showToast(res.data.analyzed ? 'Website analyzed' : 'Analyzed with limited data')
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Is the backend running?')
    } finally { setAnalyzing(false) }
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    if (!form.primary_keyword || !form.website_url) {
      setError('Primary keyword and website URL are required.')
      return
    }
    setLoading(true); setError('')
    try {
      const res = await generateArticles({ ...form, num_cities: Number(form.num_cities), num_articles: Number(form.num_articles) })
      setArticles(res.data.pages)
      // Backend analyzes the site during generation; surface it if we didn't already.
      showToast(`${res.data.pages.length} articles generated!`)
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100)
    } catch (err) {
      setError(err.response?.data?.detail || 'Generation failed. Configure a free LLM key (GROQ/GEMINI) or check backend logs.')
    } finally { setLoading(false) }
  }

  const handlePublishOne = async (block, i) => {
    if (!wpConfig.wp_url) { setError('Configure WordPress first (panel below).'); return }
    setPublishResults(r => ({ ...r, [i]: 'loading' }))
    try {
      const res = await publishToWordPress(block, wpConfig)
      setPublishResults(r => ({ ...r, [i]: res.data }))
    } catch (e) {
      setPublishResults(r => ({ ...r, [i]: { success: false, error: e.response?.data?.detail || e.message } }))
    }
  }

  const handlePublishAll = async () => {
    if (!wpConfig.wp_url || !articles.length) { setError('Configure WordPress first (panel below).'); return }
    setPublishingAll(true); setError('')
    try {
      const res = await publishBulkToWordPress(articles, wpConfig)
      const map = {}
      res.data.forEach((r, i) => { map[i] = r })
      setPublishResults(map)
      showToast('Published to WordPress — click a link to open the live post')
    } catch (e) {
      setError(e.response?.data?.detail || 'WordPress publish failed.')
    } finally { setPublishingAll(false) }
  }

  return (
    <div className="space-y-5 fade-in">
      {toast && (
        <div className={`fixed top-5 right-5 z-50 flex items-center gap-3 px-5 py-3 rounded-xl shadow-2xl text-sm font-semibold
          ${toast.type === 'success' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'}`}>
          <CheckCircle size={16} />{toast.msg}
          <button onClick={() => setToast(null)} className="ml-2 opacity-70 hover:opacity-100"><X size={14} /></button>
        </div>
      )}

      <div>
        <h1 className="text-xl font-bold text-white">AI Article Generation</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Generate multiple unique articles from a keyword — grounded in your website, with internal links & AEO optimization
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        {/* Setup form */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Zap size={14} className="text-indigo-400" /> Article Setup
          </h3>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Primary Keyword</label>
              <input type="text" value={form.primary_keyword}
                onChange={e => update({ primary_keyword: e.target.value })}
                placeholder="e.g. commercial roofing"
                className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                <MapPin size={10} className="inline mr-1" />Location
              </label>
              <input type="text" value={form.location}
                onChange={e => update({ location: e.target.value })}
                placeholder="e.g. Austin, TX"
                className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                <Globe size={10} className="inline mr-1" />Website URL
              </label>
              <div className="flex gap-2">
                <input type="url" value={form.website_url}
                  onChange={e => update({ website_url: e.target.value })}
                  placeholder="https://yourbusiness.com"
                  className="flex-1 bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
                <button type="button" onClick={handleAnalyze} disabled={analyzing}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-emerald-600/20 border border-emerald-600/30 text-emerald-300 hover:bg-emerald-600/30 transition-colors text-xs font-medium disabled:opacity-50">
                  <Search size={12} className={analyzing ? 'animate-pulse' : ''} />
                  {analyzing ? '...' : 'Analyze'}
                </button>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Nearby US Cities</label>
                <span className="text-sm font-bold text-indigo-400">{form.num_cities}</span>
              </div>
              <input type="range" min="1" max="25" value={form.num_cities}
                onChange={e => update({ num_cities: Number(e.target.value) })}
                className="w-full accent-indigo-500" />
              <p className="text-[10px] text-slate-600 mt-1">One localized post per city (target + nearest {form.num_cities - 1} cities)</p>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-white/3 border border-white/6">
              <div className="text-xs font-semibold text-slate-300">🤖 AI Model</div>
              <select value={form.llm_provider || ''} onChange={e => update({ llm_provider: e.target.value || null })}
                className="bg-white/5 border border-white/10 rounded-lg px-2 py-1 text-xs text-slate-200 focus:outline-none">
                <option value="">Auto</option>
                <option value="openai">GPT-4</option>
                <option value="gemini">Gemini</option>
                <option value="groq">Groq</option>
              </select>
            </div>
            {error && <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-xs">{error}</div>}
            <button type="submit" disabled={loading}
              className="btn-primary w-full py-2.5 rounded-lg text-white text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-60">
              {loading
                ? <><svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.2)" strokeWidth="3"/><path d="M12 2a10 10 0 0 1 10 10" stroke="white" strokeWidth="3" strokeLinecap="round"/></svg>Generating {form.num_articles} articles...</>
                : <><FileText size={14} /> Generate Articles</>}
            </button>
          </form>
        </div>

        {/* Profile / info */}
        <div className="lg:col-span-2 space-y-4">
          {profile ? <ProfileCard profile={profile} /> : (
            <div className="card p-6 flex flex-col items-center justify-center text-center h-full">
              <Globe size={28} className="text-slate-600 mb-3" />
              <p className="text-sm text-slate-400 font-medium">Analyze a website first</p>
              <p className="text-xs text-slate-600 mt-1 max-w-sm">
                We read the site's services, products, tone, and pages so generated articles match the business
                and link internally. (Analysis also runs automatically when you generate.)
              </p>
            </div>
          )}
        </div>
      </div>

      {/* WordPress publishing */}
      {articles.length > 0 && <WordPressPanel wpConfig={wpConfig} setWpConfig={setWpConfig} />}

      {/* Results */}
      {articles.length > 0 && (
        <div className="card" ref={resultsRef}>
          <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
            <div className="flex items-center gap-3">
              <h3 className="text-sm font-semibold text-white">{articles.length} Articles Generated</h3>
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">Complete</span>
            </div>
            {wpConfig.wp_url && (
              <button onClick={handlePublishAll} disabled={publishingAll}
                className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-violet-600/20 border border-violet-600/30 text-violet-300 text-sm font-medium hover:bg-violet-600/30 transition-colors disabled:opacity-50">
                <Upload size={14} className={publishingAll ? 'animate-pulse' : ''} /> {publishingAll ? 'Publishing...' : 'Publish All to WordPress'}
              </button>
            )}
          </div>
          <table className="data-table">
            <thead>
              <tr><th>#</th><th>Title / City</th><th>Score</th><th>Links</th><th>Images</th><th>WordPress</th></tr>
            </thead>
            <tbody>
              {articles.map((block, i) => {
                const score = Math.round(block.readability_score || 75)
                const links = (block.content?.match(/<a /g) || []).length
                const imgs = block.in_content_images?.length || 0
                const featured = block.in_content_images?.find(im => im.is_featured)?.url || block.featured_image_url
                const pr = publishResults[i]
                return (
                  <tr key={`${block.slug}-${i}`}>
                    <td className="text-slate-600 text-xs">{i + 1}</td>
                    <td className="max-w-[300px]">
                      <div className="flex items-center gap-2">
                        {featured && <img src={featured} alt="" className="w-9 h-9 rounded object-cover flex-shrink-0 border border-white/10" />}
                        <div className="min-w-0">
                          <div className="text-slate-200 text-xs font-medium truncate">{block.title}</div>
                          <div className="text-slate-500 text-xs truncate mt-0.5">
                            <MapPin size={9} className="inline mr-0.5" />{block.city}{block.state ? `, ${block.state}` : ''}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="w-14 h-1.5 rounded-full bg-white/8 overflow-hidden">
                          <div className="h-full rounded-full" style={{ width: `${score}%`, background: score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444' }} />
                        </div>
                        <span className={`text-xs font-bold ${score >= 75 ? 'text-emerald-400' : score >= 50 ? 'text-amber-400' : 'text-red-400'}`}>{score}</span>
                      </div>
                    </td>
                    <td className="text-xs text-slate-400"><span className="inline-flex items-center gap-1"><Link2 size={11} />{links}</span></td>
                    <td className="text-xs text-slate-400"><span className="inline-flex items-center gap-1"><ImageIcon size={11} />{imgs}</span></td>
                    <td>
                      <div className="flex items-center gap-1.5">
                        <button onClick={() => navigate('/page-preview', { state: { block, index: i, businessType: block.business_type, wpConfig } })}
                          className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs transition-colors"
                          style={{ background: 'var(--brand-soft)', border: '1px solid rgba(59,130,246,0.3)', color: 'var(--brand)' }}>
                          <Eye size={11} /> View
                        </button>
                        {webResults[i]?.url ? (
                          <a href={webResults[i].url} target="_blank" rel="noreferrer"
                            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs bg-emerald-500/15 border border-emerald-500/25 text-emerald-400 hover:bg-emerald-500/25 transition-colors">
                            <Globe size={11} /> Live
                          </a>
                        ) : (
                          <button onClick={() => handlePublishWebOne(block, i)} disabled={webResults[i] === 'loading'}
                            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs btn-primary disabled:opacity-50"
                            title={webResults[i]?.error || 'Publish to ZeOrbit — live page + blog'}>
                            <Globe size={11} /> {webResults[i] === 'loading' ? '...' : webResults[i]?.error ? 'Retry' : 'Publish to ZeOrbit'}
                          </button>
                        )}
                        {wpConfig.wp_url && pr?.success && pr?.post_url ? (
                          <a href={pr.post_url} target="_blank" rel="noreferrer"
                            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs bg-emerald-500/15 border border-emerald-500/25 text-emerald-400 hover:bg-emerald-500/25 transition-colors">
                            <ExternalLink size={11} /> Open Live
                          </a>
                        ) : wpConfig.wp_url && (
                          <button onClick={() => handlePublishOne(block, i)} disabled={pr === 'loading'}
                            className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs transition-colors ${pr?.error ? 'bg-red-500/15 border border-red-500/25 text-red-400' : 'bg-white/5 border border-white/8 text-slate-400 hover:bg-white/8'} disabled:opacity-50`}
                            title={pr?.error || 'Publish to WordPress'}>
                            <Upload size={11} /> {pr === 'loading' ? '...' : pr?.error ? 'Retry' : 'Publish'}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
