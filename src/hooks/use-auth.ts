import { useEffect } from "react";
import { useAuthStore } from "@/stores/auth-store";

export function useAuth() {
  const { user, accessToken, isAuthenticated, isLoading, login, register, logout, checkAuth } =
    useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return {
    user,
    accessToken,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
  };
}
