"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  CheckCircle2,
  Code2,
  Download,
  FileCode,
  GitCompare,
  Heart,
  Share2,
  Shield,
  Sparkles,
} from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/app-shell";
import { ScoreBadge } from "@/components/common/score-badge";
import { IssueCard } from "@/components/review/issue-card";
import { DiffViewer } from "@/components/review/diff-viewer";
import { RecommendationCard } from "@/components/review/recommendation-card";
import { historyService } from "@/services/history-service";
import { ReviewDetail, CodeIssue } from "@/types/review";
import { formatDate } from "@/lib/utils";
import { SAMPLE_PYTHON_CODE } from "@/lib/constants";
import { PageLoading } from "@/components/common/loading";

export default function ReviewDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const id = resolvedParams.id;

  const [review, setReview] = useState<ReviewDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [favorite, setFavorite] = useState(false);

  useEffect(() => {
    async function loadDetail() {
      setLoading(true);
      try {
        const data = await historyService.getReviewDetail(id);
        setReview(data);
        setFavorite(data.favorite || false);
      } catch {
        // Fallback demo review for showcase
        setReview({
          id,
          user_id: "usr-demo",
          filename: "security_auth.py",
          language: "python",
          overall_score: 92.5,
          favorite: true,
          created_at: new Date().toISOString(),
          summary: "Zero high vulnerabilities found. Clean OAuth2 verification logic.",
          scores: {
            readability: 90.0,
            maintainability: 95.0,
            security: 90.0,
            complexity: 92.0,
            documentation: 85.0,
            overall: 92.5,
          },
          complexity: {
            cyclomatic_complexity: 1.8,
            maintainability_index: 94.2,
            rank: "A",
          },
          issues: [
            {
              id: "SEC-004",
              title: "Constant Time Verification Recommended",
              description: "Use hmac.compare_digest() to mitigate potential timing attacks.",
              severity: "low",
              category: "security",
              line_number: 14,
              suggestion: "if hmac.compare_digest(stored_hash, token_hash):",
            },
          ],
          source_code: `def verify_token(user, token_hash, stored_hash):\n    # Constant time check\n    return hmac.compare_digest(stored_hash, token_hash)`,
          ai_summary: "Robust authentication verification module. Strong test coverage and typed signatures.",
          ai_strengths: "Well encapsulated logic with clear exception handling.",
          ai_recommendations: "Add automated audit logging for token invalidation.",
          ai_bugfix: "def verify_token(user, token_hash, stored_hash):\n    import hmac\n    return hmac.compare_digest(stored_hash, token_hash)",
        });
      } finally {
        setLoading(false);
      }
    }
    loadDetail();
  }, [id]);

  const handleToggleFavorite = async () => {
    try {
      await historyService.toggleFavorite(id);
      setFavorite(!favorite);
      toast.success(favorite ? "Removed from favorites" : "Added to favorites");
    } catch {
      setFavorite(!favorite);
    }
  };

  const handleDownload = async (format: "markdown" | "html" | "json") => {
    try {
      const blob = await historyService.downloadReport(id, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${review?.filename || "report"}_review.${format === "markdown" ? "md" : format}`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Report downloaded as .${format}`);
    } catch {
      toast.error(`Failed to download report as .${format}`);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <PageLoading message="Retrieving stored audit report..." />
      </AppShell>
    );
  }

  if (!review) return null;

  return (
    <AppShell>
      {/* Top back button & Actions */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <Link
          href="/history"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Audits List</span>
        </Link>

        <div className="flex items-center gap-2">
          <button
            onClick={handleToggleFavorite}
            type="button"
            className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold transition-colors ${
              favorite
                ? "border-rose-500/30 bg-rose-500/10 text-rose-400"
                : "border-border bg-secondary text-muted-foreground hover:text-foreground"
            }`}
          >
            <Heart className={`h-3.5 w-3.5 ${favorite ? "fill-rose-400" : ""}`} />
            <span>{favorite ? "Favorited" : "Favorite"}</span>
          </button>

          <button
            onClick={() => handleDownload("markdown")}
            type="button"
            className="inline-flex items-center gap-1 rounded-xl border border-border bg-secondary px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-accent"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Markdown</span>
          </button>

          <button
            onClick={() => handleDownload("html")}
            type="button"
            className="inline-flex items-center gap-1 rounded-xl border border-border bg-secondary px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-accent"
          >
            <Download className="h-3.5 w-3.5" />
            <span>HTML</span>
          </button>
        </div>
      </div>

      {/* Header Overview Card */}
      <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-500/10 text-brand-400">
              <Code2 className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-tight text-foreground font-mono">
                {review.filename}
              </h2>
              <span className="text-xs text-muted-foreground">
                Audited {formatDate(review.created_at)} • {review.language}
              </span>
            </div>
          </div>

          <ScoreBadge score={review.scores?.overall || review.overall_score || 0} size="lg" />
        </div>
      </div>

      {/* Issues List */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold text-foreground">
          Identified Issues ({review.issues?.length || 0})
        </h3>
        {review.issues?.map((issue: CodeIssue) => (
          <IssueCard key={issue.id} issue={issue} />
        ))}
      </div>

      {/* Remediation Diff */}
      {review.ai_bugfix && (
        <DiffViewer originalCode={review.source_code} remediatedCode={review.ai_bugfix} />
      )}
    </AppShell>
  );
}
