"use client";

import { ActivityItem } from "@/types/dashboard";
import { AlertCircle, CheckCircle2, Code2, Upload } from "lucide-react";

interface ActivityFeedProps {
  items: ActivityItem[];
}

export function ActivityFeed({ items }: ActivityFeedProps) {
  const getIcon = (type: string) => {
    switch (type) {
      case "security_alert":
        return <AlertCircle className="h-4 w-4 text-rose-400" />;
      case "upload":
        return <Upload className="h-4 w-4 text-cyan-400" />;
      default:
        return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
    }
  };

  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
      <h3 className="text-base font-semibold text-foreground mb-1">Live Activity Stream</h3>
      <p className="text-xs text-muted-foreground mb-4">Real-time audit events and security checks</p>

      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.id} className="flex items-start gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-secondary border border-border">
              {getIcon(item.type)}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-semibold text-foreground">{item.title}</h4>
                <span className="text-[10px] text-muted-foreground">{item.timestamp}</span>
              </div>
              <p className="mt-0.5 text-xs text-muted-foreground">{item.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
