const TOKEN_KEY = "access_token";
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const getToken = (): string | null => localStorage.getItem(TOKEN_KEY);

export const setToken = (token: string): void =>
  localStorage.setItem(TOKEN_KEY, token);

export const removeToken = (): void => localStorage.removeItem(TOKEN_KEY);

export const isLoggedIn = (): boolean => getToken() !== null;

export const logout = async (): Promise<void> => {
  await fetch(`${BASE_URL}/auth/logout`, {
    method: "POST",
    credentials: "include",
  }).catch(() => {});
  removeToken();
  window.location.href = "/login";
};
