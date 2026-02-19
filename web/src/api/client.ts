import { getToken, removeToken, setToken } from "../lib/auth";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const res = await fetch(`${BASE_URL}/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Refresh failed");
  }
  const body = await res.json();
  setToken(body.access_token);
  return body.access_token;
}

export const client = async <T>(
  url: string,
  init: RequestInit,
): Promise<T> => {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${BASE_URL}${url}`, {
    ...init,
    headers,
    credentials: "include",
  });

  if (response.status === 401 && !url.startsWith("/auth/")) {
    // リフレッシュを1回だけ試行（同時リクエストは共有）
    try {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken();
      }
      const newToken = await refreshPromise;
      refreshPromise = null;

      // 新しいトークンでリトライ
      headers.set("Authorization", `Bearer ${newToken}`);
      const retry = await fetch(`${BASE_URL}${url}`, {
        ...init,
        headers,
        credentials: "include",
      });
      if (!retry.ok) {
        throw new Error(`HTTP error: ${retry.status}`);
      }
      if (retry.status === 204) {
        return undefined as T;
      }
      return (await retry.json()) as T;
    } catch {
      refreshPromise = null;
      removeToken();
      window.location.href = "/login";
      throw new Error("Unauthorized");
    }
  }

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
};

export default client;
