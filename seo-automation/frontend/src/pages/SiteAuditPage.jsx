import { useState, useEffect } from 'react'
import {
  Search, Globe2, ChevronDown, AlertOctagon, AlertTriangle, Lightbulb, CheckCircle2, ScanSearch,
} from 'lucide-react'
import { runSiteAudit } from '../api'
import ScoreRing from '../components/ScoreRing'

const SEVERITY_TABS = [
  { key: 'critical', label: 'Critical', icon: AlertOctagon, color: 'var(--red)' },
  { key: 'warning', label: 'Warnings', icon: AlertTriangle, color: 'var(--amber)' },
  { key: 'opportunity', label: 'Opportunities', icon: Lightbulb, color: 'var(--brand)' },
  { key: 'passed', label: 'Passed Checks', icon: CheckCircle2, color: 'var(--green)' },
]

function CategoryBar({ name, score }) {
  const color = score >= 80 ? 'var(--green)' : score >= 60 ? 'var(--amber)' : 'var(--red)'
  return (
    <div>
      <div className="flex items-center justify-between" style={{ fontSize: 12.5, marginBottom: 5 }}>
        <span style={{ color: 'var(--text-2)' }}>{name}</span>
        <span style={{ fontWeight: 700, color: 'var(--text-1)' }}>{score}</span>
      </div>
      <div style={{ height: 6, borderRadius: 4, background: 'var(--bg-raised)', overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${score}%`, background: color, transition: 'width .5s ease' }} />
      </div>
    </div>
  )
}

function IssueRow({ issue }) {
  const [open, setOpen] = useState(false)
  const tab = SEVERITY_TABS.find(t => t.key === issue.severity)
  return (
    <div style={{ border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden' }}>
      <button onClick={() => setOpen(o => !o)}
        style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left' }}>
        <span className="flex items-center gap-3">
          <tab.icon size={15} style={{ color: tab.color, flexShrink: 0 }} />
          <span style={{ fontSize: 13.5, fontWeight: 600, color: 'var(--text-1)' }}>{issue.title}</span>
          {issue.affected_pages.length > 0 && (
            <span style={{ fontSize: 11, color: 'var(--text-4)' }}>{issue.affected_pages.length} pages affected</span>
          )}
        </span>
        <ChevronDown size={15} style={{ color: 'var(--text-4)', transform: open ? 'rotate(180deg)' : 'none', transition: 'transform .15s' }} />
      </button>
      {open && (
        <div style={{ padding: '0 16px 16px', display: 'flex', flexDirection: 'column', gap: 12, borderTop: '1px solid var(--border)', paddingTop: 12 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 3 }}>What's wrong</div>
            <p style={{ fontSize: 13, color: 'var(--text-2)', margin: 0, lineHeight: 1.6 }}>{issue.what}</p>
          </div>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 3 }}>Why it matters</div>
            <p style={{ fontSize: 13, color: 'var(--text-2)', margin: 0, lineHeight: 1.6 }}>{issue.why}</p>
          </div>
          {issue.affected_pages.length > 0 && (
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 5 }}>Affected pages</div>
              <div className="flex flex-wrap gap-1.5">
                {issue.affected_pages.map(p => (
                  <span key={p} style={{ fontSize: 11.5, fontFamily: 'monospace', color: 'var(--text-2)', background: 'var(--bg-raised)', padding: '2px 8px', borderRadius: 6 }}>{p}</span>
                ))}
              </div>
            </div>
          )}
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 3 }}>How to fix</div>
            <p style={{ fontSize: 13, color: 'var(--text-2)', margin: 0, lineHeight: 1.6 }}>{issue.how_to_fix}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default function SiteAuditPage() {
  const [url, setUrl] = useState('')
  const [audit, setAudit] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('critical')

  useEffect(() => {
    try {
      const project = JSON.parse(localStorage.getItem('seo_project') || '{}')
      if (project.website) setUrl(project.website)
      if (project.audit) setAudit(project.audit)
    } catch { /* no cached project */ }
  }, [])

  const handleRun = async (e) => {
    e.preventDefault()
    if (!url.trim()) return
    setLoading(true)
    setError('')
    try {
      const res = await runSiteAudit(url.trim())
      setAudit(res.data)
    } catch {
      setError('Could not run the audit. Please try again.')
    }
    setLoading(false)
  }

  const issuesForTab = audit?.issues.filter(i => i.severity === activeTab) || []

  return (
    <div className="space-y-5 fade-in">
      <div>
        <h1 className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)' }}>Site Audit</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text-3)' }}>Crawl your site to find technical, on-page, and performance issues.</p>
      </div>

      <form onSubmit={handleRun} className="card p-4 flex items-center gap-3 flex-wrap">
        <div style={{ position: 'relative', flex: 1, minWidth: 240 }}>
          <Globe2 size={15} style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-4)' }} />
          <input type="text" value={url} onChange={e => setUrl(e.target.value)} placeholder="Enter a website URL, e.g. example.com"
            style={{ width: '100%', padding: '11px 14px 11px 38px' }} />
        </div>
        <button type="submit" disabled={loading || !url.trim()} className="btn btn-primary">
          <Search size={15} /> {loading ? 'Auditing…' : 'Run Audit'}
        </button>
      </form>

      {error && <div className="alert alert-error">⚠ {error}</div>}

      {loading && (
        <div className="card p-6">
          <div className="loading-skeleton" style={{ height: 108, width: 108, borderRadius: '50%', marginBottom: 20 }} />
          <div className="loading-skeleton" style={{ height: 14, width: '60%', borderRadius: 6, marginBottom: 10 }} />
          <div className="loading-skeleton" style={{ height: 14, width: '40%', borderRadius: 6 }} />
        </div>
      )}

      {!loading && !audit && (
        <div className="card flex flex-col items-center justify-center text-center" style={{ padding: '64px 20px' }}>
          <div style={{ width: 56, height: 56, borderRadius: 14, background: 'var(--brand-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ScanSearch size={26} style={{ color: 'var(--brand)' }} />
          </div>
          <p className="text-sm mt-3" style={{ color: 'var(--text-2)', fontWeight: 600 }}>No audit yet</p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-4)', maxWidth: 320 }}>Enter a website above and click "Run Audit" to get your SEO health score and a full issue breakdown.</p>
        </div>
      )}

      {!loading && audit && (
        <>
          <div className="card p-6 flex items-center gap-8 flex-wrap">
            <ScoreRing score={audit.overall_score} />
            <div style={{ flex: 1, minWidth: 260, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px 24px' }}>
              {audit.categories.map(c => <CategoryBar key={c.name} name={c.name} score={c.score} />)}
            </div>
          </div>

          <div className="card">
            <div className="flex gap-0 border-b" style={{ borderColor: 'var(--border)' }}>
              {SEVERITY_TABS.map(t => {
                const count = audit.issues.filter(i => i.severity === t.key).length
                return (
                  <button key={t.key} onClick={() => setActiveTab(t.key)}
                    className={activeTab === t.key ? 'tab-active' : 'tab-inactive'}
                    style={{ padding: '12px 18px', fontSize: 13, fontWeight: 600, background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
                    <t.icon size={14} style={{ color: t.color }} /> {t.label} <span style={{ color: 'var(--text-4)' }}>({count})</span>
                  </button>
                )
              })}
            </div>
            <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 10 }}>
              {issuesForTab.length === 0 ? (
                <p style={{ fontSize: 13, color: 'var(--text-4)', textAlign: 'center', padding: '20px 0' }}>Nothing here.</p>
              ) : (
                issuesForTab.map(issue => <IssueRow key={issue.id} issue={issue} />)
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
