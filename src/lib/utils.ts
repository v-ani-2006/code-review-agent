import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

export function formatDate(dateString: string | undefined): string {
  if (!dateString) return "N/A";
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  } catch {
    return dateString;
  }
}

export function getGradeColor(grade: string | undefined): {
  badge: string;
  text: string;
  bg: string;
  border: string;
} {
  const g = (grade || "C").toUpperCase();
  if (g.startsWith("A")) {
    return {
      badge: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
      text: "text-emerald-400",
      bg: "bg-emerald-500",
      border: "border-emerald-500",
    };
  }
  if (g.startsWith("B")) {
    return {
      badge: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
      text: "text-cyan-400",
      bg: "bg-cyan-500",
      border: "border-cyan-500",
    };
  }
  if (g.startsWith("C")) {
    return {
      badge: "bg-amber-500/10 text-amber-400 border-amber-500/20",
      text: "text-amber-400",
      bg: "bg-amber-500",
      border: "border-amber-500",
    };
  }
  return {
    badge: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    text: "text-rose-400",
    bg: "bg-rose-500",
    border: "border-rose-500",
  };
}

export function getScoreColor(score: number): string {
  if (score >= 85) return "text-emerald-400";
  if (score >= 70) return "text-cyan-400";
  if (score >= 50) return "text-amber-400";
  return "text-rose-400";
}
