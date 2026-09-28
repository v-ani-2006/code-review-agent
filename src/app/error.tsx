"use client";

import { useEffect } from "react";
import { AlertOctagon, RotateCcw } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("CodePilot UI Exception:", error);
  }, [error]);

  return (
    <div className="flex min-h-[70vh] flex-col items-center justify-center p-6 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-rose-500/10 text-rose-400 mb-4">
        <AlertOctagon className="h-8 w-8" />
      </div>
      <h2 className="text-xl font-bold tracking-tight text-foreground">Something went wrong</h2>
      <p className="mt-1 text-sm text-muted-foreground max-w-md">
        An unexpected application error occurred. You can retry the operation or return to the dashboard.
      </p>
      <div className="mt-6 flex items-center gap-3">
        <button
          onClick={() => reset()}
          type="button"
          className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-brand-500/20 hover:from-brand-500 hover:to-indigo-500 transition-all"
        >
          <RotateCcw className="h-4 w-4" />
          <span>Try Again</span>
        </button>
        <a
          href="/dashboard"
          className="rounded-xl border border-border bg-secondary px-4 py-2 text-sm font-medium text-foreground hover:bg-accent transition-colors"
        >
          Return to Dashboard
        </a>
      </div>
    </div>
  );
}
