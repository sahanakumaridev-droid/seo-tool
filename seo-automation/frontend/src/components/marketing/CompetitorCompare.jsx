const COLS = [
  { name: 'Your Site', domain: 'example.com', highlight: true },
  { name: 'Competitor A', domain: 'sdplumbing.com' },
  { name: 'Competitor B', domain: 'plumbersandiego.net' },
]

const ROWS = [
  { label: 'Organic Traffic', values: ['48.2K', '42.8K', '31.2K'] },
  { label: 'Keywords',        values: ['3,482', '1,840', '1,420'] },
  { label: 'Backlinks',       values: ['18.4K', '9.6K', '7.1K'] },
  { label: 'Domain Authority',values: ['46', '42', '38'] },
  { label: 'Content Gaps',    values: ['—', '312 keywords', '428 keywords'] },
  { label: 'Top Pages',       values: ['24 ranking #1–3', '18 ranking #1–3', '11 ranking #1–3'] },
]

export default function CompetitorCompare() {
  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <table className="data-table" style={{ minWidth: 560 }}>
        <thead>
          <tr>
            <th>Metric</th>
            {COLS.map(c => (
              <th key={c.name} style={{ color: c.highlight ? 'var(--brand)' : undefined }}>
                {c.name}<br />
                <span style={{ fontWeight: 400, textTransform: 'none', letterSpacing: 0, color: 'var(--text-4)' }}>{c.domain}</span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ROWS.map(r => (
            <tr key={r.label}>
              <td style={{ fontWeight: 600, color: 'var(--text-2)' }}>{r.label}</td>
              {r.values.map((v, i) => (
                <td key={i} style={{ fontWeight: i === 0 ? 700 : 500, color: i === 0 ? 'var(--text-1)' : 'var(--text-3)' }}>{v}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
