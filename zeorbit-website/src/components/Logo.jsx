/**
 * Logo — official ZeOrbit mark (orbital Z + wordmark).
 * Default: dark navy on transparent (light surfaces).
 * Pass `onDark` for black/dark surfaces — official blue mark from zeorbit.com.
 */
export default function Logo({ size = 40, onDark = false, className = '' }) {
  // onDark: brightened official blue mark (readable on black header)
  const src = onDark ? '/zeorbit-logo-nav.png?v=7' : '/zeorbit-logo.png?v=3'
  const aspect = onDark ? 632 / 180 : 1010 / 293

  return (
    <img
      src={src}
      alt="ZeOrbit"
      className={className || undefined}
      width={Math.round(size * aspect)}
      height={size}
      loading="eager"
      decoding="async"
      style={{
        height: size,
        width: 'auto',
        display: 'block',
        maxWidth: 'min(260px, 54vw)',
        objectFit: 'contain',
      }}
    />
  )
}
