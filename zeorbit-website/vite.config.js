import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5180,
    strictPort: true,
    host: '127.0.0.1',
    proxy: {
      // Point at the SEO Tool FastAPI backend
      '/api': 'http://127.0.0.1:8000',
      '/p': {
        target: 'http://127.0.0.1:8000',
        bypass(req) {
          // `/p` is article slugs; do not steal the marketing /portfolio page.
          if (req.url === '/portfolio' || req.url.startsWith('/portfolio')) return req.url
        },
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
