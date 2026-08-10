import { useState, useEffect } from 'react'
import { Users, Plus, Trash2, ExternalLink, Filter, Radar, MapPin } from 'lucide-react'
import { getLeads, createLead, updateLeadStatus, deleteLead, getLeadStats, prospectLeads } from '../api'

const STATUS_COLORS = {
  new:        'text-sky-400 bg-sky-400/10 border-sky-400/20',
  contacted:  'text-amber-400 bg-amber-400/10 border-amber-400/20',
  qualified:  'text-violet-400 bg-violet-400/10 border-violet-400/20',
  closed:     'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
}

const SOURCE_COLORS = {
  manual:          'text-slate-400 bg-slate-400/10',
  prospecting:     'text-emerald-400 bg-emerald-400/10',
  website:         'text-cyan-400 bg-cyan-400/10',
  'instant-quote': 'text-violet-400 bg-violet-400/10',
}

const STATUSES = ['new', 'contacted', 'qualified', 'closed']

function ProspectPanel({ onDone }) {
  const [form, setForm] = useState({ industry: '', location: '', limit: 20 })
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')

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
    <div className="card p-5 border-emerald-500/20">
      <div className="flex items-center gap-2 mb-3">
        <Radar size={15} className="text-emerald-400" />
        <span className="text-sm font-semibold text-white">Prospect New Leads</span>
        <span className="text-xs text-slate-500">— discover businesses via Google Places</span>
      </div>
      <div className="flex flex-wrap gap-2 items-end">
        <div className="flex-1 min-w-[140px]">
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Industry</label>
          <input value={form.industry} onChange={e => setForm(f => ({ ...f, industry: e.target.value }))}
            placeholder="e.g. roofing" className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500/50" />
        </div>
        <div className="flex-1 min-w-[140px]">
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1"><MapPin size={10} className="inline mr-1" />Location</label>
          <input value={form.location} onChange={e => setForm(f => ({ ...f, location: e.target.value }))}
            placeholder="e.g. Austin, TX" className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500/50" />
        </div>
        <div className="w-20">
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Limit</label>
          <input type="number" min="1" max="60" value={form.limit} onChange={e => setForm(f => ({ ...f, limit: e.target.value }))}
            className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500/50" />
        </div>
        <button onClick={run} disabled={loading}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600/20 border border-emerald-600/30 text-emerald-300 hover:bg-emerald-600/30 transition-colors text-sm font-medium disabled:opacity-50">
          <Radar size={14} className={loading ? 'animate-pulse' : ''} /> {loading ? 'Prospecting...' : 'Discover'}
        </button>
      </div>
      {msg && <p className="text-xs text-slate-400 mt-2">{msg}</p>}
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
      <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">{label}</label>
      <input type={type} value={form[key]} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
        placeholder={placeholder}
        className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50" />
    </div>
  )

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
      <form className="relative w-full max-w-lg card rounded-2xl p-6 space-y-4" onClick={e => e.stopPropagation()} onSubmit={handleSubmit}>
        <h2 className="text-base font-bold text-white">Add Lead</h2>
        <div className="grid grid-cols-2 gap-3">
          {field('Business Name', 'business_name', 'text', 'Acme Roofing')}
          {field('Contact Name', 'contact_name', 'text', 'John Smith')}
          {field('Website', 'website', 'url', 'https://acme.com')}
          {field('Industry', 'industry', 'text', 'Roofing')}
          {field('Email', 'email', 'email', 'john@example.com')}
          {field('Phone', 'phone', 'tel', '+1 555-0000')}
          {field('Service', 'service', 'text', 'Web Design')}
          {field('Location', 'location', 'text', 'San Diego, CA')}
          {field('Budget', 'budget', 'text', '$500-$2000')}
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Source</label>
          <select value={form.source} onChange={e => setForm(f => ({ ...f, source: e.target.value }))}
            className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500/50">
            <option value="manual">Manual</option>
            <option value="website">Website</option>
            <option value="instant-quote">Instant Quote</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Message</label>
          <textarea value={form.message} onChange={e => setForm(f => ({ ...f, message: e.target.value }))}
            rows={2} placeholder="Lead message or notes..."
            className="w-full bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 resize-none" />
        </div>
        <div className="flex gap-2 pt-1">
          <button type="button" onClick={onClose} className="flex-1 px-4 py-2 rounded-lg text-sm text-slate-400 border border-white/8 hover:bg-white/4 transition-colors">Cancel</button>
          <button type="submit" disabled={loading || (!form.name && !form.business_name)}
            className="flex-1 btn-primary px-4 py-2 rounded-lg text-sm text-white font-semibold disabled:opacity-50">
            {loading ? 'Adding...' : 'Add Lead'}
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
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)

  const loadLeads = async () => {
    setLoading(true)
    try {
      const [leadsRes, statsRes] = await Promise.all([
        getLeads({ status: filterStatus, source: filterSource }),
        getLeadStats(),
      ])
      setLeads(leadsRes.data)
      setStats(statsRes.data)
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
      setLeads(prev => prev.map(l => l.id === leadId ? { ...l, status } : l))
    } catch (e) { console.error(e) }
  }

  const handleDelete = async (leadId) => {
    if (!confirm('Delete this lead?')) return
    try {
      await deleteLead(leadId)
      setLeads(prev => prev.filter(l => l.id !== leadId))
    } catch (e) { console.error(e) }
  }

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Lead Generation</h1>
          <p className="text-sm text-slate-500 mt-0.5">Prospect new businesses, capture inbound leads, and manage your pipeline</p>
        </div>
        <button onClick={() => setShowAdd(true)}
          className="btn-primary flex items-center gap-1.5 px-4 py-2 rounded-lg text-white text-sm font-semibold">
          <Plus size={14} /> Add Lead
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'Total Leads', value: stats.total || 0, color: 'text-white' },
          { label: 'New', value: stats.by_status?.new || 0, color: 'text-sky-400' },
          { label: 'Qualified', value: stats.by_status?.qualified || 0, color: 'text-violet-400' },
          { label: 'Closed', value: stats.by_status?.closed || 0, color: 'text-emerald-400' },
        ].map(s => (
          <div key={s.label} className="card p-4">
            <div className="text-xs text-slate-500 mb-1">{s.label}</div>
            <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Prospecting */}
      <ProspectPanel onDone={loadLeads} />

      {/* Filters */}
      <div className="flex items-center gap-3">
        <Filter size={13} className="text-slate-500" />
        <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)}
          className="bg-white/4 border border-white/8 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-indigo-500/50">
          <option value="">All Statuses</option>
          {STATUSES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
        </select>
        <select value={filterSource} onChange={e => setFilterSource(e.target.value)}
          className="bg-white/4 border border-white/8 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-indigo-500/50">
          <option value="">All Sources</option>
          {['prospecting', 'manual', 'website', 'instant-quote'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <span className="text-xs text-slate-500">{leads.length} leads</span>
      </div>

      {/* Table */}
      <div className="card">
        {loading ? (
          <div className="flex items-center justify-center py-16 text-slate-500 text-sm">Loading leads...</div>
        ) : leads.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-slate-500">
            <Users size={32} className="mb-3 opacity-30" />
            <p className="text-sm">No leads yet. Add manually, prospect, or use Instant Quote.</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Service</th>
                <th>Location</th>
                <th>Source</th>
                <th>Budget</th>
                <th>Status</th>
                <th>Date</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {leads.map(lead => (
                <tr key={lead.id}>
                  <td>
                    <div className="font-semibold text-slate-200">{lead.business_name || lead.name || '—'}</div>
                    {lead.contact_name && <div className="text-[11px] text-slate-400">{lead.contact_name}</div>}
                    {lead.website && (
                      <a href={lead.website} target="_blank" rel="noreferrer"
                        className="text-[11px] text-indigo-400 hover:underline inline-flex items-center gap-1">
                        <ExternalLink size={9} />{lead.website.replace(/^https?:\/\//, '').slice(0, 30)}
                      </a>
                    )}
                    {lead.email && <div className="text-[11px] text-slate-500">{lead.email}</div>}
                    {lead.phone && <div className="text-[11px] text-slate-500">{lead.phone}</div>}
                  </td>
                  <td className="text-slate-300">{lead.service || '—'}</td>
                  <td className="text-slate-400 text-xs">{lead.location || '—'}</td>
                  <td>
                    <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium ${SOURCE_COLORS[lead.source] || SOURCE_COLORS.manual}`}>
                      {lead.source}
                    </span>
                  </td>
                  <td className="text-slate-400 text-xs">{lead.budget || '—'}</td>
                  <td>
                    <select
                      value={lead.status}
                      onChange={e => handleStatusChange(lead.id, e.target.value)}
                      className={`text-xs px-2 py-1 rounded-lg border bg-transparent cursor-pointer focus:outline-none ${STATUS_COLORS[lead.status] || STATUS_COLORS.new}`}
                    >
                      {STATUSES.map(s => <option key={s} value={s} className="bg-slate-900 text-slate-200">{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
                    </select>
                  </td>
                  <td className="text-slate-500 text-xs">
                    {lead.created_at ? new Date(lead.created_at).toLocaleDateString() : '—'}
                  </td>
                  <td>
                    <button onClick={() => handleDelete(lead.id)}
                      className="p-1.5 rounded hover:bg-red-500/10 text-slate-600 hover:text-red-400 transition-colors">
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

      {showAdd && <AddLeadModal onClose={() => setShowAdd(false)} onAdded={lead => { setLeads(prev => [lead, ...prev]); loadLeads() }} />}
    </div>
  )
}
