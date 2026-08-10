import Logo from './Logo'

const LINKS = [
  {
    title: 'Product',
    items: [
      { label: 'Dashboard', href: '/dashboard' },
      { label: 'Articles', href: '/articles' },
      { label: 'Keywords', href: '/keywords' },
      { label: 'Rankings', href: '/rankings' },
    ],
  },
  {
    title: 'Company',
    items: [
      { label: 'About', href: '#' },
      { label: 'Careers', href: '#' },
      { label: 'Contact', href: '#' },
      { label: 'Blog', href: '/blog' },
    ],
  },
  {
    title: 'Legal',
    items: [
      { label: 'Privacy Policy', href: '#' },
      { label: 'Terms of Service', href: '#' },
      { label: 'Cookie Policy', href: '#' },
    ],
  },
]

export default function Footer() {
  const year = 2026
  return (
    <footer
      style={{
        marginTop: 'auto',
        background: 'var(--bg-surface)',
        borderTop: '1px solid var(--border)',
        padding: '32px 24px 24px',
      }}
    >
      <div
        style={{
          maxWidth: 1200,
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: '1.4fr repeat(3, 1fr)',
          gap: 32,
        }}
      >
        {/* Brand */}
        <div>
          <div style={{ marginBottom: 12 }}>
            <Logo size={36} />
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-3)', lineHeight: 1.6, maxWidth: 260, margin: 0 }}>
            AI-powered local SEO automation built for U.S. businesses. Rank in every city, publish
            automatically, and capture more leads.
          </p>
        </div>

        {/* Link columns */}
        {LINKS.map((col) => (
          <div key={col.title}>
            <h4
              style={{
                fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em',
                color: 'var(--text-3)', margin: '0 0 14px',
              }}
            >
              {col.title}
            </h4>
            <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 9 }}>
              {col.items.map((item) => (
                <li key={item.label}>
                  <a
                    href={item.href}
                    style={{ fontSize: 13, color: 'var(--text-2)', textDecoration: 'none', transition: 'color .15s' }}
                    onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--brand)')}
                    onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-2)')}
                  >
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Bottom bar */}
      <div
        style={{
          maxWidth: 1200,
          margin: '24px auto 0',
          paddingTop: 18,
          borderTop: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 10,
        }}
      >
        <span style={{ fontSize: 12, color: 'var(--text-4)' }}>
          © {year} ZeOrbit — SEO Intelligence Platform. Made in the USA. 🇺🇸
        </span>
        <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
          {[
            { label: 'zeorbit.com', href: 'https://zeorbit.com' },
            { label: 'facebook', href: 'https://www.facebook.com/zeorbit.web.designers.mobileapp.developers' },
            { label: 'instagram', href: 'https://www.instagram.com/zeorbit/' },
            { label: 'linkedin', href: 'https://www.linkedin.com/company/zeorbit/' },
            { label: 'twitter', href: 'https://twitter.com/orbit_ze' },
            { label: 'youtube', href: 'https://www.youtube.com/@ZeOrbit-Firm/' },
            { label: 'pinterest', href: 'https://www.pinterest.com/zeorbitsd/' },
          ].map(({ label, href }) => (
            <a
              key={label}
              href={href}
              target="_blank"
              rel="noreferrer"
              style={{ fontSize: 12, color: 'var(--text-4)', textDecoration: 'none', transition: 'color .15s' }}
              onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-1)')}
              onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-4)')}
            >
              {label}
            </a>
          ))}
        </div>
      </div>
    </footer>
  )
}
