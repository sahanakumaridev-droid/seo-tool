import { useState, useEffect, useMemo } from 'react'
import { Users, Plus, Trash2, ExternalLink, Radar, MapPin, Search, LayoutGrid, List } from 'lucide-react'
import { getLeads, createLead, updateLeadStatus, deleteLead, getLeadStats, prospectLeads } from '../api'

const STAGES = [
  { id: 'new', label: 'New' },
  { id: 'contacted', label: 'Contacted' },
  { id: 'qualified', label: 'Qualified' },
  { id: 'closed', label: 'Won' },
]

function leadTitle(lead) {
  return lead.business_name || lead.name || lead.contact_name || 'Untitled'
}

function ProspectPanel({ onDone }) {
  const [form, setForm] = useState({ industry: '', location: '', limit: 20 })
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')
  const [open, setOpen] = useState(false)

  const run = async () => {
    if (!form.industry || !form.location) { setMsg('Industry and location required.'); return }
    setLoading(true); setMsg('')
    try {
      const res = await prospectLeads({ ...form, limit: Number(form.limit) })
      setMsg(`Discovered ${res.data.discovered} businesses.`)
      onDone()
    } catch (e) {
      setMsg(e.response?.data?.detail || e.message)
    } finally { setLoading(false) }
  }

  return (
    <div className="card" style={{ padding: 14 }}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="btn btn-ghost"
        style={{ width: '100%', justifyContent: 'space-between' }}
      >
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
          <Radar size={15} /> Prospect businesses
        </span>
        <span style={{ fontSize: 12, color: 'var(--text-3)' }}>{open ? 'Hide' : 'Show'}</span>
      </button>
      {open && (
        <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'end' }}>
          <div style={{ flex: 1, minWidth: 140 }}>
            <label className="block text-xs font-semibold mb-1" style={{ color: 'var(--text-3)' }}>Industry</label>
            <input value={form.industry} onChange={(e) => setForm((f) => ({ ...f, industry: e.target.value }))}
              placeholder="e.g. roofing" style={{ width: '100%', padding: '8px 10px', background: '#fff' }} />
          </div>
          <div style={{ flex: 1, minWidth: 140 }}>
            <label className="block text-xs font-semibold mb-1" style={{ color: 'var(--text-3)' }}>
              <MapPin size={10} className="inline mr-1" />Location
            </label>
            <input value={form.location} onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))}
              placeholder="e.g. Austin, TX" style={{ width: '100%', padding: '8px 10px', background: '#fff' }} />
          </div>
          <div style={{ width: 80 }}>
            <label className="block text-xs font-semibold mb-1" style={{ color: 'var(--text-3)' }}>Limit</label>
            <input type="number" min="1" max="60" value={form.limit} onChange={(e) => setForm((f) => ({ ...f, limit: e.target.value }))}
              style={{ width: '100%', padding: '8px 10px', background: '#fff' }} />
          </div>
          <button type="button" onClick={run} disabled={loading} className="btn btn-secondary">
            {loading ? 'Prospecting…' : 'Discover'}
          </button>
          {msg && <p className="text-xs" style={{ color: 'var(--text-3)', width: '100%', margin: 0 }}>{msg}</p>}
        </div>
      )}
    </div>
  )
}

function AddLeadModal({ onClose, onAdded }) {
  const [form, setForm] = useState({ source: 'manual', name: '', business_name: '', contact_name: '', website: '', industry: '', email: '', phone: '', service: '', location: '', budget: '', message: '' })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await createLead(form)
      onAdded(res.data)
      onClose()
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const field = (label, key, type = 'text', placeholder = '') => (
    <div>
      <label className="block text-xs font-semibold mb-1" style={{ color: 'var(--text-3)' }}>{label}</label>
      <input type={type} value={form[key]} onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
        placeholder={placeholder} style={{ width: '100%', padding: '8px 10px', background: '#fff' }} />
    </div>
  )

  return (
    <div className="modal-overlay" onClick={onClose}>
      <form className="crm-modal" onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit}>
        <h2 style={{ margin: '0 0 14px', fontSize: 18 }}>New lead</h2>
        <div className="grid grid-cols-2 gap-3">
          {field('Business', 'business_name', 'text', 'Acme Roofing')}
          {field('Contact', 'contact_name', 'text', 'Jane Smith')}
          {field('Website', 'website', 'url', 'https://acme.com')}
          {field('Industry', 'industry', 'text', 'Roofing')}
          {field('Email', 'email', 'email', 'jane@example.com')}
          {field('Phone', 'phone', 'tel', '+1 555-0000')}
          {field('Service', 'service', 'text', 'Web Design')}
          {field('Location', 'location', 'text', 'San Diego, CA')}
        </div>
        <div style={{ marginTop: 12 }}>
          <label className="block text-xs font-semibold mb-1" style={{ color: 'var(--text-3)' }}>Source</label>
          <select value={form.source} onChange={(e) => setForm((f) => ({ ...f, source: e.target.value }))}
            style={{ width: '100%', padding: '8px 10px', background: '#fff' }}>
            <option value="manual">Manual</option>
            <option value="website">Website</option>
            <option value="instant-quote">Instant Quote</option>
          </select>
        </div>
        <div style={{ marginTop: 12 }}>
          <label className="block text-xs font-semibold mb-1" style={{ color: 'var(--text-3)' }}>Notes</label>
          <textarea value={form.message} onChange={(e) => setForm((f) => ({ ...f, message: e.target.value }))}
            rows={2} placeholder="Context, budget, next step…"
            style={{ width: '100%', padding: '8px 10px', background: '#fff', resize: 'none' }} />
        </div>
        <div className="flex gap-2" style={{ marginTop: 16 }}>
          <button type="button" onClick={onClose} className="btn btn-secondary" style={{ flex: 1 }}>Cancel</button>
          <button type="submit" disabled={loading || (!form.name && !form.business_name && !form.contact_name)}
            className="btn btn-primary" style={{ flex: 1 }}>
            {loading ? 'Saving…' : 'Save lead'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default function LeadsPage() {
  const [leads, setLeads] = useState([])
  const [stats, setStats] = useState({})
  const [filterStatus, setFilterStatus] = useState('')
  const [filterSource, setFilterSource] = useState('')
  const [query, setQuery] = useState('')
  const [view, setView] = useState('pipeline')
  const [selectedId, setSelectedId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)

  const loadLeads = async () => {
    setLoading(true)
    try {
      const [leadsRes, statsRes] = await Promise.all([
        getLeads({ status: filterStatus, source: filterSource }),
        getLeadStats(),
      ])
      setLeads(Array.isArray(leadsRes.data) ? leadsRes.data : [])
      setStats(statsRes.data || {})
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadLeads() }, [filterStatus, filterSource])

  const handleStatusChange = async (leadId, status) => {
    try {
      await updateLeadStatus(leadId, status)
      setLeads((prev) => prev.map((l) => (l.id === leadId ? { ...l, status } : l)))
    } catch (e) { console.error(e) }
  }

  const handleDelete = async (leadId) => {
    if (!confirm('Delete this lead?')) return
    try {
      await deleteLead(leadId)
      setLeads((prev) => prev.filter((l) => l.id !== leadId))
      if (selectedId === leadId) setSelectedId(null)
    } catch (e) { console.error(e) }
  }

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return leads
    return leads.filter((l) =>
      [l.business_name, l.name, l.contact_name, l.email, l.service, l.location, l.industry, l.phone]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q))
    )
  }, [leads, query])

  const selected = filtered.find((l) => l.id === selectedId) || null

  return (
    <div className="crm-page fade-in">
      <div className="crm-head">
        <div>
          <h1>Contacts</h1>
          <p>Pipeline, records, and prospecting — white-label CRM for this workspace</p>
        </div>
        <button type="button" onClick={() => setShowAdd(true)} className="btn btn-primary">
          <Plus size={14} /> New lead
        </button>
      </div>

      <div className="crm-kpis">
        {[
          { label: 'Total', value: stats.total || 0, hint: 'Every captured contact' },
          { label: 'New', value: stats.by_status?.new || 0, hint: 'Waiting on first touch' },
          { label: 'Qualified', value: stats.by_status?.qualified || 0, hint: 'Ready to close' },
          { label: 'Won', value: stats.by_status?.closed || 0, hint: 'Closed this workspace' },
        ].map((s) => (
          <div key={s.label} className="crm-kpi">
            <div className="lbl">{s.label}</div>
            <div className="val">{s.value}</div>
            <div className="hint">{s.hint}</div>
          </div>
        ))}
      </div>

      <ProspectPanel onDone={loadLeads} />

      <div className="crm-toolbar">
        <div className="crm-seg" role="tablist" aria-label="View">
          <button type="button" aria-pressed={view === 'pipeline'} onClick={() => setView('pipeline')}>
            <LayoutGrid size={13} style={{ display: 'inline', marginRight: 4 }} /> Pipeline
          </button>
          <button type="button" aria-pressed={view === 'table'} onClick={() => setView('table')}>
            <List size={13} style={{ display: 'inline', marginRight: 4 }} /> Table
          </button>
        </div>
        <div className="crm-search">
          <Search size={14} style={{ position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)', color: '#86868b' }} />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search contacts…" aria-label="Search contacts" />
        </div>
        <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}
          style={{ padding: '8px 10px', background: '#fff', fontSize: 13 }}>
          <option value="">All stages</option>
          {STAGES.map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
        </select>
        <select value={filterSource} onChange={(e) => setFilterSource(e.target.value)}
          style={{ padding: '8px 10px', background: '#fff', fontSize: 13 }}>
          <option value="">All sources</option>
          {['prospecting', 'manual', 'website', 'instant-quote'].map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <span style={{ fontSize: 12, color: '#86868b' }}>{filtered.length} records</span>
      </div>

      {view === 'pipeline' ? (
        <div className="crm-split">
          <div className="crm-board">
            {STAGES.map((stage) => {
              const cards = filtered.filter((l) => (l.status || 'new') === stage.id)
              return (
                <section key={stage.id} className="crm-col">
                  <div className="crm-col-h">
                    <span>{stage.label}</span>
                    <span className="crm-count">{cards.length}</span>
                  </div>
                  <div className="crm-col-body">
                    {cards.length === 0 ? (
                      <div className="crm-empty-col">{loading ? 'Loading…' : 'No records'}</div>
                    ) : cards.map((lead) => (
                      <button
                        type="button"
                        key={lead.id}
                        className={`crm-card${selectedId === lead.id ? ' selected' : ''}`}
                        onClick={() => setSelectedId(lead.id)}
                      >
                        <div className="crm-card-title">{leadTitle(lead)}</div>
                        <div className="crm-card-meta">
                          {[lead.contact_name, lead.service, lead.location].filter(Boolean).join(' · ') || 'No details yet'}
                        </div>
                        <div className="crm-card-foot">
                          <span className={`crm-chip crm-chip-${lead.status || 'new'}`}>{lead.status || 'new'}</span>
                          <span className="crm-chip crm-chip-source">{lead.source || 'manual'}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </section>
              )
            })}
          </div>
          <aside className="crm-drawer">
            {selected ? (
              <>
                <h2>{leadTitle(selected)}</h2>
                <div className="crm-field">
                  <label>Stage</label>
                  <select value={selected.status || 'new'} onChange={(e) => handleStatusChange(selected.id, e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', background: '#fff' }}>
                    {STAGES.map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
                  </select>
                </div>
                <div className="crm-field"><label>Email</label><div>{selected.email || '—'}</div></div>
                <div className="crm-field"><label>Phone</label><div>{selected.phone || '—'}</div></div>
                <div className="crm-field">
                  <label>Website</label>
                  {selected.website ? (
                    <a href={selected.website} target="_blank" rel="noreferrer">{selected.website.replace(/^https?:\/\//, '')}</a>
                  ) : <div>—</div>}
                </div>
                <div className="crm-field"><label>Notes</label><div style={{ whiteSpace: 'pre-wrap' }}>{selected.message || '—'}</div></div>
                <button type="button" className="btn btn-ghost" style={{ marginTop: 16, color: 'var(--red)' }} onClick={() => handleDelete(selected.id)}>
                  <Trash2 size={13} /> Delete
                </button>
              </>
            ) : (
              <>
                <h2>Record</h2>
                <p style={{ marginTop: 8, fontSize: 13, color: '#6e6e73' }}>Select a card to inspect and move the deal.</p>
              </>
            )}
          </aside>
        </div>
      ) : (
        <div className="crm-table-wrap">
          {loading ? (
            <div className="flex items-center justify-center py-16 text-sm" style={{ color: 'var(--text-3)' }}>Loading…</div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16" style={{ color: 'var(--text-3)' }}>
              <Users size={28} className="mb-3 opacity-40" />
              <p className="text-sm">No leads yet. Add one, prospect, or capture from Instant Quote.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Company</th>
                    <th>Service</th>
                    <th>Location</th>
                    <th>Source</th>
                    <th>Budget</th>
                    <th>Stage</th>
                    <th>Date</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((lead) => (
                    <tr
                      key={lead.id}
                      className={selectedId === lead.id ? 'crm-row-active' : ''}
                      onClick={() => setSelectedId(lead.id)}
                    >
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text-1)' }}>{leadTitle(lead)}</div>
                        {lead.contact_name && <div className="text-[11px]" style={{ color: 'var(--text-3)' }}>{lead.contact_name}</div>}
                        {lead.website && (
                          <a href={lead.website} target="_blank" rel="noreferrer"
                            className="text-[11px] inline-flex items-center gap-1" style={{ color: 'var(--brand)' }}
                            onClick={(e) => e.stopPropagation()}>
                            <ExternalLink size={9} />{lead.website.replace(/^https?:\/\//, '').slice(0, 30)}
                          </a>
                        )}
                      </td>
                      <td>{lead.service || '—'}</td>
                      <td className="muted-cell">{lead.location || '—'}</td>
                      <td><span className="crm-chip crm-chip-source">{lead.source}</span></td>
                      <td className="muted-cell">{lead.budget || '—'}</td>
                      <td>
                        <select
                          value={lead.status}
                          onClick={(e) => e.stopPropagation()}
                          onChange={(e) => handleStatusChange(lead.id, e.target.value)}
                          style={{ padding: '4px 8px', background: '#fff', fontSize: 12 }}
                        >
                          {STAGES.map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
                        </select>
                      </td>
                      <td className="muted-cell">
                        {lead.created_at ? new Date(lead.created_at).toLocaleDateString() : '—'}
                      </td>
                      <td>
                        <button type="button" onClick={(e) => { e.stopPropagation(); handleDelete(lead.id) }}
                          className="p-1.5 rounded" style={{ color: 'var(--text-4)', background: 'none', border: 0, cursor: 'pointer' }}>
                          <Trash2 size={13} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {showAdd && <AddLeadModal onClose={() => setShowAdd(false)} onAdded={() => { loadLeads() }} />}
    </div>
  )
}
