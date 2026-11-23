import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // No Docker (Windows), o hot reload precisa de polling para enxergar mudanças.
    watch: { usePolling: true },
  },
})
