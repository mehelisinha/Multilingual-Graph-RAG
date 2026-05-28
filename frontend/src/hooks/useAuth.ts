import { useCallback, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";

import * as authApi from "../api/auth";
import { useAuthStore } from "../store/authStore";

export function useAuth() {
  const navigate = useNavigate();
  const { accessToken, refreshToken, user, isAuthenticated, setTokens, setUser, clearAuth } =
    useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const loadProfile = useCallback(async () => {
    if (!accessToken) return;
    try {
      const profile = await authApi.fetchCurrentUser();
      setUser(profile);
    } catch {
      clearAuth();
    }
  }, [accessToken, setUser, clearAuth]);

  useEffect(() => {
    if (accessToken && !user) {
      void loadProfile();
    }
  }, [accessToken, user, loadProfile]);

  const login = useCallback(
    async (email: string, password: string) => {
      setIsLoading(true);
      try {
        const tokens = await authApi.login({ email, password });
        setTokens(tokens.access_token, tokens.refresh_token ?? null);
        const profile = await authApi.fetchCurrentUser();
        setUser(profile);
        toast.success(`Welcome back, ${profile.email}`);
        navigate("/");
      } catch {
        toast.error("Invalid email or password");
        throw new Error("login_failed");
      } finally {
        setIsLoading(false);
      }
    },
    [navigate, setTokens, setUser],
  );

  const logout = useCallback(async () => {
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken);
      } catch {
        // Best-effort server logout; always clear local session.
      }
    }
    clearAuth();
    navigate("/login");
  }, [refreshToken, clearAuth, navigate]);

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    loadProfile,
  };
}
