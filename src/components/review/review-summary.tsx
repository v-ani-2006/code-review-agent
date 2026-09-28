"use client";

import { CheckCircle2, Clock, Cpu, FileSearch, Lock, Shield, Zap } from "lucide-react";
import { getGradeColor, getScoreColor } from "@/lib/utils";
import { ReviewReport } from "@/types/review";

interface ReviewSummaryProps {
  report: ReviewReport;
}

export function ReviewSummary({ report }: ReviewSummaryProps) {
  const overall = report.scores?.overall || 0;
  const grade = report.complexity?.rank || (overall >= 90 ? "A" : overall >= 80 ? "B" : overall >= 70 ? "C" : "F");
  const gradeColors = getGradeColor(grade);

  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-xl">
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between border-b border-border/80 pb-6">
        {/* Score & Grade Display */}
        <div className="flex items-center gap-5">
          <div className="relative flex h-24 w-24 shrink-0 items-center justify-center rounded-2xl bg-secondary/80 border border-border shadow-inner">
            <div className="text-center">
              <span className={`text-4xl font-black ${gradeColors.text}`}>{grade}</span>
              <span className="block text-[11px] font-medium text-muted-foreground">Rank</span>
            </div>
            {/* Glow border ring */}
            <div className={`absolute -inset-0.5 rounded-2xl ${gradeColors.bg} opacity-20 blur-sm -z-10`} />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-2xl font-bold tracking-tight text-foreground">
                {overall.toFixed(1)}
                <span className="text-base font-normal text-muted-foreground"> / 100</span>
              </h2>
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold border ${gradeColors.badge}`}>
                Overall Score
              </span>
            </div>
            <p className="mt-1 text-sm text-muted-foreground line-clamp-2 max-w-xl">
              {report.summary}
            </p>
          </div>
        </div>

        {/* Timing & Meta */}
        <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
          {report.processing_time && (
            <div className="flex items-center gap-1.5 rounded-xl border border-border bg-secondary/30 px-3 py-1.5">
              <Clock className="h-3.5 w-3.5 text-brand-400" />
              <span>{report.processing_time.toFixed(4)}s runtime</span>
            </div>
          )}
          {report.complexity && (
            <div className="flex items-center gap-1.5 rounded-xl border border-border bg-secondary/30 px-3 py-1.5">
              <Cpu className="h-3.5 w-3.5 text-cyan-400" />
              <span>CC: {report.complexity.cyclomatic_complexity.toFixed(1)}</span>
            </div>
          )}
        </div>
      </div>

      {/* Sub-Score Category Cards */}
      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-5">
        <div className="rounded-xl border border-border/80 bg-secondary/20 p-3.5 text-center">
          <Shield className="mx-auto h-4 w-4 text-emerald-400 mb-1" />
          <span className="text-[11px] text-muted-foreground block">Security</span>
          <span className={`text-lg font-bold ${getScoreColor(report.scores?.security || 0)}`}>
            {(report.scores?.security || 0).toFixed(0)}
          </span>
        </div>

        <div className="rounded-xl border border-border/80 bg-secondary/20 p-3.5 text-center">
          <Lock className="mx-auto h-4 w-4 text-cyan-400 mb-1" />
          <span className="text-[11px] text-muted-foreground block">Maintainability</span>
          <span className={`text-lg font-bold ${getScoreColor(report.scores?.maintainability || 0)}`}>
            {(report.scores?.maintainability || 0).toFixed(0)}
          </span>
        </div>

        <div className="rounded-xl border border-border/80 bg-secondary/20 p-3.5 text-center">
          <FileSearch className="mx-auto h-4 w-4 text-indigo-400 mb-1" />
          <span className="text-[11px] text-muted-foreground block">Readability</span>
          <span className={`text-lg font-bold ${getScoreColor(report.scores?.readability || 0)}`}>
            {(report.scores?.readability || 0).toFixed(0)}
          </span>
        </div>

        <div className="rounded-xl border border-border/80 bg-secondary/20 p-3.5 text-center">
          <Cpu className="mx-auto h-4 w-4 text-amber-400 mb-1" />
          <span className="text-[11px] text-muted-foreground block">Complexity</span>
          <span className={`text-lg font-bold ${getScoreColor(report.scores?.complexity || 0)}`}>
            {(report.scores?.complexity || 0).toFixed(0)}
          </span>
        </div>

        <div className="rounded-xl border border-border/80 bg-secondary/20 p-3.5 text-center col-span-2 sm:col-span-1">
          <CheckCircle2 className="mx-auto h-4 w-4 text-purple-400 mb-1" />
          <span className="text-[11px] text-muted-foreground block">Documentation</span>
          <span className={`text-lg font-bold ${getScoreColor(report.scores?.documentation || 0)}`}>
            {(report.scores?.documentation || 0).toFixed(0)}
          </span>
        </div>
      </div>
    </div>
  );
}
