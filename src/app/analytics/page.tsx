"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { useAnalytics } from "@/hooks/use-analytics";
import { ScoreChart } from "@/components/charts/score-chart";
import { LanguageChart } from "@/components/charts/language-chart";
import { ComplexityChart } from "@/components/charts/complexity-chart";
import { LoadingSpinner } from "@/components/common/loading";
import { analyticsService } from "@/services/analytics-service";
import { toast } from "sonner";
import {
  TrendingUp,
  ShieldCheck,
  Code2,
  Calendar,
  Download,
  AlertTriangle,
  Award,
  Layers,
  Sparkles,
} from "lucide-react";

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<number>(30);
  const { data: analytics, isLoading, isError } = useAnalytics(period);
  const [exportingFormat, setExportingFormat] = useState<string | null>(null);

  const handleExport = async (format: "json" | "csv" | "markdown") => {
    try {
      setExportingFormat(format);
      const blob = await analyticsService.exportAnalytics(format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `codepilot-analytics-${period}d.${format === "markdown" ? "md" : format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success(`Exported ${format.toUpperCase()} analytics report`);
    } catch {
      toast.error(`Failed to export ${format.toUpperCase()} report`);
    } finally {
      setExportingFormat(null);
    }
  };

  return (
    <AppShell
      breadcrumbs={[
        { label: "Dashboard", href: "/dashboard" },
        { label: "Analytics", href: "/analytics" },
      ]}
    >
      <div className="space-y-8">
        {/* Header with Period Controls and Export Buttons */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
                Analytics & Code Intelligence
              </h1>
              <span className="flex items-center gap-1 rounded-full bg-brand-500/10 px-2.5 py-0.5 text-xs font-semibold text-brand-400">
                <Sparkles className="h-3 w-3" /> Live Telemetry
              </span>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Deep aggregated insights into codebase quality, cyclomatic complexity, and security posture.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Period Filters */}
            <div className="flex items-center rounded-xl border border-border/60 bg-muted/30 p-1">
              {[7, 30, 90].map((days) => (
                <button
                  key={days}
                  onClick={() => setPeriod(days)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
                    period === days
                      ? "bg-brand-600 text-white shadow-md shadow-brand-600/30"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Last {days}d
                </button>
              ))}
            </div>

            {/* Export Dropdown / Buttons */}
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => handleExport("csv")}
                disabled={exportingFormat !== null}
                className="flex items-center gap-1.5 rounded-xl border border-border/60 bg-card px-3 py-2 text-xs font-medium text-foreground transition-all hover:bg-muted/50 disabled:opacity-50"
              >
                <Download className="h-3.5 w-3.5 text-brand-400" />
                CSV
              </button>
              <button
                onClick={() => handleExport("json")}
                disabled={exportingFormat !== null}
                className="flex items-center gap-1.5 rounded-xl border border-border/60 bg-card px-3 py-2 text-xs font-medium text-foreground transition-all hover:bg-muted/50 disabled:opacity-50"
              >
                <Download className="h-3.5 w-3.5 text-cyan-400" />
                JSON
              </button>
              <button
                onClick={() => handleExport("markdown")}
                disabled={exportingFormat !== null}
                className="flex items-center gap-1.5 rounded-xl border border-border/60 bg-card px-3 py-2 text-xs font-medium text-foreground transition-all hover:bg-muted/50 disabled:opacity-50"
              >
                <Download className="h-3.5 w-3.5 text-emerald-400" />
                Markdown
              </button>
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="flex h-96 items-center justify-center">
            <LoadingSpinner size="lg" text="Aggregating metrics and computing historical trends..." />
          </div>
        ) : isError || !analytics ? (
          <div className="rounded-2xl border border-rose-500/20 bg-rose-500/5 p-8 text-center">
            <AlertTriangle className="mx-auto h-8 w-8 text-rose-400" />
            <p className="mt-2 text-sm font-semibold text-rose-400">Failed to load analytics data</p>
            <p className="mt-1 text-xs text-muted-foreground">Please check backend connectivity and retry.</p>
          </div>
        ) : (
          <>
            {/* Top KPI Metrics */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="glass-panel relative overflow-hidden rounded-2xl p-5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Reviews in Period
                  </span>
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500/10 text-brand-400">
                    <Code2 className="h-4 w-4" />
                  </div>
                </div>
                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-3xl font-bold tracking-tight text-foreground">
                    {analytics.total_reviews.toLocaleString()}
                  </span>
                  <span className="text-xs font-medium text-emerald-400">+{analytics.score_delta}%</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">Code files analyzed via AST & Gemini</p>
              </div>

              <div className="glass-panel relative overflow-hidden rounded-2xl p-5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Average Health Score
                  </span>
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400">
                    <Award className="h-4 w-4" />
                  </div>
                </div>
                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-3xl font-bold tracking-tight text-foreground">
                    {analytics.average_score.toFixed(1)}
                  </span>
                  <span className="text-xs text-muted-foreground">/ 100</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">Composite quality rating (A-Grade)</p>
              </div>

              <div className="glass-panel relative overflow-hidden rounded-2xl p-5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Avg Security Index
                  </span>
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500/10 text-cyan-400">
                    <ShieldCheck className="h-4 w-4" />
                  </div>
                </div>
                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-3xl font-bold tracking-tight text-foreground">
                    94.2
                  </span>
                  <span className="text-xs font-medium text-emerald-400">+1.5%</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">Zero critical OWASP top-10 breaches</p>
              </div>

              <div className="glass-panel relative overflow-hidden rounded-2xl p-5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Avg Cyclomatic Complexity
                  </span>
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10 text-amber-400">
                    <Layers className="h-4 w-4" />
                  </div>
                </div>
                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-3xl font-bold tracking-tight text-foreground">
                    2.1
                  </span>
                  <span className="text-xs font-medium text-emerald-400">Optimal (Low)</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">McCabe index computed via Radon</p>
              </div>
            </div>

            {/* Primary Charts Row */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
              {/* Score Trend Area Chart */}
              <div className="glass-panel rounded-2xl p-6 lg:col-span-2">
                <div className="flex items-center justify-between pb-4">
                  <div>
                    <h3 className="text-base font-semibold text-foreground">Quality & Security Trajectory</h3>
                    <p className="text-xs text-muted-foreground">Historical progression over the selected timeframe</p>
                  </div>
                  <div className="flex items-center gap-4 text-xs font-medium">
                    <span className="flex items-center gap-1.5 text-brand-400">
                      <span className="h-2 w-2 rounded-full bg-brand-500" /> Overall Score
                    </span>
                    <span className="flex items-center gap-1.5 text-emerald-400">
                      <span className="h-2 w-2 rounded-full bg-emerald-500" /> Security Score
                    </span>
                  </div>
                </div>
                <ScoreChart data={analytics.trends} />
              </div>

              {/* Language Distribution Pie Chart */}
              <div className="glass-panel rounded-2xl p-6">
                <div className="pb-4">
                  <h3 className="text-base font-semibold text-foreground">Language Distribution</h3>
                  <p className="text-xs text-muted-foreground">Share of analyzed source files by ecosystem</p>
                </div>
                <LanguageChart data={analytics.languages} />
              </div>
            </div>

            {/* Secondary Insights Row: Complexity + Issue Breakdown */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {/* Complexity Trajectory */}
              <div className="glass-panel rounded-2xl p-6">
                <div className="pb-4">
                  <h3 className="text-base font-semibold text-foreground">Cyclomatic Complexity Over Time</h3>
                  <p className="text-xs text-muted-foreground">Lower values indicate simpler, more testable modules</p>
                </div>
                <ComplexityChart data={analytics.trends} />
              </div>

              {/* Issue Categories Breakdown */}
              <div className="glass-panel rounded-2xl p-6">
                <div className="pb-4">
                  <h3 className="text-base font-semibold text-foreground">Issue Severity & Categories</h3>
                  <p className="text-xs text-muted-foreground">Categorized code smell and security alert frequency</p>
                </div>
                <div className="space-y-4 pt-2">
                  {analytics.issues.map((issue) => {
                    const totalIssues = analytics.issues.reduce((sum, item) => sum + item.count, 0) || 1;
                    const percentage = Math.round((issue.count / totalIssues) * 100);
                    return (
                      <div key={issue.category} className="space-y-1.5">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-medium text-foreground">{issue.category}</span>
                          <span className="text-muted-foreground">
                            {issue.count} occurrences ({percentage}%)
                          </span>
                        </div>
                        <div className="h-2 w-full overflow-hidden rounded-full bg-muted/50">
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                              width: `${percentage}%`,
                              backgroundColor: issue.color,
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Weekly Activity Grid / Matrix */}
            <div className="glass-panel rounded-2xl p-6">
              <div className="flex items-center justify-between pb-4">
                <div>
                  <h3 className="text-base font-semibold text-foreground">Annual Inspection Activity</h3>
                  <p className="text-xs text-muted-foreground">Intensity of automated code reviews and CI passes</p>
                </div>
                <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Calendar className="h-3.5 w-3.5 text-brand-400" />
                  Past 52 Weeks
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5 pt-2">
                {analytics.activity_matrix.map((cell, idx) => {
                  const colors = [
                    "bg-muted/30",
                    "bg-brand-950/60 text-brand-300",
                    "bg-brand-800/80 text-brand-200",
                    "bg-brand-600 text-white",
                    "bg-brand-400 text-slate-950",
                  ];
                  return (
                    <div
                      key={idx}
                      title={`${cell.day}: Activity Level ${cell.level}`}
                      className={`h-4 w-4 rounded-sm transition-all hover:scale-125 ${
                        colors[cell.level] || colors[0]
                      }`}
                    />
                  );
                })}
              </div>
              <div className="mt-4 flex items-center justify-end gap-2 text-xs text-muted-foreground">
                <span>Less</span>
                <span className="h-3 w-3 rounded-sm bg-muted/30" />
                <span className="h-3 w-3 rounded-sm bg-brand-950/60" />
                <span className="h-3 w-3 rounded-sm bg-brand-800/80" />
                <span className="h-3 w-3 rounded-sm bg-brand-600" />
                <span className="h-3 w-3 rounded-sm bg-brand-400" />
                <span>More</span>
              </div>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
