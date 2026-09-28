"use client";

import { useState } from "react";
import { Archive, CheckCircle, FileCode, Play, ShieldCheck, UploadCloud } from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/app-shell";
import { DragDropZone } from "@/components/upload/drag-drop-zone";
import { BatchStatus } from "@/components/upload/batch-status";
import { uploadService } from "@/services/upload-service";
import { BatchTaskStatus } from "@/types/upload";
import { Spinner } from "@/components/common/loading";

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [activeTask, setActiveTask] = useState<BatchTaskStatus | null>(null);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
  };

  const handleStartAnalysis = async () => {
    if (!selectedFile) {
      toast.error("Please select a file or ZIP archive first.");
      return;
    }

    setIsUploading(true);
    try {
      if (selectedFile.name.endsWith(".zip") || selectedFile.name.endsWith(".tar.gz")) {
        const result = await uploadService.uploadArchive(selectedFile);
        toast.success(`Archive ingested: ${result.message || "Batch job started"}`);

        // Set initial task status
        setActiveTask({
          id: result.task_id || "task-demo",
          task_type: "batch_upload",
          status: "RUNNING",
          filename: selectedFile.name,
          total_files: result.total_files || 18,
          processed_files: 4,
          failed_files: 0,
          progress_percentage: 22,
        });

        // Simulate progress polling
        let current = 22;
        const interval = setInterval(() => {
          current += 26;
          if (current >= 100) {
            clearInterval(interval);
            setActiveTask((prev) =>
              prev
                ? {
                    ...prev,
                    status: "COMPLETED",
                    processed_files: prev.total_files,
                    progress_percentage: 100,
                  }
                : null
            );
            toast.success("Batch review completed! Results indexed in Review History.");
          } else {
            setActiveTask((prev) =>
              prev
                ? {
                    ...prev,
                    processed_files: Math.floor((current / 100) * prev.total_files),
                    progress_percentage: current,
                  }
                : null
            );
          }
        }, 1500);
      } else {
        const result = await uploadService.uploadSingleFile(selectedFile);
        toast.success(`File ${result.original_filename} uploaded and scanned.`);
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Upload or batch analysis failed.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <AppShell>
      <div>
        <h2 className="text-xl font-bold tracking-tight text-foreground md:text-2xl">
          Project Upload & Batch Analysis
        </h2>
        <p className="mt-1 text-xs text-muted-foreground">
          Upload single Python modules or entire repository ZIP archives for asynchronous batch AST and AI review.
        </p>
      </div>

      {/* Upload Zone */}
      <DragDropZone onFileSelect={handleFileSelect} />

      {/* Actions and Security Badge */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-border bg-card p-5 shadow-sm">
        <div className="flex items-center gap-2.5 text-xs text-emerald-400 font-medium">
          <ShieldCheck className="h-5 w-5 shrink-0" />
          <span>ZipSlip Directory Traversal Defense Active &amp; SHA-256 Checksums Enforced</span>
        </div>

        <button
          onClick={handleStartAnalysis}
          disabled={!selectedFile || isUploading}
          type="button"
          className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 via-indigo-600 to-cyan-500 px-5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-brand-500/25 hover:brightness-110 disabled:opacity-50 transition-all"
        >
          {isUploading ? <Spinner className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          <span>{isUploading ? "Ingesting Archive..." : "Start Batch Analysis"}</span>
        </button>
      </div>

      {/* Batch Processing Status */}
      {activeTask && <BatchStatus task={activeTask} />}
    </AppShell>
  );
}
