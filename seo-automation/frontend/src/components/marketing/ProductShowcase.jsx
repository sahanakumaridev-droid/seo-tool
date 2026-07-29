import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TRAFFIC_TREND } from '../../data/mockData'

const TOP_KEYWORDS = [
  { kw: 'seo services', pos: 3, vol: '12,100' },
  { kw: 'local seo',    pos: 6, vol: '8,100' },
  { kw: 'seo agency',   pos: 8, vol: '6,600' },
]

const STATS = [
  { label: 'Organic Traffic',  value: '48,291' },
  { label: 'Organic Keywords', value: '3,482' },
  { label: 'Average Position', value: '12.6' },
  { label: 'Backlinks',        value: '18,420' },
]

const ChartTip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="card px-3 py-2 text-xs">
      <div style={{ color: 'var(--text-3)', marginBottom: 4 }}>{label}</div>
      <div style={{ color: 'var(--text-1)', fontWeight: 700 }}>{payload[0].value?.toLocaleString?.()} sessions</div>
    </div>
  )
}

export default function ProductShowcase() {
  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '20px 26px', borderBottom: '1px solid var(--border)' }}>
        <span className="section-label">SEO Performance</span>
      </div>

      <div style={{ padding: '22px 26px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 14 }}>
        {STATS.map(s => (
          <div key={s.label}>
            <div style={{ fontSize: 12, color: 'var(--text-3)' }}>{s.label}</div>
            <div className="font-display" style={{ fontSize: 26, fontWeight: 800, color: 'var(--text-1)' }}>{s.value}</div>
          </div>
        ))}
      </div>

      <div style={{ padding: '0 26px 26px', display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: 22 }} className="showcase-grid">
        <div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={TRAFFIC_TREND} margin={{ top: 4, right: 8, left: -18, bottom: 0 }}>
              <defs>
                <linearGradient id="showcase-og" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#FF5A4E" stopOpacity={0.18} />
                  <stop offset="100%" stopColor="#FF5A4E" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#98A2B3' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#98A2B3' }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTip />} />
              <Area type="monotone" dataKey="organic" name="Organic" stroke="#FF5A4E" strokeWidth={2.5} fill="url(#showcase-og)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10 }}>Top Keywords</div>
          <table className="data-table">
            <thead><tr><th>Keyword</th><th>Position</th><th>Volume</th></tr></thead>
            <tbody>
              {TOP_KEYWORDS.map(k => (
                <tr key={k.kw}>
                  <td style={{ fontWeight: 600, color: 'var(--text-1)' }}>{k.kw}</td>
                  <td><span style={{ fontWeight: 700, color: 'var(--green)' }}>#{k.pos}</span></td>
                  <td>{k.vol}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
