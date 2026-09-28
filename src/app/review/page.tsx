"use client";

import { useState } from "react";
import {
  AlertTriangle,
  Award,
  CheckCircle2,
  Cpu,
  FileCode,
  GitCompare,
  Lightbulb,
  Play,
  RotateCcw,
  Shield,
  Sparkles,
  Zap,
} from "lucide-react";
import confetti from "canvas-confetti";
import { AppShell } from "@/components/layout/app-shell";
import { CodeEditor } from "@/components/review/code-editor";
import { ReviewSummary } from "@/components/review/review-summary";
import { IssueCard } from "@/components/review/issue-card";
import { RecommendationCard } from "@/components/review/recommendation-card";
import { DiffViewer } from "@/components/review/diff-viewer";
import { MarkdownViewer } from "@/components/common/markdown-viewer";
import { useReviewStore } from "@/stores/review-store";
import { Spinner } from "@/components/common/loading";

export default function ReviewPage() {
  const {
    code,
    report,
    aiReview,
    isAnalyzing,
    isAiReviewing,
    activeTab,
    setActiveTab,
    runStaticAnalysis,
    runAiReview,
  } = useReviewStore();

  const handleFullAudit = async () => {
    await runStaticAnalysis();
    await runAiReview();
    if (report && report.scores.overall >= 85) {
      confetti({
        particleCount: 60,
        spread: 60,
        origin: { y: 0.7 },
      });
    }
  };

  return (
    <AppShell>
      {/* Header bar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-foreground md:text-2xl flex items-center gap-2">
            <span>Interactive Code Review</span>
            <span className="rounded-full bg-brand-500/10 border border-brand-500/20 px-2.5 py-0.5 text-xs text-brand-300 font-normal">
              Python AST + Gemini 2.5
            </span>
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Edit or paste code into the Monaco Editor, run deterministic AST scans, and generate AI refactorings.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleFullAudit}
            disabled={isAnalyzing || isAiReviewing}
            type="button"
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 via-indigo-600 to-cyan-500 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-brand-500/20 hover:brightness-110 disabled:opacity-50 transition-all"
          >
            {isAnalyzing || isAiReviewing ? (
              <Spinner className="h-4 w-4" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            <span>Run Complete Audit</span>
          </button>
        </div>
      </div>

      {/* Monaco Code Editor */}
      <CodeEditor />

      {/* Review Results Section */}
      {(report || aiReview || isAnalyzing || isAiReviewing) && (
        <div className="space-y-6 pt-4">
          {/* Summary Box */}
          {report && <ReviewSummary report={report} />}

          {/* Navigation Tabs */}
          <div className="flex flex-wrap items-center gap-2 border-b border-border pb-3 text-xs font-semibold">
            <button
              onClick={() => setActiveTab("issues")}
              className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-2 transition-all ${
                activeTab === "issues"
                  ? "bg-brand-500 text-white shadow-md shadow-brand-500/20"
                  : "bg-secondary text-muted-foreground hover:text-foreground"
              }`}
            >
              <AlertTriangle className="h-3.5 w-3.5" />
              <span>Issues & Vulnerabilities ({report?.issues?.length || 0})</span>
            </button>

            <button
              onClick={() => setActiveTab("diff")}
              className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-2 transition-all ${
                activeTab === "diff"
                  ? "bg-brand-500 text-white shadow-md shadow-brand-500/20"
                  : "bg-secondary text-muted-foreground hover:text-foreground"
              }`}
            >
              <GitCompare className="h-3.5 w-3.5" />
              <span>Automated Remediation Diff</span>
            </button>

            <button
              onClick={() => setActiveTab("docs")}
              className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-2 transition-all ${
                activeTab === "docs"
                  ? "bg-brand-500 text-white shadow-md shadow-brand-500/20"
                  : "bg-secondary text-muted-foreground hover:text-foreground"
              }`}
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>Gemini AI Insights</span>
            </button>
          </div>

          {/* Tab Content: Issues */}
          {activeTab === "issues" && (
            <div className="space-y-3">
              {report?.issues && report.issues.length > 0 ? (
                report.issues.map((issue) => <IssueCard key={issue.id} issue={issue} />)
              ) : (
                <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-8 text-center text-xs text-emerald-300">
                  <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-400 mb-2" />
                  <span className="font-semibold text-sm block">Zero Issues Detected</span>
                  Your code passed all AST syntax checks, Radon complexity thresholds, and Bandit security heuristics!
                </div>
              )}
            </div>
          )}

          {/* Tab Content: Remediation Diff */}
          {activeTab === "diff" && (
            <DiffViewer
              originalCode={code}
              remediatedCode={
                aiReview?.bugfix ||
                `# Automated Remediated Code\nimport hmac\nimport subprocess\n\ndef authenticate_user(username: str, password_attempt: str, stored_hash: str) -> bool:\n    computed_hash = hashlib.sha256(password_attempt.encode()).hexdigest()\n    if hmac.compare_digest(computed_hash, stored_hash):\n        subprocess.run(["logger", f"User {username} authenticated"], check=True)\n        return True\n    return False`
              }
            />
          )}

          {/* Tab Content: AI Recommendations */}
          {activeTab === "docs" && (
            <div>
              {aiReview ? (
                <RecommendationCard aiReview={aiReview} />
              ) : (
                <div className="rounded-2xl border border-dashed border-border p-8 text-center text-xs text-muted-foreground">
                  <Sparkles className="mx-auto h-6 w-6 text-brand-400 mb-2 animate-pulse" />
                  Click <strong>&quot;Gemini AI Review&quot;</strong> in the editor toolbar to generate deep architectural insights.
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </AppShell>
  );
}
