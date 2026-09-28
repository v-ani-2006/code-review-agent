"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { Check, Copy, FileCode, Play, RotateCcw, Sparkles, Upload, Code } from "lucide-react";
import { SAMPLE_PYTHON_CODE, SUPPORTED_LANGUAGES } from "@/lib/constants";
import { useReviewStore } from "@/stores/review-store";
import { Spinner } from "@/components/common/loading";

// Error boundary to catch any CDN or runtime failure in Monaco Editor
class MonacoErrorBoundary extends React.Component<
  { fallback: React.ReactNode; children: React.ReactNode; onError?: () => void },
  { hasError: boolean }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: any) {
    console.warn("[CodePilot] Monaco Editor caught in boundary, switching to native editor:", error);
    this.props.onError?.();
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

// Resilient native code editor (works offline, 0 CDN dependency, fast & reliable)
function NativeCodeEditor({
  value,
  onChange,
}: {
  value: string;
  onChange: (val: string) => void;
}) {
  const lineCount = value.split("\n").length;
  const lineNumbers = Array.from({ length: Math.max(lineCount, 15) }, (_, i) => i + 1);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const target = e.currentTarget;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      const newValue = value.substring(0, start) + "    " + value.substring(end);
      onChange(newValue);
      setTimeout(() => {
        target.selectionStart = target.selectionEnd = start + 4;
      }, 0);
    }
  };

  return (
    <div className="flex h-full w-full overflow-hidden bg-[#1e1e1e] font-mono text-[13px]">
      {/* Line Numbers Gutter */}
      <div className="select-none border-r border-[#333] bg-[#181818] px-3 py-3 text-right text-xs text-muted-foreground/40 font-mono min-w-[45px]">
        {lineNumbers.map((num) => (
          <div key={num} className="leading-6">
            {num}
          </div>
        ))}
      </div>
      {/* Code Textarea */}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        spellCheck={false}
        className="h-full w-full resize-none border-none bg-transparent p-3 font-mono text-[13px] leading-6 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-0"
        placeholder="Paste or write code here..."
      />
    </div>
  );
}

// Dynamically import Monaco Editor to prevent SSR window issues
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[420px] w-full items-center justify-center rounded-xl border border-border bg-[#1e1e1e] text-xs text-muted-foreground">
      <Spinner className="mr-2 h-4 w-4" /> Loading Code Editor...
    </div>
  ),
});

export function CodeEditor() {
  const {
    code,
    language,
    filename,
    isAnalyzing,
    isAiReviewing,
    setCode,
    setLanguage,
    setFilename,
    runStaticAnalysis,
    runAiReview,
    reset,
  } = useReviewStore();

  const [copied, setCopied] = useState(false);
  const [monacoFailed, setMonacoFailed] = useState(false);
  const [forceNative, setForceNative] = useState(false);

  // Catch unhandled Monaco loader failures gracefully
  useEffect(() => {
    import("@monaco-editor/react")
      .then(({ loader }) => {
        loader.init().catch((err) => {
          console.warn("[CodePilot] Monaco CDN unreachable, native fallback active:", err);
          setMonacoFailed(true);
        });
      })
      .catch(() => {
        setMonacoFailed(true);
      });
  }, []);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFilename(file.name);
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target?.result as string;
        setCode(text);
      };
      reader.readAsText(file);
    }
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const nativeEditorElement = (
    <NativeCodeEditor value={code} onChange={(val) => setCode(val)} />
  );

  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-card shadow-lg">
      {/* Editor Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border bg-secondary/30 px-4 py-2.5">
        <div className="flex items-center gap-2.5">
          <FileCode className="h-4 w-4 text-brand-400" />
          <input
            type="text"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            className="w-36 rounded-lg border border-border bg-background px-2.5 py-1 font-mono text-xs text-foreground focus:border-brand-500 focus:outline-none"
            placeholder="filename.py"
          />
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="rounded-lg border border-border bg-background px-2.5 py-1 text-xs text-foreground focus:border-brand-500 focus:outline-none"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.id} value={lang.id}>
                {lang.label}
              </option>
            ))}
          </select>

          {/* Mode Indicator / Toggle */}
          <button
            type="button"
            onClick={() => setForceNative(!forceNative)}
            title="Toggle between Monaco and High-Performance Native editor"
            className="hidden sm:inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-[11px] text-muted-foreground hover:bg-secondary hover:text-foreground border border-border/50 transition-colors"
          >
            <Code className="h-3 w-3 text-brand-400" />
            <span>{monacoFailed || forceNative ? "Native Editor" : "Monaco"}</span>
          </button>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {/* File Upload Trigger */}
          <label className="cursor-pointer inline-flex items-center gap-1 rounded-lg border border-border bg-background px-2.5 py-1 text-xs text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors">
            <Upload className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Upload</span>
            <input type="file" accept=".py,.js,.ts,.go" onChange={handleFileUpload} className="hidden" />
          </label>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            type="button"
            className="inline-flex items-center gap-1 rounded-lg border border-border bg-background px-2.5 py-1 text-xs text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            <span className="hidden sm:inline">{copied ? "Copied" : "Copy"}</span>
          </button>

          {/* Reset Button */}
          <button
            onClick={reset}
            type="button"
            className="inline-flex items-center gap-1 rounded-lg border border-border bg-background px-2.5 py-1 text-xs text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
            title="Reset to sample code"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>

          {/* Run Static AST Analysis */}
          <button
            onClick={runStaticAnalysis}
            disabled={isAnalyzing}
            type="button"
            className="inline-flex items-center gap-1.5 rounded-lg bg-secondary px-3 py-1 text-xs font-semibold text-foreground hover:bg-accent disabled:opacity-50 transition-colors"
          >
            {isAnalyzing ? <Spinner className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5 text-emerald-400" />}
            <span>AST Scan</span>
          </button>

          {/* Run Deep Gemini AI Review */}
          <button
            onClick={async () => {
              await runStaticAnalysis();
              await runAiReview();
            }}
            disabled={isAiReviewing || isAnalyzing}
            type="button"
            className="inline-flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-brand-600 to-indigo-600 px-3.5 py-1 text-xs font-semibold text-white shadow-md shadow-brand-500/20 hover:from-brand-500 hover:to-indigo-500 disabled:opacity-50 transition-all"
          >
            {isAiReviewing ? <Spinner className="h-3.5 w-3.5" /> : <Sparkles className="h-3.5 w-3.5 text-cyan-300" />}
            <span>Gemini AI Review</span>
          </button>
        </div>
      </div>

      {/* Code Editor Container */}
      <div className="h-[420px] w-full bg-[#1e1e1e]">
        {monacoFailed || forceNative ? (
          nativeEditorElement
        ) : (
          <MonacoErrorBoundary
            fallback={nativeEditorElement}
            onError={() => setMonacoFailed(true)}
          >
            <MonacoEditor
              height="100%"
              language={language === "python" ? "python" : language}
              theme="vs-dark"
              value={code}
              onChange={(val) => setCode(val || "")}
              options={{
                minimap: { enabled: true },
                fontSize: 13,
                lineNumbers: "on",
                scrollBeyondLastLine: false,
                automaticLayout: true,
                tabSize: 4,
                padding: { top: 12, bottom: 12 },
                fontFamily: "JetBrains Mono, Menlo, Monaco, Consolas, monospace",
              }}
            />
          </MonacoErrorBoundary>
        )}
      </div>
    </div>
  );
}
