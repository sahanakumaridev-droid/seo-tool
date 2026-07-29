/**
 * Hero backdrop — a real photo (frontend/public/hero-bg.jpg: an analytics
 * dashboard on a laptop screen, sourced from Unsplash under the Unsplash
 * License, free for commercial use) with a vignette so the headline stays
 * readable: a solid bg-base radial fade over the text zone, easing out to
 * reveal the photo toward the edges, plus a bottom fade into the page.
 * Purely decorative: aria-hidden, ignores pointer events.
 */
export default function HeroBackground() {
  return (
    <div aria-hidden="true" style={{ position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none', zIndex: 0 }}>
      <img
        src="/hero-bg.jpg"
        alt=""
        style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'center 30%' }}
      />

      {/* Vignette: keeps the headline/subhead legible over the photo while
          still letting it show through toward the edges and bottom. */}
      <div style={{
        position: 'absolute', inset: 0,
        background: 'radial-gradient(ellipse 60% 55% at 50% 28%, var(--bg-base) 0%, var(--bg-base) 45%, rgba(250,250,248,0.85) 65%, rgba(250,250,248,0.35) 82%, rgba(250,250,248,0) 100%)',
      }} />
      <div style={{
        position: 'absolute', inset: 0,
        background: 'linear-gradient(180deg, transparent 0%, transparent 55%, rgba(250,250,248,0.55) 75%, var(--bg-base) 92%)',
      }} />

      {/* Warm brand tint so the photo reads as part of the palette, not a stock drop-in */}
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(255,107,84,0.10)', mixBlendMode: 'multiply' }} />
    </div>
  )
}
