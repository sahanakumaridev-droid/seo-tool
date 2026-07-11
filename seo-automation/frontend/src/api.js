import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || '/api'
const api = axios.create({ baseURL: BASE })

// ── Content ──────────────────────────────────────────────────────
export const generateBulk = (data) =>
  api.post('/content/generate', data)

// Keyword + website-driven articles
export const analyzeWebsite = (websiteUrl) =>
  api.post('/content/analyze-website', { website_url: websiteUrl })

export const generateArticles = (data) =>
  api.post('/content/generate-articles', data)

export const generateSingle = (businessType, city, state = 'CA', useAi = false) =>
  api.post('/content/generate/single', null, { params: { business_type: businessType, city, state, use_ai: useAi } })

export const exportJson = (data) =>
  api.post('/content/export/json', data)

export const exportWordpress = (data) =>
  api.post('/content/export/wordpress', data)

// ── Locations ────────────────────────────────────────────────────
export const getNearbyCities = (baseLocation, numCities) =>
  api.get('/locations/nearby', { params: { base_location: baseLocation, num_cities: numCities } })

// ── Keywords ─────────────────────────────────────────────────────
export const getKeywords = (businessType, city, state = 'CA') =>
  api.get('/keywords/generate', { params: { business_type: businessType, city, state } })

// ── Pages ────────────────────────────────────────────────────────
export const savePage = (businessType, city, state = 'CA') =>
  api.post('/pages/save', null, { params: { business_type: businessType, city, state } })

export const listPages = (skip = 0, limit = 20) =>
  api.get('/pages/', { params: { skip, limit } })

export const deletePage = (slug) =>
  api.delete(`/pages/${slug}`)

// ── WordPress ────────────────────────────────────────────────────
export const publishToWordPress = (seoBlock, wpConfig) =>
  api.post('/wordpress/publish', { seo_block: seoBlock, wp_config: wpConfig })

export const publishBulkToWordPress = (pages, wpConfig) =>
  api.post('/wordpress/publish/bulk', { pages, wp_config: wpConfig })

// ── Publish to Web (hosted public page on this app) ──────────────
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

export const syncBarkLeads = () =>
  api.post('/leads/sync/bark')

export const syncThumbtackLeads = () =>
  api.post('/leads/sync/thumbtack')

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
