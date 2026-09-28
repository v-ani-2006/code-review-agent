"use client";

import { CheckCircle, Lightbulb, Sparkles } from "lucide-react";
import { AIReviewResponse } from "@/types/review";

interface RecommendationCardProps {
  aiReview: AIReviewResponse;
}

export function RecommendationCard({ aiReview }: RecommendationCardProps) {
  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      <div className="rounded-2xl border border-brand-500/20 bg-brand-500/5 p-5">
        <div className="flex items-center gap-2 mb-2 text-brand-300 font-semibold text-sm">
          <Sparkles className="h-4 w-4" />
          <span>Gemini AI Executive Summary</span>
        </div>
        <p className="text-sm leading-relaxed text-slate-300">{aiReview.summary}</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Identified Strengths */}
        <div className="rounded-2xl border border-border bg-card p-5">
          <div className="flex items-center gap-2 mb-3 text-emerald-400 font-semibold text-sm">
            <CheckCircle className="h-4 w-4" />
            <span>Code Strengths</span>
          </div>
          <ul className="space-y-2 text-xs text-muted-foreground">
            {aiReview.strengths?.map((strength, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold">•</span>
                <span className="leading-relaxed">{strength}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Actionable Recommendations */}
        <div className="rounded-2xl border border-border bg-card p-5">
          <div className="flex items-center gap-2 mb-3 text-amber-400 font-semibold text-sm">
            <Lightbulb className="h-4 w-4" />
            <span>Actionable Improvements</span>
          </div>
          <ul className="space-y-2 text-xs text-muted-foreground">
            {aiReview.recommendations?.map((rec, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-amber-400 font-bold">•</span>
                <span className="leading-relaxed">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
