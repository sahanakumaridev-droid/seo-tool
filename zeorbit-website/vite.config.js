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
      '/p': 'http://127.0.0.1:8000',
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
