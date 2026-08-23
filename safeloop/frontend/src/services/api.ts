const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(message: string, public status = 500) {
    super(message);
  }
}

export function getToken() {
  return localStorage.getItem("safeloop_token");
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers
    }
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Something went wrong." }));
    throw new ApiError(body.detail ?? "Something went wrong.", response.status);
  }
  return response.json();
}

export const wsUrl = import.meta.env.VITE_WS_URL ?? "ws://127.0.0.1:8000/ws";
