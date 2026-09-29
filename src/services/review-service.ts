import { apiClient } from "./api-client";
import { AIReviewResponse, ReviewReport } from "@/types/review";

export const reviewService = {
  // Fast AST + Complexity static review
  async analyzeText(code: string, filename = "main.py", language = "python"): Promise<ReviewReport> {
    const response = await apiClient.post<ReviewReport>("/review/text", {
      code,
      filename,
      language,
    });
    return response.data;
  },

  // Deep Gemini Flash review
  async aiReview(code: string, language = "python", detailLevel = "comprehensive"): Promise<AIReviewResponse> {
    const response = await apiClient.post<any>("/ai/review", {
      code,
      language,
      detail_level: detailLevel,
    });
    const data = response.data;
    const reviewData = data.review || data;

    // Build consolidated recommendations from review sections
    const recs: string[] = [];
    if (Array.isArray(reviewData.critical_issues)) recs.push(...reviewData.critical_issues);
    if (Array.isArray(reviewData.optimization_suggestions)) recs.push(...reviewData.optimization_suggestions);
    if (Array.isArray(reviewData.refactoring_suggestions)) recs.push(...reviewData.refactoring_suggestions);
    if (Array.isArray(reviewData.best_practices)) recs.push(...reviewData.best_practices);
    if (Array.isArray(reviewData.recommendations)) recs.push(...reviewData.recommendations);

    return {
      summary: reviewData.summary || data.message || "AI review completed successfully.",
      strengths: Array.isArray(reviewData.strengths) ? reviewData.strengths : ["Code is syntactically well-structured"],
      recommendations: recs.length > 0 ? recs : ["No major structural violations detected."],
      bugfix: reviewData.bugfix || data.bugfix || null,
      model_used: data.model_used || reviewData.model_used || "gemini-3.1-flash-lite",
      processing_time: data.processing_time || reviewData.processing_time || 0,
    };
  },

  // Explain code complexity and execution flow
  async explainCode(code: string, language = "python"): Promise<{ explanation: string; time_complexity: string; space_complexity: string }> {
    const response = await apiClient.post("/ai/explain", {
      code,
      language,
    });
    return response.data;
  },

  // Automated performance optimizations
  async optimizeCode(code: string, language = "python"): Promise<{ optimized_code: string; optimization_notes: string; expected_gain: string }> {
    const response = await apiClient.post("/ai/optimize", {
      code,
      language,
    });
    return response.data;
  },

  // Automated CVE & bug fix
  async fixBugs(code: string, language = "python", issueDescription = ""): Promise<{ fixed_code: string; explanation: string; diff: string }> {
    const response = await apiClient.post("/ai/bugfix", {
      code,
      language,
      issue_description: issueDescription,
    });
    return response.data;
  },

  // Generate docstrings and API docs
  async generateDocs(code: string, language = "python", docFormat = "google"): Promise<{ documented_code: string; markdown_docs: string }> {
    const response = await apiClient.post("/ai/documentation", {
      code,
      language,
      doc_format: docFormat,
    });
    return response.data;
  },

  // Generate Pytest unit tests
  async generateTests(code: string, language = "python", framework = "pytest"): Promise<{ test_code: string; test_cases_count: number }> {
    const response = await apiClient.post("/ai/tests", {
      code,
      language,
      framework,
    });
    return response.data;
  },

  // Generator endpoints
  async generateReadme(code: string): Promise<{ readme_markdown: string }> {
    const response = await apiClient.post("/generators/readme", { code });
    return response.data;
  },

  async generateArchitecture(code: string): Promise<{ architecture_markdown: string; mermaid_diagram: string }> {
    const response = await apiClient.post("/generators/architecture", { code });
    return response.data;
  },

  async generateChangelog(code: string): Promise<{ changelog_markdown: string }> {
    const response = await apiClient.post("/generators/changelog", { code });
    return response.data;
  },
};
