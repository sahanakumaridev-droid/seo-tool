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

  const website = project.website || ''
  const seoHealth = project.audit?.overall_score ?? byKey('seoHealth').value

  return (
    <div
      className="fade-in dash-overview"
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 14,
        width: '100%',
        maxWidth: 1120,
        minHeight: 'calc(100vh - 78px)',
      }}
    >
      {/* Compact header */}
      <div className="flex items-end justify-between gap-3 flex-wrap">
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-1)', margin: 0, letterSpacing: '-0.02em' }}>
            {greeting()}, {project.business_name || 'there'}
          </h1>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-3)', margin: 0 }}>
            {website || 'Add website in Onboarding'} · Last 30 days
          </p>
        </div>
      </div>

      {/* Main grid — fits at 100% zoom without horizontal sprawl */}
      <div
        className="dash-overview-grid"
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1.05fr) minmax(0, 1.35fr)',
          gap: 14,
          alignItems: 'stretch',
          flex: 1,
        }}
      >
        {/* Left: score + KPIs */}
        <div className="card p-4" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <ScoreRing score={seoHealth} size={88} />
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--text-3)' }}>
                SEO Health
              </div>
              <div style={{ fontSize: 13, color: 'var(--text-2)', marginTop: 4, lineHeight: 1.35 }}>
                Snapshot of traffic, keywords, and visibility for this workspace.
              </div>
            </div>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
              gap: 10,
            }}
          >
            {['traffic', 'keywords', 'backlinks', 'avgPosition', 'aiVisibility'].map(key => {
              const kpi = byKey(key)
              if (!kpi) return null
              return (
                <div
                  key={key}
                  style={{
                    padding: '10px 12px',
                    borderRadius: 10,
                    background: 'var(--bg-raised)',
                    border: '1px solid var(--border)',
                  }}
                >
                  <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-1)', lineHeight: 1.1 }}>
                    {kpi.value}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 3 }}>{kpi.label}</div>
                  {kpi.delta ? (
                    <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--green)', marginTop: 4 }}>▲ {kpi.delta}</div>
                  ) : null}
                </div>
              )
            })}
          </div>
        </div>

        {/* Right: traffic + opportunities stacked to fill height */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14, minWidth: 0 }}>
          <div className="card p-4" style={{ flex: '1 1 auto', minHeight: 0 }}>
            <h2 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-1)', margin: '0 0 10px' }}>Organic Traffic</h2>
            <ResponsiveContainer width="100%" height={168}>
              <AreaChart data={ORGANIC_PERFORMANCE} margin={{ top: 4, right: 6, left: -22, bottom: 0 }}>
                <defs>
                  <linearGradient id="og" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#FF5A4E" stopOpacity={0.18} />
                    <stop offset="100%" stopColor="#FF5A4E" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="month" tick={{ fontSize: 10, fill: '#98A2B3' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: '#98A2B3' }} axisLine={false} tickLine={false} width={36} />
                <Tooltip content={<ChartTip />} />
                <Area type="monotone" dataKey="traffic" stroke="#FF5A4E" strokeWidth={2} fill="url(#og)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="card p-4">
            <h2 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-1)', margin: '0 0 8px' }}>Top Opportunities</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {SEO_OPPORTUNITIES.slice(0, 4).map(o => (
                <button
                  key={o.label}
                  onClick={() => navigate(o.to)}
                  className="btn"
                  style={{
                    justifyContent: 'space-between',
                    width: '100%',
                    padding: '8px 6px',
                    background: 'none',
                    border: 'none',
                    textAlign: 'left',
                  }}
                >
                  <span className="flex items-center gap-2" style={{ fontSize: 12.5, color: 'var(--text-2)' }}>
                    <AlertTriangle size={13} style={{ color: TONE_DOT[o.tone], flexShrink: 0 }} />
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{o.label}</span>
                  </span>
                  <ChevronRight size={13} style={{ color: 'var(--text-4)', flexShrink: 0 }} />
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
