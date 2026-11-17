import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, Copy, Download, RefreshCw, Save, FileText, Calendar, Layers, CheckCircle2, Search, MapPin, Building2, Hash, Building, Home, Sparkles } from 'lucide-react'
import { generateKeywordBlog, generateKeywordBlogBatch, getGeoAreas, getGeoCities, getGeoCounties, getGeoStates, getPage, getWriteCalendar, getWriteStats, publishToWeb, saveKeywordBlog, zeorbitArticleUrl } from '../api'

function shiftMonth(month, step) {
  const [year, mon] = month.split('-').map(Number)
  const next = new Date(year, mon - 1 + step, 1)
  return `${next.getFullYear()}-${String(next.getMonth() + 1).padStart(2, '0')}`
}

function MonthCalendar({ month, data, onMonth }) {
  const [year, mon] = month.split('-').map(Number)
  const first = new Date(year, mon - 1, 1)
  const days = data?.days || []
  const byDate = Object.fromEntries(days.map((day) => [day.date, day]))
  const cells = [...Array(first.getDay()).fill(null), ...Array.from({ length: new Date(year, mon, 0).getDate() }, (_, index) => index + 1)]
  const label = first.toLocaleString('en-US', { month: 'long', year: 'numeric' })
  return (
    <section className="write-cal" aria-label="Clicks, impressions, and indexed pages">
      <div className="write-cal-head">
        <button type="button" onClick={() => onMonth(shiftMonth(month, -1))} aria-label="Previous month">‹</button>
        <strong>{label}</strong>
        <button type="button" onClick={() => onMonth(shiftMonth(month, 1))} aria-label="Next month">›</button>
      </div>
      <div className="write-cal-week">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((name) => <span key={name}>{name}</span>)}
      </div>
      <div className="write-cal-grid">
        {cells.map((day, index) => {
          if (!day) return <div key={`empty-${index}`} className="write-cal-day is-empty" />
          const key = `${month}-${String(day).padStart(2, '0')}`
          const row = byDate[key] || { clicks: 0, impressions: 0, indexed: 0 }
          return (
            <div key={key} className="write-cal-day">
              <b>{day}</b>
              <span>{row.clicks} clicks</span>
              <span>{row.impressions} impr.</span>
              <span>{row.indexed} indexed</span>
            </div>
          )
        })}
      </div>
      <p className="write-cal-note">Clicks and impressions come from Search Console and usually arrive two days later.</p>
    </section>
  )
}

function plainText(html) {
  const box = document.createElement('div')
  box.innerHTML = (html || '').replace(/<style[\s\S]*?<\/style>/gi, '')
  box.querySelectorAll('h1,h2,h3,p,li').forEach((el) => {
    el.insertAdjacentText('afterend', '\n')
  })
  return (box.innerText || '').replace(/\n{3,}/g, '\n\n').trim()
}

export function stashPreview(blog, batch) {
  const payload = JSON.stringify({ blog, batch })
  try {
    sessionStorage.setItem('zeorbit-write-preview', payload)
  } catch {
    const slim = batch?.created
      ? { ...batch, created: batch.created.map(({ content_html, ...rest }) => rest) }
      : batch
    sessionStorage.setItem('zeorbit-write-preview', JSON.stringify({ blog, batch: slim }))
  }
  if (batch?.created?.length) {
    try {
      sessionStorage.setItem('zeorbit-write-batch', JSON.stringify({ keyword: batch.keyword || '', batch }))
    } catch {
      const slim = { ...batch, created: batch.created.map(({ content_html, ...rest }) => rest) }
      sessionStorage.setItem('zeorbit-write-batch', JSON.stringify({ keyword: batch.keyword || '', batch: slim }))
    }
  }
}

function savedBatch() {
  try {
    const saved = JSON.parse(sessionStorage.getItem('zeorbit-write-batch') || 'null')
    if (saved?.batch?.created?.length) return saved.batch
  } catch {
    /* ignore broken storage */
  }
  try {
    const preview = JSON.parse(sessionStorage.getItem('zeorbit-write-preview') || 'null')
    if (preview?.batch?.created?.length) return preview.batch
  } catch {
    /* ignore broken storage */
  }
  return null
}

export default function KeywordBlogPage() {
  const navigate = useNavigate()
  const [keyword, setKeyword] = useState(() => {
    try {
      const saved = savedBatch()
      return saved?.keyword || ''
    } catch {
      return ''
    }
  })
  const [blog, setBlog] = useState(null)
  const [busy, setBusy] = useState(false)
  const [progress, setProgress] = useState(null)
  const [elapsed, setElapsed] = useState(0)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [editing, setEditing] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [mode, setMode] = useState('single')
  const [uniqueEach, setUniqueEach] = useState(false)
  const [keywordLength, setKeywordLength] = useState('short')
  const [zipCode, setZipCode] = useState('')
  const [locState, setLocState] = useState('California')
  const [locCounty, setLocCounty] = useState('San Diego County')
  const [stateGroups, setStateGroups] = useState([])
  const [countyGroups, setCountyGroups] = useState([])
  const [countyCities, setCountyCities] = useState([])
  const [cityQuery, setCityQuery] = useState('')
  const [cityOpen, setCityOpen] = useState(false)
  const [cityNote, setCityNote] = useState('')
  const [chosenCities, setChosenCities] = useState([])
  const [areas, setAreas] = useState([])
  const [areaQuery, setAreaQuery] = useState('')
  const [areaOpen, setAreaOpen] = useState(false)
  const placeMenuRef = useRef(null)
  const [areaNote, setAreaNote] = useState('')
  const [chosenAreas, setChosenAreas] = useState([])
  const [batch, setBatch] = useState(savedBatch)
  const [shownSlug, setShownSlug] = useState('')
  const [stats, setStats] = useState(null)
  const [calendarMonth, setCalendarMonth] = useState(() => {
    const now = new Date()
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  })
  const [calendar, setCalendar] = useState(null)

  useEffect(() => {
    getWriteStats().then((res) => setStats(res.data || null)).catch(() => setStats(null))
  }, [batch, notice])

  useEffect(() => {
    let cancelled = false
    getWriteCalendar(calendarMonth).then((res) => {
      if (!cancelled) setCalendar(res.data || null)
    }).catch(() => {
      if (!cancelled) setCalendar(null)
    })
    return () => { cancelled = true }
  }, [calendarMonth])

  useEffect(() => {
    if (!busy) return undefined
    setElapsed(0)
    const id = setInterval(() => setElapsed((seconds) => seconds + 1), 1000)
    return () => clearInterval(id)
  }, [busy])

  useEffect(() => {
    if (!cityOpen && !areaOpen) return undefined
    const close = (event) => {
      if (placeMenuRef.current && !placeMenuRef.current.contains(event.target)) {
        setCityOpen(false)
        setAreaOpen(false)
      }
    }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [cityOpen, areaOpen])

  useEffect(() => {
    getGeoStates('United States')
      .then((res) => setStateGroups(res.data?.groups || []))
      .catch(() => setStateGroups([]))
  }, [])

  useEffect(() => {
    if (mode !== 'multiple' || !locState) return
    let cancelled = false
    getGeoCounties('United States', locState)
      .then((res) => {
        if (cancelled) return
        const groups = res.data?.groups || []
        setCountyGroups(groups)
        const all = groups.flatMap((g) => g.counties || [])
        if (locCounty && !all.some((name) => name.toLowerCase() === locCounty.toLowerCase())) {
          setLocCounty(all[0] || '')
        }
      })
      .catch(() => { if (!cancelled) setCountyGroups([]) })
    return () => { cancelled = true }
  }, [mode, locState])

  useEffect(() => {
    if (mode !== 'multiple' || !locState || !locCounty) {
      setCountyCities([])
      return
    }
    let cancelled = false
    setCityNote('Loading cities…')
    getGeoCities('United States', locState, locCounty)
      .then((res) => {
        if (cancelled) return
        setCountyCities(res.data?.cities || [])
        setCityNote('')
      })
      .catch(() => {
        if (!cancelled) {
          setCountyCities([])
          setCityNote('Cities could not be loaded.')
        }
      })
    return () => { cancelled = true }
  }, [mode, locState, locCounty])

  useEffect(() => {
    if (mode !== 'multiple' || !locCounty) {
      setAreas([])
      setAreaNote('')
      return
    }
    let cancelled = false
    setAreaNote('Loading local areas…')
    const cityFilter = chosenCities.map((row) => row.city.toLowerCase())
    getGeoAreas('United States', locState, '', locCounty)
      .then((res) => {
        if (cancelled) return
        const items = res.data?.items || (res.data?.areas || []).map((name) => ({ name, city: '' }))
        const all = items
          .map((item) => ({
            name: item.name || item,
            city: item.city || '',
            state: locState,
            state_name: locState,
          }))
          .filter((item) => item.name)
        const matched = cityFilter.length
          ? all.filter((item) => cityFilter.includes(String(item.city).toLowerCase()))
          : all
        const flat = matched.length ? matched : all
        setAreas(flat)
        setChosenAreas((picked) => picked.filter((item) => flat.some((row) => row.name === item.name && row.city === item.city)))
        if (!all.length) setAreaNote('No local areas for this county yet.')
        else if (cityFilter.length && !matched.length) setAreaNote('Those cities have no separate neighborhoods, so the county list stays open.')
        else setAreaNote('')
      })
      .catch(() => {
        if (!cancelled) {
          setAreas([])
          setAreaNote('Local areas could not be loaded.')
        }
      })
    return () => { cancelled = true }
  }, [mode, locState, locCounty, chosenCities])

  async function generate(nextKeyword = keyword) {
    const value = nextKeyword.trim()
    if (value.length < 2) {
      setError('Enter a keyword.')
      return
    }
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const res = await generateKeywordBlog(value, { keywordLength })
      stashPreview({ ...res.data, entered_keyword: value }, null)
      navigate('/write/preview')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'The article could not be generated.')
    } finally {
      setBusy(false)
    }
  }

  async function generateBatch() {
    if (keyword.trim().length < 2) {
      setError('Enter a keyword.')
      return
    }
    const places = [
      ...chosenCities,
      ...chosenAreas.map((item) => ({
        label: `${item.name}, ${item.city}, ${item.state}`,
        city: item.name,
        state: item.state,
        state_name: item.state_name,
        county: item.city,
      })),
    ]
    if (!places.length) {
      setError('Choose at least one city.')
      return
    }
    if (places.length > 200) {
      setError('Multiple posts can include up to 200 places at a time.')
      return
    }
    setBusy(true)
    setError('')
    setNotice('')
    setBatch(null)
    const rows = places.map((place) => ({ city: place.city, state: 'waiting' }))
    const created = []
    const failed = []
    setProgress({ done: 0, total: places.length, rows })
    try {
      for (let index = 0; index < places.length; index += 1) {
        const place = places[index]
        rows[index] = { city: place.city, state: 'writing' }
        setProgress({ done: created.length, total: places.length, rows: [...rows] })
        let made = []
        let reason = 'This post was not written.'
        for (let attempt = 0; attempt < 3 && !made.length; attempt += 1) {
          try {
            const res = await generateKeywordBlogBatch({
              keyword: keyword.trim(),
              cities: [place],
            })
            made = res.data?.created || []
            reason = res.data?.failed?.[0]?.error || reason
          } catch (err) {
            const detail = err.response?.data?.detail
            reason = typeof detail === 'string' ? detail : reason
          }
        }
        if (made.length) {
          created.push(made[0])
          rows[index] = { city: place.city, state: 'done' }
        } else {
          failed.push({ city: place.city, error: reason })
          rows[index] = { city: place.city, state: 'failed' }
        }
        setProgress({ done: created.length, total: places.length, rows: [...rows] })
      }
      const batch = { keyword: keyword.trim(), requested: places.length, created, failed }
      setBatch(batch)
      if (created.length === places.length && created[0]) {
        stashPreview({ ...created[0], entered_keyword: keyword.trim() }, batch)
        navigate('/write/preview')
        return
      }
      if (created[0]) {
        stashPreview({ ...created[0], entered_keyword: keyword.trim() }, batch)
        setError(`${created.length} of ${places.length} posts were written. ${failed.map((item) => item.city).join(', ')} still need another try.`)
        navigate('/write/preview')
        return
      }
      setError(failed[0]?.error || 'None of the posts could be written.')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'The batch could not be generated.')
    } finally {
      setBusy(false)
    }
  }

  async function copy(text, label) {
    try {
      await navigator.clipboard.writeText(text)
      setNotice(`${label} copied.`)
    } catch {
      setNotice('Copy failed.')
    }
  }

  function download() {
    if (!blog) return
    const blob = new Blob([blog.content_html || ''], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${blog.slug || 'blog'}.html`
    a.click()
    URL.revokeObjectURL(url)
  }

  async function publish() {
    if (!blog) return
    setPublishing(true)
    setError('')
    setNotice('')
    try {
      const res = await publishToWeb({
        title: blog.seo_title || blog.title,
        h1: blog.title,
        slug: blog.slug,
        meta_description: blog.meta_description || blog.title,
        intro: '',
        content: plainText(blog.content_html),
        content_html: blog.content_html,
        cta: 'Talk with ZeOrbit',
        h2s: ['Guide'],
        h3s: [],
        city: '',
        state: '',
        content_type: 'blog',
        business_type: blog.detected_industry || 'ZeOrbit',
        focus_keyword: blog.primary_keyword || blog.keyword,
        keywords: {
          primary: blog.keyword || blog.primary_keyword || blog.title,
          secondary: blog.related_keywords || [],
          long_tail: [],
          near_me: [],
        },
        schema_markup: {},
        faqs: [],
        featured_image_url: '',
        quality_score: 92,
        readability_score: 92,
        keyword_density: 92,
        publishable: true,
      })
      const url = zeorbitArticleUrl(res.data?.public_url || res.data?.slug || blog.slug)
      setNotice(`Published on ZeOrbit: ${url}`)
    } catch (err) {
      const detail = err.response?.data?.detail
      const message = detail?.message || (typeof detail === 'string' ? detail : 'Publish failed.')
      setError(message)
    } finally {
      setPublishing(false)
    }
  }

  async function openPreview(item) {
    setError('')
    if (item.content_html) {
      setBlog(item)
      setEditing(false)
      return
    }
    try {
      const res = await getPage(item.slug)
      const block = res.data?.seo_block || {}
      setBlog({ ...block, slug: item.slug, city: item.city })
      setEditing(false)
    } catch {
      setError('That post could not be opened.')
    }
  }

  function withPlace(text, fromCity, toCity) {
    if (!text || !fromCity || fromCity === toCity) return text || ''
    return text.replace(new RegExp(fromCity.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), toCity)
  }

  async function applyEditToAll() {
    if (!blog || !batch?.created?.length) return
    const fromCity = blog.city || ''
    const next = batch.created.map((item) => ({
      ...item,
      seo_title: withPlace(blog.seo_title, fromCity, item.city),
      meta_description: withPlace(blog.meta_description, fromCity, item.city),
      content_html: withPlace(blog.content_html, fromCity, item.city),
      title: withPlace(blog.title, fromCity, item.city),
    }))
    setBatch({ ...batch, created: next })
    setNotice('Saving this edit on every city…')
    try {
      for (const item of next) await saveKeywordBlog(item)
      setNotice(`Updated ${next.length} posts.`)
    } catch {
      setError('The edit was applied on screen, but saving every post failed.')
    }
  }

  async function save() {
    if (!blog) return
    setNotice('')
    try {
      await saveKeywordBlog(blog)
      setNotice('Draft saved.')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'The draft could not be saved.')
    }
  }

  return (
    <div style={{ maxWidth: 980, margin: '0 auto', padding: '8px 0 48px' }}>
      <div className="write-title">
        <span className="write-mark" aria-hidden="true"><FileText size={18} /></span>
        <div>
          <h1>Generate Blog Posts</h1>
          <p>Each post takes the next template, so the layout and the article both change. Every place you select is included.</p>
        </div>
      </div>
      <div className="write-stats">
        {[
          [FileText, 'Published', stats?.published, ''],
          [Calendar, 'Generated', stats?.yesterday, stats?.yesterday_label ? `Yesterday, ${stats.yesterday_label}` : 'Yesterday'],
          [Calendar, 'Generated', stats?.today, stats?.today_label ? `Today, ${stats.today_label}` : 'Today'],
          [FileText, 'Published', stats?.published_yesterday, stats?.yesterday_label ? `Yesterday, ${stats.yesterday_label}` : 'Yesterday'],
          [FileText, 'Published', stats?.published_today, stats?.today_label ? `Today, ${stats.today_label}` : 'Today'],
          [Calendar, stats?.month_label || 'This month', stats?.month, ''],
          [Layers, 'Crawled', stats?.crawled, ''],
          [CheckCircle2, 'Indexed', stats?.indexed, ''],
          [CheckCircle2, 'Successful', stats?.successful, ''],
        ].map(([Icon, label, count, when]) => (
          <div key={`${label}-${when}`} className="write-stat">
            <Icon size={18} />
            <div>
              <span>{label}{when ? ` - ${when}` : ''}</span>
              <strong>{count ?? '—'}</strong>
            </div>
          </div>
        ))}
      </div>
      <p className="write-tz">Dates are US Pacific time.</p>
      <MonthCalendar month={calendarMonth} data={calendar} onMonth={setCalendarMonth} />
      <div className="write-modes">
        <div className="write-mode-group">
          <span>Post type</span>
          <div>
            {['single', 'multiple'].map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => { setMode(item); setError(''); setNotice('') }}
                className={mode === item ? 'is-on' : ''}
              >
                {item === 'single' ? 'Single post' : 'Multiple posts'}
              </button>
            ))}
          </div>
        </div>
        {mode === 'multiple' ? (
          <div className="write-mode-group">
            <span>Generation mode</span>
            <div>
              <button type="button" onClick={() => setUniqueEach(false)} className={uniqueEach ? '' : 'is-on'}>Fast for every place</button>
              <button type="button" onClick={() => setUniqueEach(true)} className={uniqueEach ? 'is-on' : ''}>SEO: unique article each place</button>
            </div>
          </div>
        ) : null}
      </div>
      <div style={{ display: 'grid', gap: 16 }}>
      <form onSubmit={(e) => { e.preventDefault(); mode === 'single' ? generate() : generateBatch() }} className="write-card">
        <div className="kw-block">
          <div className="kw-head">
            <span className="loc-label"><Search size={16} /> Keyword</span>
            <div className="kw-switch" role="group" aria-label="Keyword length">
              {[['short', 'Short keyword'], ['long', 'Long keyword']].map(([id, label]) => (
                <button
                  key={id}
                  type="button"
                  aria-pressed={keywordLength === id}
                  onClick={() => setKeywordLength(id)}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          <input
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder={keywordLength === 'short' ? 'app development' : 'best app development company in San Diego'}
            aria-label="Keyword or topic"
            className="loc-control"
          />
        </div>
        {mode === 'multiple' ? (
          <div className="loc-form">
            <div className="loc-row">
              <label className="loc-label">
                <MapPin size={16} /> State
                <select
                  className="loc-control"
                  value={locState}
                  onChange={(e) => { setLocState(e.target.value); setLocCounty(''); setChosenCities([]); setChosenAreas([]) }}
                >
                  {stateGroups.flatMap((group) => (group.states || []).map((name) => (
                    <option key={name} value={name}>{name}</option>
                  )))}
                  {!stateGroups.length ? <option value="California">California</option> : null}
                </select>
              </label>
              <label className="loc-label">
                <Building2 size={16} /> County
                <select
                  className="loc-control"
                  value={locCounty}
                  onChange={(e) => { setLocCounty(e.target.value); setChosenCities([]); setChosenAreas([]) }}
                >
                  {countyGroups.flatMap((group) => (group.counties || []).map((name) => (
                    <option key={name} value={name}>{name}</option>
                  )))}
                </select>
              </label>
              <label className="loc-label loc-zip">
                <Hash size={16} /> Zip code
                <input
                  className="loc-control"
                  inputMode="numeric"
                  maxLength={5}
                  pattern="[0-9]{5}"
                  placeholder="92101"
                  value={zipCode}
                  onChange={(e) => setZipCode(e.target.value.replace(/\D/g, '').slice(0, 5))}
                  aria-label="Five digit zip code"
                />
              </label>
            </div>
            <div className="loc-stack" ref={placeMenuRef}>
              <div className="loc-drop">
                <span className="loc-label"><Building size={16} /> City{countyCities.length ? ` · ${countyCities.length}` : ''}</span>
                <button
                  type="button"
                  className="loc-control loc-trigger"
                  onClick={() => { setCityOpen((open) => !open); setAreaOpen(false) }}
                  aria-expanded={cityOpen}
                >
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {chosenCities.length ? `${chosenCities.length} selected` : 'Choose cities'}
                  </span>
                  <span className="loc-chevron" aria-hidden="true" />
                </button>
                {cityOpen ? (
                  <div className="loc-panel">
                    <div className="loc-panel-bar">
                      <input
                        className="loc-search"
                        value={cityQuery}
                        onChange={(e) => setCityQuery(e.target.value)}
                        placeholder={`Search ${locCounty || 'cities'}`}
                        aria-label="Search US cities"
                      />
                      {countyCities.length ? (
                        <button type="button" className="loc-all" onClick={() => setChosenCities(countyCities.map((name) => ({ label: `${name}, ${locState}`, city: name, state: locState, state_name: locState, county: locCounty })))}>
                          Select all
                        </button>
                      ) : null}
                    </div>
                    <div className="loc-scroll">
                      {countyCities.filter((name) => name.toLowerCase().replace(/\s+/g, '').includes(cityQuery.trim().toLowerCase().replace(/\s+/g, ''))).map((name) => {
                        const label = `${name}, ${locState}`
                        const on = chosenCities.some((row) => row.label === label)
                        return (
                          <button
                            key={name}
                            type="button"
                            onClick={() => {
                              setChosenCities((rows) => on ? rows.filter((row) => row.label !== label) : [...rows, { label, city: name, state: locState, state_name: locState, county: locCounty }])
                            }}
                            className={on ? 'loc-option is-on' : 'loc-option'}
                          >
                            <span>{name}</span>
                            <span className="loc-check">{on ? '✓' : ''}</span>
                          </button>
                        )
                      })}
                    </div>
                    {cityNote ? <p className="loc-note is-error">{cityNote}</p> : null}
                  </div>
                ) : null}
              </div>
              <div className="loc-drop">
                <span className="loc-label"><Home size={16} /> Local area{areas.length ? ` · ${areas.length}` : ''}</span>
                <button
                  type="button"
                  className="loc-control loc-trigger"
                  onClick={() => { setAreaOpen((open) => !open); setCityOpen(false) }}
                  aria-expanded={areaOpen}
                >
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {chosenAreas.length ? `${chosenAreas.length} selected` : 'Choose neighborhoods'}
                  </span>
                  <span className="loc-chevron" aria-hidden="true" />
                </button>
                {areaOpen ? (
                  <div className="loc-panel">
                    <div className="loc-panel-bar">
                      <input
                        className="loc-search"
                        value={areaQuery}
                        onChange={(e) => setAreaQuery(e.target.value)}
                        placeholder="Search neighborhoods"
                        aria-label="Search local areas"
                      />
                      {areas.length ? (
                        <button type="button" className="loc-all" onClick={() => setChosenAreas(areas)}>
                          Select all
                        </button>
                      ) : null}
                    </div>
                    <div className="loc-scroll">
                      {areas.filter((item) => `${item.name} ${item.city}`.toLowerCase().includes(areaQuery.trim().toLowerCase())).map((item) => {
                        const on = chosenAreas.some((row) => row.name === item.name && row.city === item.city)
                        return (
                          <button
                            key={`${item.city}-${item.name}`}
                            type="button"
                            onClick={() => {
                              setChosenAreas((rows) => on
                                ? rows.filter((row) => !(row.name === item.name && row.city === item.city))
                                : [...rows, item])
                            }}
                            className={on ? 'loc-option is-on' : 'loc-option'}
                          >
                            <span>{item.name} <span className="loc-muted">· {item.city}</span></span>
                            <span className="loc-check">{on ? '✓' : ''}</span>
                          </button>
                        )
                      })}
                    </div>
                    {areaNote ? <p className="loc-note">{areaNote}</p> : null}
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        ) : null}
        <button type="submit" disabled={busy} className="loc-submit">
          {busy ? <Loader2 size={16} className="blog-spin" /> : <Sparkles size={16} />}
          {busy && progress ? `${progress.done} of ${progress.total}` : 'Generate'}
        </button>
        {busy && progress ? (
          <p className="loc-time" role="status">
            {clock(elapsed)} elapsed
            {' · '}
            about 3:00 left
            {progress.rows.find((row) => row.state === 'writing') ? ` · ${progress.rows.find((row) => row.state === 'writing').city}` : ''}
          </p>
        ) : null}
        <style>{`
          .write-title { display: flex; gap: 12px; align-items: flex-start; margin-bottom: 16px; }
          .write-title h1 { margin: 0; font-size: 28px; letter-spacing: -0.03em; }
          .write-title p { margin: 4px 0 0; color: #6b7280; font-size: 14px; }
          .write-mark { width: 36px; height: 36px; border-radius: 10px; background: #ecfdf3; color: #16a34a; display: grid; place-items: center; flex: none; }
          .write-stats { display: flex; align-items: center; gap: 0; background: #f3faf4; border-radius: 16px; padding: 14px 8px; margin-bottom: 6px; overflow-x: auto; }
          .write-tz { margin: 0 0 14px; color: #6b7280; font-size: 12px; }
          .write-cal { border: 1px solid #e5e7eb; border-radius: 12px; padding: 8px; margin-bottom: 14px; background: #fff; }
          .write-cal-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; font-size: 14px; }
          .write-cal-head button { width: 24px; height: 24px; border: 0; border-radius: 999px; background: #f3f4f6; cursor: pointer; font-size: 14px; }
          .write-cal-week, .write-cal-grid { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 3px; }
          .write-cal-week span { color: #6b7280; font-size: 10px; font-weight: 650; padding: 0 2px 2px; }
          .write-cal-day { min-height: 46px; border-radius: 6px; background: #f8faf8; padding: 3px 4px; display: grid; align-content: start; gap: 0; }
          .write-cal-day.is-empty { background: transparent; }
          .write-cal-day b { font-size: 11px; }
          .write-cal-day span { color: #3f3f46; font-size: 9px; line-height: 1.2; }
          .write-cal-note { margin: 6px 0 0; color: #6b7280; font-size: 11px; }
          .write-stat { display: flex; align-items: center; gap: 10px; color: #16a34a; padding: 0 18px; border-left: 1px solid #d9f0df; min-width: max-content; }
          .write-stat:first-child { border-left: 0; }
          .write-stat span { display: block; color: #6b7280; font-size: 13px; font-weight: 600; }
          .write-stat strong { display: block; color: #111; font-size: 20px; letter-spacing: -0.03em; }
          .write-modes { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 28px; margin-bottom: 14px; }
          .write-mode-group { display: grid; gap: 8px; }
          .write-mode-group > span { color: #6b7280; font-size: 13px; font-weight: 650; }
          .write-mode-group > div { display: flex; gap: 8px; }
          .write-mode-group button { border: 1px solid #e5e7eb; background: #fff; color: #111; border-radius: 999px; padding: 8px 14px; font-weight: 650; cursor: pointer; }
          .write-mode-group button.is-on { background: #111; color: #fff; border-color: #111; }
          .write-card { display: grid; gap: 14px; border: 1px solid #e5e7eb; border-radius: 18px; padding: 16px; background: #fff; }
          .kw-block { display: grid; gap: 8px; }
          .kw-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
          .kw-switch { display: inline-flex; padding: 3px; border-radius: 999px; background: #f3f4f6; }
          .kw-switch button { border: 0; background: transparent; color: #3f3f46; border-radius: 999px; padding: 6px 12px; font-size: 13px; font-weight: 650; cursor: pointer; }
          .kw-switch button[aria-pressed="true"] { background: #111; color: #fff; }
          .loc-form { display: grid; gap: 12px; }
          .loc-row, .loc-stack { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
          @media (max-width: 720px) {
            .loc-row, .loc-stack { grid-template-columns: 1fr; }
            .kw-head { align-items: flex-start; flex-direction: column; }
          }
          .loc-zip { grid-column: 1 / -1; }
          .loc-label { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 700; color: #111; }
          label.loc-label, .loc-drop > .loc-label { display: grid; grid-template-columns: auto 1fr; align-items: center; }
          label.loc-label > .loc-control, .loc-drop > .loc-label + .loc-control { grid-column: 1 / -1; }
          .loc-control { width: 100%; height: 52px; border: 0; border-radius: 14px; background: #f3f4f6; color: #111; padding: 0 16px; font-size: 16px; }
          select.loc-control { appearance: none; background-image: linear-gradient(45deg, transparent 50%, #6b7280 50%), linear-gradient(135deg, #6b7280 50%, transparent 50%); background-position: calc(100% - 18px) 24px, calc(100% - 12px) 24px; background-size: 6px 6px, 6px 6px; background-repeat: no-repeat; padding-right: 36px; }
          .loc-trigger { display: flex; align-items: center; justify-content: space-between; cursor: pointer; text-align: left; }
          .loc-chevron { width: 8px; height: 8px; border-right: 2px solid #6b7280; border-bottom: 2px solid #6b7280; transform: rotate(45deg); margin-right: 4px; flex: none; }
          .loc-drop { position: relative; display: grid; gap: 8px; }
          .loc-panel { position: absolute; z-index: 30; left: 0; right: 0; top: calc(100% + 6px); background: #fff; border-radius: 14px; box-shadow: 0 16px 40px rgba(17, 17, 17, 0.12); overflow: hidden; }
          .loc-panel-bar { display: flex; gap: 8px; align-items: center; padding: 8px; background: #fff; }
          .loc-search { flex: 1; height: 40px; border: 0; border-radius: 10px; background: #f3f4f6; padding: 0 12px; font-size: 15px; }
          .loc-all { border: 0; background: transparent; color: #16a34a; font-size: 14px; font-weight: 700; cursor: pointer; white-space: nowrap; }
          .loc-scroll { max-height: 280px; overflow-y: auto; }
          .loc-option { width: 100%; display: flex; justify-content: space-between; gap: 8px; text-align: left; border: 0; border-top: 1px solid #f3f4f6; background: #fff; padding: 12px 16px; font-size: 15px; cursor: pointer; }
          .loc-option.is-on { background: #f3faf4; }
          .loc-check { color: #16a34a; font-weight: 700; }
          .loc-muted { color: #6b7280; }
          .loc-note { margin: 0; padding: 8px 16px 12px; color: #6b7280; font-size: 13px; }
          .loc-note.is-error { color: #b42318; }
          .loc-submit { width: 100%; border: 0; border-radius: 14px; background: #16a34a; color: #fff; min-height: 52px; padding: 0 18px; font-size: 16px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; gap: 8px; cursor: pointer; }
          .loc-submit:disabled { opacity: 0.6; cursor: default; }
          .loc-time { margin: 0; color: #3f3f46; font-size: 14px; font-weight: 650; }
          .blog-spin { animation: blog-spin 0.8s linear infinite; }
          @keyframes blog-spin { to { transform: rotate(360deg); } }
          .blog-writing { display: grid; gap: 10px; padding: 16px; border: 1px solid #e6e6e8; border-radius: 12px; background: #fafafa; }
          .blog-writing p { margin: 0; font-size: 14px; color: #334155; }
          .blog-writing-bar { height: 4px; border-radius: 999px; background: #16a34a; }
          .blog-progress { list-style: none; margin: 0; padding: 0; max-height: 280px; overflow: auto; display: grid; gap: 6px; }
          .blog-progress li { display: flex; justify-content: space-between; gap: 12px; font-size: 14px; padding: 8px 10px; border-radius: 10px; background: #fff; }
          .blog-progress .is-writing { background: #f3faf4; }
          .blog-progress .is-done span:last-child { color: #16a34a; font-weight: 700; }
          .blog-progress .is-failed span:last-child { color: #b42318; font-weight: 700; }
          .blog-progress .is-waiting span:last-child { color: #6b7280; }
          .blog-writing-line { display: block; height: 12px; border-radius: 999px; background: #e7e7ea; animation: blog-pulse 1.4s ease-in-out infinite; }
          .blog-writing-line.is-short { width: 68%; }
          @keyframes blog-bar { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }
          @keyframes blog-pulse { 0%, 100% { opacity: 0.45; } 50% { opacity: 1; } }
          @media (prefers-reduced-motion: reduce) {
            .blog-spin, .blog-writing-bar, .blog-writing-line { animation: none; }
          }
        `}</style>
      </form>
      </div>
      {error ? <p style={{ color: '#b42318', marginTop: 12 }}>{error}</p> : null}
      {notice ? <p style={{ color: '#067647', marginTop: 12 }}>{notice}</p> : null}
      {batch?.created?.length ? (
        <section style={{ marginTop: 20, display: 'grid', gap: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
            <h2 style={{ margin: 0, fontSize: 18 }}>Previous posts ({batch.created.length})</h2>
            <button
              type="button"
              onClick={() => {
                sessionStorage.removeItem('zeorbit-write-batch')
                sessionStorage.removeItem('zeorbit-write-preview')
                setBatch(null)
              }}
              style={btn}
            >
              Clear
            </button>
          </div>
          {batch.created.map((item) => (
            <article key={item.slug} style={{ border: '1px solid #e6e6e8', borderRadius: 12, padding: 12 }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <strong>{item.city ? `${item.city}${item.state ? `, ${item.state}` : ''}` : item.title}</strong>
                  <div style={{ fontSize: 13, color: '#64748b', marginTop: 4 }}>/{String(item.slug || '').replace(/^\/?blog\/?/i, '')}</div>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button type="button" onClick={() => { stashPreview({ ...item, entered_keyword: item.entered_keyword || batch?.keyword || '' }, batch); navigate('/write/preview') }} style={btn}>Preview</button>
                  <button type="button" onClick={() => setShownSlug((current) => current === item.slug ? '' : item.slug)} style={btn}>
                    {shownSlug === item.slug ? 'Hide' : 'Show'}
                  </button>
                </div>
              </div>
              {shownSlug === item.slug ? (
                <div className="blog-html" style={{ marginTop: 12, fontSize: 15, lineHeight: 1.6 }} dangerouslySetInnerHTML={{ __html: item.content_html || '' }} />
              ) : null}
            </article>
          ))}
        </section>
      ) : null}
    </div>
  )
}

const field = { border: '1px solid #d6d6d8', borderRadius: 10, padding: '12px 14px', fontSize: 15, background: '#fff' }

function clock(seconds) {
  const total = Math.max(0, Math.round(seconds))
  const hours = Math.floor(total / 3600)
  const minutes = Math.floor((total % 3600) / 60)
  const secs = total % 60
  if (hours) return `${hours}h ${minutes}m`
  return `${minutes}:${String(secs).padStart(2, '0')}`
}
const btn = {
  border: '1px solid #d6d6d8', background: '#fff', borderRadius: 8, padding: '8px 12px',
  display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 600, cursor: 'pointer',
}
const card = { background: '#f6f6f7', borderRadius: 12, padding: 16 }
const kicker = { fontSize: 12, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#64748b', fontWeight: 700 }
