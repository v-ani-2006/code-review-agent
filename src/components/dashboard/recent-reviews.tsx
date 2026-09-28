"use client";

import Link from "next/link";
import { ArrowRight, Code2, ExternalLink } from "lucide-react";
import { RecentReviewItem } from "@/types/dashboard";
import { ScoreBadge } from "@/components/common/score-badge";
import { formatDate } from "@/lib/utils";

interface RecentReviewsProps {
  items: RecentReviewItem[];
}

export function RecentReviews({ items }: RecentReviewsProps) {
  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-foreground">Recent Audits</h3>
          <p className="text-xs text-muted-foreground">Latest reviewed files and static passes</p>
        </div>
        <Link
          href="/history"
          className="inline-flex items-center gap-1 text-xs font-semibold text-brand-400 hover:text-brand-300"
        >
          <span>View All</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      <div className="divide-y divide-border/60">
        {items.map((item) => (
          <div key={item.id} className="flex items-center justify-between py-3.5 hover:bg-secondary/20 px-2 rounded-xl transition-colors">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-secondary text-brand-400">
                <Code2 className="h-4 w-4" />
              </div>
              <div>
                <span className="font-mono text-xs font-semibold text-foreground block">
                  {item.filename}
                </span>
                <span className="text-[11px] text-muted-foreground">{formatDate(item.created_at)}</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <ScoreBadge score={item.overall_score} size="sm" />
              <Link
                href={`/history/${item.id}`}
                className="rounded-lg p-1 text-muted-foreground hover:text-foreground"
                title="View Review Details"
              >
                <ExternalLink className="h-4 w-4" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
