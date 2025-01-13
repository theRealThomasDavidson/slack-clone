const BACKEND_HOST = 'localhost:8000';
const BACKEND_PROTOCOL = 'http';
const WS_PROTOCOL = 'ws';

// API paths should match backend configuration and work with Vite proxy
export const API_BASE_URL = `/api/v1`;  // Updated to match backend API version
export const WS_BASE_URL = `${WS_PROTOCOL}://${BACKEND_HOST}/api/v1/ws`;

// For development/production switching
export const isProduction = process.env.NODE_ENV === 'production'; 