"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bot, Eye, EyeOff, Lock, LogIn, Mail, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { useAuthStore } from "@/stores/auth-store";
import { Spinner } from "@/components/common/loading";

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading } = useAuthStore();
  const [username, setUsername] = useState("developer");
  const [password, setPassword] = useState("SuperSecretPassword123!");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      toast.error("Please enter both username/email and password.");
      return;
    }

    try {
      await login({ username, password });
      toast.success("Welcome back to CodePilot AI!");
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Authentication failed. Check your credentials.");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-6 bg-background relative overflow-hidden">
      {/* Background glow accents */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[450px] w-[450px] rounded-full bg-brand-500/10 blur-[100px] pointer-events-none" />

      <div className="w-full max-w-md space-y-6 relative z-10">
        {/* Header */}
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-brand-600 to-cyan-400 text-white shadow-xl shadow-brand-500/25 mb-2">
            <Bot className="h-6 w-6" />
          </Link>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Sign In to CodePilot AI</h1>
          <p className="text-xs text-muted-foreground">Access your automated code reviews and audit history</p>
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-border bg-card/80 p-8 shadow-xl backdrop-blur-xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-foreground mb-1.5">
                Username or Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="developer@codepilot.ai"
                  required
                  className="w-full rounded-xl border border-border bg-secondary/50 py-2.5 pl-10 pr-4 text-sm text-foreground focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold text-foreground">Password</label>
                <Link
                  href="/forgot-password"
                  className="text-[11px] font-medium text-brand-400 hover:text-brand-300"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full rounded-xl border border-border bg-secondary/50 py-2.5 pl-10 pr-10 text-sm text-foreground focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center gap-2 cursor-pointer text-muted-foreground">
                <input type="checkbox" defaultChecked className="rounded border-border" />
                <span>Remember me</span>
              </label>
              <span className="text-[11px] text-muted-foreground font-mono">Demo mode active</span>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 via-indigo-600 to-cyan-500 py-3 text-sm font-semibold text-white shadow-lg shadow-brand-500/25 hover:brightness-110 disabled:opacity-50 transition-all mt-2"
            >
              {isLoading ? <Spinner className="h-4 w-4" /> : <LogIn className="h-4 w-4" />}
              <span>Sign In</span>
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-muted-foreground">
            Don&apos;t have an account yet?{" "}
            <Link href="/register" className="font-semibold text-brand-400 hover:text-brand-300">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
