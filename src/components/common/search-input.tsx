"use client";

import { Search, X } from "lucide-react";

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function SearchInput({
  value,
  onChange,
  placeholder = "Search audits, files, rules...",
  className = "",
}: SearchInputProps) {
  return (
    <div className={`relative flex items-center ${className}`}>
      <Search className="absolute left-3.5 h-4 w-4 text-muted-foreground pointer-events-none" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-xl border border-border bg-secondary/50 py-2 pl-10 pr-9 text-sm text-foreground placeholder:text-muted-foreground focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 transition-colors"
      />
      {value && (
        <button
          onClick={() => onChange("")}
          type="button"
          className="absolute right-3 text-muted-foreground hover:text-foreground"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
