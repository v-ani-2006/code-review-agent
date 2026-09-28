import React from "react";
import Link from "next/link";
import { FolderSearch } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description: string;
  actionText?: string;
  actionHref?: string;
  icon?: React.ReactNode;
}

export function EmptyState({
  title,
  description,
  actionText,
  actionHref,
  icon,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border/80 p-12 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-500/10 text-brand-400 mb-4">
        {icon || <FolderSearch className="h-8 w-8" />}
      </div>
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      <p className="mt-1.5 max-w-sm text-sm text-muted-foreground">{description}</p>
      {actionText && actionHref && (
        <Link
          href={actionHref}
          className="mt-5 inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-lg shadow-brand-500/20 hover:from-brand-500 hover:to-indigo-500 transition-all"
        >
          {actionText}
        </Link>
      )}
    </div>
  );
}
