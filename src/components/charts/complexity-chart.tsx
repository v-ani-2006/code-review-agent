"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { TrendPoint } from "@/types/analytics";

interface ComplexityChartProps {
  data: TrendPoint[];
}

export function ComplexityChart({ data }: ComplexityChartProps) {
  const chartData = (data || []).slice(-10);

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="date" stroke="#6b7280" fontSize={11} tickLine={false} />
          <YAxis stroke="#6b7280" fontSize={11} tickLine={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(15, 23, 42, 0.9)",
              borderRadius: "0.75rem",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              color: "#f8fafc",
              fontSize: "12px",
            }}
          />
          <Bar dataKey="complexity" name="Cyclomatic Complexity" fill="#06b6d4" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
