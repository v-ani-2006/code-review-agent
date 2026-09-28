"use client";

import { useState } from "react";
import { AlertCircle, AlertTriangle, ChevronDown, ChevronUp, Info, ShieldAlert } from "lucide-react";
import { CodeIssue } from "@/types/review";
import { CopyButton } from "@/components/common/copy-button";

interface IssueCardProps {
  issue: CodeIssue;
}

export function IssueCard({ issue }: IssueCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getSeverityStyle = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return {
          badge: "bg-rose-500/10 text-rose-400 border-rose-500/30",
          icon: ShieldAlert,
          border: "border-l-rose-500",
        };
      case "high":
        return {
          badge: "bg-amber-500/10 text-amber-400 border-amber-500/30",
          icon: AlertCircle,
          border: "border-l-amber-500",
        };
      case "medium":
        return {
          badge: "bg-cyan-500/10 text-cyan-400 border-cyan-500/30",
          icon: AlertTriangle,
          border: "border-l-cyan-500",
        };
      default:
        return {
          badge: "bg-indigo-500/10 text-indigo-400 border-indigo-500/30",
          icon: Info,
          border: "border-l-indigo-500",
        };
    }
  };

  const style = getSeverityStyle(issue.severity);
  const Icon = style.icon;

  return (
    <div
      className={`rounded-xl border border-border border-l-4 ${style.border} bg-card transition-all hover:border-border/80`}
    >
      <div
        onClick={() => setExpanded(!expanded)}
        className="flex cursor-pointer items-start justify-between gap-3 p-4 select-none"
      >
        <div className="flex items-start gap-3">
          <Icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <span className={`rounded-md border px-2 py-0.5 text-[11px] font-semibold uppercase ${style.badge}`}>
                {issue.severity}
              </span>
              <span className="rounded-md bg-secondary px-2 py-0.5 text-[11px] font-mono text-muted-foreground">
                Line {issue.line_number}
              </span>
              <span className="text-xs font-mono text-muted-foreground">[{issue.id}]</span>
            </div>
            <h4 className="text-sm font-semibold text-foreground">{issue.title}</h4>
          </div>
        </div>

        <button type="button" className="text-muted-foreground hover:text-foreground p-1">
          {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </div>

      {expanded && (
        <div className="border-t border-border/60 bg-secondary/10 p-4 pt-3 text-xs">
          <p className="text-muted-foreground leading-relaxed mb-3">{issue.description}</p>
          {issue.suggestion && (
            <div className="rounded-lg border border-border bg-[#0d1117] p-3 font-mono text-xs">
              <div className="flex items-center justify-between text-[11px] text-muted-foreground mb-1">
                <span className="font-semibold text-brand-400">💡 Suggested Fix:</span>
                <CopyButton text={issue.suggestion} />
              </div>
              <pre className="text-slate-200 overflow-x-auto whitespace-pre-wrap">{issue.suggestion}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
