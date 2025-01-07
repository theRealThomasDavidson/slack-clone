const BACKEND_HOST = 'localhost:8000';
const BACKEND_PROTOCOL = 'http';
const WS_PROTOCOL = 'ws';

// Ensure trailing slashes are consistent
export const API_BASE_URL = `${BACKEND_PROTOCOL}://${BACKEND_HOST}/api`;
export const WS_BASE_URL = `${WS_PROTOCOL}://${BACKEND_HOST}/api/ws`;

// For development/production switching
export const isProduction = process.env.NODE_ENV === 'production'; 