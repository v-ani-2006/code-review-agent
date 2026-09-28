import { AlertTriangle, RotateCcw } from "lucide-react";

interface ErrorCardProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export function ErrorCard({
  title = "Something went wrong",
  message = "Failed to communicate with the CodePilot backend service.",
  onRetry,
}: ErrorCardProps) {
  return (
    <div className="rounded-2xl border border-rose-500/20 bg-rose-500/5 p-6 text-center">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-rose-500/10 text-rose-400 mb-3">
        <AlertTriangle className="h-6 w-6" />
      </div>
      <h4 className="text-base font-semibold text-rose-200">{title}</h4>
      <p className="mt-1 text-sm text-rose-300/80 max-w-md mx-auto">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          type="button"
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-rose-500/20 px-3.5 py-1.5 text-xs font-semibold text-rose-200 hover:bg-rose-500/30 transition-colors"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Retry Request
        </button>
      )}
    </div>
  );
}
