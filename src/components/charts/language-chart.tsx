"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { LanguageMetric } from "@/types/analytics";

interface LanguageChartProps {
  data: LanguageMetric[];
}

const COLORS = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#8b5cf6"];

export function LanguageChart({ data }: LanguageChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-xs text-muted-foreground">
        No language metrics available
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="count"
              nameKey="language"
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={4}
            >
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "rgba(15, 23, 42, 0.9)",
                borderRadius: "0.75rem",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                color: "#f8fafc",
                fontSize: "12px",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Legend list */}
      <div className="flex flex-wrap items-center justify-center gap-4 text-xs">
        {data.map((item, index) => (
          <div key={item.language} className="flex items-center gap-1.5">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: COLORS[index % COLORS.length] }}
            />
            <span className="font-medium text-foreground">{item.language}</span>
            <span className="text-muted-foreground">({item.percentage}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
