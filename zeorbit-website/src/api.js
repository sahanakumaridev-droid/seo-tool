import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || '/api'
const api = axios.create({ baseURL: BASE })

/** Public blog feed from the SEO Tool backend */
export const listBlogPosts = (skip = 0, limit = 24) =>
  api.get('/pages/blog', { params: { skip, limit } })

export const getPublishedPage = (slug) =>
  api.get(`/pages/${encodeURIComponent(slug)}`)

/** Live Google Business Profile reviews */
export const fetchGoogleReviews = () => api.get('/google-reviews')

export default api
