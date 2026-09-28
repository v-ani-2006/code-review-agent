import { apiClient } from "./api-client";
import { LoginCredentials, RegisterData, TokenResponse, User } from "@/types/auth";

export const authService = {
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const params = new URLSearchParams();
    params.append("username", credentials.username);
    params.append("password", credentials.password);

    const response = await apiClient.post<TokenResponse>("/auth/login", params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    if (response.data.access_token) {
      localStorage.setItem("cp_access_token", response.data.access_token);
      localStorage.setItem("cp_refresh_token", response.data.refresh_token);
    }

    return response.data;
  },

  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>("/auth/register", data);
    return response.data;
  },

  async getMe(): Promise<User> {
    const response = await apiClient.get<User>("/auth/me");
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post("/auth/logout");
    } finally {
      localStorage.removeItem("cp_access_token");
      localStorage.removeItem("cp_refresh_token");
    }
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>("/auth/change-password", {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};
