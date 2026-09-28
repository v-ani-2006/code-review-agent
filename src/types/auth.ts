export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in?: number;
}

export interface LoginCredentials {
  username: string; // Accepts username or email
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
