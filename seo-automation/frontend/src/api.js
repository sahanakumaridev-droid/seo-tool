import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const generateBulk = (data) =>
  api.post('/content/generate', data)

export const generateSingle = (businessType, city, state = 'CA') =>
  api.post('/content/generate/single', null, { params: { business_type: businessType, city, state } })

export const getNearbyCities = (baseLocation, numCities) =>
  api.get('/locations/nearby', { params: { base_location: baseLocation, num_cities: numCities } })

export const getKeywords = (businessType, city, state = 'CA') =>
  api.get('/keywords/generate', { params: { business_type: businessType, city, state } })

export const exportJson = (data) =>
  api.post('/content/export/json', data)

export const exportWordpress = (data) =>
  api.post('/content/export/wordpress', data)

export const savePage = (businessType, city, state = 'CA') =>
  api.post('/pages/save', null, { params: { business_type: businessType, city, state } })

export const listPages = (skip = 0, limit = 20) =>
  api.get('/pages/', { params: { skip, limit } })
