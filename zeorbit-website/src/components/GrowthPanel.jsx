const DEFAULT_METRICS = [
  { label: 'Crash-free', value: '99.8%' },
  { label: 'Funnel lift', value: '+24%' },
  { label: 'Store rating', value: '4.9' },
  { label: 'Time to signal', value: '7d' },
]

export default function GrowthPanel({ metrics = DEFAULT_METRICS }) {
  const items = metrics.length ? metrics : DEFAULT_METRICS

  return (
    <div className="wds-growth-media wds-growth-panel" aria-hidden="true">
      <div className="wds-growth-panel-bar">
        <span>Live product</span>
        <b>Healthy</b>
      </div>
      <div className="wds-growth-panel-grid">
        {items.map((item) => (
          <div key={item.label} className="wds-growth-stat">
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </div>
        ))}
      </div>
    </div>
  )
}
