"use client";

import { CheckCircle2, Clock, Loader2, XCircle } from "lucide-react";
import { BatchTaskStatus } from "@/types/upload";

interface BatchStatusProps {
  task: BatchTaskStatus;
}

export function BatchStatus({ task }: BatchStatusProps) {
  const isRunning = task.status === "RUNNING" || task.status === "PENDING";
  const isCompleted = task.status === "COMPLETED";
  const isFailed = task.status === "FAILED";

  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {isRunning && <Loader2 className="h-4 w-4 animate-spin text-brand-400" />}
          {isCompleted && <CheckCircle2 className="h-4 w-4 text-emerald-400" />}
          {isFailed && <XCircle className="h-4 w-4 text-rose-400" />}
          <span className="font-semibold text-sm text-foreground">
            Batch Task: {task.id.slice(0, 8)}...
          </span>
        </div>
        <span
          className={`rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase ${
            isCompleted
              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
              : isFailed
              ? "bg-rose-500/10 text-rose-400 border border-rose-500/30"
              : "bg-brand-500/10 text-brand-400 border border-brand-500/30"
          }`}
        >
          {task.status}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full rounded-full bg-secondary h-2.5 overflow-hidden my-3">
        <div
          className="h-full bg-gradient-to-r from-brand-500 to-cyan-400 transition-all duration-500"
          style={{ width: `${task.progress_percentage || 0}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-xs text-muted-foreground mt-2">
        <span>
          Processed: {task.processed_files} / {task.total_files} files
        </span>
        <span>{task.progress_percentage.toFixed(0)}% Complete</span>
      </div>
    </div>
  );
}
