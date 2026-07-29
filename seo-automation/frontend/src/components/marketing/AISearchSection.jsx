const ENGINES = ['Google AI Overviews', 'ChatGPT', 'Perplexity', 'Gemini']

const METRICS = [
  { label: 'AI Visibility Score', value: '68%' },
  { label: 'Brand Mentions', value: '142' },
  { label: 'Citation Sources', value: '37' },
  { label: 'Competitor Mentions', value: '89' },
]

const QUERIES = [
  { q: '"best plumber near me"', engine: 'Google AI Overviews', mentioned: true },
  { q: '"how to choose an SEO agency"', engine: 'ChatGPT', mentioned: true },
  { q: '"top local seo tools"', engine: 'Perplexity', mentioned: false },
  { q: '"affordable web design company"', engine: 'Gemini', mentioned: true },
]

export default function AISearchSection() {
  return (
    <div className="card" style={{ padding: 26 }}>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20 }}>
        {ENGINES.map(e => (
          <span key={e} style={{ fontSize: 12, fontWeight: 600, padding: '5px 12px', borderRadius: 999, background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-2)' }}>{e}</span>
        ))}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4" style={{ marginBottom: 22 }}>
        {METRICS.map(m => (
          <div key={m.label} style={{ border: '1px solid var(--border)', borderRadius: 12, padding: '14px 16px' }}>
            <div style={{ fontSize: 12, color: 'var(--text-3)' }}>{m.label}</div>
            <div className="font-display" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-1)', marginTop: 2 }}>{m.value}</div>
          </div>
        ))}
      </div>

      <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10 }}>AI Search Queries</div>
      <table className="data-table">
        <thead><tr><th>Query</th><th>Engine</th><th>Brand mentioned</th></tr></thead>
        <tbody>
          {QUERIES.map(q => (
            <tr key={q.q}>
              <td style={{ color: 'var(--text-1)' }}>{q.q}</td>
              <td style={{ color: 'var(--text-3)' }}>{q.engine}</td>
              <td>
                <span style={{
                  fontSize: 11, fontWeight: 700, padding: '2px 9px', borderRadius: 999,
                  color: q.mentioned ? 'var(--green)' : 'var(--text-4)',
                  background: q.mentioned ? 'var(--green-soft)' : 'var(--bg-raised)',
                }}>
                  {q.mentioned ? 'Mentioned' : 'Not mentioned'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
