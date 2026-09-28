"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { reviewService } from "@/services/review-service";
import { MarkdownViewer } from "@/components/common/markdown-viewer";
import { CopyButton } from "@/components/common/copy-button";
import { LoadingSpinner } from "@/components/common/loading";
import { SAMPLE_PYTHON_CODE } from "@/lib/constants";
import { toast } from "sonner";
import {
  FileText,
  Sparkles,
  BookOpen,
  GitBranch,
  CheckCircle2,
  Download,
  Copy,
  Layers,
  FlaskConical,
  RotateCcw,
} from "lucide-react";

type DocType = "readme" | "docstrings" | "architecture" | "tests" | "changelog";

export default function DocumentationPage() {
  const [activeType, setActiveType] = useState<DocType>("readme");
  const [code, setCode] = useState<string>(SAMPLE_PYTHON_CODE);
  const [docFormat, setDocFormat] = useState<string>("google");
  const [testFramework, setTestFramework] = useState<string>("pytest");
  const [loading, setLoading] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<"preview" | "raw">("preview");

  const [generatedContent, setGeneratedContent] = useState<string>(
    `# CodePilot AI Generated Documentation\n\nSelect a documentation generator above and click **Generate with Gemini AI** to produce professional READMEs, docstrings, architectural diagrams, or unit tests automatically.\n\n### Available Modules:\n* **README Generator**: High-impact GitHub repository README with installation, badges, and quickstart.\n* **Docstring & API Specs**: PEP 257 compliant documentation (Google, Sphinx, NumPy format).\n* **Architecture Specs**: System architecture blueprint with Mermaid sequence diagrams.\n* **Unit Test Suite**: Pytest test cases with boundary value mocks.\n* **Changelog**: Keep-A-Changelog semver changelog release notes.`
  );

  const handleGenerate = async () => {
    if (!code.trim()) {
      toast.error("Please provide Python source code to document");
      return;
    }

    setLoading(true);
    try {
      if (activeType === "readme") {
        const res = await reviewService.generateReadme(code);
        setGeneratedContent(res.readme_markdown);
        toast.success("Generated GitHub README");
      } else if (activeType === "docstrings") {
        const res = await reviewService.generateDocs(code, "python", docFormat);
        setGeneratedContent(
          `# Documented Source Code\n\`\`\`python\n${res.documented_code}\n\`\`\`\n\n# API Documentation\n${res.markdown_docs}`
        );
        toast.success(`Generated ${docFormat.toUpperCase()} Docstrings`);
      } else if (activeType === "architecture") {
        const res = await reviewService.generateArchitecture(code);
        setGeneratedContent(
          `${res.architecture_markdown}\n\n## Architecture Blueprint Diagram\n\`\`\`mermaid\n${res.mermaid_diagram}\n\`\`\``
        );
        toast.success("Generated Architecture Blueprint & Mermaid Diagram");
      } else if (activeType === "tests") {
        const res = await reviewService.generateTests(code, "python", testFramework);
        setGeneratedContent(
          `# Generated ${testFramework.toUpperCase()} Unit Test Suite\nGenerated **${res.test_cases_count}** test cases with edge cases and exception handling.\n\n\`\`\`python\n${res.test_code}\n\`\`\``
        );
        toast.success(`Generated Unit Tests with ${res.test_cases_count} test cases`);
      } else if (activeType === "changelog") {
        const res = await reviewService.generateChangelog(code);
        setGeneratedContent(res.changelog_markdown);
        toast.success("Generated Release Changelog");
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to generate documentation");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([generatedContent], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${activeType}-output.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success("Documentation downloaded");
  };

  return (
    <AppShell
      breadcrumbs={[
        { label: "Dashboard", href: "/dashboard" },
        { label: "Documentation", href: "/documentation" },
      ]}
    >
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
                AI Documentation & Scaffolding
              </h1>
              <span className="flex items-center gap-1 rounded-full bg-cyan-500/10 px-2.5 py-0.5 text-xs font-semibold text-cyan-400">
                <Sparkles className="h-3 w-3" /> Gemini 2.5
              </span>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Automatically generate production-grade READMEs, PEP 257 docstrings, Pytest suites, and architecture specs.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setCode(SAMPLE_PYTHON_CODE)}
              className="flex items-center gap-1.5 rounded-xl border border-border/60 bg-card px-3 py-2 text-xs font-medium text-foreground transition-all hover:bg-muted/50"
            >
              <RotateCcw className="h-3.5 w-3.5 text-muted-foreground" />
              Reset Sample
            </button>
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-brand-500/25 transition-all hover:opacity-90 disabled:opacity-50"
            >
              <Sparkles className="h-4 w-4" />
              {loading ? "Synthesizing Docs..." : "Generate with Gemini"}
            </button>
          </div>
        </div>

        {/* Generator Type Selector */}
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
          <button
            onClick={() => setActiveType("readme")}
            className={`flex items-center justify-center gap-2 rounded-xl border p-3 text-xs font-medium transition-all ${
              activeType === "readme"
                ? "border-brand-500/50 bg-brand-500/10 text-brand-400 shadow-sm"
                : "border-border/60 bg-card/60 text-muted-foreground hover:bg-card hover:text-foreground"
            }`}
          >
            <BookOpen className="h-4 w-4" />
            README.md
          </button>

          <button
            onClick={() => setActiveType("docstrings")}
            className={`flex items-center justify-center gap-2 rounded-xl border p-3 text-xs font-medium transition-all ${
              activeType === "docstrings"
                ? "border-brand-500/50 bg-brand-500/10 text-brand-400 shadow-sm"
                : "border-border/60 bg-card/60 text-muted-foreground hover:bg-card hover:text-foreground"
            }`}
          >
            <FileText className="h-4 w-4" />
            PEP 257 Docstrings
          </button>

          <button
            onClick={() => setActiveType("architecture")}
            className={`flex items-center justify-center gap-2 rounded-xl border p-3 text-xs font-medium transition-all ${
              activeType === "architecture"
                ? "border-brand-500/50 bg-brand-500/10 text-brand-400 shadow-sm"
                : "border-border/60 bg-card/60 text-muted-foreground hover:bg-card hover:text-foreground"
            }`}
          >
            <Layers className="h-4 w-4" />
            Architecture & Mermaid
          </button>

          <button
            onClick={() => setActiveType("tests")}
            className={`flex items-center justify-center gap-2 rounded-xl border p-3 text-xs font-medium transition-all ${
              activeType === "tests"
                ? "border-brand-500/50 bg-brand-500/10 text-brand-400 shadow-sm"
                : "border-border/60 bg-card/60 text-muted-foreground hover:bg-card hover:text-foreground"
            }`}
          >
            <FlaskConical className="h-4 w-4" />
            Pytest Unit Suite
          </button>

          <button
            onClick={() => setActiveType("changelog")}
            className={`flex items-center justify-center gap-2 rounded-xl border p-3 text-xs font-medium transition-all ${
              activeType === "changelog"
                ? "border-brand-500/50 bg-brand-500/10 text-brand-400 shadow-sm"
                : "border-border/60 bg-card/60 text-muted-foreground hover:bg-card hover:text-foreground"
            }`}
          >
            <GitBranch className="h-4 w-4" />
            Changelog Release
          </button>
        </div>

        {/* Options Row */}
        {activeType === "docstrings" && (
          <div className="flex items-center gap-3 rounded-xl border border-border/60 bg-card/60 px-4 py-2 text-xs">
            <span className="font-medium text-foreground">Docstring Format:</span>
            {["google", "sphinx", "numpy"].map((fmt) => (
              <label key={fmt} className="flex cursor-pointer items-center gap-1.5 capitalize text-muted-foreground hover:text-foreground">
                <input
                  type="radio"
                  name="docFormat"
                  value={fmt}
                  checked={docFormat === fmt}
                  onChange={(e) => setDocFormat(e.target.value)}
                  className="text-brand-600 focus:ring-brand-500"
                />
                {fmt} Style
              </label>
            ))}
          </div>
        )}

        {activeType === "tests" && (
          <div className="flex items-center gap-3 rounded-xl border border-border/60 bg-card/60 px-4 py-2 text-xs">
            <span className="font-medium text-foreground">Test Framework:</span>
            {["pytest", "unittest"].map((fw) => (
              <label key={fw} className="flex cursor-pointer items-center gap-1.5 capitalize text-muted-foreground hover:text-foreground">
                <input
                  type="radio"
                  name="testFramework"
                  value={fw}
                  checked={testFramework === fw}
                  onChange={(e) => setTestFramework(e.target.value)}
                  className="text-brand-600 focus:ring-brand-500"
                />
                {fw}
              </label>
            ))}
          </div>
        )}

        {/* Split Layout: Code Input vs Generated Output */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Source Code Input */}
          <div className="glass-panel flex flex-col rounded-2xl overflow-hidden">
            <div className="flex items-center justify-between border-b border-border/60 bg-muted/20 px-4 py-3">
              <span className="text-xs font-semibold text-foreground">Source Code Input (Python)</span>
              <span className="text-[11px] text-muted-foreground">{code.split("\n").length} lines</span>
            </div>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Paste Python class or function to document..."
              className="h-[520px] w-full resize-none bg-background/50 p-4 font-mono text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-0"
              spellCheck={false}
            />
          </div>

          {/* Generated Result Output */}
          <div className="glass-panel flex flex-col rounded-2xl overflow-hidden">
            <div className="flex items-center justify-between border-b border-border/60 bg-muted/20 px-4 py-2.5">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setViewMode("preview")}
                  className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                    viewMode === "preview"
                      ? "bg-brand-500/20 text-brand-400"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Rich Preview
                </button>
                <button
                  onClick={() => setViewMode("raw")}
                  className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                    viewMode === "raw"
                      ? "bg-brand-500/20 text-brand-400"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Raw Markdown
                </button>
              </div>

              <div className="flex items-center gap-1.5">
                <CopyButton text={generatedContent} />
                <button
                  onClick={handleDownload}
                  className="flex items-center gap-1 rounded-lg border border-border/60 bg-card px-2.5 py-1 text-xs font-medium text-foreground hover:bg-muted/50"
                  title="Download Markdown"
                >
                  <Download className="h-3 w-3 text-brand-400" />
                  Export .md
                </button>
              </div>
            </div>

            <div className="h-[520px] overflow-y-auto p-5">
              {loading ? (
                <div className="flex h-full items-center justify-center">
                  <LoadingSpinner
                    size="lg"
                    text={`Synthesizing ${activeType} with Gemini Flash...`}
                  />
                </div>
              ) : viewMode === "preview" ? (
                <MarkdownViewer content={generatedContent} />
              ) : (
                <pre className="whitespace-pre-wrap font-mono text-xs text-muted-foreground">
                  {generatedContent}
                </pre>
              )}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
