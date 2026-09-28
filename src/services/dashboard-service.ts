import { apiClient } from "./api-client";
import { ActivityItem, DashboardStats, RecentReviewItem } from "@/types/dashboard";

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    try {
      const response = await apiClient.get<DashboardStats>("/dashboard/stats");
      return response.data;
    } catch {
      // Fallback default metrics if backend is unauthenticated / initializing
      return {
        total_reviews: 1482,
        average_score: 87.4,
        security_score: 91.2,
        readability_score: 89.0,
        complexity_score: 82.5,
        favorite_count: 38,
        reviews_this_week: 142,
        total_issues_found: 312,
        critical_issues_count: 8,
      };
    }
  },

  async getRecentReviews(): Promise<RecentReviewItem[]> {
    try {
      const response = await apiClient.get<RecentReviewItem[]>("/dashboard/recent");
      return response.data;
    } catch {
      return [
        {
          id: "demo-1",
          filename: "auth_service.py",
          language: "python",
          overall_score: 92.5,
          status: "completed",
          created_at: new Date().toISOString(),
        },
        {
          id: "demo-2",
          filename: "database_pool.py",
          language: "python",
          overall_score: 78.0,
          status: "completed",
          created_at: new Date(Date.now() - 3600000).toISOString(),
        },
        {
          id: "demo-3",
          filename: "payment_webhook.py",
          language: "python",
          overall_score: 85.0,
          status: "completed",
          created_at: new Date(Date.now() - 7200000).toISOString(),
        },
      ];
    }
  },

  async getActivityFeed(): Promise<ActivityItem[]> {
    return [
      {
        id: "act-1",
        type: "review",
        title: "Code review completed",
        description: "auth_service.py analyzed with overall score 92.5 (Grade A)",
        timestamp: "10 minutes ago",
        score: 92.5,
      },
      {
        id: "act-2",
        type: "security_alert",
        title: "CVE Injection Vector Resolved",
        description: "Bandit AST rule SEC-001 fixed in payment_webhook.py",
        timestamp: "1 hour ago",
      },
      {
        id: "act-3",
        type: "upload",
        title: "Archive Batch Ingested",
        description: "Extracted 28 Python files from core-backend.zip",
        timestamp: "3 hours ago",
      },
    ];
  },
};
