export interface CodeIssue {
  id: string;
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  category: "security" | "bug_risk" | "complexity" | "style" | "readability" | "performance";
  line_number: number;
  column?: number | null;
  suggestion?: string | null;
}

export interface ComplexityMetrics {
  cyclomatic_complexity: number;
  maintainability_index: number;
  rank: "A" | "B" | "C" | "D" | "F";
}

export interface ReviewScores {
  readability: number;
  maintainability: number;
  security: number;
  complexity: number;
  documentation: number;
  overall: number;
}

export interface ReviewReport {
  id?: string;
  summary: string;
  scores: ReviewScores;
  issues: CodeIssue[];
  top_issues?: CodeIssue[];
  complexity: ComplexityMetrics;
  suggestions?: Record<string, string[]>;
  security_findings?: any[];
  processing_time?: number;
  version?: string;
  timestamp?: string;
}

export interface AIReviewResponse {
  summary: string;
  strengths: string[];
  recommendations: string[];
  bugfix?: string | null;
  model_used: string;
  processing_time: number;
}

export interface ReviewDetail extends ReviewReport {
  id: string;
  user_id: string;
  filename: string;
  language: string;
  source_code: string;
  favorite: boolean;
  ai_summary?: string | null;
  ai_strengths?: string | null;
  ai_recommendations?: string | null;
  ai_bugfix?: string | null;
  ai_documentation?: string | null;
  ai_test_code?: string | null;
  overall_score?: number;
  created_at: string;
}

export interface ReviewListItem {
  id: string;
  filename: string;
  language: string;
  overall_score: number;
  status: string;
  favorite: boolean;
  created_at: string;
  summary?: string;
}
