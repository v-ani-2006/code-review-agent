"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { useHistory } from "@/hooks/use-history";
import { historyService } from "@/services/history-service";
import { ScoreBadge } from "@/components/common/score-badge";
import { SearchInput } from "@/components/common/search-input";
import { LoadingSpinner } from "@/components/common/loading";
import { EmptyState } from "@/components/common/empty-state";
import { ReviewListItem } from "@/types/review";
import { toast } from "sonner";
import {
  FileText,
  Download,
  Search,
  FileCode,
  FileArchive,
  Eye,
  Trash2,
  Calendar,
  Layers,
  Sparkles,
  ExternalLink,
} from "lucide-react";
import Link from "next/link";

export default function ReportsPage() {
  const [search, setSearch] = useState("");
  const { items: reports, isLoading } = useHistory({ search });
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const handleDownload = async (
    id: string,
    filename: string,
    format: "markdown" | "html" | "json"
  ) => {
    try {
      setDownloadingId(`${id}-${format}`);
      const blob = await historyService.downloadReport(id, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const ext = format === "markdown" ? "md" : format;
      a.download = `${filename.replace(/\.[^/.]+$/, "")}-report.${ext}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success(`Downloaded ${format.toUpperCase()} report`);
    } catch {
      toast.error(`Failed to download ${format.toUpperCase()} report`);
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <AppShell
      breadcrumbs={[
        { label: "Dashboard", href: "/dashboard" },
        { label: "Reports", href: "/reports" },
      ]}
    >
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
                Generated Review Deliverables
              </h1>
              <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-400">
                <FileArchive className="h-3 w-3" /> Multi-Format
              </span>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Instant downloads and export artifacts: Markdown, standalone HTML with syntax styling, JSON schemas, and ZIPs.
            </p>
          </div>

          <div className="w-full sm:w-72">
            <SearchInput
              value={search}
              onChange={setSearch}
              placeholder="Search reports by filename..."
            />
          </div>
        </div>

        {/* Reports Table/Grid */}
        {isLoading ? (
          <div className="flex h-72 items-center justify-center">
            <LoadingSpinner size="lg" text="Loading report archives..." />
          </div>
        ) : reports.length === 0 ? (
          <EmptyState
            title="No inspection reports found"
            description="Run a static code review or project upload to generate shareable audit reports."
            actionText="Start New Review"
            actionHref="/review"
          />
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {reports.map((report: ReviewListItem) => (
              <div
                key={report.id}
                className="glass-panel group relative flex flex-col gap-4 rounded-2xl p-5 transition-all hover:border-border/80 lg:flex-row lg:items-center lg:justify-between"
              >
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-500/10 text-brand-400 transition-colors group-hover:bg-brand-500/20">
                    <FileCode className="h-6 w-6" />
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Link
                        href={`/history/${report.id}`}
                        className="text-base font-semibold text-foreground transition-colors hover:text-brand-400"
                      >
                        {report.filename}
                      </Link>
                      <ScoreBadge score={report.overall_score} size="sm" />
                      <span className="rounded-md bg-secondary/80 px-2 py-0.5 text-[10px] uppercase font-mono tracking-wider text-muted-foreground">
                        {report.language}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-1">
                      {report.summary || "Full AST cyclomatic inspection & Gemini quality report."}
                    </p>
                    <div className="flex items-center gap-4 text-[11px] text-muted-foreground/70">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(report.created_at).toLocaleDateString(undefined, {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })}
                      </span>
                      <span>ID: {report.id.substring(0, 8)}</span>
                    </div>
                  </div>
                </div>

                {/* Export Format Actions */}
                <div className="flex flex-wrap items-center gap-2 pt-2 lg:pt-0">
                  <Link
                    href={`/history/${report.id}`}
                    className="flex items-center gap-1 rounded-xl border border-border/60 bg-secondary/40 px-3 py-1.5 text-xs font-medium text-foreground transition-all hover:bg-secondary"
                  >
                    <Eye className="h-3.5 w-3.5 text-muted-foreground" />
                    Preview
                  </Link>

                  <button
                    onClick={() => handleDownload(report.id, report.filename, "markdown")}
                    disabled={downloadingId === `${report.id}-markdown`}
                    className="flex items-center gap-1 rounded-xl border border-border/60 bg-card px-3 py-1.5 text-xs font-medium text-foreground transition-all hover:bg-muted/50 disabled:opacity-50"
                  >
                    <Download className="h-3.5 w-3.5 text-brand-400" />
                    .MD
                  </button>

                  <button
                    onClick={() => handleDownload(report.id, report.filename, "html")}
                    disabled={downloadingId === `${report.id}-html`}
                    className="flex items-center gap-1 rounded-xl border border-border/60 bg-card px-3 py-1.5 text-xs font-medium text-foreground transition-all hover:bg-muted/50 disabled:opacity-50"
                  >
                    <Download className="h-3.5 w-3.5 text-emerald-400" />
                    .HTML
                  </button>

                  <button
                    onClick={() => handleDownload(report.id, report.filename, "json")}
                    disabled={downloadingId === `${report.id}-json`}
                    className="flex items-center gap-1 rounded-xl border border-border/60 bg-card px-3 py-1.5 text-xs font-medium text-foreground transition-all hover:bg-muted/50 disabled:opacity-50"
                  >
                    <Download className="h-3.5 w-3.5 text-cyan-400" />
                    .JSON
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
