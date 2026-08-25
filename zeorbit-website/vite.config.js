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
