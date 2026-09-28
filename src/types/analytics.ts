export interface TrendPoint {
  date: string;
  score: number;
  reviews_count: number;
  security_score: number;
  complexity: number;
}

export interface LanguageMetric {
  language: string;
  count: number;
  percentage: number;
  average_score: number;
}

export interface IssueDistribution {
  category: string;
  count: number;
  color: string;
}

export interface AnalyticsSummary {
  period_days: number;
  total_reviews: number;
  average_score: number;
  score_delta: number;
  trends: TrendPoint[];
  languages: LanguageMetric[];
  issues: IssueDistribution[];
  activity_matrix: { day: string; level: number }[];
}
