"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bot, CheckCircle, Lock } from "lucide-react";
import { toast } from "sonner";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      toast.error("Passwords do not match.");
      return;
    }
    toast.success("Password updated successfully! Please sign in.");
    router.push("/login");
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-6 bg-background relative overflow-hidden">
      <div className="w-full max-w-md space-y-6 relative z-10">
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-brand-600 to-cyan-400 text-white shadow-xl shadow-brand-500/25 mb-2">
            <Bot className="h-6 w-6" />
          </Link>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Set New Password</h1>
          <p className="text-xs text-muted-foreground">Create a secure password with at least 8 characters</p>
        </div>

        <div className="rounded-2xl border border-border bg-card/80 p-8 shadow-xl backdrop-blur-xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-foreground mb-1.5">New Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full rounded-xl border border-border bg-secondary/50 py-2.5 pl-10 pr-4 text-sm text-foreground focus:border-brand-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-foreground mb-1.5">Confirm New Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full rounded-xl border border-border bg-secondary/50 py-2.5 pl-10 pr-4 text-sm text-foreground focus:border-brand-500 focus:outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 py-3 text-sm font-semibold text-white shadow-lg shadow-brand-500/25 hover:brightness-110 transition-all"
            >
              <CheckCircle className="h-4 w-4" />
              <span>Update Password</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
