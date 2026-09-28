"use client";

import { useState } from "react";
import { ArrowRight, Check, Copy, Download, GitCompare } from "lucide-react";
import { CopyButton } from "@/components/common/copy-button";

interface DiffViewerProps {
  originalCode: string;
  remediatedCode: string;
  title?: string;
}

export function DiffViewer({
  originalCode,
  remediatedCode,
  title = "Automated AI Remediation & Code Diff",
}: DiffViewerProps) {
  const [copied, setCopied] = useState(false);

  const handleDownload = () => {
    const blob = new Blob([remediatedCode], { type: "text/x-python" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "optimized_code.py";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-2xl border border-border bg-card overflow-hidden shadow-xl">
      {/* Header bar */}
      <div className="flex items-center justify-between border-b border-border bg-secondary/30 px-5 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
          <GitCompare className="h-4 w-4 text-brand-400" />
          <span>{title}</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleDownload}
            type="button"
            className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-background px-3 py-1 text-xs font-medium text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Download</span>
          </button>
          <CopyButton text={remediatedCode} />
        </div>
      </div>

      {/* Side-by-side view */}
      <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-border">
        {/* Left: Original Code */}
        <div className="p-4 bg-[#0d1117]">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-border/40 text-xs font-mono text-rose-400">
            <span>🔴 ORIGINAL (Vulnerable / Inefficient)</span>
          </div>
          <pre className="overflow-x-auto font-mono text-xs text-rose-200/90 leading-relaxed max-h-[380px]">
            {originalCode}
          </pre>
        </div>

        {/* Right: Remediated Code */}
        <div className="p-4 bg-[#0d1117]">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-border/40 text-xs font-mono text-emerald-400">
            <span>🟢 REMEDIATED (Hardened & Optimized)</span>
          </div>
          <pre className="overflow-x-auto font-mono text-xs text-emerald-200/90 leading-relaxed max-h-[380px]">
            {remediatedCode}
          </pre>
        </div>
      </div>
    </div>
  );
}
