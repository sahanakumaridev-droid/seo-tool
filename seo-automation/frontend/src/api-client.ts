/**
 * api-client.ts — Modern API client with React Query integration
 * Features: Automatic retries, caching, deduplication, streaming support
 */
import axios, { AxiosInstance, AxiosError } from 'axios'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

// Create axios instance with interceptors
const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    // Handle 401 - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// ── Authentication ──────────────────────────────────────────────
export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export const authAPI = {
  register: (email: string, password: string, name: string) =>
    apiClient.post<LoginResponse>('/auth/register', { email, password, name }),

  login: (email: string, password: string) =>
    apiClient.post<LoginResponse>('/auth/login', { email, password }),

  logout: () => apiClient.post('/auth/logout'),

  getCurrentUser: () => apiClient.get('/auth/me'),
}

// ── Content Generation ──────────────────────────────────────────
export const contentAPI = {
  generateBulk: (data: any) => apiClient.post('/content/generate', data),
  generateSingle: (businessType: string, city: string, state?: string) =>
    apiClient.post('/content/generate/single', null, {
      params: { business_type: businessType, city, state: state || 'CA' },
    }),
}

// ── Streaming ───────────────────────────────────────────────────
export const streamingAPI = {
  streamJobProgress: (jobId: string) => {
    const eventSource = new EventSource(`${BASE_URL}/stream/job/${jobId}/progress`)
    return eventSource
  },

  streamContentGeneration: (prompt: string, model: string = 'gpt-4') => {
    const token = localStorage.getItem('access_token')
    const eventSource = new EventSource(
      `${BASE_URL}/stream/generate/stream?prompt=${encodeURIComponent(prompt)}&model=${model}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      } as any
    )
    return eventSource
  },

  streamNotifications: () => {
    const token = localStorage.getItem('access_token')
    const eventSource = new EventSource(`${BASE_URL}/stream/notifications`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    } as any)
    return eventSource
  },
}

// ── Semantic Search & AI ────────────────────────────────────────
export const semanticAPI = {
  search: (query: string, businessType: string, topK?: number) =>
    apiClient.post('/semantic/search', { query, business_type: businessType, top_k: topK || 5 }),

  analyzeCompetitor: (competitorUrl: string, businessType: string, city: string) =>
    apiClient.post('/semantic/competitor-analysis', {
      competitor_url: competitorUrl,
      business_type: businessType,
      city,
    }),

  getSEORecommendations: (content: string, targetKeywords: string[], businessType: string) =>
    apiClient.post('/semantic/seo-recommendations', {
      content,
      target_keywords: targetKeywords,
      business_type: businessType,
    }),

  generateContentVariants: (content: string, numVariants?: number, tone?: string) =>
    apiClient.post('/semantic/content-variants', {
      content,
      num_variants: numVariants || 3,
      tone: tone || 'professional',
    }),

  embedText: (text: string) => apiClient.post('/semantic/embed', { text }),
}

// ── React Query Hooks ───────────────────────────────────────────
export const useLogin = () => {
  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authAPI.login(email, password),
    onSuccess: (response) => {
      const { access_token, refresh_token } = response.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
    },
  })
}

export const useLogout = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => authAPI.logout(),
    onSuccess: () => {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      queryClient.clear()
    },
  })
}

export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: () => authAPI.getCurrentUser(),
    enabled: !!localStorage.getItem('access_token'),
  })
}

export const useGenerateContent = () => {
  return useMutation({
    mutationFn: (data: any) => contentAPI.generateBulk(data),
  })
}

export const useSemanticSearch = () => {
  return useMutation({
    mutationFn: ({ query, businessType, topK }: any) =>
      semanticAPI.search(query, businessType, topK),
  })
}

export const useCompetitorAnalysis = () => {
  return useMutation({
    mutationFn: ({ competitorUrl, businessType, city }: any) =>
      semanticAPI.analyzeCompetitor(competitorUrl, businessType, city),
  })
}

export const useSEORecommendations = () => {
  return useMutation({
    mutationFn: ({ content, targetKeywords, businessType }: any) =>
      semanticAPI.getSEORecommendations(content, targetKeywords, businessType),
  })
}

export const useContentVariants = () => {
  return useMutation({
    mutationFn: ({ content, numVariants, tone }: any) =>
      semanticAPI.generateContentVariants(content, numVariants, tone),
  })
}

export default apiClient
