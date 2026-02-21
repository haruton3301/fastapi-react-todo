import { useAuthStore } from "../store/auth";
import { refreshAccessToken } from "../lib/auth";
import { BASE_URL } from "../lib/config";

export const client = async <T>(
  url: string,
  init: RequestInit,
): Promise<T> => {
  for (let retry = 0; retry < 2; retry++) {
    const token = useAuthStore.getState().accessToken;
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
      if (retry === 0) {
        try {
          await refreshAccessToken();
          continue;
        } catch {
          // refresh 失敗 → 下の clearAuth + リダイレクトへ
        }
      }
      useAuthStore.getState().clearAuth();
      window.location.href = "/login";
      throw new Error("Unauthorized");
    }

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  }

  throw new Error(`Unexpected end of retry loop: ${url}`)
};

export default client;
