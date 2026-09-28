"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bot, Lock, Mail, User, UserPlus } from "lucide-react";
import { toast } from "sonner";
import { useAuthStore } from "@/stores/auth-store";
import { Spinner } from "@/components/common/loading";

export default function RegisterPage() {
  const router = useRouter();
  const { register: registerUser, isLoading } = useAuthStore();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !email.trim() || !password.trim()) {
      toast.error("Please fill in all required fields.");
      return;
    }

    try {
      await registerUser({
        username,
        email,
        full_name: fullName,
        password,
      });
      toast.success("Account created successfully! Welcome to CodePilot AI.");
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Registration failed. Try a different username or email.");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-6 bg-background relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[450px] w-[450px] rounded-full bg-cyan-500/10 blur-[100px] pointer-events-none" />

      <div className="w-full max-w-md space-y-6 relative z-10">
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-brand-600 to-cyan-400 text-white shadow-xl shadow-brand-500/25 mb-2">
            <Bot className="h-6 w-6" />
          </Link>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Create Your Account</h1>
          <p className="text-xs text-muted-foreground">Start auditing codebases with AST & Google Gemini AI</p>
        </div>

        <div className="rounded-2xl border border-border bg-card/80 p-8 shadow-xl backdrop-blur-xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-foreground mb-1.5">Username *</label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="alex_dev"
                  required
                  className="w-full rounded-xl border border-border bg-secondary/50 py-2.5 pl-10 pr-4 text-sm text-foreground focus:border-brand-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-foreground mb-1.5">Full Name</label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Alex Rivers"
                  className="w-full rounded-xl border border-border bg-secondary/50 py-2.5 pl-10 pr-4 text-sm text-foreground focus:border-brand-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-foreground mb-1.5">Email Address *</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex@company.com"
                  required
                  className="w-full rounded-xl border border-border bg-secondary/50 py-2.5 pl-10 pr-4 text-sm text-foreground focus:border-brand-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-foreground mb-1.5">Password *</label>
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

            <button
              type="submit"
              disabled={isLoading}
              className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 via-indigo-600 to-cyan-500 py-3 text-sm font-semibold text-white shadow-lg shadow-brand-500/25 hover:brightness-110 disabled:opacity-50 transition-all mt-2"
            >
              {isLoading ? <Spinner className="h-4 w-4" /> : <UserPlus className="h-4 w-4" />}
              <span>Create Account</span>
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-muted-foreground">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-brand-400 hover:text-brand-300">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
