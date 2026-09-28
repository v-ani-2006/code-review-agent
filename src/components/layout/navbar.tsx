"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, Command, Menu, PlusCircle, Search, ShieldCheck } from "lucide-react";
import { useUIStore } from "@/stores/ui-store";
import { ThemeToggle } from "./theme-toggle";

export function Navbar() {
  const pathname = usePathname();
  const { setMobileSidebarOpen, setSearchOpen } = useUIStore();

  // Compute page title from path
  const getPageTitle = (path: string) => {
    if (path.startsWith("/review")) return "Interactive Code Review";
    if (path.startsWith("/dashboard")) return "Executive Dashboard";
    if (path.startsWith("/upload")) return "Project Upload & Batch Analysis";
    if (path.startsWith("/history")) return "Review Audit History";
    if (path.startsWith("/analytics")) return "Quality & Security Analytics";
    if (path.startsWith("/documentation")) return "AI Documentation Suite";
    if (path.startsWith("/reports")) return "Deliverable Reports";
    if (path.startsWith("/monitoring")) return "System Health & Monitoring";
    if (path.startsWith("/settings")) return "Settings & Preferences";
    if (path.startsWith("/profile")) return "Developer Profile";
    return "CodePilot AI";
  };

  return (
    <header className="sticky top-0 z-20 flex h-16 w-full items-center justify-between border-b border-border/80 bg-background/80 px-4 md:px-6 backdrop-blur-xl">
      {/* Left: Mobile trigger & Page title */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setMobileSidebarOpen(true)}
          type="button"
          className="md:hidden flex h-9 w-9 items-center justify-center rounded-xl border border-border text-muted-foreground hover:bg-secondary"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-base font-bold tracking-tight text-foreground md:text-lg">
            {getPageTitle(pathname)}
          </h1>
        </div>
      </div>

      {/* Right: Actions, Search, Docs, Theme */}
      <div className="flex items-center gap-2.5">
        {/* Swagger Docs Link */}
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noreferrer"
          className="hidden lg:inline-flex items-center gap-1.5 rounded-xl border border-border/80 bg-secondary/40 px-3 py-1.5 text-xs font-semibold text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
          title="Open interactive FastAPI Swagger documentation"
        >
          <BookOpen className="h-3.5 w-3.5 text-brand-400" />
          <span>Swagger API</span>
        </a>

        {/* Global Search Button */}
        <button
          onClick={() => setSearchOpen(true)}
          type="button"
          className="hidden sm:inline-flex items-center gap-2 rounded-xl border border-border/80 bg-secondary/40 px-3 py-1.5 text-xs text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
        >
          <Search className="h-3.5 w-3.5" />
          <span>Quick search...</span>
          <kbd className="hidden lg:inline-block rounded border border-border bg-secondary px-1.5 py-0.5 text-[10px] font-mono">
            ⌘K
          </kbd>
        </button>

        {/* New Review Quick Action */}
        <Link
          href="/review"
          className="inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-brand-600 via-indigo-600 to-cyan-500 px-3.5 py-1.5 text-xs font-semibold text-white shadow-md shadow-brand-500/20 hover:brightness-110 transition-all"
        >
          <PlusCircle className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">New Review</span>
        </Link>

        {/* Theme Toggle */}
        <ThemeToggle />
      </div>
    </header>
  );
}
