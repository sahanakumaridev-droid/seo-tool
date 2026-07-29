/**
 * Logo — the real ZeOrbit brand mark (frontend/public/zeorbit-logo.png).
 * `size` sets the rendered height in px (width follows the image's aspect ratio).
 * Pass `onDark` when placing it on a dark surface — the mark's navy/red
 * linework has low contrast on dark backgrounds, so this wraps it in a
 * small white pill instead of trying to recolor a raster image.
 */
export default function Logo({ size = 18, onDark = false }) {
  const img = (
    <img
      src="/zeorbit-logo.png"
      alt="ZeOrbit"
      style={{ height: size, width: 'auto', display: 'block' }}
    />
  )

  if (!onDark) return img

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', background: '#fff', borderRadius: 8, padding: '4px 8px' }}>
      {img}
    </span>
  )
}
