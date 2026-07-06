import { useState } from 'react'
import { Globe, Upload, CheckCircle, XCircle, Settings, Info, Calendar, Tag, Image, Zap } from 'lucide-react'
import { publishBulkToWordPress, listPages, startBulkPublishJob } from '../api'

const SEO_PLUGINS = [
  { value: 'rankmath', label: 'RankMath', desc: 'rank_math_title, rank_math_description, rank_math_focus_keyword' },
  { value: 'aioseo', label: 'All in One SEO', desc: '_aioseo_title, _aioseo_description, _aioseo_keywords' },
  { value: 'yoast', label: 'Yoast SEO', desc: '_yoast_wpseo_title, _yoast_wpseo_metadesc, _yoast_wpseo_focuskw' },
]

export default function WordPressPage() {
  const [wpConfig, setWpConfig] = useState({
    wp_url: '', wp_username: '', wp_app_password: '',
    seo_plugin: 'rankmath', status: 'draft',
    category_ids: [], tag_ids: [],
    scheduled_at: '', fetch_image: true,
  })
  const [categoryInput, setCategoryInput] = useState('')
  const [tagInput, setTagInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState([])
  const [error, setError] = useState('')
  const [jobId, setJobId] = useState('')
  const [useAsync, setUseAsync] = useState(false)

  const selectedPlugin = SEO_PLUGINS.find(p => p.value === wpConfig.seo_plugin)

  const buildConfig = () => ({
    ...wpConfig,
    category_ids: categoryInput.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n)),
    tag_ids: tagInput.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n)),
    scheduled_at: wpConfig.scheduled_at || null,
  })

  const handlePublishSaved = async () => {
    if (!wpConfig.wp_url || !wpConfig.wp_username || !wpConfig.wp_app_password) {
      setError('Please fill in all WordPress credentials.')
      return
    }
    setLoading(true)
    setError('')
    setResults([])
    setJobId('')
    try {
      const pagesRes = await listPages(0, 100)
      const blocks = pagesRes.data.map(p => p.seo_block)
      if (!blocks.length) { setError('No saved pages found. Generate and save pages from the Content tab first.'); return }

      const config = buildConfig()

      if (useAsync) {
        // Async job — returns job_id for polling
        const res = await startBulkPublishJob(blocks, config)
        setJobId(res.data.job_id)
        // Save to localStorage for Jobs page
        const existing = JSON.parse(localStorage.getItem('seo_jobs') || '[]')
        localStorage.setItem('seo_jobs', JSON.stringify([res.data.job_id, ...existing]))
      } else {
        const res = await publishBulkToWordPress(blocks, config)
        setResults(res.data)
      }
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally { setLoading(false) }
  }

  const successCount = results.filter(r => r.success).length
  const failCount = results.filter(r => !r.success).length

  return (
    <div className="space-y-6 fade-in">
      <div>
        <h1 className="text-xl font-bold text-white">WordPress Integration</h1>
        <p className="text-sm text-slate-500 mt-0.5">Auto-publish SEO pages with featured images, categories, tags, and scheduling</p>
      </div>

      {/* Config card */}
      <div className="card p-6 space-y-5">
        <div className="flex items-center gap-2 mb-1">
          <Settings size={15} className="text-indigo-400" />
          <span className="text-sm font-semibold text-white">WordPress Credentials</span>
        </div>
        <div className="rounded-lg bg-indigo-500/8 border border-indigo-500/20 p-3 flex gap-2">
          <Info size={13} className="text-indigo-400 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-slate-400">
            Use a WordPress{' '}
            <a href="https://wordpress.org/documentation/article/application-passwords/"
              target="_blank" rel="noreferrer" className="text-indigo-400 underline">Application Password</a>
            {' '}(not your login password). Go to WP Admin → Users → Profile → Application Passwords.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">WordPress Site URL</label>
            <input type="url" value={wpConfig.wp_url}
              onChange={e => setWpConfig(c => ({ ...c, wp_url: e.target.value }))}
              placeholder="https://yoursite.com"
              className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Username</label>
            <input type="text" value={wpConfig.wp_username}
              onChange={e => setWpConfig(c => ({ ...c, wp_username: e.target.value }))}
              placeholder="your_wp_username"
              className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Application Password</label>
            <input type="password" value={wpConfig.wp_app_password}
              onChange={e => setWpConfig(c => ({ ...c, wp_app_password: e.target.value }))}
              placeholder="xxxx xxxx xxxx xxxx xxxx xxxx"
              className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">SEO Plugin</label>
            <select value={wpConfig.seo_plugin}
              onChange={e => setWpConfig(c => ({ ...c, seo_plugin: e.target.value }))}
              className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500/50">
              {SEO_PLUGINS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
            {selectedPlugin && <p className="text-xs text-slate-600 mt-1">Meta fields: {selectedPlugin.desc}</p>}
          </div>
        </div>

        {/* Categories & Tags */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1">
              <Tag size={10} /> Category IDs <span className="text-slate-600 normal-case font-normal">(comma-separated)</span>
            </label>
            <input type="text" value={categoryInput}
              onChange={e => setCategoryInput(e.target.value)}
              placeholder="1, 5, 12"
              className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
            <p className="text-xs text-slate-600 mt-1">Find IDs in WP Admin → Posts → Categories</p>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1">
              <Tag size={10} /> Tag IDs <span className="text-slate-600 normal-case font-normal">(comma-separated)</span>
            </label>
            <input type="text" value={tagInput}
              onChange={e => setTagInput(e.target.value)}
              placeholder="3, 7, 22"
              className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
          </div>
        </div>

        {/* Scheduling */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1">
              <Calendar size={10} /> Schedule Publish <span className="text-slate-600 normal-case font-normal">(optional)</span>
            </label>
            <input type="datetime-local" value={wpConfig.scheduled_at}
              onChange={e => setWpConfig(c => ({ ...c, scheduled_at: e.target.value }))}
              className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500/50" />
            <p className="text-xs text-slate-600 mt-1">Leave empty to publish immediately</p>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Post Status</label>
            <div className="flex gap-2">
              {['draft', 'publish'].map(s => (
                <button key={s} type="button"
                  onClick={() => setWpConfig(c => ({ ...c, status: s }))}
                  className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${wpConfig.status === s ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-600/30' : 'bg-white/4 text-slate-400 border border-white/6 hover:border-white/15'}`}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Featured image toggle */}
        <div className="flex items-center gap-3 p-3 rounded-lg bg-white/3 border border-white/6">
          <Image size={14} className="text-violet-400" />
          <div className="flex-1">
            <div className="text-xs font-semibold text-slate-300">Auto-fetch Featured Images</div>
            <div className="text-xs text-slate-500">Fetches from Unsplash/Pexels and uploads to WordPress media library</div>
          </div>
          <button
            onClick={() => setWpConfig(c => ({ ...c, fetch_image: !c.fetch_image }))}
            className={`w-10 h-5 rounded-full transition-colors relative ${wpConfig.fetch_image ? 'bg-indigo-500' : 'bg-white/10'}`}
          >
            <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${wpConfig.fetch_image ? 'left-5' : 'left-0.5'}`} />
          </button>
        </div>

        {/* Async toggle */}
        <div className="flex items-center gap-3 p-3 rounded-lg bg-white/3 border border-white/6">
          <Zap size={14} className="text-amber-400" />
          <div className="flex-1">
            <div className="text-xs font-semibold text-slate-300">Async Bulk Publish (Recommended for 10+ pages)</div>
            <div className="text-xs text-slate-500">Runs in background — get a job ID to track progress in the Jobs page</div>
          </div>
          <button
            onClick={() => setUseAsync(a => !a)}
            className={`w-10 h-5 rounded-full transition-colors relative ${useAsync ? 'bg-amber-500' : 'bg-white/10'}`}
          >
            <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${useAsync ? 'left-5' : 'left-0.5'}`} />
          </button>
        </div>

        {error && <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-xs">{error}</div>}

        {jobId && (
          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs">
            ✓ Job started — ID: <code className="font-mono">{jobId}</code>
            <span className="ml-2 text-slate-400">Track progress in the Jobs page</span>
          </div>
        )}

        <button onClick={handlePublishSaved} disabled={loading}
          className="btn-primary flex items-center gap-2 px-6 py-2.5 rounded-lg text-white text-sm font-semibold disabled:opacity-60">
          <Upload size={14} />
          {loading ? 'Publishing...' : useAsync ? 'Start Async Publish Job' : 'Publish All Saved Pages to WordPress'}
        </button>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-4 px-5 py-4 border-b border-white/5">
            <h3 className="text-sm font-semibold text-white">Publish Results</h3>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">{successCount} published</span>
            {failCount > 0 && <span className="text-xs px-2 py-0.5 rounded-full bg-red-400/10 text-red-400 border border-red-400/20">{failCount} failed</span>}
          </div>
          <table className="data-table">
            <thead>
              <tr><th>City</th><th>Status</th><th>Post ID</th><th>Image</th><th>URL</th></tr>
            </thead>
            <tbody>
              {results.map((r, i) => (
                <tr key={i}>
                  <td className="font-semibold text-slate-200">{r.city}</td>
                  <td>
                    {r.success
                      ? <span className="flex items-center gap-1 text-emerald-400 text-xs"><CheckCircle size={11} /> Published</span>
                      : <span className="flex items-center gap-1 text-red-400 text-xs"><XCircle size={11} /> {r.error?.slice(0, 60)}</span>}
                  </td>
                  <td className="text-slate-500 text-xs">{r.post_id || '—'}</td>
                  <td className="text-xs">
                    {r.featured_image_id
                      ? <span className="text-emerald-400">✓ #{r.featured_image_id}</span>
                      : <span className="text-slate-600">—</span>}
                  </td>
                  <td>
                    {r.post_url
                      ? <a href={r.post_url} target="_blank" rel="noreferrer" className="text-indigo-400 text-xs underline truncate max-w-[200px] block">{r.post_url}</a>
                      : <span className="text-slate-600 text-xs">—</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
