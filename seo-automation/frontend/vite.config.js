import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const apiTarget = process.env.SEO_API_URL || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      // Local dev: proxy API + public articles to FastAPI
      '/api': apiTarget,
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  }
})
