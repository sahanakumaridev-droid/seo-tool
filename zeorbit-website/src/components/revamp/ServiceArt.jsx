/** Crisp HD SVG illustrations for each service — no stock photos */

function ServiceWeb() {
  return (
    <svg viewBox="0 0 480 260" className="rv-service-svg" aria-hidden="true">
      <defs>
        <linearGradient id="svc-web-bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#eef4ff" />
          <stop offset="100%" stopColor="#e0eaff" />
        </linearGradient>
        <linearGradient id="svc-web-screen" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#5872ff" />
          <stop offset="100%" stopColor="#38bdf8" />
        </linearGradient>
      </defs>
      <rect width="480" height="260" rx="20" fill="url(#svc-web-bg)" />
      <rect x="56" y="36" width="368" height="168" rx="16" fill="#0f172a" />
      <rect x="70" y="52" width="340" height="138" rx="10" fill="url(#svc-web-screen)" />
      <circle cx="88" cy="44" r="4" fill="#f87171" />
      <circle cx="104" cy="44" r="4" fill="#fbbf24" />
      <circle cx="120" cy="44" r="4" fill="#4ade80" />
      <rect x="88" y="72" width="140" height="12" rx="6" fill="#fff" opacity="0.92" />
      <rect x="88" y="94" width="100" height="8" rx="4" fill="#fff" opacity="0.45" />
      <rect x="88" y="118" width="160" height="48" rx="12" fill="#fff" opacity="0.2" />
      <rect x="270" y="72" width="120" height="94" rx="14" fill="#fff" opacity="0.18" />
      <rect x="180" y="218" width="120" height="10" rx="5" fill="#94a3b8" opacity="0.45" />
    </svg>
  )
}

function ServiceApp() {
  return (
    <svg viewBox="0 0 480 260" className="rv-service-svg" aria-hidden="true">
      <defs>
        <linearGradient id="svc-app-bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#ecfeff" />
          <stop offset="100%" stopColor="#e0f2fe" />
        </linearGradient>
        <linearGradient id="svc-app-screen" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#06b6d4" />
          <stop offset="100%" stopColor="#5872ff" />
        </linearGradient>
      </defs>
      <rect width="480" height="260" rx="20" fill="url(#svc-app-bg)" />
      <rect x="188" y="24" width="104" height="200" rx="22" fill="#0f172a" />
      <rect x="200" y="42" width="80" height="156" rx="12" fill="url(#svc-app-screen)" />
      <rect x="218" y="52" width="44" height="7" rx="3.5" fill="#fff" opacity="0.85" />
      <rect x="210" y="72" width="60" height="36" rx="10" fill="#fff" opacity="0.22" />
      <rect x="210" y="118" width="26" height="26" rx="8" fill="#fff" opacity="0.35" />
      <rect x="244" y="118" width="26" height="26" rx="8" fill="#fff" opacity="0.35" />
      <rect x="224" y="208" width="32" height="5" rx="2.5" fill="#64748b" />
      <rect x="86" y="70" width="72" height="110" rx="16" fill="#fff" stroke="#bae6fd" strokeWidth="2" />
      <rect x="100" y="88" width="44" height="8" rx="4" fill="#06b6d4" opacity="0.5" />
      <rect x="100" y="106" width="32" height="8" rx="4" fill="#5872ff" opacity="0.35" />
      <rect x="322" y="70" width="72" height="110" rx="16" fill="#fff" stroke="#bae6fd" strokeWidth="2" />
      <rect x="336" y="88" width="44" height="8" rx="4" fill="#5872ff" opacity="0.5" />
      <rect x="336" y="106" width="32" height="8" rx="4" fill="#06b6d4" opacity="0.35" />
    </svg>
  )
}

function ServiceSoftware() {
  return (
    <svg viewBox="0 0 480 260" className="rv-service-svg" aria-hidden="true">
      <defs>
        <linearGradient id="svc-sw-bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#fff7ed" />
          <stop offset="100%" stopColor="#eef2ff" />
        </linearGradient>
        <linearGradient id="svc-sw-accent" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f97316" />
          <stop offset="100%" stopColor="#5872ff" />
        </linearGradient>
      </defs>
      <rect width="480" height="260" rx="20" fill="url(#svc-sw-bg)" />
      {/* Dashboard panel */}
      <rect x="48" y="40" width="240" height="180" rx="16" fill="#fff" stroke="#e2e8f0" strokeWidth="2" />
      <rect x="68" y="60" width="90" height="10" rx="5" fill="#0f172a" opacity="0.85" />
      <rect x="68" y="84" width="64" height="48" rx="12" fill="url(#svc-sw-accent)" opacity="0.9" />
      <rect x="144" y="84" width="64" height="48" rx="12" fill="#e0e7ff" />
      <rect x="220" y="84" width="48" height="48" rx="12" fill="#ffedd5" />
      <rect x="68" y="148" width="200" height="10" rx="5" fill="#cbd5e1" />
      <rect x="68" y="168" width="150" height="10" rx="5" fill="#e2e8f0" />
      <rect x="68" y="188" width="180" height="10" rx="5" fill="#e2e8f0" />
      {/* Connected nodes / system map */}
      <circle cx="360" cy="80" r="28" fill="url(#svc-sw-accent)" />
      <circle cx="360" cy="80" r="10" fill="#fff" />
      <circle cx="420" cy="140" r="22" fill="#fff" stroke="#f97316" strokeWidth="3" />
      <circle cx="320" cy="170" r="22" fill="#fff" stroke="#5872ff" strokeWidth="3" />
      <path d="M360 108v20M382 95l22 28M340 100l-8 48" stroke="#94a3b8" strokeWidth="3" strokeLinecap="round" />
      <rect x="404" y="188" width="36" height="24" rx="8" fill="#0f172a" />
      <rect x="410" y="194" width="24" height="6" rx="3" fill="#38bdf8" />
    </svg>
  )
}

function ServiceSeo() {
  return (
    <svg viewBox="0 0 480 260" className="rv-service-svg" aria-hidden="true">
      <defs>
        <linearGradient id="svc-seo-bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#ecfdf5" />
          <stop offset="100%" stopColor="#eef2ff" />
        </linearGradient>
        <linearGradient id="svc-seo-line" x1="0" y1="1" x2="1" y2="0">
          <stop offset="0%" stopColor="#22c55e" />
          <stop offset="100%" stopColor="#5872ff" />
        </linearGradient>
      </defs>
      <rect width="480" height="260" rx="20" fill="url(#svc-seo-bg)" />
      <rect x="56" y="48" width="280" height="164" rx="16" fill="#fff" stroke="#d1fae5" strokeWidth="2" />
      <path
        d="M84 168c36-10 52-58 88-66s56 36 92 28 44-50 84-60"
        fill="none"
        stroke="url(#svc-seo-line)"
        strokeWidth="6"
        strokeLinecap="round"
      />
      <circle cx="172" cy="102" r="7" fill="#22c55e" />
      <circle cx="264" cy="130" r="7" fill="#5872ff" />
      <circle cx="348" cy="70" r="8" fill="#0f172a" />
      <rect x="360" y="100" width="72" height="88" rx="14" fill="#0f172a" />
      <rect x="372" y="116" width="48" height="8" rx="4" fill="#4ade80" />
      <rect x="372" y="134" width="36" height="8" rx="4" fill="#64748b" />
      <rect x="372" y="152" width="48" height="8" rx="4" fill="#38bdf8" />
      <text x="396" y="182" textAnchor="middle" fill="#fff" fontSize="11" fontWeight="700" fontFamily="system-ui,sans-serif">
        SEO
      </text>
    </svg>
  )
}

function ServiceEcommerce() {
  return (
    <svg viewBox="0 0 480 260" className="rv-service-svg" aria-hidden="true">
      <defs>
        <linearGradient id="svc-ecom-bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#fdf2f8" />
          <stop offset="100%" stopColor="#eef2ff" />
        </linearGradient>
        <linearGradient id="svc-ecom-card" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#ec4899" />
          <stop offset="100%" stopColor="#5872ff" />
        </linearGradient>
      </defs>
      <rect width="480" height="260" rx="20" fill="url(#svc-ecom-bg)" />
      <rect x="64" y="44" width="140" height="172" rx="16" fill="#fff" stroke="#fbcfe8" strokeWidth="2" />
      <rect x="80" y="60" width="108" height="72" rx="12" fill="url(#svc-ecom-card)" opacity="0.85" />
      <rect x="80" y="148" width="80" height="10" rx="5" fill="#0f172a" opacity="0.8" />
      <rect x="80" y="168" width="56" height="8" rx="4" fill="#94a3b8" />
      <rect x="80" y="188" width="64" height="14" rx="7" fill="#ec4899" />
      <rect x="224" y="44" width="140" height="172" rx="16" fill="#fff" stroke="#c7d2fe" strokeWidth="2" />
      <rect x="240" y="60" width="108" height="72" rx="12" fill="#e0e7ff" />
      <rect x="240" y="148" width="80" height="10" rx="5" fill="#0f172a" opacity="0.8" />
      <rect x="240" y="168" width="56" height="8" rx="4" fill="#94a3b8" />
      <rect x="240" y="188" width="64" height="14" rx="7" fill="#5872ff" />
      <circle cx="412" cy="120" r="36" fill="#0f172a" />
      <path d="M398 120h20M408 110v20" stroke="#fff" strokeWidth="4" strokeLinecap="round" />
      <circle cx="424" cy="132" r="6" fill="#ec4899" />
    </svg>
  )
}

function ServiceData() {
  return (
    <svg viewBox="0 0 480 260" className="rv-service-svg" aria-hidden="true">
      <defs>
        <linearGradient id="svc-data-bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f0f9ff" />
          <stop offset="100%" stopColor="#eef2ff" />
        </linearGradient>
        <linearGradient id="svc-data-bar" x1="0" y1="1" x2="0" y2="0">
          <stop offset="0%" stopColor="#38bdf8" />
          <stop offset="100%" stopColor="#5872ff" />
        </linearGradient>
      </defs>
      <rect width="480" height="260" rx="20" fill="url(#svc-data-bg)" />
      <rect x="52" y="48" width="220" height="164" rx="16" fill="#fff" stroke="#bae6fd" strokeWidth="2" />
      <rect x="76" y="160" width="28" height="32" rx="6" fill="url(#svc-data-bar)" opacity="0.55" />
      <rect x="116" y="132" width="28" height="60" rx="6" fill="url(#svc-data-bar)" opacity="0.7" />
      <rect x="156" y="100" width="28" height="92" rx="6" fill="url(#svc-data-bar)" opacity="0.85" />
      <rect x="196" y="76" width="28" height="116" rx="6" fill="url(#svc-data-bar)" />
      <rect x="300" y="56" width="128" height="40" rx="12" fill="#0f172a" />
      <rect x="312" y="68" width="64" height="8" rx="4" fill="#38bdf8" />
      <rect x="312" y="82" width="40" height="6" rx="3" fill="#64748b" />
      <rect x="300" y="110" width="128" height="40" rx="12" fill="#fff" stroke="#c7d2fe" strokeWidth="2" />
      <rect x="312" y="122" width="64" height="8" rx="4" fill="#5872ff" opacity="0.55" />
      <rect x="312" y="136" width="40" height="6" rx="3" fill="#94a3b8" />
      <rect x="300" y="164" width="128" height="40" rx="12" fill="#fff" stroke="#c7d2fe" strokeWidth="2" />
      <rect x="312" y="176" width="64" height="8" rx="4" fill="#22c55e" opacity="0.55" />
      <rect x="312" y="190" width="40" height="6" rx="3" fill="#94a3b8" />
    </svg>
  )
}

const ART = {
  website: ServiceWeb,
  app: ServiceApp,
  software: ServiceSoftware,
  seo: ServiceSeo,
  ecommerce: ServiceEcommerce,
  data: ServiceData,
}

export default function ServiceArt({ artKey, title }) {
  const Comp = ART[artKey]
  if (!Comp) return null
  return (
    <div className="rv-service-art" role="img" aria-label={title}>
      <Comp />
    </div>
  )
}
