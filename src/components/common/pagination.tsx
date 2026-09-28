"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-between border-t border-border pt-4">
      <p className="text-xs text-muted-foreground">
        Showing page <span className="font-medium text-foreground">{currentPage}</span> of{" "}
        <span className="font-medium text-foreground">{totalPages}</span>
      </p>
      <div className="flex items-center gap-1.5">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-border text-muted-foreground hover:bg-secondary disabled:opacity-40 disabled:pointer-events-none transition-colors"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <span className="px-3 text-xs font-semibold text-foreground">
          {currentPage} / {totalPages}
        </span>
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-border text-muted-foreground hover:bg-secondary disabled:opacity-40 disabled:pointer-events-none transition-colors"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
