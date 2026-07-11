/**
 * MarketplacePage — Browse open service requests (Bark/Thumbtack style)
 * Professionals can see leads and submit quotes.
 * Clients can post new requests.
 */
import { useState, useEffect } from 'react'
import {
  Briefcase, MapPin, DollarSign, Clock, Tag, Plus,
  Search, Filter, ChevronRight, Star, CheckCircle, Loader2
} from 'lucide-react'
import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || '/api'
const api  = axios.create({ baseURL: BASE })

const CATEGORIES = [
  'All', 'SEO', 'Web Development', 'Digital Marketing',
  'Content Writing', 'Social Media', 'PPC / Ads',
  'Email Marketing', 'Graphic Design', 'Video Production',
  'Business Consulting', 'Other',
]

const STATUS_COLORS = {
  open:      'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
  quoted:    'text-amber-400  bg-amber-400/10  border-amber-400/20',
  hired:     'text-violet-400 bg-violet-400/10 border-violet-400/20',
  completed: 'text-sky-400    bg-sky-400/10    border-sky-400/20',
  cancelled: 'text-red-400    bg-red-400/10    border-red-400/20',
}

// ── Post Request Modal ────────────────────────────────────────────────────────
function PostRequestModal({ onClose, onPosted }) {
  const [form, setForm] = useState({
    title: '', description: '', category: 'SEO',
    budget_min: '', budget_max: '', location: '',
    remote_ok: true, deadline: '', skills_needed: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true); setError('')
    try {
      const token = localStorage.getItem('mp_token')
      const payload = {
        ...form,
        budget_min: form.budget_min ? parseFloat(form.budget_min) : null,
        budget_max: form.budget_max ? parseFloat(form.budget_max) : null,
        skills_needed: form.skills_needed ? form.skills_needed.split(',').map(s => s.trim()) : [],
      }
      const res = await api.post('/marketplace/requests', payload, {
        headers: { Authorization: `Bearer ${token}` }
      })
      onPosted(res.data)
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to post request')
    } finally {
      setLoading(false)
    }
  }

  const field = (label, key, type = 'text', placeholder = '', required = false) => (
    <div>
      <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--text-3)' }}>
        {label}{required && ' *'}
      </label>
      <input
        type={type} value={form[key]} required={required}
        onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
        placeholder={placeholder}
        className="w-full rounded-lg px-3 py-2 text-sm"
        style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)' }}
      />
    </div>
  )

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <form
        className="relative w-full max-w-2xl rounded-2xl p-6 space-y-4 overflow-y-auto max-h-[90vh]"
        style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
        onClick={e => e.stopPropagation()}
        onSubmit={handleSubmit}
      >
        <h2 className="text-lg font-bold" style={{ color: 'var(--text-1)' }}>Post a Service Request</h2>
        <p className="text-sm" style={{ color: 'var(--text-3)' }}>
          Describe what you need and professionals will send you quotes.
        </p>

        {field('Title', 'title', 'text', 'e.g. Need SEO audit for my e-commerce site', true)}

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--text-3)' }}>
            Description *
          </label>
          <textarea
            value={form.description} required
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            rows={4} placeholder="Describe your project in detail..."
            className="w-full rounded-lg px-3 py-2 text-sm resize-none"
            style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)' }}
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--text-3)' }}>Category *</label>
            <select
              value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
              className="w-full rounded-lg px-3 py-2 text-sm"
              style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)' }}
            >
              {CATEGORIES.filter(c => c !== 'All').map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          {field('Location', 'location', 'text', 'e.g. San Diego, CA')}
        </div>

        <div className="grid grid-cols-2 gap-3">
          {field('Budget Min ($)', 'budget_min', 'number', '500')}
          {field('Budget Max ($)', 'budget_max', 'number', '2000')}
        </div>

        <div className="grid grid-cols-2 gap-3">
          {field('Deadline', 'deadline', 'date', '')}
          {field('Skills Needed', 'skills_needed', 'text', 'SEO, WordPress, Analytics')}
        </div>

        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox" checked={form.remote_ok}
            onChange={e => setForm(f => ({ ...f, remote_ok: e.target.checked }))}
            className="w-4 h-4 rounded"
          />
          <span className="text-sm" style={{ color: 'var(--text-2)' }}>Remote work OK</span>
        </label>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose}
            className="flex-1 px-4 py-2 rounded-lg text-sm font-medium"
            style={{ border: '1px solid var(--border)', color: 'var(--text-2)' }}>
            Cancel
          </button>
          <button type="submit" disabled={loading}
            className="flex-1 btn-primary px-4 py-2 rounded-lg text-sm text-white font-semibold disabled:opacity-50">
            {loading ? 'Posting...' : 'Post Request'}
          </button>
        </div>
      </form>
    </div>
  )
}

// ── Quote Modal ───────────────────────────────────────────────────────────────
function QuoteModal({ request, onClose, onSubmitted }) {
  const [form, setForm] = useState({ price: '', delivery_days: '', cover_letter: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true); setError('')
    try {
      const token = localStorage.getItem('mp_token')
      await api.post('/marketplace/quotes', {
        request_id: request.id,
        price: parseFloat(form.price),
        delivery_days: parseInt(form.delivery_days),
        cover_letter: form.cover_letter,
      }, { headers: { Authorization: `Bearer ${token}` } })
      onSubmitted()
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit quote')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <form
        className="relative w-full max-w-lg rounded-2xl p-6 space-y-4"
        style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
        onClick={e => e.stopPropagation()}
        onSubmit={handleSubmit}
      >
        <div>
          <h2 className="text-base font-bold" style={{ color: 'var(--text-1)' }}>Submit a Quote</h2>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-3)' }}>
            For: <span className="font-medium" style={{ color: 'var(--text-2)' }}>{request.title}</span>
          </p>
          <p className="text-xs mt-1 text-amber-400">⚡ Costs 2 credits to respond to this lead</p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--text-3)' }}>Your Price ($) *</label>
            <input type="number" value={form.price} required min="1"
              onChange={e => setForm(f => ({ ...f, price: e.target.value }))}
              placeholder="500"
              className="w-full rounded-lg px-3 py-2 text-sm"
              style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)' }}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--text-3)' }}>Delivery (days) *</label>
            <input type="number" value={form.delivery_days} required min="1"
              onChange={e => setForm(f => ({ ...f, delivery_days: e.target.value }))}
              placeholder="7"
              className="w-full rounded-lg px-3 py-2 text-sm"
              style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)' }}
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--text-3)' }}>Cover Letter *</label>
          <textarea
            value={form.cover_letter} required
            onChange={e => setForm(f => ({ ...f, cover_letter: e.target.value }))}
            rows={5} placeholder="Introduce yourself and explain why you're the best fit..."
            className="w-full rounded-lg px-3 py-2 text-sm resize-none"
            style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)' }}
          />
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <div className="flex gap-2">
          <button type="button" onClick={onClose}
            className="flex-1 px-4 py-2 rounded-lg text-sm font-medium"
            style={{ border: '1px solid var(--border)', color: 'var(--text-2)' }}>
            Cancel
          </button>
          <button type="submit" disabled={loading}
            className="flex-1 btn-primary px-4 py-2 rounded-lg text-sm text-white font-semibold disabled:opacity-50">
            {loading ? 'Submitting...' : 'Submit Quote (2 credits)'}
          </button>
        </div>
      </form>
    </div>
  )
}

// ── Request Card ──────────────────────────────────────────────────────────────
function RequestCard({ req, onQuote }) {
  const budget = req.budget_min && req.budget_max
    ? `$${req.budget_min.toLocaleString()} – $${req.budget_max.toLocaleString()}`
    : req.budget_min ? `From $${req.budget_min.toLocaleString()}`
    : req.budget_max ? `Up to $${req.budget_max.toLocaleString()}`
    : 'Budget flexible'

  return (
    <div className="card card-hover p-5 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm leading-snug truncate" style={{ color: 'var(--text-1)' }}>
            {req.title}
          </h3>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-3)' }}>
            by {req.client_name} · {req.quote_count} quote{req.quote_count !== 1 ? 's' : ''}
          </p>
        </div>
        <span className={`text-[11px] px-2 py-0.5 rounded-full border font-medium flex-shrink-0 ${STATUS_COLORS[req.status] || STATUS_COLORS.open}`}>
          {req.status}
        </span>
      </div>

      <p className="text-xs leading-relaxed line-clamp-2" style={{ color: 'var(--text-2)' }}>
        {req.description}
      </p>

      <div className="flex flex-wrap gap-2">
        <span className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full"
          style={{ background: 'var(--brand-soft)', color: '#3B82F6' }}>
          <Tag size={9} /> {req.category}
        </span>
        {req.location && (
          <span className="flex items-center gap-1 text-[11px]" style={{ color: 'var(--text-3)' }}>
            <MapPin size={9} /> {req.location}
          </span>
        )}
        <span className="flex items-center gap-1 text-[11px]" style={{ color: 'var(--text-3)' }}>
          <DollarSign size={9} /> {budget}
        </span>
        {req.deadline && (
          <span className="flex items-center gap-1 text-[11px]" style={{ color: 'var(--text-3)' }}>
            <Clock size={9} /> Due {req.deadline}
          </span>
        )}
      </div>

      {req.skills_needed?.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {req.skills_needed.slice(0, 4).map(s => (
            <span key={s} className="text-[10px] px-1.5 py-0.5 rounded"
              style={{ background: 'var(--bg-raised)', color: 'var(--text-3)', border: '1px solid var(--border)' }}>
              {s}
            </span>
          ))}
        </div>
      )}

      <button
        onClick={() => onQuote(req)}
        className="w-full btn-primary py-2 rounded-lg text-sm text-white font-semibold flex items-center justify-center gap-1.5"
      >
        Submit Quote <ChevronRight size={13} />
      </button>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function MarketplacePage() {
  const [requests, setRequests]   = useState([])
  const [loading, setLoading]     = useState(true)
  const [search, setSearch]       = useState('')
  const [category, setCategory]   = useState('All')
  const [location, setLocation]   = useState('')
  const [showPost, setShowPost]   = useState(false)
  const [quoteTarget, setQuoteTarget] = useState(null)

  const loadRequests = async () => {
    setLoading(true)
    try {
      const params = { status: 'open', limit: 50 }
      if (category !== 'All') params.category = category
      if (location) params.location = location
      const res = await api.get('/marketplace/requests', { params })
      setRequests(res.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadRequests() }, [category, location])

  const filtered = requests.filter(r =>
    !search || r.title.toLowerCase().includes(search.toLowerCase()) ||
    r.description.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-1)' }}>Service Marketplace</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>
            Browse client requests and submit quotes to win new business
          </p>
        </div>
        <button
          onClick={() => setShowPost(true)}
          className="btn-primary flex items-center gap-1.5 px-4 py-2 rounded-lg text-white text-sm font-semibold"
        >
          <Plus size={14} /> Post a Request
        </button>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Open Requests', value: requests.filter(r => r.status === 'open').length, color: 'text-emerald-400' },
          { label: 'Categories', value: CATEGORIES.length - 1, color: 'text-indigo-400' },
          { label: 'Avg. Budget', value: '$' + Math.round(requests.filter(r => r.budget_max).reduce((a, r) => a + r.budget_max, 0) / Math.max(requests.filter(r => r.budget_max).length, 1)).toLocaleString(), color: 'text-amber-400' },
        ].map(s => (
          <div key={s.label} className="card p-4 text-center">
            <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
            <div className="text-xs mt-0.5" style={{ color: 'var(--text-3)' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-48">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-3)' }} />
          <input
            value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search requests..."
            className="w-full pl-8 pr-3 py-2 rounded-lg text-sm"
            style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)' }}
          />
        </div>
        <select
          value={category} onChange={e => setCategory(e.target.value)}
          className="rounded-lg px-3 py-2 text-sm"
          style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)' }}
        >
          {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <input
          value={location} onChange={e => setLocation(e.target.value)}
          placeholder="Location (e.g. San Diego)"
          className="rounded-lg px-3 py-2 text-sm"
          style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)', width: 200 }}
        />
        <span className="text-xs" style={{ color: 'var(--text-3)' }}>{filtered.length} results</span>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 size={24} className="animate-spin" style={{ color: 'var(--brand)' }} />
        </div>
      ) : filtered.length === 0 ? (
        <div className="card p-16 text-center">
          <Briefcase size={40} className="mx-auto mb-3 opacity-20" style={{ color: 'var(--text-3)' }} />
          <p className="text-sm" style={{ color: 'var(--text-3)' }}>
            No open requests found. Be the first to post one!
          </p>
          <button onClick={() => setShowPost(true)}
            className="btn-primary mt-4 px-6 py-2 rounded-lg text-white text-sm font-semibold">
            Post a Request
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map(req => (
            <RequestCard key={req.id} req={req} onQuote={setQuoteTarget} />
          ))}
        </div>
      )}

      {showPost && (
        <PostRequestModal
          onClose={() => setShowPost(false)}
          onPosted={r => { setRequests(prev => [r, ...prev]); setShowPost(false) }}
        />
      )}
      {quoteTarget && (
        <QuoteModal
          request={quoteTarget}
          onClose={() => setQuoteTarget(null)}
          onSubmitted={() => { loadRequests(); setQuoteTarget(null) }}
        />
      )}
    </div>
  )
}
