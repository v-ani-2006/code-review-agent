"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { useAuthStore } from "@/stores/auth-store";
import { toast } from "sonner";
import {
  User,
  Mail,
  Calendar,
  Shield,
  KeyRound,
  CheckCircle2,
  Award,
  Star,
  FileCode,
  Save,
  Lock,
} from "lucide-react";

export default function ProfilePage() {
  const { user } = useAuthStore();

  const [fullName, setFullName] = useState(user?.full_name || "CodePilot Developer");
  const [email, setEmail] = useState(user?.email || "developer@codepilot.ai");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleUpdateProfile = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success("Profile information updated successfully");
  };

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentPassword) {
      toast.error("Please enter your current password");
      return;
    }
    if (newPassword.length < 8) {
      toast.error("New password must be at least 8 characters");
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error("New passwords do not match");
      return;
    }
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    toast.success("Password changed successfully");
  };

  const initials = (user?.username || "Dev")
    .substring(0, 2)
    .toUpperCase();

  return (
    <AppShell
      breadcrumbs={[
        { label: "Dashboard", href: "/dashboard" },
        { label: "Profile", href: "/profile" },
      ]}
    >
      <div className="space-y-8">
        {/* Profile Card Header */}
        <div className="glass-panel relative overflow-hidden rounded-2xl p-6">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
            {/* Avatar */}
            <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-brand-600 via-indigo-600 to-cyan-500 text-2xl font-bold text-white shadow-xl shadow-brand-500/20">
              {initials}
            </div>

            <div className="space-y-1.5">
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
                  {fullName}
                </h1>
                <span className="flex items-center gap-1 rounded-full bg-brand-500/10 px-2.5 py-0.5 text-xs font-semibold text-brand-400">
                  <Shield className="h-3 w-3" />
                  {user?.is_admin ? "Administrator" : "Developer"}
                </span>
                <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-400">
                  <CheckCircle2 className="h-3 w-3" /> Active
                </span>
              </div>
              <p className="font-mono text-xs text-muted-foreground">@{user?.username || "developer"}</p>
              <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
                <span className="flex items-center gap-1.5">
                  <Mail className="h-3.5 w-3.5 text-brand-400" />
                  {email}
                </span>
                <span className="flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5 text-cyan-400" />
                  Joined September 2026
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="glass-panel rounded-2xl p-5">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Reviews Completed</span>
              <FileCode className="h-4 w-4 text-brand-400" />
            </div>
            <div className="mt-2 text-2xl font-bold text-foreground">1,482</div>
            <p className="mt-1 text-[11px] text-muted-foreground">Total automated code inspections</p>
          </div>

          <div className="glass-panel rounded-2xl p-5">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Starred Reviews</span>
              <Star className="h-4 w-4 text-amber-400" />
            </div>
            <div className="mt-2 text-2xl font-bold text-foreground">24</div>
            <p className="mt-1 text-[11px] text-muted-foreground">Flagged review blueprints</p>
          </div>

          <div className="glass-panel rounded-2xl p-5">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Average Code Score</span>
              <Award className="h-4 w-4 text-emerald-400" />
            </div>
            <div className="mt-2 text-2xl font-bold text-emerald-400">89.4 / 100</div>
            <p className="mt-1 text-[11px] text-muted-foreground">Quality rating across projects</p>
          </div>
        </div>

        {/* Forms Row: Edit Profile & Change Password */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Edit Profile */}
          <div className="glass-panel rounded-2xl p-6">
            <h3 className="text-base font-semibold text-foreground">Account Information</h3>
            <p className="text-xs text-muted-foreground">
              Update personal details and notification routing address.
            </p>

            <form onSubmit={handleUpdateProfile} className="mt-5 space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-foreground">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full rounded-xl border border-border/80 bg-background/50 px-3.5 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-foreground">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-xl border border-border/80 bg-background/50 px-3.5 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-foreground">Username</label>
                <input
                  type="text"
                  value={user?.username || "developer"}
                  disabled
                  className="w-full rounded-xl border border-border/40 bg-muted/30 px-3.5 py-2 font-mono text-xs text-muted-foreground"
                />
              </div>

              <button
                type="submit"
                className="flex items-center gap-1.5 rounded-xl bg-brand-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-brand-500/20 hover:bg-brand-500"
              >
                <Save className="h-3.5 w-3.5" />
                Save Changes
              </button>
            </form>
          </div>

          {/* Change Password */}
          <div className="glass-panel rounded-2xl p-6">
            <h3 className="text-base font-semibold text-foreground">Change Password</h3>
            <p className="text-xs text-muted-foreground">
              Ensure your account is protected with a robust master passphrase.
            </p>

            <form onSubmit={handleChangePassword} className="mt-5 space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-foreground">Current Password</label>
                <input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full rounded-xl border border-border/80 bg-background/50 px-3.5 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-foreground">New Password</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  className="w-full rounded-xl border border-border/80 bg-background/50 px-3.5 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-foreground">Confirm New Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Repeat new password"
                  className="w-full rounded-xl border border-border/80 bg-background/50 px-3.5 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
              </div>

              <button
                type="submit"
                className="flex items-center gap-1.5 rounded-xl bg-secondary px-4 py-2 text-xs font-semibold text-foreground hover:bg-secondary/80"
              >
                <Lock className="h-3.5 w-3.5 text-brand-400" />
                Update Password
              </button>
            </form>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
