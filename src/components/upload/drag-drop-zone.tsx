"use client";

import { useCallback, useState } from "react";
import { Archive, CheckCircle, FileCode, UploadCloud } from "lucide-react";
import { formatBytes } from "@/lib/utils";

interface DragDropZoneProps {
  onFileSelect: (file: File) => void;
  accept?: string;
  maxSizeMB?: number;
}

export function DragDropZone({
  onFileSelect,
  accept = ".py,.zip,.tar.gz",
  maxSizeMB = 50,
}: DragDropZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        const file = e.dataTransfer.files[0];
        setSelectedFile(file);
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      className={`relative flex min-h-[240px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition-all ${
        isDragging
          ? "border-brand-500 bg-brand-500/10 scale-[1.01]"
          : "border-border hover:border-brand-500/50 hover:bg-secondary/20"
      }`}
    >
      <input
        type="file"
        accept={accept}
        onChange={handleChange}
        className="absolute inset-0 h-full w-full opacity-0 cursor-pointer"
      />

      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-500/10 text-brand-400 mb-4 shadow-lg shadow-brand-500/10">
        {selectedFile ? (
          selectedFile.name.endsWith(".zip") ? (
            <Archive className="h-8 w-8 text-cyan-400" />
          ) : (
            <FileCode className="h-8 w-8 text-emerald-400" />
          )
        ) : (
          <UploadCloud className="h-8 w-8 text-brand-400" />
        )}
      </div>

      {selectedFile ? (
        <div>
          <span className="font-semibold text-sm text-foreground block">{selectedFile.name}</span>
          <span className="text-xs text-muted-foreground">{formatBytes(selectedFile.size)}</span>
          <span className="mt-2 inline-flex items-center gap-1 text-xs text-emerald-400 font-medium">
            <CheckCircle className="h-3.5 w-3.5" /> Ready for Analysis
          </span>
        </div>
      ) : (
        <div>
          <h4 className="text-sm font-semibold text-foreground">
            Drag & drop your code file or project archive here
          </h4>
          <p className="mt-1 text-xs text-muted-foreground max-w-sm">
            Supports single Python scripts (<code>.py</code>) or zipped codebases (<code>.zip</code>, up to {maxSizeMB}MB)
          </p>
          <span className="mt-4 inline-flex items-center rounded-xl bg-secondary px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-accent transition-colors">
            Browse Computer
          </span>
        </div>
      )}
    </div>
  );
}
