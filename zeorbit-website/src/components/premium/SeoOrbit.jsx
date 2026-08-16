import Logo from '../Logo'

const INNER = ['Google', 'Maps', 'YouTube', 'Bing', 'GBP']
const OUTER = [
  'Local SEO',
  'Technical SEO',
  'PPC',
  'Content',
  'Schema',
  'Rankings',
  'Keywords',
  'Analytics',
  'AI Search',
]

function OrbitTrack({ items, ring }) {
  const step = 360 / items.length
  return (
    <div className={`cz-seo-orbit-track is-${ring}`}>
      {items.map((label, i) => {
        const angle = step * i
        return (
          <span
            key={label}
            className="cz-seo-orbit-slot"
            style={{ '--a': `${angle}deg`, '--unspin': `${-angle}deg` }}
          >
            <span className="cz-seo-orbit-tag">{label}</span>
          </span>
        )
      })}
    </div>
  )
}

export default function SeoOrbit() {
  return (
    <div
      className="cz-seo-orbit"
      role="img"
      aria-label="ZeOrbit at the center of search: Google, Maps, local SEO, PPC, content, and AI search"
    >
      <span className="cz-seo-orbit-ring is-a" aria-hidden="true" />
      <span className="cz-seo-orbit-ring is-b" aria-hidden="true" />
      <span className="cz-seo-orbit-ring is-c" aria-hidden="true" />

      <OrbitTrack items={INNER} ring="inner" />
      <OrbitTrack items={OUTER} ring="outer" />

      <div className="cz-seo-orbit-hub">
        <Logo size={48} className="cz-seo-orbit-logo" />
      </div>
    </div>
  )
}
