"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { Check, Copy, FileCode, Play, RotateCcw, Sparkles, Upload } from "lucide-react";
import { SAMPLE_PYTHON_CODE, SUPPORTED_LANGUAGES } from "@/lib/constants";
import { useReviewStore } from "@/stores/review-store";
import { Spinner } from "@/components/common/loading";

// Dynamically import Monaco Editor to prevent SSR window issues
const Editor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[420px] w-full items-center justify-center rounded-xl border border-border bg-[#1e1e1e] text-xs text-muted-foreground">
      <Spinner className="mr-2 h-4 w-4" /> Loading Monaco Code Editor...
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

      {/* Monaco Code Editor Container */}
      <div className="h-[420px] w-full bg-[#1e1e1e]">
        <Editor
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
      </div>
    </div>
  );
}
