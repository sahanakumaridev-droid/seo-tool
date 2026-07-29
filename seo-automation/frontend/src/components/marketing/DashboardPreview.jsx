import { TrendingUp, Search, ShieldCheck, Sparkles } from 'lucide-react'
import { HERO_METRICS } from '../../data/mockData'

const MINI_TRAFFIC = [38, 44, 41, 52, 58, 55, 64, 70, 66, 78, 84, 92]

function MiniChart() {
  const max = Math.max(...MINI_TRAFFIC)
  const points = MINI_TRAFFIC.map((v, i) => {
    const x = (i / (MINI_TRAFFIC.length - 1)) * 100
    const y = 100 - (v / max) * 100
    return `${x},${y}`
  }).join(' ')
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ width: '100%', height: 72 }}>
      <polyline points={`0,100 ${points} 100,100`} fill="rgba(255,90,78,0.10)" stroke="none" />
      <polyline points={points} fill="none" stroke="var(--brand)" strokeWidth="2.2" vectorEffect="non-scaling-stroke" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

const TOP_KEYWORDS = [
  { kw: 'seo services', pos: 3, vol: '12.1K' },
  { kw: 'local seo', pos: 6, vol: '8.1K' },
  { kw: 'seo agency', pos: 8, vol: '6.6K' },
]

function FloatingCard({ icon: Icon, label, value, style, tone = 'brand', floatClass }) {
  const toneColor = { brand: 'var(--brand)', green: 'var(--green)', violet: 'var(--purple)' }[tone]
  return (
    <div
      className={`fade-in ${floatClass}`}
      style={{
        position: 'absolute', display: 'flex', alignItems: 'center', gap: 10,
        background: '#fff', border: '1px solid var(--border)', borderRadius: 14,
        padding: '10px 14px', boxShadow: '0 12px 32px rgba(16,24,40,0.10)',
        ...style,
      }}
    >
      <div style={{ width: 32, height: 32, borderRadius: 9, background: `${toneColor}14`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
        <Icon size={15} style={{ color: toneColor }} />
      </div>
      <div>
        <div style={{ fontSize: 10, color: 'var(--text-3)', lineHeight: 1.2 }}>{label}</div>
        <div style={{ fontSize: 14, fontWeight: 800, color: 'var(--text-1)', lineHeight: 1.2 }}>{value}</div>
      </div>
    </div>
  )
}

export default function DashboardPreview() {
  return (
    <div style={{ position: 'relative', maxWidth: 760, margin: '0 auto', padding: '0 8px' }}>
      {/* Browser-style frame */}
      <div style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: 16, boxShadow: '0 24px 64px rgba(16,24,40,0.12)', overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '10px 16px', borderBottom: '1px solid var(--border)', background: 'var(--bg-raised)' }}>
          <span style={{ width: 9, height: 9, borderRadius: '50%', background: '#F2988D' }} />
          <span style={{ width: 9, height: 9, borderRadius: '50%', background: '#F4CB85' }} />
          <span style={{ width: 9, height: 9, borderRadius: '50%', background: '#9BD3A8' }} />
          <span style={{ marginLeft: 12, fontSize: 11.5, color: 'var(--text-4)' }}>app.zeorbit.com/dashboard</span>
        </div>

        <div style={{ padding: '20px 24px', textAlign: 'left' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-3)' }}>example.com · Last 30 Days</div>
              <div className="font-display" style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-1)' }}>SEO Performance</div>
            </div>
            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--green)', background: 'var(--green-soft)', padding: '4px 10px', borderRadius: 999 }}>▲ 18.4%</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10, marginBottom: 16 }}>
            {[
              { label: 'Organic Traffic', value: '48,291' },
              { label: 'Organic Keywords', value: '3,482' },
              { label: 'Average Position', value: '12.6' },
              { label: 'Backlinks', value: '18,420' },
            ].map(s => (
              <div key={s.label} style={{ border: '1px solid var(--border)', borderRadius: 10, padding: '10px 12px' }}>
                <div style={{ fontSize: 10, color: 'var(--text-3)' }}>{s.label}</div>
                <div style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-1)', marginTop: 2 }}>{s.value}</div>
              </div>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 14 }}>
            <div style={{ border: '1px solid var(--border)', borderRadius: 10, padding: '12px 14px' }}>
              <MiniChart />
            </div>
            <div style={{ border: '1px solid var(--border)', borderRadius: 10, padding: '10px 12px' }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>Top Keywords</div>
              {TOP_KEYWORDS.map(k => (
                <div key={k.kw} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '5px 0', fontSize: 12 }}>
                  <span style={{ color: 'var(--text-2)' }}>{k.kw}</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontWeight: 700, color: 'var(--green)' }}>#{k.pos}</span>
                    <span style={{ color: 'var(--text-4)', fontSize: 11 }}>{k.vol}</span>
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Floating metric cards — each bobs on its own loop (see index.css .float-bob-*) */}
      <FloatingCard icon={TrendingUp} label={HERO_METRICS[0].label} value={HERO_METRICS[0].value} tone="green"
        floatClass="float-bob-1" style={{ top: -30, left: -28 }} />
      <FloatingCard icon={Search} label={HERO_METRICS[1].label} value={HERO_METRICS[1].value} tone="brand"
        floatClass="float-bob-2" style={{ top: 76, right: -36 }} />
      <FloatingCard icon={ShieldCheck} label={HERO_METRICS[2].label} value={HERO_METRICS[2].value} tone="green"
        floatClass="float-bob-3" style={{ bottom: 54, left: -40 }} />
      <FloatingCard icon={Sparkles} label={HERO_METRICS[3].label} value={HERO_METRICS[3].value} tone="violet"
        floatClass="float-bob-4" style={{ bottom: -20, right: -18 }} />
    </div>
  )
}
