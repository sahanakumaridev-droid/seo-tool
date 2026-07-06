/**
 * ProfessionalsPage — Browse verified professionals (Bark/Thumbtack directory style)
 */
import { useState, useEffect } from 'react'
import {
  Star, MapPin, Globe, CheckCircle, Search,
  Briefcase, Loader2, MessageSquare, DollarSign
} from 'lucide-react'
import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || '/api'
const api  = axios.create({ baseURL: BASE })

function StarRating({ rating, count }) {
  if (!rating) return <span className="text-xs" style={{ color: 'var(--text-4)' }}>No reviews yet</span>
  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: 5 }, (_, i) => (
        <Star key={i} size={11}
          className={i < Math.round(rating) ? 'text-amber-400 fill-amber-400' : 'text-slate-600'} />
      ))}
      <span className="text-xs ml-0.5" style={{ color: 'var(--text-3)' }}>
        {rating.toFixed(1)} ({count})
      </span>
    </div>
  )
}

function ProfessionalCard({ pro }) {
  const initials = pro.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)

  return (
    <div className="card card-hover p-5 space-y-4">
      <div className="flex items-start gap-3">
        {pro.avatar_url ? (
          <img src={pro.avatar_url} alt={pro.name}
            className="w-12 h-12 rounded-full object-cover flex-shrink-0" />
        ) : (
          <div className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold text-white"
            style={{ background: 'var(--brand-grad)' }}>
            {initials}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <h3 className="font-semibold text-sm" style={{ color: 'var(--text-1)' }}>{pro.name}</h3>
            {pro.is_verified && (
              <CheckCircle size={13} className="text-emerald-400 flex-shrink-0" />
            )}
          </div>
          <StarRating rating={pro.rating} count={pro.review_count} />
        </div>
        {pro.hourly_rate && (
          <div className="text-right flex-shrink-0">
            <p className="text-sm font-bold" style={{ color: 'var(--brand)' }}>${pro.hourly_rate}/hr</p>
          </div>
        )}
      </div>

      {pro.bio && (
        <p className="text-xs leading-relaxed line-clamp-3" style={{ color: 'var(--text-2)' }}>
          {pro.bio}
        </p>
      )}

      {pro.skills?.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {pro.skills.slice(0, 5).map(s => (
            <span key={s} className="text-[10px] px-1.5 py-0.5 rounded"
              style={{ background: 'var(--bg-raised)', color: 'var(--text-3)', border: '1px solid var(--border)' }}>
              {s}
            </span>
          ))}
          {pro.skills.length > 5 && (
            <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ color: 'var(--text-4)' }}>
              +{pro.skills.length - 5} more
            </span>
          )}
        </div>
      )}

      <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--text-3)' }}>
        {pro.location && (
          <span className="flex items-center gap-1"><MapPin size={10} /> {pro.location}</span>
        )}
        {pro.website && (
          <a href={pro.website} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-indigo-400 transition-colors">
            <Globe size={10} /> Website
          </a>
        )}
      </div>

      <button
        className="w-full py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-1.5 transition-colors"
        style={{ border: '1px solid var(--border)', color: 'var(--text-2)', background: 'var(--bg-raised)' }}
        onClick={() => {
          localStorage.setItem('msg_recipient', pro.id)
          window.location.href = '/messages'
        }}
      >
        <MessageSquare size={13} /> Contact
      </button>
    </div>
  )
}

export default function ProfessionalsPage() {
  const [professionals, setProfessionals] = useState([])
  const [loading, setLoading]             = useState(true)
  const [search, setSearch]               = useState('')
  const [location, setLocation]           = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const params = { limit: 50 }
      if (location) params.location = location
      const res = await api.get('/marketplace/professionals', { params })
      setProfessionals(res.data)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [location])

  const filtered = professionals.filter(p =>
    !search ||
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    (p.bio || '').toLowerCase().includes(search.toLowerCase()) ||
    (p.skills || []).some(s => s.toLowerCase().includes(search.toLowerCase()))
  )

  return (
    <div className="space-y-6 fade-in">
      <div>
        <h1 className="text-xl font-bold" style={{ color: 'var(--text-1)' }}>Find Professionals</h1>
        <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>
          Browse verified SEO and digital marketing experts
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-3)' }} />
          <input
            value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search by name, skill..."
            className="w-full pl-8 pr-3 py-2 rounded-lg text-sm"
            style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)' }}
          />
        </div>
        <input
          value={location} onChange={e => setLocation(e.target.value)}
          placeholder="Location (e.g. San Diego)"
          className="rounded-lg px-3 py-2 text-sm"
          style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)', width: 220 }}
        />
        <span className="text-xs self-center" style={{ color: 'var(--text-3)' }}>{filtered.length} professionals</span>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 size={24} className="animate-spin" style={{ color: 'var(--brand)' }} />
        </div>
      ) : filtered.length === 0 ? (
        <div className="card p-16 text-center">
          <Briefcase size={40} className="mx-auto mb-3 opacity-20" style={{ color: 'var(--text-3)' }} />
          <p className="text-sm" style={{ color: 'var(--text-3)' }}>
            No professionals found. Register as a professional to appear here.
          </p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map(pro => <ProfessionalCard key={pro.id} pro={pro} />)}
        </div>
      )}
    </div>
  )
}
