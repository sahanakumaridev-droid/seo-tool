/**
 * Logo — the ZeOrbit wordmark. Clean text-only "ZEORBIT".
 * `size` is the font size in px.
 *
 * To use a real brand logo image instead, drop the file at
 * frontend/public/zeorbit-logo.png and render <img src="/zeorbit-logo.png" />.
 */
export default function Logo({ size = 18, color = 'var(--text-1)' }) {
  return (
    <span
      style={{
        fontFamily: "'Sora', 'Inter', sans-serif",
        fontWeight: 800,
        fontSize: size,
        letterSpacing: '1.5px',
        color,
        lineHeight: 1,
        whiteSpace: 'nowrap',
      }}
    >
      ZEORBIT
    </span>
  )
}
