import Link from "next/link";
import { ArrowLeft, FileQuestion } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex min-h-[70vh] flex-col items-center justify-center p-6 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-500/10 text-brand-400 mb-4">
        <FileQuestion className="h-8 w-8" />
      </div>
      <h1 className="text-3xl font-black tracking-tight text-foreground">404</h1>
      <h2 className="text-base font-semibold text-foreground mt-1">Page Not Found</h2>
      <p className="mt-1 text-xs text-muted-foreground max-w-sm">
        The requested review report, page, or resource could not be found.
      </p>
      <Link
        href="/dashboard"
        className="mt-6 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-brand-500/20 hover:from-brand-500 hover:to-indigo-500 transition-all"
      >
        <ArrowLeft className="h-4 w-4" />
        <span>Back to Dashboard</span>
      </Link>
    </div>
  );
}
