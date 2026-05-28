const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export { API_BASE_URL };

export function getApiBaseUrl(): string {
  return API_BASE_URL.replace(/\/$/, "");
}
