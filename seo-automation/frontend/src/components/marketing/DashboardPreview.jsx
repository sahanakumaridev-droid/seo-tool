import { ArrowUpRight, Globe, MapPin, Sparkles } from 'lucide-react'

const TRAFFIC = [32, 38, 36, 48, 54, 51, 62, 70, 66, 78, 86, 94]
const KEYWORDS = [
  { kw: 'seo services san diego', pos: 2, vol: '12.1K', delta: '+3' },
  { kw: 'local seo agency', pos: 4, vol: '8.4K', delta: '+6' },
  { kw: 'near me plumber', pos: 1, vol: '18.2K', delta: '+1' },
  { kw: 'website design la jolla', pos: 7, vol: '4.6K', delta: '+4' },
]

function Sparkline() {
  const max = Math.max(...TRAFFIC)
  const pts = TRAFFIC.map((v, i) => {
    const x = (i / (TRAFFIC.length - 1)) * 240
    const y = 86 - (v / max) * 72
    return `${x.toFixed(1)},${y.toFixed(1)}`
  })
  const line = pts.join(' ')
  const area = `0,88 ${line} 240,88`
  return (
    <svg viewBox="0 0 240 88" preserveAspectRatio="none" className="rv-dash-spark" aria-hidden>
      <defs>
        <linearGradient id="rvSparkFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#3D8BFF" stopOpacity="0.38" />
          <stop offset="100%" stopColor="#3D8BFF" stopOpacity="0" />
        </linearGradient>
        <linearGradient id="rvSparkStroke" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#3D8BFF" />
          <stop offset="100%" stopColor="#6EC8FF" />
        </linearGradient>
      </defs>
      <polygon points={area} fill="url(#rvSparkFill)" />
      <polyline points={line} fill="none" stroke="url(#rvSparkStroke)" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function HealthRing({ score = 94 }) {
  const r = 28
  const c = 2 * Math.PI * r
  const offset = c * (1 - score / 100)
  return (
    <div className="rv-dash-ring">
      <svg viewBox="0 0 72 72" width="72" height="72">
        <defs>
          <linearGradient id="rvRing" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#3D8BFF" />
            <stop offset="100%" stopColor="#6EC8FF" />
          </linearGradient>
        </defs>
        <circle cx="36" cy="36" r={r} fill="none" stroke="#243044" strokeWidth="6" />
        <circle
          cx="36" cy="36" r={r} fill="none" stroke="url(#rvRing)" strokeWidth="6"
          strokeLinecap="round" strokeDasharray={c} strokeDashoffset={offset}
          transform="rotate(-90 36 36)"
        />
      </svg>
      <strong>{score}</strong>
    </div>
  )
}

export default function DashboardPreview() {
  return (
    <div className="rv-dash" aria-hidden="true">
      <div className="rv-dash-chrome">
        <span className="rv-dash-dot" />
        <span className="rv-dash-dot" />
        <span className="rv-dash-dot" />
        <div className="rv-dash-url">
          <Globe size={11} />
          app.zeorbit.com/dashboard
        </div>
      </div>

      <div className="rv-dash-body">
        <aside className="rv-dash-side">
          <div className="rv-dash-side-mark">Z</div>
          {['Overview', 'Keywords', 'Content', 'Local', 'Ads'].map((item, i) => (
            <span key={item} className={i === 0 ? 'active' : ''}>{item}</span>
          ))}
        </aside>

        <div className="rv-dash-main">
          <div className="rv-dash-head">
            <div>
              <p>Pacific Dental · Last 30 days</p>
              <h3>Visibility command center</h3>
            </div>
            <span className="rv-dash-live"><span /> Live</span>
          </div>

          <div className="rv-dash-kpis">
            <div>
              <span>Organic traffic</span>
              <b>48,291</b>
              <em>+18.4%</em>
            </div>
            <div>
              <span>Keywords in top 10</span>
              <b>1,284</b>
              <em>+92</em>
            </div>
            <div>
              <span>AI citations</span>
              <b>76</b>
              <em>+14</em>
            </div>
            <div className="rv-dash-health">
              <HealthRing />
              <div>
                <span>Site health</span>
                <b>Excellent</b>
              </div>
            </div>
          </div>

          <div className="rv-dash-split">
            <div className="rv-dash-chart">
              <div className="rv-dash-chart-label">
                <span>Organic growth</span>
                <strong>+124%</strong>
              </div>
              <Sparkline />
            </div>
            <div className="rv-dash-keys">
              <div className="rv-dash-chart-label">
                <span>Winning keywords</span>
                <Sparkles size={12} />
              </div>
              {KEYWORDS.map((k) => (
                <div key={k.kw} className="rv-dash-key">
                  <span>{k.kw}</span>
                  <b>#{k.pos}</b>
                  <em>{k.delta}</em>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="rv-dash-float rv-dash-float-a">
        <MapPin size={14} />
        <div>
          <span>Local pack</span>
          <b>#1 in 18 cities</b>
        </div>
      </div>
      <div className="rv-dash-float rv-dash-float-b">
        <ArrowUpRight size={14} />
        <div>
          <span>Indexed pages</span>
          <b>214 live</b>
        </div>
      </div>
    </div>
  )
}
