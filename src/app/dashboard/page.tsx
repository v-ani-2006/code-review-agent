"use client";

import { AppShell } from "@/components/layout/app-shell";
import { OverviewCards } from "@/components/dashboard/overview-cards";
import { QuickActions } from "@/components/dashboard/quick-actions";
import { RecentReviews } from "@/components/dashboard/recent-reviews";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { ScoreChart } from "@/components/charts/score-chart";
import { useDashboard } from "@/hooks/use-dashboard";
import { useAnalytics } from "@/hooks/use-analytics";
import { Sparkles } from "lucide-react";

export default function DashboardPage() {
  const { stats, recentReviews, activityFeed } = useDashboard();
  const { data: analyticsData } = useAnalytics(30);

  return (
    <AppShell>
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-brand-500/30 bg-gradient-to-r from-brand-600/15 via-indigo-600/10 to-cyan-500/15 p-6 md:p-8 backdrop-blur-xl">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-brand-500/30 bg-brand-500/10 px-3 py-1 text-xs font-semibold text-brand-300 mb-3">
            <Sparkles className="h-3.5 w-3.5 text-cyan-300" />
            <span>AI Code Review Platform v1.0.0</span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Welcome to CodePilot AI Dashboard
          </h2>
          <p className="mt-2 text-xs md:text-sm text-muted-foreground leading-relaxed">
            Autonomous static AST scanning, Radon complexity calculation, and Google Gemini 2.5 Flash reasoning. All systems operational.
          </p>
        </div>
      </div>

      {/* Metrics Overview Cards */}
      <OverviewCards stats={stats} />

      {/* Quick Action Shortcuts */}
      <QuickActions />

      {/* Main Grid: Chart + Recent Reviews */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left 2 Cols: Score Trend Chart */}
        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-foreground">Quality Score Trajectory</h3>
              <p className="text-xs text-muted-foreground">Rolling 30-day composite score & security health</p>
            </div>
            <span className="rounded-md border border-brand-500/30 bg-brand-500/10 px-2.5 py-1 text-xs font-semibold text-brand-300">
              Avg: {(stats?.average_score || 88.5).toFixed(1)}%
            </span>
          </div>
          <ScoreChart data={analyticsData?.trends || []} />
        </div>

        {/* Right 1 Col: Live Activity Stream */}
        <ActivityFeed items={activityFeed} />
      </div>

      {/* Recent Audits Table */}
      <RecentReviews items={recentReviews} />
    </AppShell>
  );
}
