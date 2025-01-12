import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api/v1': {
        target: 'http://api:8000',
        changeOrigin: true,
        secure: false,
      },
      '/ws': {
        target: 'ws://api:8000',
        ws: true,
      }
    }
  }
}); 