/**
 * Logo — ZeOrbit brand mark (public/zeorbit-logo.png).
 * Dark navy linework: use default on light surfaces.
 * Pass `onDark` for dark surfaces — uses light wordmark variant.
 */
export default function Logo({ size = 40, onDark = false }) {
  const src = onDark ? '/zeorbit-logo-light.png' : '/zeorbit-logo.png'

  return (
    <img
      src={src}
      alt="ZeOrbit"
      width={Math.round(size * (1010 / 293))}
      height={size}
      loading="eager"
      decoding="async"
      style={{
        height: size,
        width: 'auto',
        display: 'block',
        maxWidth: 'min(220px, 46vw)',
        objectFit: 'contain',
      }}
    />
  )
}
