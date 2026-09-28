"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Bot, Mail, Send } from "lucide-react";
import { toast } from "sonner";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setSubmitted(true);
    toast.success("Password reset instructions dispatched to your email!");
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-6 bg-background relative overflow-hidden">
      <div className="w-full max-w-md space-y-6 relative z-10">
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-brand-600 to-cyan-400 text-white shadow-xl shadow-brand-500/25 mb-2">
            <Bot className="h-6 w-6" />
          </Link>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Reset Password</h1>
          <p className="text-xs text-muted-foreground">Enter your verified account email to recover access</p>
        </div>

        <div className="rounded-2xl border border-border bg-card/80 p-8 shadow-xl backdrop-blur-xl">
          {submitted ? (
            <div className="text-center space-y-4">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400">
                <Mail className="h-6 w-6" />
              </div>
              <h3 className="text-sm font-semibold text-foreground">Check your inbox</h3>
              <p className="text-xs text-muted-foreground">
                We sent a password recovery link to <span className="font-semibold text-foreground">{email}</span>.
              </p>
              <Link
                href="/login"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand-400 hover:text-brand-300 pt-2"
              >
                <ArrowLeft className="h-3.5 w-3.5" /> Back to Sign In
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-foreground mb-1.5">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="developer@company.com"
                    required
                    className="w-full rounded-xl border border-border bg-secondary/50 py-2.5 pl-10 pr-4 text-sm text-foreground focus:border-brand-500 focus:outline-none"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 py-3 text-sm font-semibold text-white shadow-lg shadow-brand-500/25 hover:brightness-110 transition-all"
              >
                <Send className="h-4 w-4" />
                <span>Send Reset Link</span>
              </button>

              <div className="text-center pt-2">
                <Link
                  href="/login"
                  className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  <ArrowLeft className="h-3.5 w-3.5" /> Back to Sign In
                </Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
