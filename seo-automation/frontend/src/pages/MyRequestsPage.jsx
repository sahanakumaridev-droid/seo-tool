/**
 * MyRequestsPage — Client view: manage their own service requests and view quotes
 */
import { useState, useEffect } from 'react'
import {
  Briefcase, Plus, ChevronDown, ChevronUp, Star,
  CheckCircle, XCircle, Clock, Loader2, MessageSquare
} from 'lucide-react'
import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || '/api'
const api  = axios.create({ baseURL: BASE })

const STATUS_COLORS = {
  open:      'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
  quoted:    'text-amber-400  bg-amber-400/10  border-amber-400/20',
  hired:     'text-violet-400 bg-violet-400/10 border-violet-400/20',
  completed: 'text-sky-400    bg-sky-400/10    border-sky-400/20',
  cancelled: 'text-red-400    bg-red-400/10    border-red-400/20',
}

function QuoteCard({ quote, onAccept }) {
  const stars = Array.from({ length: 5 }, (_, i) => i < Math.round(quote.professional_rating || 0))
  return (
    <div className="rounded-xl p-4 space-y-2" style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)' }}>
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>{quote.professional_name}</p>
          <div className="flex items-center gap-0.5 mt-0.5">
            {stars.map((filled, i) => (
              <Star key={i} size={10} className={filled ? 'text-amber-400 fill-amber-400' : 'text-slate-600'} />
            ))}
            {quote.professional_rating && (
              <span className="text-[10px] ml-1" style={{ color: 'var(--text-3)' }}>{quote.professional_rating.toFixed(1)}</span>
            )}
          </div>
        </div>
        <div className="text-right">
          <p className="text-base font-bold" style={{ color: 'var(--brand)' }}>${quote.price.toLocaleString()}</p>
          <p className="text-[11px]" style={{ color: 'var(--text-3)' }}>{quote.delivery_days} days</p>
        </div>
      </div>
      <p className="text-xs leading-relaxed" style={{ color: 'var(--text-2)' }}>{quote.cover_letter}</p>
      {quote.status === 'pending' && (
        <button
          onClick={() => onAccept(quote.id)}
          className="w-full btn-primary py-1.5 rounded-lg text-xs text-white font-semibold flex items-center justify-center gap-1"
        >
          <CheckCircle size={12} /> Accept Quote
        </button>
      )}
      {quote.status === 'accepted' && (
        <div className="flex items-center gap-1 text-xs text-emerald-400">
          <CheckCircle size={12} /> Accepted
        </div>
      )}
      {quote.status === 'rejected' && (
        <div className="flex items-center gap-1 text-xs text-red-400">
          <XCircle size={12} /> Rejected
        </div>
      )}
    </div>
  )
}

function RequestRow({ req }) {
  const [expanded, setExpanded] = useState(false)
  const [quotes, setQuotes]     = useState([])
  const [loadingQ, setLoadingQ] = useState(false)

  const loadQuotes = async () => {
    if (quotes.length > 0) { setExpanded(e => !e); return }
    setLoadingQ(true)
    try {
      const token = localStorage.getItem('mp_token')
      const res = await api.get(`/marketplace/quotes/request/${req.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setQuotes(res.data)
      setExpanded(true)
    } catch (e) { console.error(e) }
    finally { setLoadingQ(false) }
  }

  const handleAccept = async (quoteId) => {
    try {
      const token = localStorage.getItem('mp_token')
      await api.patch(`/marketplace/quotes/${quoteId}/accept`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setQuotes(prev => prev.map(q =>
        q.id === quoteId ? { ...q, status: 'accepted' }
        : q.status === 'pending' ? { ...q, status: 'rejected' } : q
      ))
    } catch (e) { alert(e.response?.data?.detail || 'Failed to accept quote') }
  }

  return (
    <div className="card overflow-hidden">
      <div className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-sm" style={{ color: 'var(--text-1)' }}>{req.title}</h3>
            <p className="text-xs mt-0.5" style={{ color: 'var(--text-3)' }}>
              {req.category} · Posted {req.created_at ? new Date(req.created_at).toLocaleDateString() : '—'}
            </p>
          </div>
          <span className={`text-[11px] px-2 py-0.5 rounded-full border font-medium flex-shrink-0 ${STATUS_COLORS[req.status] || STATUS_COLORS.open}`}>
            {req.status}
          </span>
        </div>
        <p className="text-xs mt-2 line-clamp-2" style={{ color: 'var(--text-2)' }}>{req.description}</p>
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs" style={{ color: 'var(--text-3)' }}>
            {req.quote_count} quote{req.quote_count !== 1 ? 's' : ''} received
          </span>
          <button
            onClick={loadQuotes}
            className="flex items-center gap-1 text-xs font-medium"
            style={{ color: 'var(--brand)' }}
          >
            {loadingQ ? <Loader2 size={11} className="animate-spin" /> : null}
            {expanded ? <><ChevronUp size={12} /> Hide quotes</> : <><ChevronDown size={12} /> View quotes</>}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="px-5 pb-5 space-y-3 border-t" style={{ borderColor: 'var(--border)' }}>
          <p className="text-xs font-semibold uppercase tracking-wider pt-4" style={{ color: 'var(--text-3)' }}>
            Quotes ({quotes.length})
          </p>
          {quotes.length === 0 ? (
            <p className="text-xs" style={{ color: 'var(--text-3)' }}>No quotes yet.</p>
          ) : (
            quotes.map(q => <QuoteCard key={q.id} quote={q} onAccept={handleAccept} />)
          )}
        </div>
      )}
    </div>
  )
}

export default function MyRequestsPage() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading]   = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const token = localStorage.getItem('mp_token')
        const res = await api.get('/marketplace/requests/my', {
          headers: { Authorization: `Bearer ${token}` }
        })
        setRequests(res.data)
      } catch (e) { console.error(e) }
      finally { setLoading(false) }
    }
    load()
  }, [])

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-1)' }}>My Requests</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>
            Track your service requests and review incoming quotes
          </p>
        </div>
        <a href="/marketplace"
          className="btn-primary flex items-center gap-1.5 px-4 py-2 rounded-lg text-white text-sm font-semibold">
          <Plus size={14} /> New Request
        </a>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 size={24} className="animate-spin" style={{ color: 'var(--brand)' }} />
        </div>
      ) : requests.length === 0 ? (
        <div className="card p-16 text-center">
          <Briefcase size={40} className="mx-auto mb-3 opacity-20" style={{ color: 'var(--text-3)' }} />
          <p className="text-sm" style={{ color: 'var(--text-3)' }}>
            You haven't posted any requests yet.
          </p>
          <a href="/marketplace"
            className="btn-primary inline-block mt-4 px-6 py-2 rounded-lg text-white text-sm font-semibold">
            Post Your First Request
          </a>
        </div>
      ) : (
        <div className="space-y-4">
          {requests.map(req => <RequestRow key={req.id} req={req} />)}
        </div>
      )}
    </div>
  )
}
