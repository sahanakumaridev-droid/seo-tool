import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search, Sparkles, FileText, Images, Zap, Settings } from 'lucide-react'
import { getLeads, getLeadStats, updateLeadStatus, listPages } from '../api'
import useProjectInfo from '../hooks/useProjectInfo'

const STAGES = [
  { id: 'new', label: 'New' },
  { id: 'contacted', label: 'Contacted' },
  { id: 'qualified', label: 'Qualified' },
  { id: 'closed', label: 'Won' },
]

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 18) return 'Good afternoon'
  return 'Good evening'
}

function leadTitle(lead) {
  return lead.business_name || lead.name || lead.contact_name || 'Untitled'
}

function leadSub(lead) {
  return [lead.contact_name && lead.contact_name !== lead.business_name ? lead.contact_name : null, lead.service || lead.industry, lead.location]
    .filter(Boolean)
    .join(' · ')
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const project = useProjectInfo()
  const [leads, setLeads] = useState([])
  const [stats, setStats] = useState({})
  const [query, setQuery] = useState('')
  const [selectedId, setSelectedId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [savedPages, setSavedPages] = useState([])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      try {
        const [leadsRes, statsRes, pagesRes] = await Promise.all([
          getLeads(),
          getLeadStats(),
          listPages(0, 250).catch(() => ({ data: [] })),
        ])
        if (cancelled) return
        const rows = Array.isArray(leadsRes.data) ? leadsRes.data : []
        setLeads(rows)
        setStats(statsRes.data || {})
        setSavedPages(Array.isArray(pagesRes.data) ? pagesRes.data : [])
      } catch {
        if (!cancelled) {
          setLeads([])
          setStats({})
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => { cancelled = true }
  }, [])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return leads
    return leads.filter((l) =>
      [l.business_name, l.name, l.contact_name, l.email, l.service, l.location, l.industry]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q))
    )
  }, [leads, query])

  const selected = filtered.find((l) => l.id === selectedId) || null

  const move = async (leadId, status) => {
    try {
      await updateLeadStatus(leadId, status)
      setLeads((prev) => prev.map((l) => (l.id === leadId ? { ...l, status } : l)))
    } catch {
      /* keep local UI if API fails silently */
    }
  }

  const website = project.website || 'Workspace'
  const closed = stats.by_status?.closed || 0
  const total = stats.total || leads.length || 0

  const articles = useMemo(() => {
    return savedPages.filter((row) => {
      const kind = String(row?.seo_block?.content_type || '').toLowerCase()
      return kind === 'blog' || kind === 'post'
    })
  }, [savedPages])
  const imageCount = savedPages.filter((row) => row?.seo_block?.featured_image_url).length
  const month = new Date().getMonth()
  const year = new Date().getFullYear()
  const thisMonth = savedPages.filter((row) => {
    const created = row?.created_at ? new Date(row.created_at) : null
    return created && created.getMonth() === month && created.getFullYear() === year
  }).length

  const brand = project.business_name || 'ZeOrbit'
  const [topics, setTopics] = useState(() => [
    { id: 'guide', title: `${brand}: A Practical Beginner's Guide`, tag: 'guide', blurb: 'Built from the site topic, with a direct answer, sections, and a short reference list.' },
    { id: 'choose', title: `How to Choose the Right ${brand} Option`, tag: 'comparison', blurb: 'A comparison article for people close to picking a service.' },
    { id: 'mistakes', title: `${brand} Mistakes to Avoid`, tag: 'mistakes', blurb: 'A high-engagement list of mistakes, written for this niche.' },
  ])

  const startTopic = (topic) => {
    try {
      sessionStorage.setItem('seo_keywords', JSON.stringify([topic.title.toLowerCase()]))
      sessionStorage.setItem('seo_content_kind', 'post')
    } catch { /* ignore */ }
    navigate('/content')
  }

  return (
    <div className="crm-page fade-in">
      <div style={{ background: '#0e1117', color: '#fff', borderRadius: 20, padding: 18, display: 'grid', gap: 16 }}>
        <div style={{ background: 'linear-gradient(90deg, #7c5cff, #d946ef)', borderRadius: 18, padding: '26px 26px 22px' }}>
          <h1 style={{ margin: 0, fontSize: 32, letterSpacing: '-0.03em' }}>Welcome to the SEO Tool</h1>
          <p style={{ margin: '8px 0 16px', maxWidth: 640, color: 'rgba(255,255,255,.92)' }}>
            Generate high-quality, SEO-optimized content with AI-powered research, images, and WordPress publishing.
          </p>
          <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 8 }}>Main option — choose what to generate</div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <button type="button" onClick={() => { try { sessionStorage.setItem('seo_content_kind', 'page') } catch { /* ignore */ } navigate('/content') }} style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: '#fff', color: '#1c305c', border: 0, borderRadius: 12, padding: '12px 16px', fontWeight: 700, cursor: 'pointer', textAlign: 'left' }}>
              <FileText size={16} />
              <span>Page<br /><span style={{ fontWeight: 500, fontSize: 12 }}>Service and location pages</span></span>
            </button>
            <button type="button" onClick={() => { try { sessionStorage.setItem('seo_content_kind', 'post') } catch { /* ignore */ } navigate('/content') }} style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: '#1c305c', color: '#fff', border: 0, borderRadius: 12, padding: '12px 16px', fontWeight: 700, cursor: 'pointer', textAlign: 'left' }}>
              <Sparkles size={16} />
              <span>Post / Blog<br /><span style={{ fontWeight: 500, fontSize: 12, color: 'rgba(255,255,255,.8)' }}>How-to articles</span></span>
            </button>
          </div>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            ['Generated Articles', String(articles.length), FileText, ''],
            ['Images Created', String(imageCount), Images, ''],
            ['Free API', '8 / hour', Zap, 'Starts over each hour, all day'],
            ['This Month', String(thisMonth), Sparkles, ''],
          ].map(([label, value, Icon, hint]) => (
            <div key={label} style={{ background: '#171b24', border: '1px solid #2a3142', borderRadius: 14, padding: '14px 16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: 13 }}>{label}<Icon size={14} /></div>
              <div style={{ fontSize: 28, fontWeight: 800, marginTop: 10 }}>{value}</div>
              {hint ? <div style={{ color: '#94a3b8', fontSize: 12, marginTop: 4 }}>{hint}</div> : null}
            </div>
          ))}
        </div>

        <div style={{ border: '1px solid #2a3142', borderRadius: 16, padding: 16 }}>
          <div style={{ fontWeight: 700 }}>Your starter topics</div>
          <p style={{ margin: '4px 0 12px', color: '#94a3b8', fontSize: 13 }}>Click a topic to open the generator with that title ready.</p>
          <div className="grid md:grid-cols-3 gap-3">
            {topics.map((topic) => (
              <div key={topic.id} style={{ background: '#171b24', border: '1px solid #2a3142', borderRadius: 14, padding: 14 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
                  <strong>{topic.title}</strong>
                  <button type="button" aria-label="Dismiss topic" onClick={() => setTopics((list) => list.filter((item) => item.id !== topic.id))} style={{ background: 'none', border: 0, color: '#94a3b8', cursor: 'pointer' }}>×</button>
                </div>
                <div style={{ marginTop: 8, fontSize: 11, color: '#c4b5fd' }}>{topic.tag}</div>
                <p style={{ color: '#94a3b8', fontSize: 13, minHeight: 48 }}>{topic.blurb}</p>
                <button type="button" onClick={() => startTopic(topic)} style={{ width: '100%', background: '#6d5efc', color: '#fff', border: 0, borderRadius: 8, padding: '8px 10px', fontWeight: 700, cursor: 'pointer' }}>Generate →</button>
              </div>
            ))}
          </div>
        </div>

        <h2 style={{ margin: 0, fontSize: 18 }}>Quick Actions</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            ['New Article', 'Generate SEO content', '/content', Sparkles],
            ['View Content', 'Manage articles', '/posted-blogs', FileText],
            ['Bulk Generate', 'Create multiple articles', '/articles', Zap],
            ['Settings', 'Configure integrations', '/integrations', Settings],
          ].map(([title, sub, to, Icon]) => (
            <button key={title} type="button" onClick={() => navigate(to)} className="text-left" style={{ background: '#171b24', color: '#fff', borderRadius: 14, padding: 16, border: '1px solid #2a3142' }}>
              <Icon size={16} color="#a78bfa" />
              <div style={{ fontWeight: 700, marginTop: 8 }}>{title}</div>
              <div style={{ fontSize: 13, color: '#94a3b8' }}>{sub}</div>
            </button>
          ))}
        </div>

        <div style={{ border: '1px solid #6d5efc', borderRadius: 16, padding: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center', marginBottom: 12 }}>
            <strong>Premium Features</strong>
            <span style={{ fontSize: 12, color: '#c4b5fd' }}>8 articles each hour, then the count starts over. Free all day.</span>
          </div>
          <div className="grid md:grid-cols-3 gap-3">
            {[
              ['Bulk Generation', 'Generate a batch of articles from one keyword and location.'],
              ['WordPress Publishing', 'Publish a finished article to your WordPress site in one step.'],
              ['Free API articles', 'About 8 full articles every hour. When the hour ends, you get another 8. That continues through the day.'],
            ].map(([title, sub]) => (
              <div key={title}>
                <div style={{ fontWeight: 700 }}>{title}</div>
                <div style={{ fontSize: 13, color: '#94a3b8', marginTop: 4 }}>{sub}</div>
              </div>
            ))}
          </div>
        </div>

        <h2 style={{ margin: 0, fontSize: 18 }}>Recent Activity</h2>
        <div style={{ background: '#171b24', border: '1px solid #2a3142', borderRadius: 16, padding: 20, minHeight: 180 }}>
          {articles.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '36px 12px' }}>
              <FileText size={28} color="#64748b" style={{ margin: '0 auto 10px' }} />
              <div style={{ color: '#94a3b8', marginBottom: 12 }}>No articles generated yet</div>
              <button type="button" onClick={() => navigate('/content')} style={{ background: '#1e293b', color: '#fff', border: '1px solid #334155', borderRadius: 8, padding: '8px 14px', cursor: 'pointer' }}>
                Create Your First Article
              </button>
            </div>
          ) : (
            <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'grid', gap: 8 }}>
              {articles.slice(0, 5).map((row) => (
                <li key={row.id || row.slug} style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                  <span>{row.seo_block?.title || row.slug}</span>
                  <span style={{ color: '#94a3b8', fontSize: 12 }}>{row.city || ''}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="crm-head">
        <div>
          <h1>{greeting()}, {project.business_name || 'there'}</h1>
          <p>{website} · Pipeline for inbound and prospected contacts</p>
        </div>
        <div className="crm-toolbar">
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/leads')}>
            Open contacts
          </button>
          <button type="button" className="btn btn-primary" onClick={() => navigate('/leads')}>
            <Plus size={14} /> New lead
          </button>
        </div>
      </div>

      <div className="crm-kpis">
        <div className="crm-kpi">
          <div className="lbl">Open pipeline</div>
          <div className="val">{loading ? '—' : total}</div>
          <div className="hint">All contacts in this workspace</div>
        </div>
        <div className="crm-kpi">
          <div className="lbl">New</div>
          <div className="val">{loading ? '—' : stats.by_status?.new || 0}</div>
          <div className="hint">Not yet contacted</div>
        </div>
        <div className="crm-kpi">
          <div className="lbl">In conversation</div>
          <div className="val">{loading ? '—' : (stats.by_status?.contacted || 0) + (stats.by_status?.qualified || 0)}</div>
          <div className="hint">Contacted + qualified</div>
        </div>
        <div className="crm-kpi">
          <div className="lbl">Won</div>
          <div className="val">{loading ? '—' : closed}</div>
          <div className="hint">Closed deals</div>
        </div>
      </div>

      <div className="crm-toolbar">
        <div className="crm-search">
          <Search size={14} style={{ position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)', color: '#86868b' }} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search companies, people, cities…"
            aria-label="Search pipeline"
          />
        </div>
        <span style={{ fontSize: 12, color: '#86868b', fontVariantNumeric: 'tabular-nums' }}>
          {filtered.length} shown
        </span>
      </div>

      <div className="crm-split">
        <div className="crm-board" role="list">
          {STAGES.map((stage) => {
            const cards = filtered.filter((l) => (l.status || 'new') === stage.id)
            return (
              <section key={stage.id} className="crm-col" aria-label={stage.label}>
                <div className="crm-col-h">
                  <span>{stage.label}</span>
                  <span className="crm-count">{cards.length}</span>
                </div>
                <div className="crm-col-body">
                  {cards.length === 0 ? (
                    <div className="crm-empty-col">{loading ? 'Loading…' : 'No records'}</div>
                  ) : (
                    cards.map((lead) => (
                      <button
                        type="button"
                        key={lead.id}
                        className={`crm-card${selectedId === lead.id ? ' selected' : ''}`}
                        onClick={() => setSelectedId(lead.id)}
                      >
                        <div className="crm-card-title">{leadTitle(lead)}</div>
                        <div className="crm-card-meta">{leadSub(lead) || 'No details yet'}</div>
                        <div className="crm-card-foot">
                          <span className="crm-chip crm-chip-source">{lead.source || 'manual'}</span>
                          {lead.budget ? <span style={{ fontSize: 11, color: '#6e6e73' }}>{lead.budget}</span> : null}
                        </div>
                      </button>
                    ))
                  )}
                </div>
              </section>
            )
          })}
        </div>

        <aside className="crm-drawer">
          {selected ? (
            <>
              <h2>{leadTitle(selected)}</h2>
              <p style={{ margin: '4px 0 0', fontSize: 13, color: '#6e6e73' }}>{leadSub(selected) || 'Contact'}</p>
              <div className="crm-field">
                <label>Stage</label>
                <select
                  value={selected.status || 'new'}
                  onChange={(e) => move(selected.id, e.target.value)}
                  style={{ width: '100%', padding: '8px 10px', background: '#fff' }}
                >
                  {STAGES.map((s) => (
                    <option key={s.id} value={s.id}>{s.label}</option>
                  ))}
                </select>
              </div>
              <div className="crm-field">
                <label>Email</label>
                <div>{selected.email || '—'}</div>
              </div>
              <div className="crm-field">
                <label>Phone</label>
                <div>{selected.phone || '—'}</div>
              </div>
              <div className="crm-field">
                <label>Website</label>
                {selected.website ? (
                  <a href={selected.website} target="_blank" rel="noreferrer">{selected.website.replace(/^https?:\/\//, '')}</a>
                ) : <div>—</div>}
              </div>
              <div className="crm-field">
                <label>Notes</label>
                <div style={{ color: selected.message ? '#1d1d1f' : '#86868b', whiteSpace: 'pre-wrap' }}>
                  {selected.message || 'No notes'}
                </div>
              </div>
              <button type="button" className="btn btn-secondary" style={{ marginTop: 16, width: '100%' }} onClick={() => navigate('/leads')}>
                Manage in contacts
              </button>
            </>
          ) : (
            <>
              <h2>Record</h2>
              <p style={{ margin: '8px 0 0', fontSize: 13, color: '#6e6e73', lineHeight: 1.5 }}>
                Select a card to see contact details, move the stage, and open the full contacts view.
              </p>
            </>
          )}
        </aside>
      </div>
    </div>
  )
}
