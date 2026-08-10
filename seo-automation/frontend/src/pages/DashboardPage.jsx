import { useNavigate } from 'react-router-dom'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { AlertTriangle, ChevronRight } from 'lucide-react'
import { DASHBOARD_KPIS, SEO_OPPORTUNITIES, ORGANIC_PERFORMANCE } from '../data/mockData'
import ScoreRing from '../components/ScoreRing'
import useProjectInfo from '../hooks/useProjectInfo'

const ChartTip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="card px-3 py-2 text-xs" style={{ boxShadow: 'var(--shadow-md)' }}>
      <div style={{ color: 'var(--text-3)', marginBottom: 4 }}>{label}</div>
      <span style={{ color: 'var(--text-1)', fontWeight: 700 }}>{payload[0].value?.toLocaleString?.() ?? payload[0].value}</span>
    </div>
  )
}

const TONE_DOT = { red: 'var(--red)', amber: 'var(--amber)', green: 'var(--green)' }
const byKey = (key) => DASHBOARD_KPIS.find(k => k.key === key)

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 18) return 'Good afternoon'
  return 'Good evening'
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const project = useProjectInfo()

  const website = project.website || 'example.com'
  const seoHealth = project.audit?.overall_score ?? byKey('seoHealth').value

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 22, maxWidth: 980 }}>
      {/* Header */}
      <div>
        <h1 className="font-display" style={{ fontSize: 26, fontWeight: 800, color: 'var(--text-1)' }}>{greeting()}, {project.business_name || 'there'}</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text-3)' }}>{website} · Last 30 days</p>
      </div>

      {/* Hero: score + headline metrics, secondary stats de-emphasized below */}
      <div className="card p-6 flex items-center gap-8 flex-wrap">
        <ScoreRing score={seoHealth} />
        <div style={{ display: 'flex', gap: 40, flexWrap: 'wrap' }}>
          {['traffic', 'keywords'].map(key => {
            const kpi = byKey(key)
            return (
              <div key={key}>
                <div className="font-display" style={{ fontSize: 32, fontWeight: 800, color: 'var(--text-1)', lineHeight: 1.1 }}>{kpi.value}</div>
                <div className="text-sm mt-1" style={{ color: 'var(--text-3)' }}>{kpi.label}</div>
                <span className="text-xs font-semibold" style={{ color: 'var(--green)' }}>▲ {kpi.delta}</span>
              </div>
            )
          })}
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 28, flexWrap: 'wrap' }}>
          {['backlinks', 'avgPosition', 'aiVisibility'].map(key => {
            const kpi = byKey(key)
            return (
              <div key={key} style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-2)' }}>{kpi.value}</div>
                <div style={{ fontSize: 11.5, color: 'var(--text-4)' }}>{kpi.label}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Traffic trend */}
      <div className="card p-5">
        <h2 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-1)', marginBottom: 16 }}>Organic Traffic</h2>
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={ORGANIC_PERFORMANCE} margin={{ top: 4, right: 8, left: -18, bottom: 0 }}>
            <defs>
              <linearGradient id="og" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#FF5A4E" stopOpacity={0.18} />
                <stop offset="100%" stopColor="#FF5A4E" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
            <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#98A2B3' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: '#98A2B3' }} axisLine={false} tickLine={false} />
            <Tooltip content={<ChartTip />} />
            <Area type="monotone" dataKey="traffic" stroke="#FF5A4E" strokeWidth={2.5} fill="url(#og)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Top opportunities — short, focused list */}
      <div className="card p-5">
        <h2 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-1)', marginBottom: 12 }}>Top Opportunities</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {SEO_OPPORTUNITIES.slice(0, 4).map(o => (
            <button key={o.label} onClick={() => navigate(o.to)}
              className="btn"
              style={{ justifyContent: 'space-between', width: '100%', padding: '10px 8px', background: 'none', border: 'none', textAlign: 'left' }}>
              <span className="flex items-center gap-2" style={{ fontSize: 13.5, color: 'var(--text-2)' }}>
                <AlertTriangle size={14} style={{ color: TONE_DOT[o.tone] }} /> {o.label}
              </span>
              <ChevronRight size={14} style={{ color: 'var(--text-4)' }} />
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
