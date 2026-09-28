export function Spinner({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <svg
      className={`animate-spin text-current ${className}`}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

export function LoadingSpinner({
  size = "md",
  text,
  className = "",
}: {
  size?: "sm" | "md" | "lg";
  text?: string;
  className?: string;
}) {
  const sizeMap = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-10 w-10",
  };

  return (
    <div className={`flex flex-col items-center justify-center gap-3 ${className}`}>
      <Spinner className={`${sizeMap[size]} text-brand-400`} />
      {text && <p className="text-xs text-muted-foreground animate-pulse">{text}</p>}
    </div>
  );
}

export function PageLoading({ message = "Loading CodePilot AI..." }: { message?: string }) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3">
      <div className="relative">
        <div className="h-12 w-12 rounded-full border-2 border-brand-500/20 border-t-brand-500 animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-4 w-4 rounded-full bg-brand-500/80 animate-pulse" />
        </div>
      </div>
      <p className="text-sm font-medium text-muted-foreground animate-pulse">{message}</p>
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm animate-pulse">
      <div className="h-4 w-1/3 rounded bg-muted mb-4" />
      <div className="h-8 w-1/2 rounded bg-muted mb-2" />
      <div className="h-3 w-3/4 rounded bg-muted/60" />
    </div>
  );
}
