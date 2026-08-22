import { useEffect, useMemo, useState } from 'react'

/** Free OpenStreetMap + Nominatim map of selected places (no Google billing). */
export default function LocationMap({ places = [], city = 'Chula Vista, CA' }) {
  const query = useMemo(() => {
    const first = (places[0] || city || 'San Diego, CA').split('(')[0].trim()
    return first.includes(',') ? first : `${first}, San Diego County, CA`
  }, [places, city])

  const [view, setView] = useState({ lat: 32.6401, lon: -117.0842, zoom: 11 })

  useEffect(() => {
    let cancelled = false
    const ctrl = new AbortController()
    const timer = setTimeout(async () => {
      try {
        const url = `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(query)}`
        const res = await fetch(url, {
          signal: ctrl.signal,
          headers: { Accept: 'application/json' },
        })
        const data = await res.json()
        if (cancelled || !data?.[0]) return
        setView({
          lat: Number(data[0].lat),
          lon: Number(data[0].lon),
          zoom: places.length > 8 ? 11 : 13,
        })
      } catch {
        /* keep San Diego default */
      }
    }, 400)
    return () => {
      cancelled = true
      ctrl.abort()
      clearTimeout(timer)
    }
  }, [query, places.length])

  const delta = 0.08
  const bbox = [
    view.lon - delta,
    view.lat - delta,
    view.lon + delta,
    view.lat + delta,
  ].join(',')
  const src = `https://www.openstreetmap.org/export/embed.html?bbox=${encodeURIComponent(bbox)}&layer=mapnik&marker=${view.lat}%2C${view.lon}`

  return (
    <div className="loc-map-wrap">
      <iframe
        title="Selected locations map"
        src={src}
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
      />
      <p className="loc-map-caption">
        {places.length ? `${places.length} places selected` : 'Pick communities to pin this map'}
        {' · '}
        <a href={`https://www.openstreetmap.org/?mlat=${view.lat}&mlon=${view.lon}#map=${view.zoom}/${view.lat}/${view.lon}`} target="_blank" rel="noreferrer">
          OpenStreetMap
        </a>
      </p>
    </div>
  )
}
