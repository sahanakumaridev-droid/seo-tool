import { useEffect, useState } from 'react'
import { getPublishServers, savePublishServers, testPublishServers } from '../api'

const EMPTY = {
  zeorbit_url: 'https://zeorbit.com',
  wp_url: '',
  wp_username: '',
  wp_app_password: '',
  wp_seo_plugin: 'rankmath',
  shopify_store: '',
  shopify_access_token: '',
  shopify_blog_id: '',
}

function Status({ ready, label }) {
  return (
    <span style={{
      fontSize: 12,
      fontWeight: 650,
      color: ready ? '#067647' : '#9a6700',
      background: ready ? '#ecfdf3' : '#fff8eb',
      borderRadius: 999,
      padding: '3px 8px',
    }}>
      {label}
    </span>
  )
}

function Field({ label, children }) {
  return (
    <label style={{ display: 'grid', gap: 6 }}>
      <span className="block text-xs font-semibold" style={{ color: 'var(--text-3)' }}>{label}</span>
      {children}
    </label>
  )
}

export default function CustomPluginPage() {
  const [form, setForm] = useState(EMPTY)
  const [saved, setSaved] = useState({ wordpress_ready: false, shopify_ready: false, zeorbit_ready: false })
  const [checks, setChecks] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [message, setMessage] = useState('')

  const set = (key) => (event) => setForm((prev) => ({ ...prev, [key]: event.target.value }))

  useEffect(() => {
    getPublishServers()
      .then((res) => {
        const data = res.data || {}
        setSaved(data)
        setForm((prev) => ({
          ...prev,
          zeorbit_url: data.zeorbit_url || prev.zeorbit_url,
          wp_url: data.wp_url || '',
          wp_username: data.wp_username || '',
          wp_seo_plugin: data.wp_seo_plugin || 'rankmath',
          shopify_store: data.shopify_store || '',
          shopify_blog_id: data.shopify_blog_id || '',
        }))
      })
      .catch((err) => {
        const detail = err.response?.data?.detail
        setMessage(typeof detail === 'string' ? detail : 'Could not load the saved servers.')
      })
      .finally(() => setLoading(false))
  }, [])

  async function save(event) {
    event.preventDefault()
    setSaving(true)
    setMessage('')
    try {
      const res = await savePublishServers(form)
      setSaved(res.data)
      setChecks(res.data.checks || null)
      setForm((prev) => ({ ...prev, wp_app_password: '', shopify_access_token: '' }))
      setMessage('Saved. Publish now uses these servers.')
    } catch (err) {
      const detail = err.response?.data?.detail
      setMessage(typeof detail === 'string' ? detail : 'The servers could not be saved.')
    } finally {
      setSaving(false)
    }
  }

  async function test() {
    setTesting(true)
    setMessage('')
    try {
      const res = await testPublishServers()
      setChecks(res.data.checks || null)
    } catch (err) {
      const detail = err.response?.data?.detail
      setMessage(typeof detail === 'string' ? detail : 'The connection test did not finish.')
    } finally {
      setTesting(false)
    }
  }

  return (
    <form className="crm-page fade-in" onSubmit={save}>
      <div className="crm-head">
        <div>
          <h1>Custom Plugin</h1>
          <p>Server details for the main site, WordPress, and Shopify. Publish uses what you save here.</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button type="button" className="btn btn-secondary" onClick={test} disabled={loading || testing || saving}>
            {testing ? 'Checking…' : 'Test connections'}
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading || saving}>
            {saving ? 'Saving…' : 'Save servers'}
          </button>
        </div>
      </div>

      {message ? <p style={{ margin: 0, fontSize: 13, color: '#1d1d1f' }}>{message}</p> : null}

      <section className="card" style={{ padding: 16, display: 'grid', gap: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
          <h2 style={{ margin: 0, fontSize: 16 }}>ZeOrbit</h2>
          <Status ready={saved.zeorbit_ready} label={saved.zeorbit_ready ? 'Ready' : 'Needs a URL'} />
        </div>
        <Field label="Main site URL">
          <input value={form.zeorbit_url} onChange={set('zeorbit_url')} placeholder="https://zeorbit.com" autoComplete="off" />
        </Field>
        {checks?.zeorbit ? <p style={{ margin: 0, fontSize: 13, color: '#6e6e73' }}>{checks.zeorbit.detail}</p> : null}
      </section>

      <section className="card" style={{ padding: 16, display: 'grid', gap: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
          <h2 style={{ margin: 0, fontSize: 16 }}>WordPress</h2>
          <Status ready={saved.wordpress_ready} label={saved.wordpress_ready ? 'Connected' : 'Not connected'} />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
          <Field label="Site URL">
            <input value={form.wp_url} onChange={set('wp_url')} placeholder="https://zeorbit.com" autoComplete="off" />
          </Field>
          <Field label="Username">
            <input value={form.wp_username} onChange={set('wp_username')} placeholder="WordPress login" autoComplete="off" />
          </Field>
          <Field label="Application password">
            <input
              type="password"
              value={form.wp_app_password}
              onChange={set('wp_app_password')}
              placeholder={saved.wp_password_set ? 'Saved. Type a new one to replace it.' : 'xxxx xxxx xxxx xxxx'}
              autoComplete="new-password"
            />
          </Field>
          <Field label="SEO plugin">
            <select value={form.wp_seo_plugin} onChange={set('wp_seo_plugin')}>
              <option value="rankmath">Rank Math</option>
              <option value="yoast">Yoast</option>
              <option value="aioseo">All in One SEO</option>
            </select>
          </Field>
        </div>
        <p style={{ margin: 0, fontSize: 12, color: '#6e6e73' }}>
          Use an application password from WordPress → Users → Profile → Application Passwords. Leave the password blank to keep the one already saved.
        </p>
        {checks?.wordpress ? <p style={{ margin: 0, fontSize: 13, color: '#1d1d1f' }}>{checks.wordpress.detail}</p> : null}
      </section>

      <section className="card" style={{ padding: 16, display: 'grid', gap: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
          <h2 style={{ margin: 0, fontSize: 16 }}>Shopify</h2>
          <Status ready={saved.shopify_ready} label={saved.shopify_ready ? 'Connected' : 'Not connected'} />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
          <Field label="Store">
            <input value={form.shopify_store} onChange={set('shopify_store')} placeholder="your-store.myshopify.com" autoComplete="off" />
          </Field>
          <Field label="Admin API access token">
            <input
              type="password"
              value={form.shopify_access_token}
              onChange={set('shopify_access_token')}
              placeholder={saved.shopify_token_set ? 'Saved. Type a new one to replace it.' : 'shpat_…'}
              autoComplete="new-password"
            />
          </Field>
          <Field label="Blog ID">
            <input value={form.shopify_blog_id} onChange={set('shopify_blog_id')} placeholder="Optional. First blog is used if empty." autoComplete="off" />
          </Field>
        </div>
        <p style={{ margin: 0, fontSize: 12, color: '#6e6e73' }}>
          In Shopify: Settings → Apps and sales channels → Develop apps. The app needs read_content and write_content.
        </p>
        {checks?.shopify ? <p style={{ margin: 0, fontSize: 13, color: '#1d1d1f' }}>{checks.shopify.detail}</p> : null}
      </section>
    </form>
  )
}
