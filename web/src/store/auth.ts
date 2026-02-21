import { create } from "zustand";
import type { UserResponse } from "../api/generated";

interface AuthState {
  accessToken: string | null;
  user: UserResponse | null;
  setAccessToken: (token: string) => void;
  setUser: (user: UserResponse) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  setAccessToken: (token) => set({ accessToken: token }),
  setUser: (user) => set({ user }),
  clearAuth: () => set({ accessToken: null, user: null }),
}));
