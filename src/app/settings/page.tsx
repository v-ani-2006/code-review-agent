"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { useTheme } from "next-themes";
import { CopyButton } from "@/components/common/copy-button";
import { toast } from "sonner";
import {
  Key,
  Moon,
  Sun,
  Laptop,
  Bell,
  Shield,
  Trash2,
  Sparkles,
  Zap,
  CheckCircle2,
  RefreshCw,
  Plus,
} from "lucide-react";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [apiKey, setApiKey] = useState("cp_live_99d8b742e88147d3aa40c21340b");
  const [copiedKey, setCopiedKey] = useState(false);

  // Notification toggles
  const [notifyOnComplete, setNotifyOnComplete] = useState(true);
  const [notifyOnSecurity, setNotifyOnSecurity] = useState(true);
  const [notifyWeeklyDigest, setNotifyWeeklyDigest] = useState(false);

  const handleGenerateKey = () => {
    const newKey = "cp_live_" + Array.from(crypto.getRandomValues(new Uint8Array(16)))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    setApiKey(newKey);
    toast.success("Generated new production API key");
  };

  const handlePurgeCache = () => {
    toast.success("Redis cache invalidated successfully");
  };

  return (
    <AppShell
      breadcrumbs={[
        { label: "Dashboard", href: "/dashboard" },
        { label: "Settings", href: "/settings" },
      ]}
    >
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
            Settings & Preferences
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Configure appearance, authentication tokens, automated notifications, and connected services.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            {/* Theme Settings */}
            <div className="glass-panel space-y-4 rounded-2xl p-6">
              <h3 className="text-base font-semibold text-foreground">Appearance & Interface Theme</h3>
              <p className="text-xs text-muted-foreground">
                Customize how CodePilot AI looks on your workstation.
              </p>
              <div className="grid grid-cols-3 gap-3 pt-2">
                <button
                  onClick={() => setTheme("dark")}
                  className={`flex flex-col items-center justify-center gap-2 rounded-xl border p-4 text-xs font-medium transition-all ${
                    theme === "dark"
                      ? "border-brand-500 bg-brand-500/10 text-brand-400 shadow-sm"
                      : "border-border/60 bg-card hover:bg-muted/50 text-muted-foreground"
                  }`}
                >
                  <Moon className="h-5 w-5" />
                  Dark Theme
                </button>

                <button
                  onClick={() => setTheme("light")}
                  className={`flex flex-col items-center justify-center gap-2 rounded-xl border p-4 text-xs font-medium transition-all ${
                    theme === "light"
                      ? "border-brand-500 bg-brand-500/10 text-brand-400 shadow-sm"
                      : "border-border/60 bg-card hover:bg-muted/50 text-muted-foreground"
                  }`}
                >
                  <Sun className="h-5 w-5" />
                  Light Theme
                </button>

                <button
                  onClick={() => setTheme("system")}
                  className={`flex flex-col items-center justify-center gap-2 rounded-xl border p-4 text-xs font-medium transition-all ${
                    theme === "system"
                      ? "border-brand-500 bg-brand-500/10 text-brand-400 shadow-sm"
                      : "border-border/60 bg-card hover:bg-muted/50 text-muted-foreground"
                  }`}
                >
                  <Laptop className="h-5 w-5" />
                  System Default
                </button>
              </div>
            </div>

            {/* API Key Management */}
            <div className="glass-panel space-y-4 rounded-2xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-semibold text-foreground">API Access Keys</h3>
                  <p className="text-xs text-muted-foreground">
                    Authenticate CLI scripts, GitHub Actions, and CI/CD pipelines.
                  </p>
                </div>
                <button
                  onClick={handleGenerateKey}
                  className="flex items-center gap-1.5 rounded-xl bg-brand-600 px-3 py-1.5 text-xs font-semibold text-white shadow-md shadow-brand-500/20 transition-all hover:bg-brand-500"
                >
                  <Plus className="h-3.5 w-3.5" />
                  Roll Key
                </button>
              </div>

              <div className="flex items-center justify-between rounded-xl border border-border/80 bg-background/60 p-3 font-mono text-xs">
                <span className="text-foreground truncate max-w-sm sm:max-w-md">{apiKey}</span>
                <CopyButton text={apiKey} />
              </div>

              <div className="rounded-xl border border-border/40 bg-muted/20 p-3 text-xs text-muted-foreground">
                <p>
                  Include this key in your HTTP requests as header:{" "}
                  <code className="text-brand-400 font-mono">Authorization: Bearer {apiKey.substring(0, 14)}...</code>
                </p>
              </div>
            </div>

            {/* Notification Preferences */}
            <div className="glass-panel space-y-4 rounded-2xl p-6">
              <h3 className="text-base font-semibold text-foreground">Notification Preferences</h3>
              <div className="space-y-4 pt-2">
                <label className="flex cursor-pointer items-center justify-between">
                  <div className="space-y-0.5">
                    <span className="text-xs font-medium text-foreground">Review Completed Alerts</span>
                    <p className="text-[11px] text-muted-foreground">
                      Receive an instant notification when asynchronous batch reviews complete
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifyOnComplete}
                    onChange={(e) => setNotifyOnComplete(e.target.checked)}
                    className="h-4 w-4 rounded border-border text-brand-600 focus:ring-brand-500"
                  />
                </label>

                <label className="flex cursor-pointer items-center justify-between">
                  <div className="space-y-0.5">
                    <span className="text-xs font-medium text-foreground">High-Severity Security Flag</span>
                    <p className="text-[11px] text-muted-foreground">
                      Immediate alert when CWE or SQLi vulnerabilities are detected
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifyOnSecurity}
                    onChange={(e) => setNotifyOnSecurity(e.target.checked)}
                    className="h-4 w-4 rounded border-border text-brand-600 focus:ring-brand-500"
                  />
                </label>

                <label className="flex cursor-pointer items-center justify-between">
                  <div className="space-y-0.5">
                    <span className="text-xs font-medium text-foreground">Weekly Digest</span>
                    <p className="text-[11px] text-muted-foreground">
                      Aggregated quality trend reports sent to registered email
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifyWeeklyDigest}
                    onChange={(e) => setNotifyWeeklyDigest(e.target.checked)}
                    className="h-4 w-4 rounded border-border text-brand-600 focus:ring-brand-500"
                  />
                </label>
              </div>
            </div>

            {/* Danger Zone */}
            <div className="glass-panel space-y-4 rounded-2xl border-rose-500/20 p-6 bg-rose-500/5">
              <h3 className="text-base font-semibold text-rose-400">Danger Zone</h3>
              <p className="text-xs text-muted-foreground">
                Irreversible actions affecting your inspection history and stored review reports.
              </p>
              <div className="flex flex-wrap items-center gap-3 pt-2">
                <button
                  onClick={handlePurgeCache}
                  className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-2 text-xs font-medium text-rose-300 hover:bg-rose-500/20"
                >
                  Purge Redis Cache
                </button>
                <button
                  onClick={() => toast.error("Account deletion is restricted for demo administrator")}
                  className="rounded-xl border border-rose-500/50 bg-rose-500 px-4 py-2 text-xs font-medium text-white hover:bg-rose-600"
                >
                  Delete Account
                </button>
              </div>
            </div>
          </div>

          {/* Connected Services Info */}
          <div className="space-y-6">
            <div className="glass-panel space-y-4 rounded-2xl p-6">
              <h3 className="text-base font-semibold text-foreground">Connected Services</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-xl border border-border/40 bg-muted/20 p-3">
                  <div className="flex items-center gap-2.5">
                    <Sparkles className="h-4 w-4 text-cyan-400" />
                    <div>
                      <span className="text-xs font-medium text-foreground">Gemini 2.5 Flash</span>
                      <p className="text-[10px] text-muted-foreground">Active LLM Provider</p>
                    </div>
                  </div>
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                </div>

                <div className="flex items-center justify-between rounded-xl border border-border/40 bg-muted/20 p-3">
                  <div className="flex items-center gap-2.5">
                    <Zap className="h-4 w-4 text-rose-400" />
                    <div>
                      <span className="text-xs font-medium text-foreground">Redis Server</span>
                      <p className="text-[10px] text-muted-foreground">Rate limit & token cache</p>
                    </div>
                  </div>
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                </div>
              </div>
            </div>

            <div className="glass-panel space-y-3 rounded-2xl p-6 text-xs text-muted-foreground">
              <h4 className="font-semibold text-foreground">CodePilot AI Version</h4>
              <p>v1.0.0-production (Build commit 2cf03d2)</p>
              <p>© 2026 CodePilot AI Inc. All rights reserved.</p>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
