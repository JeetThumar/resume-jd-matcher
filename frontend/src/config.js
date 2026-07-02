/**
 * config.js — Single source of truth for the backend API URL.
 *
 * In development (`npm run dev`):
 *   Vite loads .env.development → VITE_API_URL=http://localhost:8000
 *
 * In production (`npm run build`):
 *   Vite loads .env.production → VITE_API_URL=https://resume-jd-matcher-e1mq.onrender.com
 *   (also set in the Vercel dashboard under Environment Variables)
 *
 * Usage:
 *   import { API_URL } from './config'
 *   axios.post(`${API_URL}/analyze`, formData)
 */

export const API_URL = import.meta.env.VITE_API_URL;
