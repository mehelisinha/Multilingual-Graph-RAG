import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import type { AuthState, UserProfile } from "../types/auth.types";

const createAuthState = (
  set: (partial: Partial<AuthState> | ((state: AuthState) => Partial<AuthState>)) => void,
): AuthState => ({
  accessToken: null,
  refreshToken: null,
  user: null,
  isAuthenticated: false,
  setTokens: (accessToken, refreshToken) =>
    set({
      accessToken,
      refreshToken,
      isAuthenticated: Boolean(accessToken),
    }),
  setUser: (user: UserProfile | null) => set({ user }),
  clearAuth: () =>
    set({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
    }),
});

const isTestEnv = import.meta.env.MODE === "test";

export const useAuthStore = isTestEnv
  ? create<AuthState>()(createAuthState)
  : create<AuthState>()(
      persist(createAuthState, {
        name: "auth-storage",
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({
          accessToken: state.accessToken,
          refreshToken: state.refreshToken,
          user: state.user,
          isAuthenticated: state.isAuthenticated,
        }),
      }),
    );
