import "@testing-library/jest-dom/vitest";
import { beforeEach } from "vitest";

import { useAuthStore } from "../store/authStore";

beforeEach(() => {
  useAuthStore.setState({
    accessToken: null,
    refreshToken: null,
    user: null,
    isAuthenticated: false,
  });
  localStorage.clear();
});
