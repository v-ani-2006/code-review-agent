"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Code2,
  ExternalLink,
  Filter,
  Heart,
  Search,
  Trash2,
} from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/app-shell";
import { SearchInput } from "@/components/common/search-input";
import { ScoreBadge } from "@/components/common/score-badge";
import { Pagination } from "@/components/common/pagination";
import { EmptyState } from "@/components/common/empty-state";
import { useHistory } from "@/hooks/use-history";
import { formatDate } from "@/lib/utils";

export default function HistoryPage() {
  const [search, setSearch] = useState("");
  const [favoriteOnly, setFavoriteOnly] = useState(false);
  const [page, setPage] = useState(1);

  const { items, total, totalPages, isLoading, refetch } = useHistory({
    page,
    page_size: 10,
    search,
    favorite_only: favoriteOnly,
  });

  const filteredItems = items.filter((item) => {
    if (search && !item.filename.toLowerCase().includes(search.toLowerCase())) {
      return false;
    }
    if (favoriteOnly && !item.favorite) {
      return false;
    }
    return true;
  });

  return (
    <AppShell>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-foreground md:text-2xl">
            Review History &amp; Audits
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Search, inspect, and export past static analysis and AI reviews.
          </p>
        </div>

        {/* Filter controls */}
        <div className="flex items-center gap-3">
          <SearchInput
            value={search}
            onChange={(val) => {
              setSearch(val);
              setPage(1);
            }}
            className="w-56"
          />

          <button
            onClick={() => setFavoriteOnly(!favoriteOnly)}
            type="button"
            className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-semibold transition-all ${
              favoriteOnly
                ? "border-rose-500/40 bg-rose-500/10 text-rose-400"
                : "border-border bg-secondary/50 text-muted-foreground hover:bg-secondary hover:text-foreground"
            }`}
          >
            <Heart className={`h-3.5 w-3.5 ${favoriteOnly ? "fill-rose-400" : ""}`} />
            <span>Favorites</span>
          </button>
        </div>
      </div>

      {/* History Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden shadow-sm">
        {filteredItems.length === 0 ? (
          <div className="p-8">
            <EmptyState
              title="No audits found"
              description="No stored reviews match your current search or favorite filter criteria."
              actionText="Run New Review"
              actionHref="/review"
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-border bg-secondary/30 text-xs font-semibold text-muted-foreground">
                <tr>
                  <th className="py-3 px-4">Source File</th>
                  <th className="py-3 px-4">Language</th>
                  <th className="py-3 px-4">Overall Score</th>
                  <th className="py-3 px-4">Audited At</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {filteredItems.map((item) => (
                  <tr key={item.id} className="hover:bg-secondary/20 transition-colors">
                    <td className="py-3.5 px-4 font-mono text-xs font-medium text-foreground">
                      <div className="flex items-center gap-2.5">
                        <Code2 className="h-4 w-4 text-brand-400" />
                        <span>{item.filename}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-xs capitalize text-muted-foreground">
                      {item.language}
                    </td>
                    <td className="py-3.5 px-4">
                      <ScoreBadge score={item.overall_score} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 text-xs text-muted-foreground">
                      {formatDate(item.created_at)}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="inline-flex items-center gap-2">
                        <Link
                          href={`/history/${item.id}`}
                          className="inline-flex items-center gap-1 rounded-lg border border-border bg-secondary px-2.5 py-1 text-xs font-medium text-foreground hover:bg-accent transition-colors"
                        >
                          <ExternalLink className="h-3.5 w-3.5" />
                          <span>View Details</span>
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="p-4">
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={(p) => setPage(p)}
          />
        </div>
      </div>
    </AppShell>
  );
}
