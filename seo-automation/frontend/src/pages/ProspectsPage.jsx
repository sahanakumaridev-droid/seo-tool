import { useEffect, useMemo, useState } from 'react'
import { Building2, Download, MapPin, Search, Trash2 } from 'lucide-react'
import { deleteProspect, getProspects, searchProspects } from '../api'

const COLUMNS = [
  'Business name',
  'Email',
  'Phone',
  'Website',
  'Category',
  'Address',
  'City',
  'State',
  'ZIP',
  'Rating',
  'Reviews',
  'Maps',
  'Social',
]

function socialLabel(socials) {
  const entries = Object.entries(socials || {})
  if (!entries.length) return '—'
  return entries.map(([key]) => key).join(', ')
}

function csvCell(value) {
  const text = value == null ? '' : String(value)
  if (/[",\n]/.test(text)) return `"${text.replace(/"/g, '""')}"`
  return text
}

function downloadCsv(rows) {
  const header = [
    'Business name', 'Email', 'Phone', 'Website', 'Category', 'Address',
    'City', 'State', 'ZIP', 'Rating', 'Reviews', 'Google Maps URL', 'Social profiles',
  ]
  const lines = rows.map((row) => [
    row.business_name, row.email, row.phone, row.website, row.category, row.address,
    row.city, row.state, row.zip_code, row.rating ?? '', row.review_count ?? '',
    row.maps_url, socialLabel(row.socials) === '—' ? '' : socialLabel(row.socials),
  ].map(csvCell).join(','))
  const blob = new Blob([[header.join(','), ...lines].join('\n')], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'zeorbit-prospects.csv'
  link.click()
  URL.revokeObjectURL(url)
}

export default function ProspectsPage() {
  const [form, setForm] = useState({ industry: '', location: '', limit: 10 })
  const [rows, setRows] = useState([])
  const [readyCount, setReadyCount] = useState(0)
  const [total, setTotal] = useState(0)
  const [readyOnly, setReadyOnly] = useState(true)
  const [loading, setLoading] = useState(false)
  const [searching, setSearching] = useState(false)
  const [message, setMessage] = useState('')

  const load = async (onlyReady = readyOnly) => {
    setLoading(true)
    try {
      const res = await getProspects({ ready_only: onlyReady })
      setRows(res.data.prospects || [])
      setReadyCount(res.data.ready || 0)
      setTotal(res.data.total || 0)
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Could not load prospects.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load(true) }, [])

  const visible = useMemo(() => rows, [rows])
  const missing = Math.max(total - readyCount, 0)

  const search = async (event) => {
    event.preventDefault()
    if (!form.industry.trim() || !form.location.trim()) {
      setMessage('Add a business category and a city.')
      return
    }
    setSearching(true)
    setMessage('')
    try {
      const res = await searchProspects({
        industry: form.industry.trim(),
        location: form.location.trim(),
        limit: Number(form.limit) || 10,
      })
      const found = res.data.discovered || 0
      const ready = res.data.ready || 0
      setMessage(`${found} businesses checked. ${ready} have both a public email and a phone number.`)
      setReadyOnly(true)
      await load(true)
    } catch (err) {
      const detail = err.response?.data?.detail
      setMessage(typeof detail === 'string' ? detail : 'Search did not complete.')
    } finally {
      setSearching(false)
    }
  }

  const toggleReady = async () => {
    const next = !readyOnly
    setReadyOnly(next)
    await load(next)
  }

  const remove = async (id) => {
    const row = rows.find((item) => item.id === id)
    try {
      await deleteProspect(id)
      setRows((prev) => prev.filter((item) => item.id !== id))
      setTotal((n) => Math.max(n - 1, 0))
      if (row?.ready) setReadyCount((n) => Math.max(n - 1, 0))
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Could not remove that row.')
    }
  }

  return (
    <div className="crm-page fade-in">
      <div className="crm-head">
        <div>
          <h1>Prospects</h1>
          <p>Public business listings for ZeOrbit outreach. A row can start a cold email only when it has both an email and a phone number.</p>
        </div>
        <button
          type="button"
          className="btn btn-secondary"
          disabled={!visible.some((row) => row.ready)}
          onClick={() => downloadCsv(visible.filter((row) => row.ready))}
        >
          <Download size={14} /> Export ready list
        </button>
      </div>

      <form onSubmit={search} className="card" style={{ padding: 16, display: 'grid', gap: 12 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(0, 1.2fr) 88px', gap: 10, alignItems: 'end' }}>
        <div>
          <label className="block text-xs font-semibold mb-1" style={{ color: 'var(--text-3)' }}>Category</label>
          <input
            value={form.industry}
            onChange={(e) => setForm((f) => ({ ...f, industry: e.target.value }))}
            placeholder="dentists, roofers, gyms"
            style={{ width: '100%', padding: '8px 10px', background: '#fff' }}
          />
        </div>
        <div>
          <label className="block text-xs font-semibold mb-1" style={{ color: 'var(--text-3)' }}>
            <MapPin size={10} style={{ display: 'inline', marginRight: 4 }} />City
          </label>
          <input
            value={form.location}
            onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))}
            placeholder="San Diego, CA"
            style={{ width: '100%', padding: '8px 10px', background: '#fff' }}
          />
        </div>
        <div>
          <label className="block text-xs font-semibold mb-1" style={{ color: 'var(--text-3)' }}>Limit</label>
          <input
            type="number"
            min="1"
            max="20"
            value={form.limit}
            onChange={(e) => setForm((f) => ({ ...f, limit: e.target.value }))}
            style={{ width: '100%', padding: '8px 10px', background: '#fff' }}
          />
        </div>
        </div>
        <div>
        <button type="submit" className="btn btn-primary" disabled={searching}>
          <Search size={14} /> {searching ? 'Searching…' : 'Build list'}
        </button>
        </div>
        <p style={{ margin: 0, fontSize: 12, color: '#6e6e73', lineHeight: 1.45, maxWidth: 760 }}>
          This search uses free OpenStreetMap listings, so no Google card or API key is required.
          Email and social links are added when the business publishes them. Google rating and review count stay empty on these rows.
        </p>
        {message && <p style={{ width: '100%', margin: 0, fontSize: 13, color: '#1d1d1f' }}>{message}</p>}
      </form>

      <div className="crm-kpis">
        <div className="crm-kpi">
          <div className="lbl">Saved</div>
          <div className="val">{total}</div>
          <div className="hint">Businesses on this list</div>
        </div>
        <div className="crm-kpi">
          <div className="lbl">Ready</div>
          <div className="val">{readyCount}</div>
          <div className="hint">Email and phone both present</div>
        </div>
        <div className="crm-kpi">
          <div className="lbl">Needs contact</div>
          <div className="val">{missing}</div>
          <div className="hint">Missing a public email or phone</div>
        </div>
        <div className="crm-kpi">
          <div className="lbl">Showing</div>
          <div className="val">{visible.length}</div>
          <div className="hint">{readyOnly ? 'Ready rows only' : 'Every saved row'}</div>
        </div>
      </div>

      <div className="crm-toolbar">
        <div className="crm-seg" role="tablist" aria-label="Prospect filter">
          <button type="button" aria-pressed={readyOnly} onClick={() => { if (!readyOnly) toggleReady() }}>Ready</button>
          <button type="button" aria-pressed={!readyOnly} onClick={() => { if (readyOnly) toggleReady() }}>All saved</button>
        </div>
        <span style={{ fontSize: 12, color: '#86868b' }}>{loading ? 'Loading…' : `${visible.length} rows`}</span>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'auto' }}>
        {visible.length === 0 ? (
          <div style={{ padding: '36px 20px', textAlign: 'center', color: '#6e6e73' }}>
            <Building2 size={22} style={{ margin: '0 auto 8px' }} />
            <p style={{ margin: 0, fontSize: 14 }}>
              {readyOnly
                ? 'No ready prospects yet. Search a category and city. Rows appear here after a public email and a phone number are both found.'
                : 'No saved prospects yet.'}
            </p>
          </div>
        ) : (
          <table className="data-table" style={{ minWidth: 1080 }}>
            <thead>
              <tr>
                {COLUMNS.map((col) => <th key={col}>{col}</th>)}
                <th />
              </tr>
            </thead>
            <tbody>
              {visible.map((row) => (
                <tr key={row.id}>
                  <td>{row.business_name || '—'}</td>
                  <td>{row.email || '—'}</td>
                  <td>{row.phone || '—'}</td>
                  <td>
                    {row.website ? <a href={row.website} target="_blank" rel="noreferrer">{row.website.replace(/^https?:\/\//, '').replace(/\/$/, '')}</a> : '—'}
                  </td>
                  <td>{row.category || '—'}</td>
                  <td>{row.address || '—'}</td>
                  <td>{row.city || '—'}</td>
                  <td>{row.state || '—'}</td>
                  <td>{row.zip_code || '—'}</td>
                  <td>{row.rating ?? '—'}</td>
                  <td>{row.review_count ?? '—'}</td>
                  <td>
                    {row.maps_url ? <a href={row.maps_url} target="_blank" rel="noreferrer">Maps</a> : '—'}
                  </td>
                  <td>
                    {Object.keys(row.socials || {}).length
                      ? Object.entries(row.socials).map(([key, href]) => (
                        <a key={key} href={href} target="_blank" rel="noreferrer" style={{ marginRight: 8 }}>{key}</a>
                      ))
                      : '—'}
                  </td>
                  <td>
                    <button type="button" className="btn btn-ghost" aria-label={`Remove ${row.business_name}`} onClick={() => remove(row.id)}>
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
