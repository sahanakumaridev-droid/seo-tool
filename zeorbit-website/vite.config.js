import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { spaPublicShells } from './vite.spa-shells.js'

const apiTarget = process.env.SEO_API_URL || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react(), tailwindcss(), spaPublicShells()],
  server: {
    port: 5180,
    strictPort: true,
    host: '127.0.0.1',
    proxy: {
      // Point at the SEO Tool FastAPI backend
      '/api': apiTarget,
      '/p': {
        target: apiTarget,
        bypass(req) {
          // `/p` is article slugs; do not steal marketing pages that start with "p".
          const url = req.url || ''
          if (
            url === '/portfolio' ||
            url.startsWith('/portfolio') ||
            url === '/privacy-policy' ||
            url.startsWith('/privacy-policy') ||
            url === '/privacy' ||
            url.startsWith('/privacy?') ||
            url.startsWith('/privacy/')
          ) {
            return url
          }
        },
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
