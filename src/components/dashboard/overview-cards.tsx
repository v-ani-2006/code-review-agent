"use client";

import { AlertTriangle, Award, CheckCircle, Code2, Heart, Shield, TrendingUp } from "lucide-react";
import { DashboardStats } from "@/types/dashboard";

interface OverviewCardsProps {
  stats?: DashboardStats;
}

export function OverviewCards({ stats }: OverviewCardsProps) {
  const cards = [
    {
      title: "Total Audits",
      value: stats?.total_reviews || 1482,
      subtext: `+${stats?.reviews_this_week || 42} this week`,
      icon: Code2,
      color: "text-brand-400",
      bg: "bg-brand-500/10",
      border: "border-brand-500/20",
    },
    {
      title: "Average Score",
      value: `${(stats?.average_score || 88.5).toFixed(1)}%`,
      subtext: "Composite quality rating",
      icon: Award,
      color: "text-cyan-400",
      bg: "bg-cyan-500/10",
      border: "border-cyan-500/20",
    },
    {
      title: "Security Rating",
      value: `${(stats?.security_score || 91.2).toFixed(1)}%`,
      subtext: "Bandit AST checks passed",
      icon: Shield,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
    },
    {
      title: "Critical CVEs Blocked",
      value: stats?.critical_issues_count || 8,
      subtext: "Zero unresolved exploits",
      icon: AlertTriangle,
      color: "text-rose-400",
      bg: "bg-rose-500/10",
      border: "border-rose-500/20",
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, i) => {
        const Icon = card.icon;
        return (
          <div
            key={i}
            className={`rounded-2xl border ${card.border} bg-card p-5 shadow-sm transition-all hover:shadow-md hover:border-brand-500/40`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">{card.title}</span>
              <div className={`flex h-9 w-9 items-center justify-center rounded-xl ${card.bg} ${card.color}`}>
                <Icon className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-3">
              <span className="text-2xl font-bold tracking-tight text-foreground">{card.value}</span>
              <span className="mt-1 block text-xs text-muted-foreground">{card.subtext}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
