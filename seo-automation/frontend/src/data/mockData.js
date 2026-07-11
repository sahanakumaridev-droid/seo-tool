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
  Transactional: 'text-indigo-400',
  Commercial: 'text-violet-400',
  Informational: 'text-sky-400',
  Navigational: 'text-slate-400',
}[intent] || 'text-slate-400')
