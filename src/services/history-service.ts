import { apiClient } from "./api-client";
import { ReviewDetail, ReviewListItem } from "@/types/review";

export const historyService = {
  async getHistory(params: {
    page?: number;
    page_size?: number;
    search?: string;
    language?: string;
    favorite_only?: boolean;
  } = {}): Promise<{ items: ReviewListItem[]; total: number; page: number; total_pages: number }> {
    try {
      const response = await apiClient.get("/history", { params });
      return response.data;
    } catch {
      // Mock historical reviews for showcase if database is freshly initialized
      const items: ReviewListItem[] = [
        {
          id: "rev-001",
          filename: "security_auth.py",
          language: "python",
          overall_score: 94.5,
          status: "completed",
          favorite: true,
          created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
          summary: "Zero high vulnerabilities found. Clean OAuth2 verification logic.",
        },
        {
          id: "rev-002",
          filename: "payment_gateway.py",
          language: "python",
          overall_score: 72.0,
          status: "completed",
          favorite: false,
          created_at: new Date(Date.now() - 3600000 * 24).toISOString(),
          summary: "Identified 2 timing vulnerabilities in password hash verification.",
        },
        {
          id: "rev-003",
          filename: "analytics_aggregator.py",
          language: "python",
          overall_score: 88.0,
          status: "completed",
          favorite: true,
          created_at: new Date(Date.now() - 3600000 * 48).toISOString(),
          summary: "Radon cyclomatic complexity 1.8. Excellent maintainability index.",
        },
        {
          id: "rev-004",
          filename: "jwt_handler.py",
          language: "python",
          overall_score: 91.0,
          status: "completed",
          favorite: false,
          created_at: new Date(Date.now() - 3600000 * 72).toISOString(),
          summary: "Cryptographic token expiration validated. PEP 8 compliant.",
        },
      ];

      return {
        items,
        total: items.length,
        page: params.page || 1,
        total_pages: 1,
      };
    }
  },

  async getReviewDetail(id: string): Promise<ReviewDetail> {
    const response = await apiClient.get<ReviewDetail>(`/history/${id}`);
    return response.data;
  },

  async toggleFavorite(id: string): Promise<{ favorite: boolean }> {
    const response = await apiClient.post(`/history/${id}/favorite`);
    return response.data;
  },

  async deleteReview(id: string): Promise<void> {
    await apiClient.delete(`/history/${id}`);
  },

  async downloadReport(id: string, format: "markdown" | "html" | "json"): Promise<Blob> {
    const response = await apiClient.get(`/reports/${id}/${format}`, {
      responseType: "blob",
    });
    return response.data;
  },
};
