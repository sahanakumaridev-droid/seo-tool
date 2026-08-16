/**
 * Logo — official ZeOrbit mark.
 * Light surfaces: original navy lockup.
 * Dark surfaces: bright official mark (no white plate).
 */
export default function Logo({ size = 40, onDark = false }) {
  const src = onDark ? '/zeorbit-logo-nav.png?v=8' : '/zeorbit-logo.png?v=9'
  const aspect = onDark ? 632 / 180 : 1010 / 293

  return (
    <img
      src={src}
      alt="ZeOrbit"
      width={Math.round(size * aspect)}
      height={size}
      loading="eager"
      decoding="async"
      style={{
        height: size,
        width: 'auto',
        display: 'block',
        maxWidth: 'min(220px, 48vw)',
        objectFit: 'contain',
      }}
    />
  )
}
