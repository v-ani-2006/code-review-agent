"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  Bot,
  ChevronLeft,
  ChevronRight,
  Code2,
  Files,
  FileText,
  History,
  LayoutDashboard,
  LogOut,
  Settings,
  Sparkles,
  UploadCloud,
  User,
} from "lucide-react";
import { NAVIGATION_ITEMS } from "@/lib/constants";
import { useAuthStore } from "@/stores/auth-store";
import { useUIStore } from "@/stores/ui-store";

const iconMap: Record<string, any> = {
  LayoutDashboard,
  Code2,
  UploadCloud,
  History,
  BarChart3,
  FileText,
  Files,
  Activity,
  Settings,
  User,
};

export function Sidebar() {
  const pathname = usePathname();
  const { isSidebarOpen, toggleSidebar } = useUIStore();
  const { user, logout } = useAuthStore();

  return (
    <aside
      className={`relative hidden md:flex flex-col border-r border-border bg-card/60 backdrop-blur-xl transition-all duration-300 z-30 ${
        isSidebarOpen ? "w-64" : "w-20"
      }`}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-border/80">
        <Link href="/dashboard" className="flex items-center gap-3 overflow-hidden">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-500 to-cyan-400 text-white shadow-lg shadow-brand-500/20">
            <Bot className="h-5 w-5" />
          </div>
          {isSidebarOpen && (
            <div className="flex flex-col">
              <span className="font-bold tracking-tight text-foreground text-sm flex items-center gap-1.5">
                CodePilot AI
                <span className="rounded bg-brand-500/20 px-1 py-0.2 text-[10px] font-semibold text-brand-400">
                  v1.0
                </span>
              </span>
              <span className="text-[11px] text-muted-foreground truncate">AST & AI Code Review</span>
            </div>
          )}
        </Link>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 space-y-1.5 overflow-y-auto px-3 py-4">
        {NAVIGATION_ITEMS.map((item) => {
          const Icon = iconMap[item.icon] || Code2;
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                isActive
                  ? "bg-brand-500/15 text-brand-300 shadow-sm shadow-brand-500/10 border border-brand-500/30"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
              title={!isSidebarOpen ? item.title : undefined}
            >
              <Icon
                className={`h-5 w-5 shrink-0 transition-colors ${
                  isActive ? "text-brand-400" : "text-muted-foreground group-hover:text-foreground"
                }`}
              />
              {isSidebarOpen && <span className="truncate">{item.title}</span>}
            </Link>
          );
        })}
      </nav>

      {/* User & Collapse Footer */}
      <div className="border-t border-border/80 p-3">
        {isSidebarOpen && (
          <div className="mb-2 flex items-center justify-between rounded-xl bg-secondary/50 p-2">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-500/20 text-brand-300 font-semibold text-xs">
                {user?.username ? user.username.charAt(0).toUpperCase() : "U"}
              </div>
              <div className="flex flex-col truncate">
                <span className="text-xs font-semibold text-foreground truncate">
                  {user?.full_name || user?.username || "Developer"}
                </span>
                <span className="text-[10px] text-muted-foreground truncate">
                  {user?.email || "developer@codepilot.ai"}
                </span>
              </div>
            </div>
            <button
              onClick={() => logout()}
              type="button"
              className="rounded-lg p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
              title="Sign Out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        )}

        <button
          onClick={toggleSidebar}
          type="button"
          className="flex w-full items-center justify-center rounded-xl border border-border bg-secondary/40 py-2 text-xs font-medium text-muted-foreground hover:bg-secondary hover:text-foreground transition-all"
        >
          {isSidebarOpen ? (
            <>
              <ChevronLeft className="mr-1.5 h-4 w-4" /> Collapse Sidebar
            </>
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </button>
      </div>
    </aside>
  );
}
