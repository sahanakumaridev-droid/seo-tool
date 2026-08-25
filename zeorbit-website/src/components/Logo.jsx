/**
 * Logo — official ZeOrbit mark (orbital Z + wordmark).
 * Default: dark navy on transparent (light surfaces).
 * Pass `onDark` for black/dark surfaces — brightened nav mark.
 * Keep a stable rendered height so header spacing stays identical in both modes.
 */
export default function Logo({ size = 40, onDark = false, className = '' }) {
  const src = onDark ? '/zeorbit-logo-nav.webp?v=9' : '/zeorbit-logo-official.webp?v=9'

  return (
    <img
      src={src}
      alt="ZeOrbit"
      className={className || undefined}
      height={size}
      loading="eager"
      decoding="async"
      fetchPriority="low"
      style={{
        height: size,
        width: 'auto',
        display: 'block',
        maxWidth: 'min(180px, 48vw)',
        objectFit: 'contain',
        objectPosition: 'left center',
      }}
    />
  )
}
