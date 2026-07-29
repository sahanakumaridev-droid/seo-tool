import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      // Local dev: proxy API + public published pages to FastAPI (IPv4 explicit)
      '/api': 'http://127.0.0.1:8000',
      '/p': 'http://127.0.0.1:8000',
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  }
})
