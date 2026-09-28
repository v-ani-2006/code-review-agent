"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  Bot,
  Code2,
  Files,
  FileText,
  History,
  LayoutDashboard,
  LogOut,
  Settings,
  UploadCloud,
  User,
  X,
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

export function MobileSidebar() {
  const pathname = usePathname();
  const { isMobileSidebarOpen, setMobileSidebarOpen } = useUIStore();
  const { user, logout } = useAuthStore();

  if (!isMobileSidebarOpen) return null;

  return (
    <div className="fixed inset-0 z-50 md:hidden flex">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-background/80 backdrop-blur-sm"
        onClick={() => setMobileSidebarOpen(false)}
      />

      {/* Drawer */}
      <div className="relative flex w-72 flex-col bg-card border-r border-border p-4 shadow-2xl z-10">
        <div className="flex items-center justify-between border-b border-border/80 pb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-500 to-cyan-400 text-white shadow-lg shadow-brand-500/20">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <span className="font-bold tracking-tight text-foreground text-sm block">CodePilot AI</span>
              <span className="text-[10px] text-muted-foreground">AST & AI Code Review</span>
            </div>
          </div>
          <button
            onClick={() => setMobileSidebarOpen(false)}
            type="button"
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-secondary"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1.5 overflow-y-auto py-4">
          {NAVIGATION_ITEMS.map((item) => {
            const Icon = iconMap[item.icon] || Code2;
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileSidebarOpen(false)}
                className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                  isActive
                    ? "bg-brand-500/15 text-brand-300 border border-brand-500/30"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                }`}
              >
                <Icon className={`h-5 w-5 ${isActive ? "text-brand-400" : "text-muted-foreground"}`} />
                <span>{item.title}</span>
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-border pt-4">
          <button
            onClick={() => {
              logout();
              setMobileSidebarOpen(false);
            }}
            type="button"
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-destructive hover:bg-destructive/10"
          >
            <LogOut className="h-5 w-5" />
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
