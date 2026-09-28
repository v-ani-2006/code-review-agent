import Link from "next/link";
import { Activity, BookOpen, Code2, FileCode, Sparkles, UploadCloud } from "lucide-react";

export function QuickActions() {
  const actions = [
    {
      title: "Interactive Review",
      description: "Paste snippet into Monaco Editor",
      href: "/review",
      icon: Code2,
      color: "from-brand-600 to-indigo-600",
    },
    {
      title: "Upload Project Zip",
      description: "Batch audit full repository archive",
      href: "/upload",
      icon: UploadCloud,
      color: "from-indigo-600 to-cyan-600",
    },
    {
      title: "AI Documentation",
      description: "Generate README, docstrings & tests",
      href: "/documentation",
      icon: FileCode,
      color: "from-purple-600 to-pink-600",
    },
    {
      title: "System Diagnostics",
      description: "Inspect Redis, Postgres & Gemini",
      href: "/monitoring",
      icon: Activity,
      color: "from-emerald-600 to-teal-600",
    },
  ];

  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
      <h3 className="text-base font-semibold text-foreground mb-1">Quick Actions</h3>
      <p className="text-xs text-muted-foreground mb-4">Fast shortcuts to core AI services</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {actions.map((act, i) => {
          const Icon = act.icon;
          return (
            <Link
              key={i}
              href={act.href}
              className="group flex flex-col justify-between rounded-xl border border-border bg-secondary/30 p-4 transition-all hover:bg-secondary/60 hover:border-brand-500/40"
            >
              <div className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr ${act.color} text-white mb-3 shadow-md shadow-brand-500/10`}>
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-foreground group-hover:text-brand-300 transition-colors">
                  {act.title}
                </h4>
                <p className="mt-0.5 text-xs text-muted-foreground">{act.description}</p>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
