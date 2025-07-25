import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/socket.io': {
        target: 'http://backend:8000',
        changeOrigin: true,
        ws: true
      },
      '/ws': {
        target: 'http://backend:8000',
        changeOrigin: true,
        ws: true
      }
    }
  }
})
