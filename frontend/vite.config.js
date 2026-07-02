import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
//
// NOTE: No dev proxy needed here.
// API calls use VITE_API_URL (set in .env.development / .env.production),
// which Vite injects at build time via import.meta.env.VITE_API_URL.
//   • npm run dev   → .env.development → http://localhost:8000
//   • npm run build → .env.production  → https://resume-jd-matcher-e1mq.onrender.com
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})
