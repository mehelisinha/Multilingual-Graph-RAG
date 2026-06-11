const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export { API_BASE_URL };

export function getApiBaseUrl(): string {
  return API_BASE_URL.replace(/\/$/, "");
}

/**
 * WebSocket base URL, derived from the API base so it always points at the same
 * host/prefix the REST API is served from. Handles both absolute
 * (http://host:8000/api/v1) and relative (/api/v1) configurations.
 */
export function getWsBaseUrl(): string {
  const base = getApiBaseUrl();
  if (/^https?:\/\//i.test(base)) {
    return base.replace(/^http/i, "ws");
  }
  // Relative base: resolve against the current page origin.
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  const path = base.startsWith("/") ? base : `/${base}`;
  return `${proto}//${window.location.host}${path}`;
}
