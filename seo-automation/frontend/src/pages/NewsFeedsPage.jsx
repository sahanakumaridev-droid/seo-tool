import { useEffect, useState } from 'react'
import { addNewsFeed, hideNewsArticle, listNewsArticles, listNewsFeeds, syncNews, syncNewsFeed, updateNewsFeed } from '../api'

const EMPTY = { name: '', url: '', filter_software: true, enabled: true }

function when(iso) {
  if (!iso) return 'Not synced yet'
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return 'Not synced yet'
  return date.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' })
}

export default function NewsFeedsPage() {
  const [feeds, setFeeds] = useState([])
  const [articles, setArticles] = useState([])
  const [form, setForm] = useState(EMPTY)
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)

  async function load() {
    const [feedRes, articleRes] = await Promise.all([listNewsFeeds(), listNewsArticles()])
    setFeeds(feedRes.data.feeds || [])
    setArticles(articleRes.data.articles || [])
  }

  useEffect(() => {
    load().catch(() => setMessage('Could not load news feeds.'))
  }, [])

  async function saveFeed(event) {
    event.preventDefault()
    setBusy(true)
    setMessage('')
    try {
      await addNewsFeed(form)
      setForm(EMPTY)
      await load()
      setMessage('Feed saved. Use Sync now to pull stories.')
    } catch (err) {
      setMessage(err?.response?.data?.detail || 'Could not save that feed.')
    } finally {
      setBusy(false)
    }
  }

  async function toggle(feed, patch) {
    await updateNewsFeed(feed.id, { ...feed, ...patch })
    await load()
  }

  async function syncAll() {
    setBusy(true)
    setMessage('')
    try {
      const { data } = await syncNews()
      const added = (data.results || []).reduce((sum, row) => sum + (row.added || 0), 0)
      setMessage(`Sync finished. ${added} new stories.`)
      await load()
    } catch {
      setMessage('Sync failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="crm-page" style={{ display: 'grid', gap: 22 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-end' }}>
        <div>
          <h1 style={{ margin: 0 }}>News feeds</h1>
          <p style={{ margin: '8px 0 0', color: 'var(--text-3)', maxWidth: 640, lineHeight: 1.5 }}>
            Software and design sources for zeorbit.com/news. Stories are short summaries that link to the original article. The ZeOrbit blog is separate.
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={syncAll} disabled={busy}>
          {busy ? 'Syncing…' : 'Sync now'}
        </button>
      </div>
      {message ? <p style={{ margin: 0 }}>{message}</p> : null}

      <form onSubmit={saveFeed} style={{ display: 'grid', gridTemplateColumns: '1.1fr 1.6fr auto auto', gap: 10, alignItems: 'end' }}>
        <label style={{ display: 'grid', gap: 6 }}>
          <span style={{ fontSize: 12, fontWeight: 650 }}>Publisher</span>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        </label>
        <label style={{ display: 'grid', gap: 6 }}>
          <span style={{ fontSize: 12, fontWeight: 650 }}>RSS URL</span>
          <input value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} required />
        </label>
        <label style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: 13, paddingBottom: 10 }}>
          <input type="checkbox" checked={form.filter_software} onChange={(e) => setForm({ ...form, filter_software: e.target.checked })} />
          Software only
        </label>
        <button type="submit" className="btn btn-secondary" disabled={busy}>Add feed</button>
      </form>

      <div style={{ display: 'grid', gap: 10 }}>
        {feeds.map((feed) => (
          <article key={feed.id} style={{ border: '1px solid var(--border)', borderRadius: 12, padding: 14, display: 'grid', gap: 6 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
              <strong>{feed.name}</strong>
              <span style={{ fontSize: 12, color: feed.last_status === 'ok' ? '#067647' : '#9a6700' }}>
                {feed.last_status === 'ok' ? 'Synced' : feed.last_status === 'error' ? 'Failed' : 'Waiting'}
              </span>
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-3)', wordBreak: 'break-all' }}>{feed.url}</div>
            <div style={{ fontSize: 13, color: 'var(--text-2)' }}>
              Last success check: {when(feed.last_synced_at)} · {feed.last_added || 0} new
              {feed.last_error ? ` · ${feed.last_error}` : ''}
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button type="button" className="btn btn-secondary" onClick={() => toggle(feed, { enabled: !feed.enabled })}>
                {feed.enabled ? 'Disable' : 'Enable'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => toggle(feed, { filter_software: !feed.filter_software })}>
                {feed.filter_software ? 'Industry filter on' : 'Take every story'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={async () => { await syncNewsFeed(feed.id); await load() }}>
                Sync this feed
              </button>
            </div>
          </article>
        ))}
      </div>

      <div>
        <h2 style={{ fontSize: 18 }}>Recent stories</h2>
        <div style={{ display: 'grid', gap: 8 }}>
          {articles.map((article) => (
            <div key={article.id} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontWeight: 650 }}>{article.title}</div>
                <div style={{ fontSize: 12, color: 'var(--text-3)' }}>{article.source_name} · {article.hidden ? 'Hidden' : 'On the news page'}</div>
              </div>
              <button type="button" className="btn btn-secondary" onClick={async () => { await hideNewsArticle(article.id); await load() }}>
                {article.hidden ? 'Show' : 'Hide'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
