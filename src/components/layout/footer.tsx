import Link from "next/link";
import { Bot, GitBranch, Github, Heart } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border/80 bg-background/50 px-6 py-6 text-xs text-muted-foreground backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 md:flex-row">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-brand-500/10 text-brand-400">
            <Bot className="h-3.5 w-3.5" />
          </div>
          <span className="font-semibold text-foreground">CodePilot AI</span>
          <span>— Production AST & Gemini Code Review</span>
          <span className="rounded bg-secondary px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">
            v1.0.0
          </span>
        </div>

        <div className="flex items-center gap-6">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="hover:text-foreground transition-colors"
          >
            Swagger API
          </a>
          <a
            href="https://github.com/v-ani-2006/code-review-agent"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 hover:text-foreground transition-colors"
          >
            <Github className="h-3.5 w-3.5" />
            GitHub
          </a>
          <Link href="/monitoring" className="hover:text-foreground transition-colors">
            System Status
          </Link>
        </div>
      </div>
    </footer>
  );
}
