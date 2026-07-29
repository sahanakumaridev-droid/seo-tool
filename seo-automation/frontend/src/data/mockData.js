// Deterministic mock data for demo — replace with real API calls in production

export const KEYWORD_DATA = [
  { keyword: 'plumbing services san diego', volume: 8100, difficulty: 42, cpc: 18.40, intent: 'Commercial', trend: '+12%', position: 4 },
  { keyword: 'plumber near me san diego', volume: 14800, difficulty: 67, cpc: 24.10, intent: 'Transactional', trend: '+8%', position: 7 },
  { keyword: 'emergency plumber san diego', volume: 5400, difficulty: 55, cpc: 31.20, intent: 'Transactional', trend: '+22%', position: 12 },
  { keyword: 'best plumber san diego', volume: 3600, difficulty: 38, cpc: 15.80, intent: 'Commercial', trend: '+5%', position: 9 },
  { keyword: 'drain cleaning san diego', volume: 2900, difficulty: 29, cpc: 12.40, intent: 'Commercial', trend: '+18%', position: 3 },
  { keyword: 'water heater repair san diego', volume: 2400, difficulty: 33, cpc: 22.60, intent: 'Transactional', trend: '+9%', position: 6 },
  { keyword: 'pipe repair san diego', volume: 1900, difficulty: 25, cpc: 14.20, intent: 'Commercial', trend: '+3%', position: 11 },
  { keyword: 'sewer line repair san diego', volume: 1600, difficulty: 44, cpc: 28.90, intent: 'Transactional', trend: '+15%', position: 8 },
  { keyword: 'plumbing company san diego ca', volume: 1300, difficulty: 36, cpc: 16.50, intent: 'Commercial', trend: '+7%', position: 5 },
  { keyword: 'affordable plumber san diego', volume: 1100, difficulty: 22, cpc: 11.30, intent: 'Commercial', trend: '+11%', position: 14 },
  { keyword: 'plumbing services la jolla', volume: 880, difficulty: 18, cpc: 13.70, intent: 'Commercial', trend: '+19%', position: 2 },
  { keyword: 'plumber carlsbad ca', volume: 720, difficulty: 15, cpc: 12.10, intent: 'Commercial', trend: '+24%', position: 1 },
]

export const COMPETITOR_DATA = [
  { domain: 'sdplumbing.com', traffic: 42800, keywords: 1840, overlap: 68, da: 42, gap: 312 },
  { domain: 'plumbersandiego.net', traffic: 31200, keywords: 1420, overlap: 54, da: 38, gap: 428 },
  { domain: 'allcityplumbing.com', traffic: 28600, keywords: 1180, overlap: 47, da: 35, gap: 516 },
  { domain: 'rooterman.com', traffic: 24100, keywords: 980, overlap: 39, da: 44, gap: 284 },
  { domain: 'rotorouter.com', traffic: 19800, keywords: 860, overlap: 31, da: 52, gap: 198 },
]

export const RANKING_HISTORY = [
  { date: 'Jan', pos1: 2, pos2: 8, pos3: 14 },
  { date: 'Feb', pos1: 3, pos2: 7, pos3: 12 },
  { date: 'Mar', pos1: 4, pos2: 6, pos3: 11 },
  { date: 'Apr', pos1: 3, pos2: 5, pos3: 9 },
  { date: 'May', pos1: 4, pos2: 6, pos3: 8 },
  { date: 'Jun', pos1: 3, pos2: 4, pos3: 7 },
  { date: 'Jul', pos1: 2, pos2: 4, pos3: 6 },
]

// Organic Performance dashboard chart — one row per month, one field per switchable series
export const ORGANIC_PERFORMANCE = [
  { month: 'Aug', traffic: 3200, impressions: 41000, clicks: 1180, position: 18.4 },
  { month: 'Sep', traffic: 4100, impressions: 46500, clicks: 1420, position: 17.1 },
  { month: 'Oct', traffic: 5800, impressions: 52800, clicks: 1960, position: 15.8 },
  { month: 'Nov', traffic: 7200, impressions: 59200, clicks: 2510, position: 14.6 },
  { month: 'Dec', traffic: 6900, impressions: 58100, clicks: 2380, position: 14.9 },
  { month: 'Jan', traffic: 8400, impressions: 65400, clicks: 2940, position: 13.7 },
  { month: 'Feb', traffic: 9800, impressions: 71200, clicks: 3410, position: 13.0 },
  { month: 'Mar', traffic: 11200, impressions: 78900, clicks: 3980, position: 12.6 },
]

export const TRAFFIC_TREND = [
  { month: 'Aug', organic: 3200, paid: 800 },
  { month: 'Sep', organic: 4100, paid: 900 },
  { month: 'Oct', organic: 5800, paid: 1100 },
  { month: 'Nov', organic: 7200, paid: 1300 },
  { month: 'Dec', organic: 6900, paid: 1200 },
  { month: 'Jan', organic: 8400, paid: 1500 },
  { month: 'Feb', organic: 9800, paid: 1700 },
  { month: 'Mar', organic: 11200, paid: 1900 },
]

export const INTENT_DIST = [
  { name: 'Transactional', value: 38, color: '#1D4ED8' },
  { name: 'Commercial', value: 44, color: '#2563EB' },
  { name: 'Informational', value: 14, color: '#06b6d4' },
  { name: 'Navigational', value: 4, color: '#64748b' },
]

export const CITIES_DATA = [
  { city: 'San Diego', pages: 1, score: 84, traffic: 11200, status: 'live' },
  { city: 'La Jolla', pages: 1, score: 91, traffic: 3400, status: 'live' },
  { city: 'Chula Vista', pages: 1, score: 78, traffic: 4200, status: 'live' },
  { city: 'Carlsbad', pages: 1, score: 88, traffic: 2900, status: 'live' },
  { city: 'Escondido', pages: 1, score: 76, traffic: 2100, status: 'draft' },
  { city: 'Oceanside', pages: 1, score: 82, traffic: 2600, status: 'live' },
  { city: 'El Cajon', pages: 1, score: 74, traffic: 1800, status: 'draft' },
  { city: 'Vista', pages: 1, score: 79, traffic: 1600, status: 'draft' },
]

export const difficultyLabel = (d) => {
  if (d < 30) return { label: 'Easy', cls: 'diff-easy' }
  if (d < 55) return { label: 'Medium', cls: 'diff-medium' }
  return { label: 'Hard', cls: 'diff-hard' }
}

export const intentColor = (intent) => ({
  Transactional: 'text-indigo-600',
  Commercial: 'text-violet-600',
  Informational: 'text-sky-600',
  Navigational: 'text-slate-500',
}[intent] || 'text-slate-500')

// ── Dashboard (main SEO analytics overview) ───────────────────────
export const DASHBOARD_KPIS = [
  { key: 'seoHealth',   label: 'SEO Health',       value: 92,      suffix: '/100', delta: '+4',    deltaUp: true },
  { key: 'traffic',     label: 'Organic Traffic',  value: '48.2K', delta: '+18.4%', deltaUp: true },
  { key: 'keywords',    label: 'Organic Keywords', value: '3,482', delta: '+8.2%', deltaUp: true },
  { key: 'backlinks',   label: 'Backlinks',        value: '18.4K', delta: '+4.1%', deltaUp: true },
  { key: 'avgPosition', label: 'Average Position', value: 12.6,    delta: '+2.3', deltaUp: true },
  { key: 'aiVisibility',label: 'AI Visibility',    value: '68%',   delta: '+12%', deltaUp: true },
]

export const SEO_OPPORTUNITIES = [
  { label: '18 critical technical issues',   to: '/site-audit', tone: 'red' },
  { label: '32 pages missing meta descriptions', to: '/site-audit', tone: 'amber' },
  { label: '14 keywords close to page 1',    to: '/keywords',   tone: 'green' },
  { label: '8 declining keywords',           to: '/keywords',   tone: 'red' },
  { label: '27 content opportunities',       to: '/keywords',   tone: 'amber' },
  { label: '12 broken links',                to: '/site-audit', tone: 'red' },
]

// ── Marketing homepage demo data ──────────────────────────────────
export const HERO_METRICS = [
  { label: 'Organic Traffic', value: '+28.4%' },
  { label: 'Keywords',        value: '1,284' },
  { label: 'SEO Health',      value: '92/100' },
  { label: 'AI Visibility',   value: '68%' },
  { label: 'Backlinks',       value: '12.8K' },
  { label: 'Average Position',value: '8.4' },
]

export const TRUSTED_LOGOS = ['Acme Co', 'Nova Retail', 'Brightline Agency', 'Harbor & Co', 'Fieldstone Group', 'Lumen Digital']

export const CASE_STUDIES = [
  { value: '+214%', label: 'Organic Traffic', sub: 'Example results, 6 months' },
  { value: '+86%',  label: 'Qualified Leads', sub: 'Example results, 4 months' },
  { value: '#1–3',  label: 'Google Rankings', sub: 'Example results, primary keywords' },
]

export const PRICING_TIERS = [
  { name: 'Starter', price: '$49', period: '/mo', desc: 'For small businesses getting started with SEO.', features: ['1 website', 'Weekly rank tracking', 'Site audit', '100 tracked keywords'] },
  { name: 'Professional', price: '$129', period: '/mo', desc: 'For growing businesses and in-house marketers.', featured: true, features: ['5 websites', 'Daily rank tracking', 'Competitor analysis', '1,000 tracked keywords', 'AI visibility tracking'] },
  { name: 'Agency', price: '$349', period: '/mo', desc: 'For agencies managing multiple clients.', features: ['25 websites', 'White-label reports', 'All Professional features', '10,000 tracked keywords', 'Priority support'] },
]
