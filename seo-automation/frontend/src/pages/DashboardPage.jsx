import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search } from 'lucide-react'
import { getLeads, getLeadStats, updateLeadStatus } from '../api'
import useProjectInfo from '../hooks/useProjectInfo'

const STAGES = [
  { id: 'new', label: 'New' },
  { id: 'contacted', label: 'Contacted' },
  { id: 'qualified', label: 'Qualified' },
  { id: 'closed', label: 'Won' },
]

const DEMO_LEADS = [
  { id: 'd1', business_name: 'Harbor Roofing', contact_name: 'Maya Chen', status: 'new', source: 'website', service: 'Local SEO pages', location: 'San Diego, CA', email: 'maya@harbor.co', phone: '(619) 555-0142', budget: '$2–4k', message: 'Wants service pages for 12 coastal cities.' },
  { id: 'd2', business_name: 'Pacific Dental', contact_name: 'James Ortiz', status: 'new', source: 'instant-quote', service: 'Website + SEO', location: 'La Jolla, CA', email: 'james@pacificdental.com', phone: '(858) 555-0190', budget: '$8k', message: 'Quote request from homepage form.' },
  { id: 'd3', business_name: 'North County HVAC', contact_name: 'Priya Shah', status: 'contacted', source: 'prospecting', service: 'Google Ads', location: 'Carlsbad, CA', email: 'priya@nchvac.com', phone: '(760) 555-0118', budget: '$1.5k/mo', message: 'Follow-up scheduled Thursday.' },
  { id: 'd4', business_name: 'Solana Surf Co', contact_name: 'Evan Brooks', status: 'contacted', source: 'manual', service: 'Content', location: 'Solana Beach, CA', email: 'evan@solanasurf.co', budget: '$900', message: 'Sent draft outlines.' },
  { id: 'd5', business_name: 'Vista Auto Care', contact_name: 'Luis Mendoza', status: 'qualified', source: 'website', service: 'GBP + reviews', location: 'Vista, CA', email: 'luis@vistaauto.com', budget: '$3k', message: 'Decision maker confirmed.' },
  { id: 'd6', business_name: 'Coronado Inn', contact_name: 'Helen Park', status: 'closed', source: 'manual', service: 'SEO retainer', location: 'Coronado, CA', email: 'helen@coronadoinn.com', budget: '$2.2k/mo', message: 'Signed. Kickoff next week.' },
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

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      try {
        const [leadsRes, statsRes] = await Promise.all([getLeads(), getLeadStats()])
        if (cancelled) return
        const rows = Array.isArray(leadsRes.data) ? leadsRes.data : []
        setLeads(rows.length ? rows : DEMO_LEADS)
        setStats(statsRes.data?.total ? statsRes.data : {
          total: DEMO_LEADS.length,
          by_status: { new: 2, contacted: 2, qualified: 1, closed: 1 },
        })
      } catch {
        if (!cancelled) {
          setLeads(DEMO_LEADS)
          setStats({ total: DEMO_LEADS.length, by_status: { new: 2, contacted: 2, qualified: 1, closed: 1 } })
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

  return (
    <div className="crm-page fade-in">
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
