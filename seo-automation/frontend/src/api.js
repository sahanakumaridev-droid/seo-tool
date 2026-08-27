import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || '/api'
const api = axios.create({ baseURL: BASE })

// Attach JWT when present (marketplace / SEO login)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('mp_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function storeAuthTokens(data) {
  if (data?.access_token) {
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('mp_token', data.access_token)
  }
  if (data?.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
  if (data?.user) localStorage.setItem('mp_user', JSON.stringify(data.user))
}

export function clearAuthTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('mp_token')
  localStorage.removeItem('mp_user')
  localStorage.removeItem('seo_auth')
}

export const loginUser = async (email, password) => {
  const res = await api.post('/users/login', { email, password })
  storeAuthTokens(res.data)
  return res
}

export const registerUser = async ({ name, email, password, role = 'client' }) => {
  const res = await api.post('/users/register', { name, email, password, role })
  storeAuthTokens(res.data)
  return res
}

// ── Content ──────────────────────────────────────────────────────
export const generateBulk = (data) =>
  api.post('/content/generate', data, { timeout: 600000 })

export const suggestContentBrief = (data) =>
  api.post('/content/suggest-brief', data)

// Keyword + website-driven articles
export const analyzeWebsite = (websiteUrl) =>
  api.post('/content/analyze-website', { website_url: websiteUrl })

export const generateArticles = (data) =>
  api.post('/content/generate-articles', data)

export const generateSingle = (businessType, city, state = 'CA', useAi = false) =>
  api.post('/content/generate/single', null, { params: { business_type: businessType, city, state, use_ai: useAi } })

export const boostPageScores = (block) =>
  api.post('/content/boost-scores', block)

export const exportJson = (data) =>
  api.post('/content/export/json', data)

export const exportWordpress = (data) =>
  api.post('/content/export/wordpress', data)

// ── Locations ────────────────────────────────────────────────────
export const getNearbyCities = (baseLocation, numCities) =>
  api.get('/locations/nearby', { params: { base_location: baseLocation, num_cities: numCities } })

export const getSanDiegoCounty = () =>
  api.get('/locations/san-diego-county')

export const searchCities = (q = '', limit = 40) =>
  api.get('/locations/cities', { params: { q, limit } })

// ── Keywords ─────────────────────────────────────────────────────
export const getKeywords = (businessType, city, state = 'CA') =>
  api.get('/keywords/generate', { params: { business_type: businessType, city, state } })

export const researchKeywords = (keyword, location = 'US') =>
  api.get('/keywords/research', { params: { keyword, location } })

// ── Site Audit ───────────────────────────────────────────────────
export const runSiteAudit = (url) =>
  api.post('/seo-audit/run', { url }, { timeout: 90000 })

// ── Rankings ─────────────────────────────────────────────────────
export const getRankings = (businessType, baseLocation, website) =>
  api.get('/rankings', { params: { business_type: businessType, base_location: baseLocation, website } })

// ── Competitor Analysis ────────────────────────────────────────────
export const analyzeCompetitor = (competitorUrl, businessType, city) =>
  api.post('/semantic/competitor-analysis', { competitor_url: competitorUrl, business_type: businessType, city })

export const discoverCompetitors = (website, businessType, city) =>
  api.post('/semantic/discover-competitors', { website, business_type: businessType, city })

// ── Pages ────────────────────────────────────────────────────────
export const savePage = (businessType, city, state = 'CA') =>
  api.post('/pages/save', null, { params: { business_type: businessType, city, state } })

export const saveEditedBlock = (block, { businessType = '', applyGlobally = true } = {}) =>
  api.post('/pages/save-block', {
    block,
    business_type: businessType || block?.business_type || '',
    apply_globally: applyGlobally,
  })

export const listPages = (skip = 0, limit = 20) =>
  api.get('/pages/', { params: { skip, limit } })

/** Public blog feed: published /p/{slug} pages + tracked live WordPress URLs */
export const listBlogPosts = (skip = 0, limit = 24) =>
  api.get('/pages/blog', { params: { skip, limit } })

/** Published SEO/WordPress URLs for Google Ads final URL picker */
export const listLandingPagesForAds = (skip = 0, limit = 50) =>
  api.get('/pages/landing-pages', { params: { skip, limit } })

export const deletePage = (slug) =>
  api.delete(`/pages/${slug}`)

// ── WordPress ────────────────────────────────────────────────────
export const publishToWordPress = (seoBlock, wpConfig) =>
  api.post('/wordpress/publish', { seo_block: seoBlock, wp_config: wpConfig })

export const publishBulkToWordPress = (pages, wpConfig) =>
  api.post('/wordpress/publish/bulk', { pages, wp_config: wpConfig })

// ── Publish to ZeOrbit (public page → appears on ZeOrbit blog) ───
export const ZEORBIT_SITE_URL =
  import.meta.env.VITE_ZEORBIT_SITE_URL || 'https://zeorbit.com'

export const zeorbitBlogUrl = () => `${ZEORBIT_SITE_URL.replace(/\/$/, '')}/blog`

/** Live article URL on zeorbit.com — keyword-city path, never /p/ or the SEO-tool host. */
export function zeorbitArticleUrl(slugOrUrl) {
  const base = ZEORBIT_SITE_URL.replace(/\/$/, '')
  if (!slugOrUrl) return zeorbitBlogUrl()
  let path = ''
  if (/^https?:\/\//i.test(slugOrUrl)) {
    try { path = new URL(slugOrUrl).pathname } catch { return zeorbitBlogUrl() }
  } else {
    path = slugOrUrl.startsWith('/') ? slugOrUrl : `/${slugOrUrl}`
  }
  path = path.replace(/\/$/, '')
  if (path.startsWith('/p/')) path = `/${path.slice(3)}`
  if (path && path !== '/' && path !== '/blog') return `${base}${path}`
  return zeorbitBlogUrl()
}

export const publishToWeb = (seoBlock) =>
  api.post('/pages/publish-web', seoBlock)

export const publishAllToWeb = (pages) =>
  api.post('/pages/publish-web/bulk', pages)

// ── Jobs (async bulk operations) ─────────────────────────────────
export const startBulkGenerateJob = (data) =>
  api.post('/jobs/generate', data)

export const getJob = (jobId) =>
  api.get(`/jobs/${jobId}`)

export const startBulkPublishJob = (pages, wpConfig) =>
  api.post('/jobs/publish', { pages, wp_config: wpConfig })

export const getJobStatus = (jobId) =>
  api.get(`/jobs/${jobId}`)

// ── Social Media ─────────────────────────────────────────────────
export const shareToSocial = (data) =>
  api.post('/social/share', data)

export const getSocialPlatforms = () =>
  api.get('/social/platforms')

// ── Google Ads ───────────────────────────────────────────────────
export const getGoogleAdsStatus = () =>
  api.get('/google-ads/status')

export const getGoogleLiveStatus = () =>
  api.get('/google/live-status')

export const createGoogleAdsCampaign = (data) =>
  api.post('/google-ads/create-campaign', data)

export const launchGoogleAdsCampaign = (data) =>
  api.post('/google-ads/launch', data)

export const listGoogleAdsCampaigns = (limit = 50) =>
  api.get('/google-ads/campaigns', { params: { limit } })

export const setGoogleAdsCampaignStatus = (campaign_id, enable = true) =>
  api.post('/google-ads/campaigns/status', { campaign_id, enable })

export const suggestGoogleAdsCopy = (data) =>
  api.post('/google-ads/suggest', data)

// ── Google Search Automation (sitemap + Search Console) ───────────
export const getSeoIndexingStatus = () =>
  api.get('/seo-indexing/status')

export const getSeoIndexingSetup = () =>
  api.get('/seo-indexing/setup')

export const pushAllSeoIndexing = () =>
  api.post('/seo-indexing/push-all', null, { timeout: 120000 })

export const refreshSeoIndexing = (id) =>
  api.post('/seo-indexing/refresh', null, { params: id ? { id } : {}, timeout: 90000 })

export const inspectSeoIndexingUrl = (data) =>
  api.post('/seo-indexing/inspect', data)

export const notifyBingIndexing = () =>
  api.post('/seo-indexing/notify-bing', null, { timeout: 60000 })

// ── Leads ────────────────────────────────────────────────────────
export const getLeads = (params = {}) =>
  api.get('/leads/', { params })

export const createLead = (data) =>
  api.post('/leads/', data)

export const updateLeadStatus = (leadId, status) =>
  api.patch(`/leads/${leadId}/status`, null, { params: { status } })

export const deleteLead = (leadId) =>
  api.delete(`/leads/${leadId}`)

export const getLeadStats = () =>
  api.get('/leads/stats')

export const prospectLeads = (data) =>
  api.post('/leads/prospect', data)

// ── Marketplace ───────────────────────────────────────────────────────────────
const mpHeaders = () => {
  const token = localStorage.getItem('mp_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// Auth
export const mpRegister = (data) =>
  api.post('/users/register', data)

export const mpLogin = (data) =>
  api.post('/users/login', data)

export const mpGetMe = () =>
  api.get('/users/me', { headers: mpHeaders() })

export const mpUpdateMe = (data) =>
  api.patch('/users/me', data, { headers: mpHeaders() })

export const mpGetProfessionals = (params = {}) =>
  api.get('/users/professionals', { params })

// Service Requests
export const mpCreateRequest = (data) =>
  api.post('/marketplace/requests', data, { headers: mpHeaders() })

export const mpListRequests = (params = {}) =>
  api.get('/marketplace/requests', { params })

export const mpMyRequests = () =>
  api.get('/marketplace/requests/my', { headers: mpHeaders() })

export const mpGetRequest = (id) =>
  api.get(`/marketplace/requests/${id}`)

export const mpUpdateRequestStatus = (id, status) =>
  api.patch(`/marketplace/requests/${id}/status`, null, { params: { new_status: status }, headers: mpHeaders() })

// Quotes
export const mpSubmitQuote = (data) =>
  api.post('/marketplace/quotes', data, { headers: mpHeaders() })

export const mpGetQuotes = (requestId) =>
  api.get(`/marketplace/quotes/request/${requestId}`, { headers: mpHeaders() })

export const mpAcceptQuote = (quoteId) =>
  api.patch(`/marketplace/quotes/${quoteId}/accept`, {}, { headers: mpHeaders() })

// Messages
export const mpSendMessage = (data) =>
  api.post('/marketplace/messages', data, { headers: mpHeaders() })

export const mpGetInbox = () =>
  api.get('/marketplace/messages/inbox', { headers: mpHeaders() })

export const mpMarkRead = (msgId) =>
  api.patch(`/marketplace/messages/${msgId}/read`, {}, { headers: mpHeaders() })

// Reviews
export const mpCreateReview = (data) =>
  api.post('/marketplace/reviews', data, { headers: mpHeaders() })

export const mpGetReviews = (professionalId) =>
  api.get(`/marketplace/reviews/professional/${professionalId}`)

// Credits
export const mpGetPackages = () =>
  api.get('/marketplace/credits/packages')

export const mpPurchaseCredits = (packageId) =>
  api.post('/marketplace/credits/purchase', { package_id: packageId }, { headers: mpHeaders() })

export const mpGetBalance = () =>
  api.get('/marketplace/credits/balance', { headers: mpHeaders() })

export const mpCreditHistory = () =>
  api.get('/marketplace/credits/history', { headers: mpHeaders() })

// Admin
export const mpAdminStats = () =>
  api.get('/marketplace/admin/stats', { headers: mpHeaders() })

export const mpAdminUsers = (params = {}) =>
  api.get('/marketplace/admin/users', { params, headers: mpHeaders() })

export const mpVerifyUser = (userId) =>
  api.patch(`/marketplace/admin/users/${userId}/verify`, {}, { headers: mpHeaders() })
