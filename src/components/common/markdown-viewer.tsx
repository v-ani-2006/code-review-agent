"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CopyButton } from "./copy-button";

interface MarkdownViewerProps {
  content: string;
  className?: string;
}

export function MarkdownViewer({ content, className = "" }: MarkdownViewerProps) {
  return (
    <div className={`prose prose-invert max-w-none prose-pre:p-0 prose-pre:bg-transparent ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || "");
            const codeString = String(children).replace(/\n$/, "");

            if (!inline) {
              return (
                <div className="relative my-4 overflow-hidden rounded-xl border border-border bg-[#0d1117] font-mono text-xs">
                  <div className="flex items-center justify-between border-b border-border/80 bg-secondary/30 px-4 py-1.5 text-xs text-muted-foreground">
                    <span>{match ? match[1].toUpperCase() : "CODE"}</span>
                    <CopyButton text={codeString} />
                  </div>
                  <pre className="p-4 overflow-x-auto text-slate-200">
                    <code className={className} {...props}>
                      {children}
                    </code>
                  </pre>
                </div>
              );
            }
            return (
              <code className="rounded bg-secondary/80 px-1.5 py-0.5 font-mono text-xs text-brand-300" {...props}>
                {children}
              </code>
            );
          },
          table({ children }) {
            return (
              <div className="my-4 overflow-x-auto rounded-xl border border-border">
                <table className="w-full text-left text-sm">{children}</table>
              </div>
            );
          },
          th({ children }) {
            return <th className="border-b border-border bg-secondary/50 px-4 py-2 font-semibold text-foreground">{children}</th>;
          },
          td({ children }) {
            return <td className="border-b border-border/50 px-4 py-2 text-muted-foreground">{children}</td>;
          },
          h1({ children }) {
            return <h1 className="text-2xl font-bold tracking-tight text-foreground mt-6 mb-3">{children}</h1>;
          },
          h2({ children }) {
            return <h2 className="text-xl font-semibold tracking-tight text-foreground mt-5 mb-2.5">{children}</h2>;
          },
          h3({ children }) {
            return <h3 className="text-lg font-semibold text-foreground mt-4 mb-2">{children}</h3>;
          },
          p({ children }) {
            return <p className="leading-relaxed text-muted-foreground mb-3">{children}</p>;
          },
          ul({ children }) {
            return <ul className="list-disc list-inside space-y-1 text-muted-foreground mb-3">{children}</ul>;
          },
          ol({ children }) {
            return <ol className="list-decimal list-inside space-y-1 text-muted-foreground mb-3">{children}</ol>;
          },
          blockquote({ children }) {
            return (
              <blockquote className="border-l-4 border-brand-500 bg-brand-500/5 px-4 py-2 italic text-muted-foreground rounded-r-lg my-3">
                {children}
              </blockquote>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
