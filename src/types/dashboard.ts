export interface DashboardStats {
  total_reviews: number;
  average_score: number;
  security_score: number;
  readability_score: number;
  complexity_score: number;
  favorite_count: number;
  reviews_this_week: number;
  total_issues_found: number;
  critical_issues_count: number;
}

export interface ActivityItem {
  id: string;
  type: "review" | "upload" | "report" | "security_alert";
  title: string;
  description: string;
  timestamp: string;
  score?: number;
  badge?: string;
}

export interface RecentReviewItem {
  id: string;
  filename: string;
  language: string;
  overall_score: number;
  status: string;
  created_at: string;
}
