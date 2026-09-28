"use client";

import { AlertTriangle, X } from "lucide-react";

interface ConfirmationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: "danger" | "warning" | "info";
  isLoading?: boolean;
}

export function ConfirmationDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  variant = "danger",
  isLoading = false,
}: ConfirmationDialogProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-fade-in">
      <div className="glass-panel relative w-full max-w-md rounded-2xl border border-border/80 p-6 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-lg p-1 text-muted-foreground hover:bg-muted/40 hover:text-foreground"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="flex items-start gap-4">
          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
              variant === "danger"
                ? "bg-rose-500/10 text-rose-400"
                : variant === "warning"
                ? "bg-amber-500/10 text-amber-400"
                : "bg-brand-500/10 text-brand-400"
            }`}
          >
            <AlertTriangle className="h-5 w-5" />
          </div>

          <div className="space-y-1">
            <h3 className="text-base font-bold text-foreground">{title}</h3>
            <p className="text-xs text-muted-foreground">{description}</p>
          </div>
        </div>

        <div className="mt-6 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            disabled={isLoading}
            className="rounded-xl border border-border/60 bg-card px-4 py-2 text-xs font-medium text-foreground hover:bg-muted/50 disabled:opacity-50"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className={`rounded-xl px-4 py-2 text-xs font-semibold text-white shadow-md disabled:opacity-50 ${
              variant === "danger"
                ? "bg-rose-600 hover:bg-rose-500 shadow-rose-600/20"
                : "bg-brand-600 hover:bg-brand-500 shadow-brand-600/20"
            }`}
          >
            {isLoading ? "Processing..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
