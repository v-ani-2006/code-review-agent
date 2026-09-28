"use client";

import { Sidebar } from "./sidebar";
import { Navbar } from "./navbar";
import { MobileSidebar } from "./mobile-sidebar";
import { Footer } from "./footer";
import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";

interface AppShellProps {
  children: React.ReactNode;
  breadcrumbs?: { label: string; href: string }[];
}

export function AppShell({ children, breadcrumbs }: AppShellProps) {
  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {/* Desktop Sidebar */}
      <Sidebar />

      {/* Mobile Drawer */}
      <MobileSidebar />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />

        {/* Optional Breadcrumb Nav */}
        {breadcrumbs && breadcrumbs.length > 0 && (
          <div className="border-b border-border/40 bg-card/20 px-4 py-2.5 md:px-8">
            <nav className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Link href="/dashboard" className="flex items-center gap-1 hover:text-foreground">
                <Home className="h-3 w-3" />
              </Link>
              {breadcrumbs.map((crumb, idx) => (
                <div key={crumb.href} className="flex items-center gap-1.5">
                  <ChevronRight className="h-3 w-3 text-muted-foreground/60" />
                  {idx === breadcrumbs.length - 1 ? (
                    <span className="font-semibold text-foreground">{crumb.label}</span>
                  ) : (
                    <Link href={crumb.href} className="hover:text-foreground">
                      {crumb.label}
                    </Link>
                  )}
                </div>
              ))}
            </nav>
          </div>
        )}

        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
          <div className="mx-auto max-w-7xl space-y-6">{children}</div>
        </main>
        <Footer />
      </div>
    </div>
  );
}
