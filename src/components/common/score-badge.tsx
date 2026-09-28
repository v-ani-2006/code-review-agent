"use client";

import { getGradeColor } from "@/lib/utils";

interface ScoreBadgeProps {
  score: number;
  grade?: string;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

export function ScoreBadge({ score, grade, size = "md", showLabel = true }: ScoreBadgeProps) {
  // Compute grade from score if not provided
  let computedGrade = grade;
  if (!computedGrade) {
    if (score >= 90) computedGrade = "A";
    else if (score >= 80) computedGrade = "B";
    else if (score >= 70) computedGrade = "C";
    else if (score >= 60) computedGrade = "D";
    else computedGrade = "F";
  }

  const colors = getGradeColor(computedGrade);

  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs font-medium",
    md: "px-2.5 py-1 text-sm font-semibold",
    lg: "px-3.5 py-1.5 text-base font-bold",
  };

  return (
    <div className="inline-flex items-center gap-1.5">
      <span
        className={`inline-flex items-center rounded-full border ${colors.badge} ${sizeClasses[size]} transition-all`}
      >
        <span className={`mr-1.5 h-2 w-2 rounded-full ${colors.bg}`} />
        {computedGrade}
        {showLabel && <span className="ml-1 opacity-80">({score.toFixed(1)})</span>}
      </span>
    </div>
  );
}
