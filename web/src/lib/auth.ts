import { useAuthStore } from "../store/auth";
import { BASE_URL } from "./config";

// refreshPromiseをシングルトン化
let refreshPromise: Promise<string> | null = null;

export function refreshAccessToken(): Promise<string> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    const res = await fetch(`${BASE_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });
    if (!res.ok) {
      throw new Error("Refresh failed");
    }
    const body = await res.json();
    useAuthStore.getState().setAccessToken(body.access_token);
    return body.access_token as string;
  })();

  refreshPromise.finally(() => {
    refreshPromise = null;
  });

  return refreshPromise;
}

export const logout = async (): Promise<void> => {
  try {
    await fetch(`${BASE_URL}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
  } finally {
    useAuthStore.getState().clearAuth();
    window.location.href = "/login";
  }
};
