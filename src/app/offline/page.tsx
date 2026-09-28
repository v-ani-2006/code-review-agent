"use client";

import { WifiOff, RefreshCw, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function OfflinePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4 text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-brand-500/10 text-brand-400">
        <WifiOff className="h-10 w-10" />
      </div>
      <h1 className="mt-6 text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
        You Are Currently Offline
      </h1>
      <p className="mt-2 max-w-md text-sm text-muted-foreground">
        CodePilot AI requires an active network connection to connect with local Docker backend services and Gemini LLM.
      </p>
      <div className="mt-6 flex items-center gap-3">
        <button
          onClick={() => window.location.reload()}
          className="flex items-center gap-1.5 rounded-xl bg-brand-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-brand-500/20 hover:bg-brand-500"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Retry Connection
        </button>
        <Link
          href="/dashboard"
          className="flex items-center gap-1.5 rounded-xl border border-border/60 bg-card px-4 py-2 text-xs font-medium text-foreground hover:bg-muted/50"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Dashboard
        </Link>
      </div>
    </div>
  );
}
