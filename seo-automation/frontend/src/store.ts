/**
 * store.ts — Global state management with Zustand
 * Handles auth, UI state, and app-wide data
 */
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

// ── Auth Store ──────────────────────────────────────────────────
interface AuthState {
  user: any | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  setUser: (user: any) => void
  setTokens: (accessToken: string, refreshToken: string) => void
  logout: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,

        setUser: (user) => set({ user, isAuthenticated: !!user }),
        setTokens: (accessToken, refreshToken) =>
          set({ accessToken, refreshToken, isAuthenticated: true }),
        logout: () =>
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
          }),
        setLoading: (isLoading) => set({ isLoading }),
        setError: (error) => set({ error }),
      }),
      {
        name: 'auth-store',
        partialize: (state) => ({
          accessToken: state.accessToken,
          refreshToken: state.refreshToken,
          user: state.user,
        }),
      }
    )
  )
)

// ── UI Store ────────────────────────────────────────────────────
interface UIState {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  notifications: Array<{ id: string; message: string; type: 'info' | 'success' | 'error' }>

  toggleSidebar: () => void
  setTheme: (theme: 'light' | 'dark') => void
  addNotification: (message: string, type: 'info' | 'success' | 'error') => void
  removeNotification: (id: string) => void
}

export const useUIStore = create<UIState>()(
  devtools(
    persist(
      (set) => ({
        sidebarOpen: true,
        theme: 'dark',
        notifications: [],

        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        setTheme: (theme) => set({ theme }),
        addNotification: (message, type) =>
          set((state) => ({
            notifications: [
              ...state.notifications,
              { id: Date.now().toString(), message, type },
            ],
          })),
        removeNotification: (id) =>
          set((state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          })),
      }),
      {
        name: 'ui-store',
        partialize: (state) => ({
          sidebarOpen: state.sidebarOpen,
          theme: state.theme,
        }),
      }
    )
  )
)

// ── Content Store ───────────────────────────────────────────────
interface ContentState {
  generatedContent: any[]
  selectedContent: any | null
  isGenerating: boolean
  generationProgress: number

  setGeneratedContent: (content: any[]) => void
  selectContent: (content: any) => void
  setIsGenerating: (generating: boolean) => void
  setGenerationProgress: (progress: number) => void
  clearContent: () => void
}

export const useContentStore = create<ContentState>()(
  devtools((set) => ({
    generatedContent: [],
    selectedContent: null,
    isGenerating: false,
    generationProgress: 0,

    setGeneratedContent: (content) => set({ generatedContent: content }),
    selectContent: (content) => set({ selectedContent: content }),
    setIsGenerating: (generating) => set({ isGenerating: generating }),
    setGenerationProgress: (progress) => set({ generationProgress: progress }),
    clearContent: () =>
      set({
        generatedContent: [],
        selectedContent: null,
        generationProgress: 0,
      }),
  }))
)

// ── AI Analysis Store ───────────────────────────────────────────
interface AIAnalysisState {
  competitorAnalysis: any | null
  seoRecommendations: any | null
  contentVariants: any[] | null
  isAnalyzing: boolean

  setCompetitorAnalysis: (analysis: any) => void
  setSEORecommendations: (recommendations: any) => void
  setContentVariants: (variants: any[]) => void
  setIsAnalyzing: (analyzing: boolean) => void
  clearAnalysis: () => void
}

export const useAIAnalysisStore = create<AIAnalysisState>()(
  devtools((set) => ({
    competitorAnalysis: null,
    seoRecommendations: null,
    contentVariants: null,
    isAnalyzing: false,

    setCompetitorAnalysis: (analysis) => set({ competitorAnalysis: analysis }),
    setSEORecommendations: (recommendations) => set({ seoRecommendations: recommendations }),
    setContentVariants: (variants) => set({ contentVariants: variants }),
    setIsAnalyzing: (analyzing) => set({ isAnalyzing: analyzing }),
    clearAnalysis: () =>
      set({
        competitorAnalysis: null,
        seoRecommendations: null,
        contentVariants: null,
      }),
  }))
)
