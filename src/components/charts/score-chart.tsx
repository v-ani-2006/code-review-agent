"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { TrendPoint } from "@/types/analytics";

interface ScoreChartProps {
  data: TrendPoint[];
}

export function ScoreChart({ data }: ScoreChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-xs text-muted-foreground">
        No score trajectory data available
      </div>
    );
  }

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="securityGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="date" stroke="#6b7280" fontSize={11} tickLine={false} />
          <YAxis domain={[50, 100]} stroke="#6b7280" fontSize={11} tickLine={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(15, 23, 42, 0.9)",
              borderRadius: "0.75rem",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              color: "#f8fafc",
              fontSize: "12px",
            }}
          />
          <Area
            type="monotone"
            dataKey="score"
            name="Overall Score"
            stroke="#6366f1"
            strokeWidth={2.5}
            fillOpacity={1}
            fill="url(#scoreGradient)"
          />
          <Area
            type="monotone"
            dataKey="security_score"
            name="Security Score"
            stroke="#10b981"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#securityGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
