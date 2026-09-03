import { useState } from 'react'
import {
  Trophy, Loader2, Search, Target, Link2, MapPin, Bot, Sparkles, ScanSearch, ExternalLink,
} from 'lucide-react'
import { analyzeTop3, inspectTop3Gsc } from '../api'
import './top3-engine.css'

const STATUS = {
  red: { label: 'Gap', color: '#dc2626' },
  amber: { label: 'Watch', color: '#d97706' },
  green: { label: 'OK', color: '#16a34a' },
}

function Bar({ value, color }) {
  return (
    <div className="t3-bar">
      <div className="t3-bar-fill" style={{ width: `${Math.max(0, Math.min(100, value))}%`, background: color }} />
    </div>
  )
}

export default function Top3EnginePage() {
  const [website, setWebsite] = useState('https://zeorbit.com')
  const [keyword, setKeyword] = useState('best web designer in San Diego')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)
  const [gscUrl, setGscUrl] = useState('https://zeorbit.com/web-designer-near-me')
  const [gscLoading, setGscLoading] = useState(false)
  const [gscError, setGscError] = useState('')
  const [gsc, setGsc] = useState(null)

  const run = async (e) => {
    e?.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await analyzeTop3(website, keyword)
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const runGsc = async (e) => {
    e?.preventDefault()
    setGscLoading(true)
    setGscError('')
    try {
      const res = await inspectTop3Gsc(gscUrl)
      setGsc(res.data)
    } catch (err) {
      setGscError(err.response?.data?.detail || err.message || 'Inspection failed')
    } finally {
      setGscLoading(false)
    }
  }

  const pillars = data?.pillars || {}
  const score = data?.top3_score || 0

  return (
    <div className="t3-page">
      <header className="t3-hero">
        <p className="t3-kicker"><Trophy size={14} /> Top 3 SEO Engine</p>
        <h1>What is stopping this site from Top 3 — and what to do next</h1>
        <p className="t3-lead">
          Not a 500-posts/day machine. Audit the SERP, score gaps, pick a few pages worth publishing,
          and measure. Rankings are never guaranteed.
        </p>
        <form className="t3-form" onSubmit={run}>
          <input
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
            placeholder="https://client-site.com"
            required
          />
          <input
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder='Target keyword, e.g. best catering company in Austin'
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? <Loader2 className="t3-spin" size={16} /> : <Search size={16} />}
            Run gap analysis
          </button>
        </form>
        {error && <p className="t3-error">{error}</p>}
      </header>

      <section className="t3-card t3-gsc">
        <h2><ScanSearch size={16} /> Google Search Console — is this URL live?</h2>
        <p className="t3-meta">
          Same check as Search Console → URL inspection. Indexed means Google knows the page.
          It does not mean Top 3 or AI Mode.
        </p>
        <form className="t3-form t3-gsc-form" onSubmit={runGsc}>
          <input
            value={gscUrl}
            onChange={(e) => setGscUrl(e.target.value)}
            placeholder="https://zeorbit.com/web-designer-near-me"
            required
          />
          <button type="submit" disabled={gscLoading}>
            {gscLoading ? <Loader2 className="t3-spin" size={16} /> : <ScanSearch size={16} />}
            Inspect in Google
          </button>
        </form>
        {gscError && <p className="t3-error">{gscError}</p>}
        {gsc && (
          <div className="t3-gsc-result">
            <p className="t3-gsc-verdict">
              {gsc.live_in_google === true && 'Live in Google index'}
              {gsc.live_in_google === false && gsc.gsc_ok && `Not indexed yet — ${gsc.coverage_state || gsc.gsc_status}`}
              {gsc.live_in_google == null && (gsc.gsc_detail || 'Search Console API not connected — use the Google link')}
            </p>
            <ul className="t3-mini">
              <li>HTTP on the live site: {gsc.http_live ? `OK (${gsc.http_status})` : `Issue (${gsc.http_status || gsc.crawl_error || 'fail'})`}</li>
              <li>robots.txt: {gsc.robots_allowed === false ? 'blocked' : 'allowed or unknown'}</li>
              <li>noindex: {gsc.has_noindex ? 'yes (will not index)' : 'no'}</li>
              {gsc.coverage_state ? <li>GSC coverage: {gsc.coverage_state}</li> : null}
              {gsc.verdict ? <li>GSC verdict: {gsc.verdict}</li> : null}
              {gsc.last_crawl_time ? <li>Last Google crawl: {gsc.last_crawl_time}</li> : null}
            </ul>
            <p>
              <a href={gsc.inspect_link} target="_blank" rel="noreferrer">
                Open Search Console URL inspection <ExternalLink size={12} />
              </a>
              {' · '}
              <button
                type="button"
                className="t3-copy"
                onClick={() => navigator.clipboard.writeText(gsc.url)}
              >
                Copy page URL to paste in GSC
              </button>
              {' · '}
              <a href="/indexing">Search Indexing page</a>
            </p>
            <p className="t3-disclaimer">{gsc.howto}</p>
          </div>
        )}
      </section>

      {!data && !loading && (
        <p className="t3-empty">Enter a website and keyword to build the Top 3 roadmap.</p>
      )}

      {data && (
        <>
          {data.you?.crawl_note && (
            <p className="t3-error" style={{ color: '#92400e', background: '#fffbeb', padding: '10px 12px', borderRadius: 10 }}>
              {data.you.crawl_note}
              {data.you.analyzed_url && data.you.analyzed_url !== data.website ? (
                <> Crawled: {data.you.analyzed_url}</>
              ) : null}
            </p>
          )}
          <section className="t3-score-row">
            <div className="t3-score-card">
              <div className="t3-score-num">{score}%</div>
              <div className="t3-score-label">Top 3 readiness</div>
              <p>{data.probability_note}</p>
              <p className="t3-rank">
                Snapshot rank: {data.your_rank ? `#${data.your_rank}` : 'Not in this Top 10'}
              </p>
              <p className="t3-disclaimer">{data.disclaimer}</p>
            </div>
            <div className="t3-pillars">
              {[
                ['Authority', pillars.authority, '#dc2626'],
                ['Content', pillars.content, '#d97706'],
                ['Technical', pillars.technical, '#16a34a'],
                ['Local', pillars.local, '#d97706'],
                ['Brand', pillars.brand, '#dc2626'],
              ].map(([name, val, color]) => (
                <div key={name}>
                  <div className="t3-pillar-label">
                    <span>{name}</span>
                    <strong>{val}/100</strong>
                  </div>
                  <Bar value={val} color={val >= 80 ? '#16a34a' : val >= 60 ? '#d97706' : '#dc2626'} />
                </div>
              ))}
            </div>
            <div className="t3-roadmap">
              <div className="t3-kicker">Estimated path (illustrative)</div>
              <div className="t3-path">{(data.roadmap || []).join(' → ')}</div>
              <p>Re-crawl after each action. Google and competitors still decide the SERP.</p>
            </div>
          </section>

          <section className="t3-card">
            <h2>Top 3 gap</h2>
            <div className="t3-table-wrap">
              <table className="t3-table">
                <thead>
                  <tr>
                    <th>Factor</th>
                    <th>You</th>
                    <th>#1</th>
                    <th>#2</th>
                    <th>#3</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(data.gap_table || []).map((r) => (
                    <tr key={r.factor}>
                      <td>{r.factor}</td>
                      <td>{r.you}</td>
                      <td>{r.c1}</td>
                      <td>{r.c2}</td>
                      <td>{r.c3}</td>
                      <td style={{ color: STATUS[r.status]?.color, fontWeight: 700 }}>
                        {r.status === 'red' ? '🔴' : r.status === 'amber' ? '🟠' : '🟢'} {STATUS[r.status]?.label}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="t3-card">
            <h2>What to do next</h2>
            <ol className="t3-actions">
              {(data.actions || []).map((a, i) => (
                <li key={a}>
                  <span>Priority {i + 1}</span>
                  {a}
                </li>
              ))}
            </ol>
          </section>

          <section className="t3-grid2">
            <div className="t3-card">
              <h2><Search size={16} /> SERP Top 10</h2>
              <p className="t3-meta">{data.serp_source}</p>
              <ol className="t3-serp">
                {(data.serp || []).map((s) => (
                  <li key={s.url}>
                    <strong>#{s.rank} {s.host}</strong>
                    <a href={s.url} target="_blank" rel="noreferrer">{s.title || s.url}</a>
                  </li>
                ))}
              </ol>
              {!data.serp?.length && <p>No public SERP snapshot this run. Gap table still uses your page crawl.</p>}
            </div>
            <div className="t3-card">
              <h2><Target size={16} /> Why they are beating you</h2>
              {(data.why_they_win || []).map((w) => (
                <div key={w.url} className="t3-why">
                  <strong>#{w.rank} {w.host}</strong>
                  <p>{(w.reasons || []).join(' · ')}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="t3-card">
            <h2>Content opportunity engine</h2>
            <p className="t3-funnel">
              Crawl {data.content_funnel?.found} → {data.content_funnel?.relevant} relevant → {data.content_funnel?.high_potential} high potential → {data.content_funnel?.low_competition} low competition → {data.content_funnel?.commercial} commercial → publish {data.content_funnel?.publish_now?.length || 0}
            </p>
            <p><strong>Publish now:</strong> {(data.content_funnel?.publish_now || []).join(' · ') || 'None this pass'}</p>
          </section>

          <section className="t3-grid2">
            <div className="t3-card">
              <h2>Keyword opportunity score</h2>
              {(data.opportunities || []).slice(0, 8).map((o) => (
                <div key={o.keyword} className="t3-kw">
                  <div className="t3-kw-top">
                    <span>{o.keyword}</span>
                    <strong>{o.score}/100 {o.publish ? 'Write now' : 'Skip / later'}</strong>
                  </div>
                  <p>Vol {o.volume}/10 · Comp {o.competition}/10 · Intent {o.intent}/10 · Pos ~{o.position}</p>
                </div>
              ))}
            </div>
            <div className="t3-card">
              <h2>Page 2 → Top 3 (quick wins)</h2>
              {(data.quick_wins || []).map((o) => (
                <div key={o.keyword} className="t3-kw">
                  <div className="t3-kw-top">
                    <span>{o.keyword}</span>
                    <strong>~#{o.position} {'⭐'.repeat(o.stars)}</strong>
                  </div>
                  <p>Optimize page → missing topics → internal links → relevant mentions → recheck</p>
                </div>
              ))}
            </div>
          </section>

          <section className="t3-grid2">
            <div className="t3-card">
              <h2><Link2 size={16} /> Internal links</h2>
              <p>On-page internal links crawled: {data.internal_links?.on_page}</p>
              <ul>
                {(data.internal_links?.recommendations || []).map((x) => <li key={x}>{x}</li>)}
              </ul>
            </div>
            <div className="t3-card">
              <h2>Backlink gap (discovery only)</h2>
              <p>{data.backlink_gap?.note}</p>
              <ul>
                {(data.backlink_gap?.missing || []).map((x) => <li key={x}>✓ {x}</li>)}
              </ul>
            </div>
          </section>

          <section className="t3-grid2">
            <div className="t3-card">
              <h2><MapPin size={16} /> Local Top 3</h2>
              <p>Local query: {data.local?.is_local_query ? 'Yes' : 'Treat as organic'} · Score {data.local?.score}/100</p>
              <ul>
                {(data.local?.checklist || []).map((x) => <li key={x}>{x}</li>)}
              </ul>
            </div>
            <div className="t3-card">
              <h2><Bot size={16} /> AI search visibility</h2>
              <p>{data.ai_visibility?.disclaimer}</p>
              <p>AI readiness {data.ai_visibility?.score}/100 · Schema {data.ai_visibility?.schema ? 'yes' : 'no'} · In this SERP {data.ai_visibility?.serp_presence ? 'yes' : 'no'}</p>
            </div>
          </section>

          {data.visibility && (
            <section className="t3-next">
              <p className="t3-kicker"><Sparkles size={14} /> Next section — 2026</p>
              <h2 className="t3-next-title">AI + Google Visibility</h2>
              <p className="t3-lead">{data.visibility.disclaimer}</p>

              <div className="t3-vis-grid">
                <div className="t3-card">
                  <h3>Google Organic</h3>
                  <p>This keyword in Top 3: {data.visibility.google_organic?.in_top3_this_keyword ? 'Yes' : 'No'}</p>
                  <p>This keyword in Top 10: {data.visibility.google_organic?.in_top10_this_keyword ? 'Yes' : 'No'}</p>
                  <strong>{data.visibility.google_organic?.score}/100</strong>
                </div>
                <div className="t3-card">
                  <h3>Google Maps</h3>
                  <p>{data.visibility.google_maps?.note}</p>
                  <strong>Local visibility {data.visibility.google_maps?.score}/100</strong>
                </div>
                <div className="t3-card">
                  <h3>AI search (readiness)</h3>
                  <ul className="t3-mini">
                    <li>Google AI Mode {data.visibility.ai_search?.google_ai_mode}/100</li>
                    <li>Gemini {data.visibility.ai_search?.gemini}/100</li>
                    <li>ChatGPT {data.visibility.ai_search?.chatgpt}/100</li>
                    <li>Perplexity {data.visibility.ai_search?.perplexity}/100</li>
                  </ul>
                </div>
                <div className="t3-card">
                  <h3>Entity authority</h3>
                  <strong>{data.visibility.entity?.score}/100</strong>
                  <p>Mentions this month (est.) {data.visibility.citations?.brand_mentions_this_month_est} · last month {data.visibility.citations?.brand_mentions_last_month_est}</p>
                  <p>AI citations (est.) {data.visibility.citations?.ai_citations_est}</p>
                </div>
              </div>

              <div className="t3-card">
                <h2>Entity knowledge graph</h2>
                <p className="t3-meta">{(data.visibility.entity?.graph || []).join(' · ')}</p>
                <table className="t3-table">
                  <thead>
                    <tr><th>Property</th><th>Status</th><th>Note</th></tr>
                  </thead>
                  <tbody>
                    {(data.visibility.entity?.consistency || []).map((r) => (
                      <tr key={r.property}>
                        <td>{r.property}</td>
                        <td>{r.status === 'ok' ? '✅' : r.status === 'warn' ? '⚠️' : '🔴'}</td>
                        <td>{r.note}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="t3-grid2">
                <div className="t3-card">
                  <h2>Mention gap</h2>
                  <p>{data.visibility.mention_gap?.why}</p>
                  <p>
                    You: {data.visibility.mention_gap?.you?.reviews_est} reviews · {data.visibility.mention_gap?.you?.referring_domains_est} referring domains (est.) · {data.visibility.mention_gap?.you?.news_mentions_est} news
                  </p>
                  <p>
                    Competitor: {data.visibility.mention_gap?.competitor?.reviews_est} reviews · {data.visibility.mention_gap?.competitor?.referring_domains_est} referring domains (est.) · {data.visibility.mention_gap?.competitor?.news_mentions_est} news
                  </p>
                  <p>Authority gap: you {data.visibility.authority_gap?.you} vs competitors {data.visibility.authority_gap?.competitors}</p>
                </div>
                <div className="t3-card">
                  <h2>Topic ecosystem (query fan-out)</h2>
                  <p>Optimize the cluster, not only the brand name.</p>
                  <ul>
                    {(data.visibility.topic_ecosystem || []).map((t) => <li key={t}>{t}</li>)}
                  </ul>
                </div>
              </div>

              <div className="t3-card">
                <h2>Top 5 visibility actions</h2>
                <ol className="t3-actions">
                  {(data.visibility.top_actions || []).map((a, i) => (
                    <li key={a}><span>{i + 1}</span>{a}</li>
                  ))}
                </ol>
              </div>
            </section>
          )}
        </>
      )}
    </div>
  )
}
